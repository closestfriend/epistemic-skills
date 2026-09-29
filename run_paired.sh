#!/bin/zsh
# run_paired.sh — measure skill lift on one task: paired with-skill / no-skill eval.
#
# Usage:
#   ./_skill-lift/run_paired.sh <task-id> [skills-dir] [model]
#
#   task-id     e.g. offer-letter-generator (must exist under tasks/)
#   skills-dir  default: the task's own bundled skills (curated-skill reference lift);
#               pass _skill-lift/library/skills to measure OUR library instead
#   model       default: claude-haiku-4-5-20251001 (cheap iteration signal;
#               spot-check with claude-sonnet-4-5@20250929 before trusting a delta)
#
# Environment fixes baked in (each one cost us a failed run on 2026-08-01):
#   1. source ~/.zshrc        -> ANTHROPIC_API_KEY (agent inside sandbox needs it;
#                                without it: "ACP error -32000: Authentication required")
#   2. scratch DOCKER_CONFIG  -> bypasses docker-credential-osxkeychain, which flakes
#                                (Keychain -25320) under concurrent builds from
#                                non-GUI shells; cli-plugins symlinked so `docker
#                                compose` still resolves
#   3. explicit DOCKER_HOST   -> scratch config has no "currentContext: orbstack"
#   4. sequential arms        -> concurrent builds are what trip the keychain; also
#                                keeps one container's noise out of the other's run
#   5. fresh --jobs-dir per (agent,mode) -> benchflow refuses to mix results otherwise

# Source BEFORE strict mode: oh-my-zsh references unset vars, which `set -u`
# would turn into a silent fatal exit (cost us a mystery empty run on 2026-08-01).
source ~/.zshrc >/dev/null 2>&1
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TASK="${1:?usage: run_paired.sh <task-id> [skills-dir] [model]}"
SKILLS_DIR="${2:-$REPO/tasks/$TASK/environment/skills}"
# Standard Anthropic model ID (dashes). The `model@date` form from
# experiments/configs/ routes to benchflow's hosted LiteLLM proxy and 401s
# on a personal key ("Received Model Group=benchflow-...").
MODEL="${3:-claude-haiku-4-5-20251001}"
STAMP="$(date +%m%d-%H%M)"

DOCKER_SCRATCH="$REPO/_skill-lift/.dockercfg"
mkdir -p "$DOCKER_SCRATCH"
printf '{"auths": {}}' > "$DOCKER_SCRATCH/config.json"
ln -sfn "$HOME/.docker/cli-plugins" "$DOCKER_SCRATCH/cli-plugins"
export DOCKER_CONFIG="$DOCKER_SCRATCH"
export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"

cd "$REPO"
echo "=== $TASK / $MODEL / WITH skills ($SKILLS_DIR) ==="
uv run bench eval run --tasks-dir "tasks/$TASK" \
  --agent claude-agent-acp --model "$MODEL" \
  --skill-mode with-skill --skills-dir "$SKILLS_DIR" \
  --sandbox docker --jobs-dir "jobs/$TASK-with-$STAMP" 2>&1 | tail -6

echo "=== $TASK / $MODEL / WITHOUT skills ==="
uv run bench eval run --tasks-dir "tasks/$TASK" \
  --agent claude-agent-acp --model "$MODEL" \
  --skill-mode no-skill \
  --sandbox docker --jobs-dir "jobs/$TASK-without-$STAMP" 2>&1 | tail -6

echo "=== lift readout ==="
for d in "jobs/$TASK-with-$STAMP" "jobs/$TASK-without-$STAMP"; do
  uv run python -c "
import glob, json, sys
paths = sorted(glob.glob('$d/**/summary.json', recursive=True))
d = json.load(open(paths[-1]))
acc = d.get('accuracy', d.get('pass_rate', '?'))
print('$d ->', json.dumps({k: d[k] for k in ('pass','fail','error') if k in d}), 'accuracy:', acc)"
done
