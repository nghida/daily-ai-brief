#!/bin/bash
# publish.sh — Called by Cowork scheduled task to add a new brief and push to GitHub
# Usage: ./publish.sh <brief-file.md>
#
# This script:
# 1. Copies the brief markdown file to the briefs/ folder
# 2. Commits and pushes to GitHub
# 3. Vercel auto-deploys from the new commit

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIEF_FILE="$1"

if [ -z "$BRIEF_FILE" ]; then
  echo "Usage: ./publish.sh <path-to-brief.md>"
  exit 1
fi

if [ ! -f "$BRIEF_FILE" ]; then
  echo "Error: File not found: $BRIEF_FILE"
  exit 1
fi

# Copy brief to briefs folder
FILENAME=$(basename "$BRIEF_FILE")
cp "$BRIEF_FILE" "$REPO_DIR/briefs/$FILENAME"

# Git commit and push
cd "$REPO_DIR"
git add "briefs/$FILENAME"
git commit -m "Add daily brief: $FILENAME"
git push origin main

echo "✓ Published: $FILENAME"
