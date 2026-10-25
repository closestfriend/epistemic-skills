#!/usr/bin/env python3
"""Verify SKILL.md files against Track 2 Epistemic Ledger & Calibration Gate rules."""

import re
import sys
from pathlib import Path

BANNED_DISCLAIMERS = (
    "may not always work",
    "might not work",
    "use with caution",
    "results may vary",
    "not guaranteed to work",
)

CONDUCT_SKILLS = {"task-discipline", "scope-safety"}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | tuple[None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text

    raw_yaml, body = parts[1].strip(), parts[2].strip()
    meta: dict[str, str] = {}
    current_key: str | None = None
    for line in raw_yaml.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            k, v = line.split(":", 1)
            current_key = k.strip()
            v_clean = v.strip().strip('"').strip("'")
            meta[current_key] = "" if v_clean in ("|", ">", "|-", ">-") else v_clean
        elif current_key:
            meta[current_key] = (meta[current_key] + " " + line.strip()).strip()
    return meta, body


def check_skill(skill_path: Path) -> list[str]:
    md_path = skill_path / "SKILL.md" if skill_path.is_dir() else skill_path
    if not md_path.is_file():
        return [f"Missing SKILL.md at {md_path}"]

    text = md_path.read_text(encoding="utf-8")
    errors: list[str] = []

    meta, body = parse_frontmatter(text)
    if meta is None:
        return ["Missing or malformed YAML frontmatter ('---')"]

    name = meta.get("name", "").strip()
    desc = meta.get("description", "").strip()
    skill_name = name or md_path.parent.name

    if not name:
        errors.append("Frontmatter missing 'name:' field")
    if not desc:
        errors.append("Frontmatter missing 'description:' field")
    else:
        desc_lower = desc.lower()
        if not any(t in desc_lower for t in ("use when", "use for", "read this first", "use whenever", "relevant when")):
            errors.append("Description missing positive trigger ('Use when...' / 'Use for...')")
        has_neg_in_desc = any(
            n in desc_lower for n in ("not for", "not needed for", "do not use", "don't use", "never use")
        )
        # Universal conduct skills (e.g. task-discipline) may state override boundary in Applicability
        if not has_neg_in_desc and skill_name not in CONDUCT_SKILLS:
            errors.append("Description missing negative boundary ('Not for...')")

    body_words = len(body.split())
    if body_words > 900:
        errors.append(f"Body word count ({body_words}) exceeds 900-word ceiling")

    app_match = re.search(
        r"^##\s+Applicability[^\n]*\n(.*?)(?=^##\s+|\Z)",
        body,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not app_match:
        errors.append("Missing '## Applicability & fallback' section")
    else:
        app_text = app_match.group(1)
        app_words = len(app_text.split())
        if body_words > 100 and (app_words / body_words) > 0.25:
            errors.append(
                f"Boundary-timidity violation: Applicability section is {app_words}/{body_words} words ({app_words/body_words:.0%} > 25%)"
            )
        # Strip quoted negative examples before checking for banned vague disclaimers
        unquoted_app = re.sub(r'["“”\'].*?["“”\']|`.*?`', "", app_text.lower())
        for phrase in BANNED_DISCLAIMERS:
            if phrase in unquoted_app:
                errors.append(
                    f"Banned vague disclaimer '{phrase}' in Applicability — use an observable condition + fallback"
                )

    code_blocks = re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", body, re.DOTALL)
    if skill_name not in CONDUCT_SKILLS and not code_blocks:
        errors.append("No executable code block found (weak models convert runnable snippets, not prose hints)")

    has_verify_heading = bool(
        re.search(
            r"^##\s+(Verify|Output\s+contract|Step\s+\d+\s+[—-]\s+prove|One-way\s+doors:\s+verify|Report\s+what\s+actually\s+happened)",
            body,
            re.MULTILINE | re.IGNORECASE,
        )
    )
    if not has_verify_heading:
        errors.append("Missing explicit verification / output-contract section")

    return errors


def main() -> int:
    targets = [Path(a) for a in sys.argv[1:]] or [Path(".")]
    skill_files: list[Path] = []
    for t in targets:
        if t.is_file() and t.name == "SKILL.md":
            skill_files.append(t)
        elif (t / "SKILL.md").is_file():
            skill_files.append(t / "SKILL.md")
        elif t.is_dir():
            skill_files.extend(sorted(t.rglob("SKILL.md")))

    if not skill_files:
        print("No SKILL.md files found.", file=sys.stderr)
        return 1

    failed = 0
    for sf in skill_files:
        errs = check_skill(sf)
        if errs:
            failed += 1
            print(f"[FAIL] {sf}:")
            for e in errs:
                print(f"  - {e}")
        else:
            _, body = parse_frontmatter(sf.read_text(encoding="utf-8"))
            print(f"[PASS] {sf} ({len(body.split())} body words)")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
