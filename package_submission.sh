#!/bin/zsh
# package_submission.sh — build the Track 1 submission zip, deterministically.
# Layout per competition Overview: submission.zip -> skills/<name>/SKILL.md [+ scripts/ references/]
# Usage: ./_skill-lift/package_submission.sh [label]   (label -> dist/submission-<label>.zip)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LABEL="${1:-dev}"
OUT="$ROOT/dist"
STAGE="$OUT/stage"
rm -rf "$OUT"
mkdir -p "$STAGE"

# 1. Stage exactly what ships: the skills tree + a LICENSE (winners must OSI-license).
cp -R "$ROOT/library/skills" "$STAGE/skills"
cat > "$STAGE/skills/LICENSE" <<'EOF'
Apache License 2.0

Copyright 2026 Hunter Noah Karman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
EOF

# 2. Strip anything that must never ship.
find "$STAGE" \( -name '.DS_Store' -o -name '__pycache__' -o -name '*.pyc' \
  -o -name 'evals' -type d -o -name '.git*' \) -exec rm -rf {} + 2>/dev/null || true

# 3. Zip deterministically (sorted, no extra attrs).
cd "$STAGE"
ZIP="$OUT/submission-$LABEL.zip"
find skills -type f | sort | zip -X -q "$ZIP" -@
cd "$ROOT/.."

# 4. Manifest: what this zip is, verifiably.
GIT_SHA="$(git -C "$ROOT/.." rev-parse HEAD 2>/dev/null || echo untracked)"
SKILLS=$(ls "$STAGE/skills" | grep -v LICENSE | sort | tr '\n' ' ')
WORDS=$(cat "$STAGE"/skills/*/SKILL.md | wc -w | tr -d ' ')
cat > "$OUT/manifest-$LABEL.json" <<EOF
{
  "label": "$LABEL",
  "built": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repo_commit": "$GIT_SHA",
  "skills": "$SKILLS",
  "total_skill_words": $WORDS,
  "sha256": "$(shasum -a 256 "$ZIP" | cut -d' ' -f1)"
}
EOF

echo "--- contents ---"
unzip -l "$ZIP" | tail -5
echo "--- manifest ---"
cat "$OUT/manifest-$LABEL.json"
