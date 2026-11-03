# Epistemic Skills (`skill-lift`)

[![CI](https://github.com/closestfriend/skill-lift/actions/workflows/ci.yml/badge.svg)](https://github.com/closestfriend/skill-lift/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Evaluated: BenchFlow](https://img.shields.io/badge/Evaluated-BenchFlow-success.svg)](reports/)
[![Skills: 11 + 1 Meta](https://img.shields.io/badge/Skills-11_Static_+_1_Meta-orange.svg)](library/skills/)

**Epistemic Skills** is an empirical agent skill library, meta-skill (`skill-creator`), linter, and deterministic packager for AI coding agents.

Built during the Kaggle [BenchFlow – Agent Skill Lift](https://www.kaggle.com/competitions/skill-lift) campaign, this repository moves `SKILL.md` authoring from prompt intuition to an **empirical discipline of causal lift, per-axis trajectory autopsy, and Epistemic Ledger claim gating**.

- **Post-Mortem & Empirical Findings**: [`writeup/postmortem-community.md`](writeup/postmortem-community.md)
- **Track 1 Static Freeze Certificate**: [`FREEZE-CERTIFICATE.md`](FREEZE-CERTIFICATE.md) (`dist/submission-v02.zip`, SHA256 `7ca1a460…`)
- **Track 2 Meta-Skill Design & Epistemic Ledger**: [`track2/DESIGN.md`](track2/DESIGN.md) & [`track2/meta/skill-creator/SKILL.md`](track2/meta/skill-creator/SKILL.md)
- **Hugging Face Dataset**: [`closestfriend/skill-lift-library`](https://huggingface.co/datasets/closestfriend/skill-lift-library)

---

## Evaluation Results

Evaluated on the BenchFlow harness across Claude Haiku 4.5, GLM 5.1, and GPT-5.4-mini:

| Benchmark & Model | Without skills | With Epistemic Skills | Notes |
|---|---:|---:|---|
| **Offer Letter Generator** (`docx`, Haiku 4.5) | 0/3 | **3/3** | Recursive `all_paragraphs` walker snippet used verbatim |
| **Offer Letter Generator** (`docx`, GLM 5.1) | 0/2 | **2/2** | Same pattern on a second vendor |
| **PowerPoint Reference Formatting** (`pptx`, Haiku 4.5) | 0/2 | per-axis | Bullets 5/5 · Font 5/5 · Ref 4/5 · Fit 3/5; `a:buAutoNum` snippet + free-dimension geometry rule |
| **Frontier Efficiency** (GPT-5.4-mini) | 13–16 calls (3.7m) | **6–7 calls (2.5m)** | Same pass rate both arms; ~50% fewer tool calls |
| **Off-Domain Sweep** (GLM 5.1) | unchanged | unchanged | Inert off-domain under full-context skill injection |
| **Safety Invariants** (3 mock side-effect tasks) | 12/12 PASS | **12/12 PASS** | 0 violations, 0 over-refusals |

---

## The 6 Empirical Authoring Laws

Derived from paired evaluation failures and trajectory autopsies (`STRATEGY.md`):

1. **Weak models convert executable snippets, not prose hints.**  
   Describing nested-table recursion in prose scored `0/3` on `docx`; replacing prose with the runnable `all_paragraphs(doc)` generator converted `0/3 -> 3/3` on Haiku and `0/2 -> 2/2` on GLM 5.1.
2. **Operational boundaries, never vague disclaimers (plus the Boundary-Timidity Guard).**  
   18 of 84 public benchmark tasks regress under curated skills because they prescribe a single heavyweight pipeline without boundaries. Every skill must declare observable stop/fallback conditions (`If <condition>: <lightweight fallback>`) while keeping `## Applicability & fallback` under 20–25% of body words so the skill stays decisive. Vague disclaimers (*"may not always work"*) are banned.
3. **False-Specificity Guard (Free-Dimension Law).**  
   Never prescribe an unconditional single-axis fix (*"shrink font to fit"* scored `0/6` on `pptx` v3/v4 when the task pinned font size at 16pt and left shape width free). State conditional rules keyed to whichever dimension the spec leaves free.
4. **Artifact-Noun Trigger Surface.**  
   Agents match `description` on concrete artifact nouns (`.xlsx`, `.docx`, `ffmpeg`, `scipy.optimize`), not activity verbs (`build-repair`, `tabular-data`). Frontmatter `description` must specify both positive triggers (`Use when...`) and negative scope limits (`Not for...`).
5. **Strict Token Budget ($\le 900$ words).**  
   Focused procedural skills (`+19.0pp` to `+21.5pp`) beat comprehensive manuals (`+0.7pp`) and must survive harnesses that inject all mounted skills into every prompt.
6. **Verify as Mandatory Task Steps + Reread Spec Before Strengthening.**  
   Agents skip verification framed as optional advice; frame `## Verify before finishing` as numbered task steps with runnable assertions. When a retry fails, reread the task spec and verifier before strengthening compliance language.

---

## Repository Structure

```text
├── library/skills/                 # Track 1 Frozen Static Library (11 skills, 5,865 words)
│   ├── build-repair/               # Reproducing, classifying, and proving minimal build fixes
│   ├── docx/                       # python-docx split-run replacement, nested tables, conditionals
│   ├── media-ffmpeg/               # ffmpeg/ffprobe stream surgery, filtergraphs, silence detection
│   ├── optimization-modeling/      # LP/MILP formulation, solver status checks (scipy, PuLP, OR-Tools)
│   ├── pdf/                        # pypdf/pdfplumber text & table extraction, form filling, OCR fallback
│   ├── pptx/                       # python-pptx run styling, EMUs, buAutoNum XML, working-set slides
│   ├── scope-safety/               # One-way-door verification & prompt-injection immunity
│   ├── signal-timeseries/          # FFT, filtering, detrending, peak finding (numpy/scipy)
│   ├── tabular-data/               # pandas join hygiene, dtype pitfalls, exact output formatting
│   ├── task-discipline/            # Deliverable contract extraction & independent verification
│   └── xlsx/                       # openpyxl formula preservation, data_only=False discipline
├── track2/                         # Track 2 Epistemic Meta-Skill (self-gen / verify-retry)
│   ├── DESIGN.md                   # Source-derived interface contract & Epistemic Ledger design
│   └── meta/skill-creator/         # Mountable skill-creator meta-skill + scripts/verify_claims.py
├── src/epistemic_skills/           # Python CLI linter & deterministic packager
├── reports/                        # Canonical paired-bootstrap lift reports (JSON + Markdown)
├── mock-safety/                    # 3 ClawsBench-style side-effect tasks with oracle & verifier
└── writeup/                        # Post-mortem & Track 1 static writeup
```

---

## CLI Quickstart

Install locally:

```bash
pip install -e .
```

### 1. Lint skills against the 6 Authoring Laws & Track 2 Calibration Gate
```bash
# Lint Track 1 static library (11 skills)
skill-lift lint library/skills --verbose

# Lint Track 2 meta-skill (skill-creator)
skill-lift lint track2/meta --verbose

# Emit machine-readable JSON diagnostics
skill-lift lint library/skills --json
```

### 2. Run the standalone Track 2 claim verifier inside `self-gen` loops
```bash
python3 track2/meta/skill-creator/scripts/verify_claims.py track2/meta/skill-creator library/skills
```

### 3. Build deterministic release archives
```bash
skill-lift package --library library/skills --version 1.0.0 --out dist
```

---

## License

Apache License 2.0. Copyright 2026 Hunter Noah Karman.
