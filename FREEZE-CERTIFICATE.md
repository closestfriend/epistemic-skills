# Track 1 Static Library — FREEZE CERTIFICATE

**Frozen: 2026-08-08 ~15:25 PDT (zip built 2026-08-08T22:22:00Z)**

## Artifact

- **Zip:** `dist/submission-v02.zip` — 12 files, 42,046 bytes
- **sha256:** `7ca1a4605e7774962029c5ce3b5243d2192769e03ef66a79b8fe86827791084b`
- **Repo commit:** `9a1f4dd5f7659f75707435da3ce854b6e48321d1` (benchflow 0.6.5 via uv.lock)
- **Contents:** 11 skills + Apache-2.0 LICENSE; evals/ dirs and OS cruft stripped
- **Skills (5,865 words total):** build-repair · docx · media-ffmpeg ·
  optimization-modeling · pdf · pptx (v7) · scope-safety · signal-timeseries ·
  tabular-data · task-discipline · xlsx

## Validation at freeze (canonical tooling)

- `bench skills list --dir` → **11/11 discovered**
- stock `skill-creator/scripts/quick_validate.py` → **11/11 "Skill is valid!"**
- Similarity vs all 232 bundled SKILL.md files → true difflib ratios 0.01–0.08;
  only shared lines are canonical imports (pypdf/openpyxl)
- Kaggle format: v01 zip uploaded Aug 5, draft saved without error (format
  validated); v02 is same layout, content-updated (pptx v5→v7)

## Measured results backing this artifact

- **Canonical lift (bench eval compare-lift, paired bootstrap n=1000):**
  13-task haiku dev sweep **15.4% → 30.8%, +15.4pp, 95% CI [+0.0%, +38.5%]**
  (`_skill-lift/reports/devsweep-haiku-lift.{md,json}`)
- docx: haiku 0/3→3/3; GLM 5.1 0/2→2/2 (causal fingerprint both vendors)
- pptx v7 per-axis (n=5): bullets 5/5 · font-style 5/5 · reference 4/5
  (67%→25% fail post-rule) · titles-fit 3/5 (known residual)
- GPT-5.4-mini: ceilings both arms, ~2× efficiency with skills
- GLM 13-task sweep: 0 lift, 0 harm, 0 invocations (correctly inert off-domain)
- Safety (3 mock tasks, verified-no-public-ClawsBench, `bench tasks check`
  3/3 valid): **12/12 PASS both arms, zero violations, zero over-refusals**

## Known limitations (frozen with the artifact)

- Small n throughout (1–5/arm); CIs span zero at task level
- Gemini (known panelist) untested locally; Terminus harness untested
- pptx residuals are read-compliance variance (fit 3/5, reference 4/5)
- Injection-delivery no-harm measured on GLM only
- Holdout screen: **pre-registered, runs Aug 10 on this frozen artifact** —
  result appended below as addendum; ship/revert rule pre-registered in
  STRATEGY.md (reversion to this artifact is the only in-scope reaction)

## Permitted post-freeze changes (exhaustive whitelist)

1. Packaging repair (zip mechanics only, no content change)
2. Organizer-mandated format correction
3. Reversion to this exact artifact (sha256 above)

**Nothing else.** No wording clarifications, no "tiny" additions, no
description tweaks. Any change outside the whitelist requires a new
certificate and restarts the verification clock.

## Holdout addendum (to be appended Aug 10 — result only, no re-tuning)

*Never run.* The Aug 10 holdout screen didn't happen, and the entry was never submitted.

## Correction (2026-09-29)

The safety line above says "verified-no-public-ClawsBench." That overstates what was
checked: the Aug 8 audit searched only the skillsbench repo. ClawsBench's paper, 44 task
prompts, safety labels, results, and ~7,800 agent traces have been public on Hugging Face
([benchflow/ClawsBench](https://huggingface.co/datasets/benchflow/ClawsBench)) since
2026-04-08. Its mock services, verifiers, and seed data were not public (still "coming
soon" as of this correction), so it could not be run locally, and a proxy was still needed.
But the three mock tasks could have been modeled on the real safety-task prompts instead
of written from the paper's description. The 12/12 safety result stands as measured; it
measures our proxy, not ClawsBench.
