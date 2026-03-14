# Daily AI Brief

A minimalist static site that auto-publishes daily AI briefs from Cowork.

## Quick Setup

### 1. Create GitHub repo

```bash
cd daily-brief-site
git init
git add .
git commit -m "Initial commit: daily brief site"
gh repo create daily-ai-brief --public --push --source=.
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"**
3. Import the `daily-ai-brief` repo
4. Vercel will auto-detect the config from `vercel.json`
5. Click **Deploy**

Your site will be live at `https://daily-ai-brief.vercel.app` (or similar).

### 3. Update Cowork scheduled task

The daily-ai-briefing task needs to be updated to push new briefs to the repo. The brief markdown files go in the `briefs/` folder with the format `YYYY-MM-DD.md`.

## Adding briefs manually

```bash
# Create a new brief
cp briefs/2026-03-10.md briefs/2026-03-11.md
# Edit the file...
git add briefs/2026-03-11.md
git commit -m "Add brief: 2026-03-11"
git push
```

Vercel auto-deploys on every push.

## Local development

```bash
python3 build.py
# Open dist/index.html in browser
```

## Structure

```
briefs/          ← Markdown briefs (YYYY-MM-DD.md)
public/          ← Static assets (CSS)
build.py         ← Build script (MD → HTML)
dist/            ← Generated site (git-ignored)
vercel.json      ← Vercel deployment config
publish.sh       ← Auto-publish script for Cowork
```
