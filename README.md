# Epistemic Skills

[![CI](https://github.com/closestfriend/skill-lift/actions/workflows/ci.yml/badge.svg)](https://github.com/closestfriend/skill-lift/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Measured Lift: +15.4pp](https://img.shields.io/badge/Measured_Lift-+15.4pp-success.svg)](reports/)
[![Skills: 11](https://img.shields.io/badge/Skills-11-orange.svg)](library/skills/)

**Epistemic Skills** is an empirical agent skill library, linter, and deterministic compiler for AI coding agents. 

Born out of the Kaggle [BenchFlow – Agent Skill Lift](https://www.kaggle.com/competitions/skill-lift) campaign, this repository moves agent skill engineering away from "prompt vibes" into an **empirical science of causal lift backed by deterministic test harnesses and Epistemic Ledgers**.

---

## 📊 Measured Benchmark Results

Evaluated on the official BenchFlow test harness with paired bootstrap analysis ($n=1000$):

| Benchmark & Model | Baseline | With Epistemic Skills | Lift / Delta | Verification |
|---|---:|---:|---:|---|
| **13-Task Dev Sweep** (Claude Haiku 4.5) | 15.4% | **30.8%** | **+15.4pp** | 95% CI [+0.0%, +38.5%] |
| **Offer Letter Generator** (`docx`, Haiku) | 0/3 | **3/3** | **+100%** | Recursive walker snippet verbatim |
| **Offer Letter Generator** (`docx`, GLM 5.1) | 0/2 | **2/2** | **+100%** | Cross-vendor identical causal lift |
| **PowerPoint Formatting** (`pptx`, Haiku) | 0/2 | **4/5** | **+80%** | Bullets 5/5, Font-style 5/5 |
| **Efficiency Sweep** (GPT-5.4-mini) | 13–16 calls | **6–7 calls** | **~2× Faster** | 2.5 min vs 3.7 min runtime |
| **Safety Invariants** (3 side-effect tasks) | 12/12 PASS | **12/12 PASS** | **0 Violations** | Zero over-refusals |

---

## 🏛️ The 6 Authoring Laws

Every skill in this library conforms to the empirical authoring laws purchased through paired evaluation failures:

1. **Weak models convert executable snippets, not prose hints.**  
   Models fail when given abstract advice; they succeed when given copy-paste-runnable recursive algorithms with calibrated defaults.
2. **Applicability & Fallback Boundaries are mandatory.**  
   Every skill must declare what it is NOT for and provide an immediate, lightweight fallback path when high-level tooling breaks.
3. **Dual-Trigger Frontmatter.**  
   The description must define both positive triggers (`Use when...`) and negative boundaries (`Not for...`) to eliminate misfires.
4. **Strict Token Budget ($\le 900$ words).**  
   Prune philosophical preamble; keep column mappings, quirks, and boundary assertions.
5. **Inline Verification Postconditions.**  
   Mandatory verification steps before the agent declares a task complete.
6. **Safety at Reversible Boundaries.**  
   Side-effect skills (email, deletions, permissions) stop at the reversible boundary unless explicit authorization is verified.

---

## 📚 Library Inventory

```
library/skills/
├── build-repair/           # Diagnosing and fixing broken builds, CI, and dependencies
├── docx/                   # python-docx template filling, split-run repair, tables
├── media-ffmpeg/           # Video/audio stream processing, cuts, silence detection
├── optimization-modeling/  # LP/MILP, scheduling, routing (scipy, cvxpy, OR-Tools)
├── pdf/                    # Text/table extraction, form filling, OCR fallbacks
├── pptx/                   # PowerPoint generation, slide layouts, run-level styling
├── scope-safety/           # Operational boundaries for user environments & permissions
├── signal-timeseries/      # FFT, filtering, detrending, and peak finding (numpy/scipy)
├── tabular-data/           # pandas joins, dtype pitfalls, exact-output formatting
├── task-discipline/        # Verification checklist for exact deliverable matching
└── xlsx/                   # openpyxl formula preservation, cell type discipline
```

---

## 🛠️ CLI Quickstart

Install locally with `uv` or `pip`:

```bash
git clone https://github.com/closestfriend/skill-lift.git
cd skill-lift
pip install -e ".[dev]"
```

### 1. Lint your skills against the 6 Authoring Laws
```bash
skill-lift lint library/skills
```

### 2. List all skills and their Epistemic Integrity scores
```bash
skill-lift list
```

### 3. Build a bitwise-deterministic release artifact
```bash
skill-lift package --library library/skills --version 1.0.0 --out dist
```
Generates `dist/skills-v1.0.0.zip`, `dist/manifest.json`, and `dist/RELEASE-CERTIFICATE.md` with SHA256 verification.

---

## 🚀 CI/CD Release Pipeline

This repo includes GitHub Actions workflows for continuous verification and automated releases:
- **`.github/workflows/ci.yml`**: Runs `pytest`, validates all skills with `skill-lift lint`, and enforces build reproducibility on every commit and pull request.
- **`.github/workflows/release.yml`**: Triggered by git tags (`git tag v1.0.0 && git push origin v1.0.0`), automatically compiling the deterministic zip, computing SHA256 hashes, and publishing a GitHub Release with certified release notes.

---

## 📜 License

Apache License 2.0. Copyright 2026 Hunter Noah Karman.
