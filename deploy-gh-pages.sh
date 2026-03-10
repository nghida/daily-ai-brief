#!/bin/bash
# Quick re-deploy to GitHub Pages (run after adding new briefs)
set -e

echo "→ Building..."
python3 build.py

echo "→ Deploying to gh-pages..."
TEMP_DIR=$(mktemp -d)
cp -r dist/* "$TEMP_DIR/"

git stash 2>/dev/null || true
git checkout gh-pages
rm -rf *.html *.css *.xml 2>/dev/null || true
cp -r "$TEMP_DIR"/* .
git add -A
git commit -m "Update: $(date '+%Y-%m-%d %H:%M')"
git push origin gh-pages
git checkout main
git stash pop 2>/dev/null || true
rm -rf "$TEMP_DIR"

echo "✓ Deployed! Changes live in ~1 minute."
