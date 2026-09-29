#!/bin/zsh
# run_transfer_test.sh — do our proven-lift tasks transfer to GLM?
# offer-letter-generator (docx skill: 3/3 on haiku) + pptx-reference-formatting
# (pptx skill: 2/3 on haiku), ours vs none, n=2, concurrency 1 (16GB memory rule).
# Launch: nohup ./_skill-lift/run_transfer_test.sh > _skill-lift/transfer_test.log 2>&1 &

source ~/.zshrc >/dev/null 2>&1
set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
export DOCKER_CONFIG="$REPO/_skill-lift/.dockercfg"
export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"
cd "$REPO"

for task in offer-letter-generator pptx-reference-formatting; do
  for a in 1 2; do
    echo "=== $task OURS a$a $(date +%H:%M) ==="
    uv run bench eval run --tasks-dir tasks --include $task \
      --agent opencode --model openrouter/z-ai/glm-5.1 \
      --skill-mode with-skill --skills-dir _skill-lift/library/skills \
      --sandbox docker --concurrency 1 --jobs-dir jobs/transfer-$task-ours-a$a
    echo "=== $task NONE a$a $(date +%H:%M) ==="
    uv run bench eval run --tasks-dir tasks --include $task \
      --agent opencode --model openrouter/z-ai/glm-5.1 \
      --skill-mode no-skill \
      --sandbox docker --concurrency 1 --jobs-dir jobs/transfer-$task-none-a$a
  done
done
echo "=== TRANSFER-TEST-COMPLETE $(date) ==="
