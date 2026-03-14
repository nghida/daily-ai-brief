#!/bin/bash
# ═══════════════════════════════════════════════════
# Deploy Daily AI Brief to GitHub Pages
# Run this once from your terminal to go live
# ═══════════════════════════════════════════════════

set -e

REPO_NAME="daily-ai-brief"
BRANCH="main"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Daily AI Brief — GitHub Pages      ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# ── Check prerequisites ──
if ! command -v git &> /dev/null; then
    echo "❌ git is not installed. Please install git first."
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install: brew install gh"
    echo "   Then:    gh auth login"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Not logged in to GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

# ── Build the site ──
echo "→ Building site..."
python3 build.py
echo ""

# ── Initialize git ──
if [ ! -d ".git" ]; then
    echo "→ Initializing git repo..."
    git init
    git checkout -b main
fi

# ── Commit all files ──
echo "→ Committing files..."
git add -A
git commit -m "Initial commit: Daily AI Brief site" 2>/dev/null || echo "  (no changes to commit)"
echo ""

# ── Create GitHub repo ──
echo "→ Creating GitHub repo: $REPO_NAME"
if gh repo view "$REPO_NAME" &> /dev/null; then
    echo "  Repo already exists, pushing..."
    git remote remove origin 2>/dev/null || true
    git remote add origin "$(gh repo view $REPO_NAME --json url -q .url).git"
else
    gh repo create "$REPO_NAME" --public --source=. --push
fi
echo ""

# ── Push to GitHub ──
echo "→ Pushing to GitHub..."
git push -u origin main 2>/dev/null || git push origin main
echo ""

# ── Deploy dist/ to gh-pages branch ──
echo "→ Deploying dist/ to gh-pages branch..."

# Create a temporary worktree for gh-pages
TEMP_DIR=$(mktemp -d)
cp -r dist/* "$TEMP_DIR/"

# Create orphan gh-pages branch
git checkout --orphan gh-pages 2>/dev/null || git checkout gh-pages
git rm -rf . 2>/dev/null || true
cp -r "$TEMP_DIR"/* .
git add -A
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')"
git push -f origin gh-pages

# Go back to main
git checkout main
rm -rf "$TEMP_DIR"
echo ""

# ── Enable GitHub Pages ──
echo "→ Enabling GitHub Pages..."
GITHUB_USER=$(gh api user -q .login)
gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    "/repos/$GITHUB_USER/$REPO_NAME/pages" \
    -f "source[branch]=gh-pages" \
    -f "source[path]=/" 2>/dev/null || \
gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/$GITHUB_USER/$REPO_NAME/pages" \
    -f "source[branch]=gh-pages" \
    -f "source[path]=/" 2>/dev/null || \
echo "  (Pages may already be enabled)"

echo ""
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║  ✓ DEPLOYED!                                     ║"
echo "  ║                                                   ║"
echo "  ║  Your site will be live in ~1 minute at:          ║"
echo "  ║  https://$GITHUB_USER.github.io/$REPO_NAME/      ║"
echo "  ║                                                   ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo ""
echo "To add a new brief, create a .md file in briefs/ and run:"
echo "  python3 build.py && ./deploy-gh-pages.sh"
echo ""
