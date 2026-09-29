# Paired Eval Lift Report

- Baseline: `jobs/devsweep-none`
- Trained: `jobs/devsweep-ours`
- Paired healthy tasks: 13

## Overall

| Metric | Baseline | Trained | Delta | 95% CI |
| --- | ---: | ---: | ---: | --- |
| Pass rate | 15.4% | 30.8% | +15.4% | [+0.0%, +38.5%] |
| Mean reward | 0.154 | 0.308 | +0.154 | [+0.000, +0.385] |

## Coverage

| Side | Rollouts | Healthy rollouts | Error rollouts | Unscored rollouts | Unhealthy rollouts | Healthy tasks | Healthy task coverage | Duplicate healthy rollouts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 13 | 13 | 0 | 0 | 0 | 13 | 100.0% | 0 |
| Trained | 13 | 13 | 0 | 0 | 0 | 13 | 100.0% | 0 |

## Pairing

- Baseline-only healthy tasks: 0
- Trained-only healthy tasks: 0
## Task Pairs

| Task | Base reward | Trained reward | Reward delta | Base pass | Trained pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| 3d-scan-calc | 1.000 | 1.000 | +0.000 | yes | yes |
| dynamic-object-aware-egomotion | 0.000 | 0.000 | +0.000 | no | no |
| financial-modeling-qa | 0.000 | 0.000 | +0.000 | no | no |
| fix-build-agentops | 0.000 | 0.000 | +0.000 | no | no |
| fix-erlang-ssh-cve | 1.000 | 1.000 | +0.000 | yes | yes |
| flood-risk-analysis | 0.000 | 0.000 | +0.000 | no | no |
| glm-lake-mendota | 0.000 | 0.000 | +0.000 | no | no |
| jax-computing-basics | 0.000 | 0.000 | +0.000 | no | no |
| lean4-proof | 0.000 | 1.000 | +1.000 | no | yes |
| paratransit-routing | 0.000 | 0.000 | +0.000 | no | no |
| suricata-custom-exfil | 0.000 | 0.000 | +0.000 | no | no |
| threejs-to-obj | 0.000 | 1.000 | +1.000 | no | yes |
| video-silence-remover | 0.000 | 0.000 | +0.000 | no | no |

## Limitations

- Only tasks with healthy, scored rollouts on both sides are included in paired lift metrics.
- Pass rate follows BenchFlow scoring: reward == 1.0 is pass; other numeric rewards are failures.
- No configured metadata breakdown fields were present in the paired result.json/config.json records.
