# We measured everything and never pressed Submit: a full post-mortem of an 11-skill library

**Valid as of: 2026-09-29** · Hunter Karman, with Claude

---

We competed in skill-lift for ten days, froze a complete 11-skill library on August 8
with measured lift, a safety result, and a deterministic build — and then never pressed
Submit. That failure is ours (more on it at the end, it has a lesson in it too). The
work doesn't need a leaderboard to be useful, so here is all of it: the numbers, the
authoring laws we derived from failures, the nulls, and the tooling discoveries that
would have saved us days. The library is Apache-2.0 on Hugging Face: **[closestfriend/skill-lift-library](https://huggingface.co/datasets/closestfriend/skill-lift-library)** —
zip sha256 `7ca1a460…`, matching the freeze certificate in the repo.

## What we shipped (into a freezer instead of the form)

11 skills, 5,865 words total, three layers: a core document stack (xlsx, pdf, docx,
pptx), domain packs (tabular-data, media-ffmpeg, signal-timeseries, build-repair,
optimization-modeling), and a conduct layer (task-discipline, scope-safety). House
style: trigger-surface descriptions built from artifact nouns, an Applicability &
fallback section in every skill, ≤900 words, verification framed as mandatory task
steps, safety inline. All ground-up rewrites (the bundled Anthropic skills are
license-Proprietary); similarity-checked against all 232 bundled SKILL.md files —
the only shared lines are `import` statements.

## Headline numbers

Statistics via `bench eval compare-lift` — the harness's own paired-bootstrap
reporter, which we found embarrassingly late (see "use the canonical machinery").

| Measurement | Result |
|---|---|
| 13-task stratified dev sweep, claude-haiku-4-5, paired | pass rate **15.4% → 30.8%**, +15.4pp, 95% CI [+0.0%, +38.5%] |
| offer-letter-generator (docx), haiku, n=3/arm | **0/3 → 3/3** |
| same task, GLM 5.1 via opencode, n=2/arm | **0/2 → 2/2** — cross-vendor, same causal fingerprint |
| pptx-reference-formatting, haiku | per-axis: bullets 5/5, font-style 5/5, reference 4/5, fit 3/5 (no-skill 0/2) |
| GPT-5.4-mini (both test tasks) | pass-rate ceiling both arms, **~2× efficiency with skills** (6–7 tool calls/2.5 min vs 13–16/3.7 min) |
| 13-task GLM sweep | **0 lift, 0 harm, 0 invocations** — inert off-domain, by design |
| Safety (3 side-effect tasks w/ logged stubs) | **12/12 PASS both arms**, zero violations, zero over-refusals |

The docx result is the cleanest causal story we have: every no-skill failure was one of
the two defect classes the skill teaches (placeholders inside nested tables, leftover
placeholders), and every with-skill trajectory contains the skill's recursive-walker
snippet verbatim. Same fingerprint on a second vendor. That's lift *by the taught
mechanism*, not correlation.

## The authoring laws (each one purchased with a failure)

1. **Weak models convert executable snippets, not prose hints.** Our docx v1 described
   nested-table recursion in words: 0/3. v2 made it a runnable function and added a
   mandatory rescan step: 3/3.
2. **Verification must read as task steps, not advice.** We watched an agent invoke a
   skill, do the work, and skip the verify section framed as guidance — then declare
   success unverified. Reframed as numbered steps of the task itself, compliance improved.
3. **The prescriptive fix is the canonical self-inflicted regression.** Our pptx skill
   said "shrink the font to fit" — but the task pins font size and leaves box width
   free. Two zero-scoring versions before measurement (not review) caught it. Corollary:
   when a fix stops converting, reread the task spec before strengthening the fix.
4. **Audit the verifier, not the prose — and an empty grep is not evidence of absence.**
   We cut a "colors" snippet after grepping task.md files for color demand and finding
   nothing. The verifier asserts a hex font color. The de-bloat regressed within three
   rollouts and the paired gate caught it in under an hour.
5. **Toplines lie at small n; per-axis autopsy is where causation lives.** A 2/3
   benchmark turned out to be lucky on an axis we'd never noticed. Then we declared that
   axis "fixed" at n=3 and rollout 4 un-fixed it. Small-n discipline is a practice, not
   a lesson you learn once.

## The nulls (reported with equal weight)

- **Description enrichment: null.** We A/B'd a noun-packed description on a
  never-opened skill: control 0/4 invocations, enriched 1/4, every run failed anyway.
  Open-rate is a *diagnostic*, not a KPI — route around it, don't fight it.
- **Activity-named skills never fire.** build-repair and tabular-data: zero formal
  invocations across three vendors. Artifact nouns (file types, error strings) match;
  activity nouns don't.
- **Off-domain lift is zero** — which is the design working, but caps aggregate lift on
  any mix light on document tasks. We report it rather than cherry-pick.
- **Formal invocation counters undercount.** Our pptx skill was *read* (its snippets
  appear in outputs) in runs where `n_skill_invocations=0` — ACP agents read /skills
  with ordinary file tools. And opencode doesn't invoke at all: it **injects** all
  skills into context on every task. A library must survive both delivery modes — all
  5,865 of our words rode along on every GLM task with zero measured harm.

## Use the canonical machinery (the PSA we needed on day one)

Halfway through, a collaborator called out a failure mode worth naming: **bespoke-system
bias** — when uncertain about an external system, building a smaller replacement you can
reason about instead of surveying what exists. Its partner is **assumption
ossification**: "we can't access their private eval" quietly became "we can't run their
loop," which justified designing a miniature proxy — while `bench eval run --skill-mode
self-gen --skill-creator-dir` plus `--loop-strategy 'verify-retry:k=3'` sat in the
public harness the whole time, along with the organizers' own experiment configs
(`experiments/configs/`, which also reveal the eval panel includes haiku- and
sonnet-class models — your cheap local runs measure real panelists). We also hand-rolled
a lift aggregator before finding `bench eval compare-lift`, and eyeballed skill
compliance before finding the shipped validators (`bench tasks check`, the
skill-creator's `quick_validate.py`). Audit question we now ask on every project: *what
have I concluded is impossible that is actually only unverified?*

## The epistemics thread

This part predates the competition. Before skill-lift, I'd been working on an Epistemic
Ledger: tagging claims with what kind of evidence backs them, how confident to be, and
what would falsify them. Skill authoring turned out to be a natural place to plant it.

Our Track 2 design (built, unsubmitted) treats every instruction in a generated skill
as a **claim** carrying epistemic metadata: evidence kind (measured / spec-observed /
general knowledge / assumption), validity domain, known unknowns, failure mode if
wrong, and the verification step that would catch it. An authoring gate then decides
per claim: **prescribe** (measured → imperative + snippet), **hedge with an
operational boundary** (never a disclaimer — "NOT for scanned PDFs; render those
visually" beats "may not always work"), **mark unvalidated**, or **omit**. The failure
it targets is *false specificity* — the confidently-wrong instruction — which we
committed ourselves in law #3 above. Laws 1–5 are what this framework looks like after
it has been run through a measurement loop.

## The process failure, briefly

We froze a submittable artifact on Aug 8. Our own strategy doc said "submitted
writeups remain editable until deadline — early submission costs nothing." We still
sequenced Submit *after* a Track 2 build day and a holdout screen, and when those
sessions didn't happen, the submission evaporated with them. The rule we extracted:
**once an entry is minimally viable, the irreversible step goes first**; everything
after is in-place polish. May it save one of you next competition.

## Artifacts

- Library (Apache-2.0), freeze certificate, canonical lift reports, eval scripts: **[closestfriend/skill-lift-library](https://huggingface.co/datasets/closestfriend/skill-lift-library)**
- Everything reproduces on the public harness; the reports name the exact commands.

Questions, corrections, and "you're wrong about X" are all welcome in the Community tab.
Congratulations to everyone who got an entry in.
