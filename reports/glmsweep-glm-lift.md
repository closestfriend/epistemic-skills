# Paired Eval Lift Report

- Baseline: `jobs/glmsweep-none`
- Trained: `jobs/glmsweep-ours`
- Paired healthy tasks: 6

## Overall

| Metric | Baseline | Trained | Delta | 95% CI |
| --- | ---: | ---: | ---: | --- |
| Pass rate | 16.7% | 16.7% | +0.0% | [+0.0%, +0.0%] |
| Mean reward | 0.167 | 0.167 | +0.000 | [+0.000, +0.000] |

## Coverage

| Side | Rollouts | Healthy rollouts | Error rollouts | Unscored rollouts | Unhealthy rollouts | Healthy tasks | Healthy task coverage | Duplicate healthy rollouts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 12 | 6 | 4 | 1 | 1 | 6 | 54.5% | 0 |
| Trained | 20 | 12 | 7 | 1 | 0 | 12 | 92.3% | 0 |

## Pairing

- Baseline-only healthy tasks: 0
- Trained-only healthy tasks: 6
## Task Pairs

| Task | Base reward | Trained reward | Reward delta | Base pass | Trained pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| 3d-scan-calc | 1.000 | 1.000 | +0.000 | yes | yes |
| dynamic-object-aware-egomotion | 0.000 | 0.000 | +0.000 | no | no |
| financial-modeling-qa | 0.000 | 0.000 | +0.000 | no | no |
| fix-build-agentops | 0.000 | 0.000 | +0.000 | no | no |
| flood-risk-analysis | 0.000 | 0.000 | +0.000 | no | no |
| jax-computing-basics | 0.000 | 0.000 | +0.000 | no | no |

## Limitations

- Only tasks with healthy, scored rollouts on both sides are included in paired lift metrics.
- Pass rate follows BenchFlow scoring: reward == 1.0 is pass; other numeric rewards are failures.
- No configured metadata breakdown fields were present in the paired result.json/config.json records.
