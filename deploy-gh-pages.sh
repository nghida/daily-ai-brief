#!/bin/bash
# Re-deploy updated site to GitHub Pages
# Usage: ./deploy-gh-pages.sh

set -e
cd "$(dirname "$0")"

echo ""
echo "→ Building site..."
python3 build.py

echo "→ Syncing main branch..."
git add -A
git commit -m "Update: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || echo "  (nothing to commit on main)"
git pull --rebase origin main 2>/dev/null || true
git push origin main 2>/dev/null || true

echo "→ Deploying dist/ to gh-pages..."
TEMP=$(mktemp -d)
cp dist/* "$TEMP/"

git checkout gh-pages 2>/dev/null || git checkout --orphan gh-pages
git rm -rf . --quiet 2>/dev/null || true
cp "$TEMP"/* .
rm -rf "$TEMP"

git add -A
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push -f origin gh-pages

git checkout main
echo ""
echo "✓ Done! Live in ~1 min at https://nghida.github.io/daily-ai-brief/"
echo ""
