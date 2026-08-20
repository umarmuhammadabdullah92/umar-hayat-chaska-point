#!/bin/bash
# Auto-deploy: watches for file changes, commits & pushes to GitHub
# Run: ./auto-deploy.sh
cd "$(dirname "$0")"

echo "Auto-deploy running for Umar Hayat Chaska Point..."
echo "Watching for changes... (Ctrl+C to stop)"

while true; do
  changes=$(git status --porcelain)
  if [ -n "$changes" ]; then
    git add -A
    git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M')" --quiet
    git push origin main 2>&1
    echo "[$(date '+%H:%M:%S')] Changes pushed to GitHub"
  fi
  sleep 3
done
