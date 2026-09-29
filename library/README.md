# Skill Lift submission library

`skills/` here becomes `submission.zip → skills/` (Track 1). Every skill follows
[SKILL-TEMPLATE.md](../SKILL-TEMPLATE.md); every skill gets a paired dev-set run
before it stays (`../run_paired.sh <task> _skill-lift/library/skills`).

## Roster (priority order — build top-down, ship whatever's proven by Aug 12)

**Layer 1 — core document/data stack** (largest public-task surface: xlsx×13, pdf×11)
1. ✅ `xlsx` (563w) — two-handle rule, recalc decision tree, type/format contracts.
2. ✅ `pdf` (498w) — diagnose-first, extraction quirks, AcroForm + NeedAppearances, overlay fallback.
3. ✅ `docx` (528w) — split-run-safe fills, MULTI-paragraph conditionals (bundled skill's known gap), rescan-verify.
4. ✅ `pptx` (799w, v7 2026-08-06) — object model, tables-from-data, placeholder enumeration, buAutoNum numbered bullets (XML snippet; no python-pptx API), dimension-choice overflow geometry, reference/agenda-slide working-set rule, atomic verify. (Bundled corpus version: 3,487w.)
5. ✅ `tabular-data` (470w) — dtype traps, join validation, output contracts.

**Layer 2 — domain packs** (target the top-lift domains from the paper: natural-science +28.8, media +24.1, cyber +18.9)
6. ✅ `media-ffmpeg` (~590w) — probe-first, copy-vs-reencode, silencedetect, ffprobe-verify.
7. ✅ `signal-timeseries` (504w) — FFT/Lomb-Scargle periodicity, filtering, peaks; replaces a vague "scientific-computing" plan with a concrete cross-domain method pack.
8. ✅ `build-repair` (~520w) — reproduce-first, classify code/config/dependency, minimal diff, prove green. (Corpus counterpart: a 4-skill pack incl. a 2,264w uv manual.)
9. ☐ `security-analysis` — DEFERRED pending regression study: suricata-custom-exfil regressed −7.4pp in the paper *despite well-sized skills* (198–466w) — the risk here is displacing model strategy, not verbosity. Design only with "advise, don't prescribe" evidence.
10. ✅ `optimization-modeling` (~560w) — formulate-first, tool-by-class (scipy.milp / CP-SAT / cvxpy / PDDL), feasibility debugging, **greedy-fallback-first framing** (exam-block-sequencing regressed −7.4pp in the paper via "solver the agent can't debug" — this skill is designed against that exact mode). ⚠️ Landed mid-breadth-sweep 2026-08-02 — sweep runs saw 10 or 11 skills depending on start time; annotate at aggregation. **LIBRARY FROZEN until sweep completes.**

**Layer 3 — conduct layer** (the differentiator; ClawsBench-facing)
11. ✅ `task-discipline` (448w) — contract checklist + verify-before-done. Description tuned 08-02 after trajectory audit showed conduct skills lose the "open" to domain attention.
12. ✅ `scope-safety` (462w) — one-way-door rules, injection resistance, calibrated non-refusal.

**Measured** (offer-letter-generator, haiku, n=3/arm, 2026-08-02 — `jobs/matrix-oflg*`): no-skill 0/3 · ours-v1 0/3 · **ours-v2 3/3** · bundled 3/3. V1 failed on nested-table placeholders (prose hint where haiku needed runnable recursion); v2's `all_paragraphs` walker + mandatory rescan-verify converted it fully. Standing static finding: the bundled docx skill can't handle multi-paragraph conditional blocks and its placeholder regex misses digit-bearing keys — kept ours superior on both.

**Measured** (pptx-reference-formatting, haiku, 2026-08-02→06 — `jobs/matrix-pptx*`, `jobs/pptx-v*-verify-*`): no-skill 0/2. Version arc v1→v7: 0/2, 1/3, 0/3, 0/3, 2/3, 1/3, 1/3, 1/3. Per-axis (the honest readout): **bullets 100% since v2** (buAutoNum snippet), **reference axis 4/6 fails → 0/3 after v7's working-set rule**, font-style 0 fails whenever the colors snippet is present (its removal in v6 regressed — caught by the change-control gate), titles-fit ≈50–60% residual compliance coin (agents sometimes skip the resize; v5's "2/3" was partially lucky on the reference axis).

Track 2 (`../track2/`): ONE meta-skill named `skill-creator` (harness interface
constraint — see `../track2/DESIGN.md` for the source-derived contract, stock-
creator gap table, and the Epistemic Ledger → authoring-gate mapping). Build day
Aug 9; three-arm self-gen experiment pre-registered in STRATEGY.md.
