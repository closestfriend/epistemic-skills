#!/bin/zsh
# run_glm_sweep.sh — GLM 5.1 cross-model dev sweep, both arms, resumable.
# Launch decoupled from any Claude session:
#   nohup ./_skill-lift/run_glm_sweep.sh > _skill-lift/glm_sweep.log 2>&1 &
# Progress: tail -f _skill-lift/glm_sweep.log ; results in jobs/glmsweep-*/

source ~/.zshrc >/dev/null 2>&1
set -uo pipefail   # no -e: one arm failing shouldn't kill the other

REPO="$(cd "$(dirname "$0")/.." && pwd)"
export DOCKER_CONFIG="$REPO/_skill-lift/.dockercfg"
export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"
cd "$REPO"

INC=(--include suricata-custom-exfil --include fix-erlang-ssh-cve
     --include financial-modeling-qa --include dynamic-object-aware-egomotion
     --include 3d-scan-calc --include lean4-proof --include paratransit-routing
     --include threejs-to-obj --include video-silence-remover
     --include flood-risk-analysis --include glm-lake-mendota
     --include jax-computing-basics --include fix-build-agentops)

echo "=== GLM OURS arm $(date) ==="
uv run bench eval run --tasks-dir tasks "${INC[@]}" \
  --agent opencode --model openrouter/z-ai/glm-5.1 \
  --skill-mode with-skill --skills-dir _skill-lift/library/skills \
  --sandbox docker --concurrency 2 --jobs-dir jobs/glmsweep-ours

echo "=== GLM NONE arm $(date) ==="
uv run bench eval run --tasks-dir tasks "${INC[@]}" \
  --agent opencode --model openrouter/z-ai/glm-5.1 \
  --skill-mode no-skill \
  --sandbox docker --concurrency 2 --jobs-dir jobs/glmsweep-none

echo "=== GLMSWEEP-COMPLETE $(date) ==="
