#!/usr/bin/env python3
"""Aggregate pass/fail across benchflow job dirs.

Usage:
  uv run python _skill-lift/aggregate_matrix.py [tag]        # matrix-<tag>-<arm>-a<N> dirs (default: oflg)
  uv run python _skill-lift/aggregate_matrix.py --sweep jobs/glmsweep-ours jobs/glmsweep-none
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def valid_rewards(job_dir: Path) -> tuple[int, int, int]:
    """(pass, fail, excluded) from per-rollout records, honoring reward_valid.

    summary.json counts a verifier-never-ran rollout as a FAIL; the rollout's
    own record marks it reward_valid=False. Excluding those keeps paired lift
    honest (they're measurement failures, not task failures)."""
    p = f = x = 0
    for res in job_dir.glob("*/*__*/result.json"):
        r = json.loads(res.read_text())
        rw = (r.get("rewards") or {}).get("reward")
        vjs = res.parent / "trainer" / "verifiers.jsonl"
        invalid = False
        if vjs.exists():
            try:
                rec = json.loads(vjs.read_text().strip().splitlines()[-1])
                invalid = (rec.get("info") or {}).get("reward_valid") is False
            except Exception:
                pass
        if invalid or rw is None or r.get("error"):
            x += 1
        elif rw >= 1.0:
            p += 1
        else:
            f += 1
    return p, f, x


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "oflg"

    if tag == "--sweep":
        for jd in sys.argv[2:]:
            p, f, x = valid_rewards(REPO / jd)
            n = p + f
            rate = f"{p / n:.0%}" if n else "n/a"
            print(f"{jd}: pass {p} / fail {f} / excluded {x}  (valid pass rate {rate})")
        return

    arms = defaultdict(list)
    for summary in sorted(REPO.glob(f"jobs/matrix-{tag}-*/**/summary.json")):
        m = re.search(rf"matrix-{tag}-([a-z]+)-a(\d+)", str(summary))
        if not m:
            continue
        arm, attempt = m.group(1), int(m.group(2))
        d = json.loads(summary.read_text())
        arms[arm].append((attempt, d.get("pass", 0), d.get("fail", 0), d.get("error", 0)))

    print(f"{'arm':10s} {'attempts':>8s} {'pass':>5s} {'fail':>5s} {'err':>4s} {'pass rate':>9s}")
    for arm in sorted(arms):
        rows = sorted(set(arms[arm]))          # dedupe resumed dirs
        n = len(rows)
        p = sum(r[1] for r in rows)
        f = sum(r[2] for r in rows)
        e = sum(r[3] for r in rows)
        print(f"{arm:10s} {n:8d} {p:5d} {f:5d} {e:4d} {p/n if n else 0:9.0%}")

    if {"bundled", "none"} <= arms.keys():
        def rate(a):
            rows = sorted(set(arms[a]))
            return sum(r[1] for r in rows) / len(rows) if rows else 0.0
        print(f"\nlift (bundled vs none): {rate('bundled') - rate('none'):+.0%}")
        if "ours" in arms:
            print(f"lift (ours    vs none): {rate('ours') - rate('none'):+.0%}")


if __name__ == "__main__":
    main()
