# Track 2 Design — `skill-creator` meta-skill (drafted Aug 6 night, build day Aug 9)

Everything below is **source-derived from the public harness** (benchflow 0.6.5 in our
venv + the organizers' repo at 9a1f4dd5), not guessed. File/line receipts inline.

## 1. The interface contract (from source)

- `bench eval run --skill-mode self-gen` runs **two scenes per trial**
  (`benchflow/self_gen.py`): a **creator scene** (agent + ONLY the skill-creator
  skill mounted) writes skill packs; a **solver scene** then runs the task with
  ONLY the generated skills. Creator and solver are the same agent+model.
- Creator resolution (`rollout/_skills.py:_resolve_skill_creator_root`):
  `--skill-creator-dir` flag → `BENCHFLOW_SKILL_CREATOR_DIR` env → repo/CWD
  `.claude/skills/skill-creator` → `~/.claude`, `~/.codex/.system`, `~/.agents`.
- **The organizers SHIP the stock creator** in their repo: `.agents/skills/
  skill-creator/` (`.claude/skills` is a symlink to it; moved there by commit
  e8bf3df9 "skills consolidation"). Apache-2.0 (LICENSE.txt) — studiable,
  adaptable with attribution. 356 lines, ~2.5k words + scripts/ (init, package,
  validate) + references/ (workflows, output-patterns).
- **Single-skill mount**: `_copy_single_skill` copies exactly ONE skill into the
  creator scene. With a multi-skill root, `_find_skill_creator_dir` requires a
  child literally named `skill-creator`; a single-skill root becomes the creator
  regardless of name.
  - ⇒ **Submission shape: exactly ONE meta-skill, directory + frontmatter name
    `skill-creator`.** Robust under both resolution branches; extra meta-skills
    would silently never mount. (Also satisfies the DQ rule: no pre-evolved
    library, meta-skill only.)
- **Creator invocation is FORCED** (`_self_gen_prompt`): "Use the
  {skill_creator_name} skill exactly as provided… Do not solve the task
  directly." No discovery problem in the creator scene ⇒ the description barely
  matters here; **body quality is everything** (our proven strength).
- `--loop-strategy 'verify-retry:k=N,feedback=…'` (`_types.py` module docs):
  harness re-prompts across verify-retry rounds, **scores only the final
  hardened verify** — genuine iterative refinement, harness-level. Their private
  "evolution loop with calibration split + feedback" is overwhelmingly likely a
  variant of this machinery. Read `benchflow/loop_strategies.py` on build day
  for the exact feedback template.

## 2. Stock-creator gap analysis (what ours adds)

Stock covers (don't duplicate — cite/inherit): anatomy & packaging, progressive
disclosure, conciseness ("context window is a public good"), degrees of freedom
(high/medium/low specificity vs task fragility), description-as-trigger,
imperative form, 6-step process (understand → plan → init → edit → package →
iterate).

Stock LACKS — each gap is one of our measured findings:

| Gap | Our evidence |
|---|---|
| Evidence discipline: no distinction between measured / observed / assumed instructions; "iterate" = "notice struggles" (no paired measurement, no autopsy) | docx 0/3→3/3 came from autopsy→fix→remeasure, not noticing |
| Executable-snippet law ("prefer concise examples" ≠ runnable code) | docx v1 prose hint 0/3 → v2 walker code 3/3 |
| Verify-as-mandatory-task-step framing | a2 run skipped advice-framed verify; task-step framing converted |
| Negative triggers / operational boundaries ("when NOT to use", observable stop conditions, fallbacks) | 18/84 public tasks REGRESS under curated skills |
| False-specificity guard (prescribing one fix regardless of which dimension the spec leaves free) | pptx v3/v4 self-committed 0/6; v5 dimension-choice 2/3 |
| Spec-reread law (fix stops converting → reread spec before strengthening) | pptx v4 strengthened compliance while the advice itself was wrong |
| Audit-the-verifier law (validate claims against checks, not prose; empty grep ≠ absence) | Aug 6 de-bloat regression: colors cut passed a task.md-only audit, verifier asserted #989596 |

## 3. Our meta-skill = stock structure + the epistemic layer (Hunter's Ledger, operationalized)

Every instruction in a generated skill is a **claim**. The meta-skill makes the
creator tag and gate claims:

- **Ledger fields per claim** (adapted from Hunter's Epistemic Ledger):
  evidence kind (measured on this task family / observed in spec or verifier /
  general API knowledge / assumption), validity domain (file types, library
  versions, task shapes), known unknowns, failure mode if wrong, verification
  step that would catch it.
- **Calibration Gate → authoring gate** (per claim):
  - *measured or spec-verified* → **prescribe** (imperative + runnable snippet)
  - *general knowledge, plausible variance* → **hedge with an OPERATIONAL
    boundary** ("for .docx parseable by python-docx; NOT scanned docs — render
    those visually"), never a disclaimer ("may not always work" is banned)
  - *assumption* → **mark unvalidated** or **omit**; an unvalidated prescriptive
    fix is the canonical failure (false specificity)
- **Boundary-timidity guard** (Codex round-2 concern, now a rule): a boundary
  must name an observable condition and an action, or it doesn't ship. Budget:
  boundaries ≤ ~20% of body words; the skill must remain decisive inside its
  domain.
- Inherit stock's structural doctrine by reference, compressed — our body
  re-teaches only what the gaps table adds, staying within our own ≤900-word
  house style (the stock creator is 2.5k words; ours must model the concision it
  preaches).

## 4. Aug 9 experiment (pre-registered in STRATEGY.md Endgame v2.2)

Arms on 2–3 public tasks (offer-letter-generator = known procedural gap;
one never-converted task = boundary-honesty probe):
- **A** `no-skill` baseline
- **B** `self-gen` + stock creator (zero setup: resolves via repo symlink from CWD)
- **C** `self-gen --skill-creator-dir _skill-lift/track2/meta` (root containing
  ONLY our `skill-creator`)
- verify-retry `k=3` on self-gen arms (same settings both arms)

Scoring, two levels (Endgame v2.1): authoring quality of generated packs
(operational boundaries present? universal claims? runnable snippets? verify
steps as task steps? decisive?) + downstream pass rate/regressions/token cost.
Kill criteria stand as pre-registered. Deviations from the organizers' unknown
exact protocol documented as Category-C reconstruction notes (writeup material).

## 5. Build-day checklist (Aug 9)

- [ ] Read `benchflow/loop_strategies.py` — exact feedback template & knobs
- [ ] Draft `_skill-lift/track2/meta/skill-creator/SKILL.md` (§3 spine; cite
      stock creator lineage + Apache-2.0 attribution; cite Hunter's epistemic
      framework as design source)
- [ ] Decide scripts/: likely a `verify_claims.py` checklist runner OR nothing
      (scripts must earn their words; stock's init/package scripts are
      irrelevant inside the eval loop — do NOT cargo-cult them)
- [ ] Dry-run arm C on one task before the full three-arm matrix
- [ ] Similarity pass vs stock creator (Apache attribution ≠ verbatim reuse)
- [ ] Dual-submit dry run on Kaggle (moved to Aug 9 per Endgame v2)
