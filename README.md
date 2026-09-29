# skill-lift

**Valid as of: 2026-09-28**

Campaign repo for the Kaggle [BenchFlow – Agent Skill Lift](https://www.kaggle.com/competitions/skill-lift)
competition (Aug 2026): an 11-skill agent library, the paired-eval rig that measured it, and the
full record of what worked and what didn't. The entry was frozen on Aug 8 and never submitted.
The post-mortem explains that and everything else: [`writeup/postmortem-community.md`](writeup/postmortem-community.md).

## Map

| Path | What it is |
|---|---|
| `library/skills/` | The 11 skills (Apache-2.0), the frozen artifact's source |
| `dist/submission-v02.zip` | Frozen submission, sha256 `7ca1a460…` (see certificate) |
| `FREEZE-CERTIFICATE.md` | Validation results, measured claims, limitations at freeze |
| `reports/` | Canonical lift reports from `bench eval compare-lift` |
| `STRATEGY.md` | Full decision log, including retractions |
| `INVENTORY.md` | The 87-task public corpus, mapped by domain |
| `track2/DESIGN.md` | Meta-skill design (Epistemic Ledger → authoring gate), unbuilt |
| `mock-safety/` | 3 side-effect safety tasks, a labeled proxy for ClawsBench. ClawsBench's task prompts and traces are public ([HF](https://huggingface.co/datasets/benchflow/ClawsBench)), but its mock services and verifiers aren't, so it can't be run locally. |
| `ab-lib/` | Description A/B variant library (result: null) |
| `run_paired.sh`, `run_*_sweep.sh`, `package_submission.sh`, `aggregate_matrix.py` | Eval and packaging scripts |

## Running it

The scripts assume this directory sits inside a checkout of
[benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench) at `_skill-lift/`
(they resolve `tasks/` from the parent). Then, from the skillsbench root:

```bash
./_skill-lift/run_paired.sh offer-letter-generator _skill-lift/library/skills
```
