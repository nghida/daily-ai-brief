#!/usr/bin/env python3
"""Build static site from markdown briefs — v2 redesign."""

import os, re, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
BRIEFS_DIR = ROOT / "briefs"
DIST_DIR = ROOT / "dist"
PUBLIC_DIR = ROOT / "public"

SITE_TITLE = "Daily AI Brief"
SITE_SUBTITLE = "Enterprise AI insights, curated daily by Cowork"
SITE_URL = "https://nghida.github.io/daily-ai-brief"

# ── Inline CSS ── (no external file dependency)

CSS = '''
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&display=swap');

:root {
  --bg: #fafaf9;
  --surface: #ffffff;
  --text: #1c1917;
  --text-2: #44403c;
  --text-3: #78716c;
  --muted: #a8a29e;
  --accent: #c2410c;
  --accent-light: #fff7ed;
  --accent-mid: #fed7aa;
  --border: #e7e5e4;
  --border-light: #f5f5f4;
  --shadow-sm: 0 1px 2px rgba(28,25,23,.05);
  --shadow-md: 0 4px 16px rgba(28,25,23,.06), 0 1px 3px rgba(28,25,23,.04);
  --radius: 12px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a0a0a;
    --surface: #171717;
    --text: #fafaf9;
    --text-2: #d6d3d1;
    --text-3: #a8a29e;
    --muted: #78716c;
    --accent: #fb923c;
    --accent-light: #1c1210;
    --accent-mid: #431407;
    --border: #262626;
    --border-light: #1c1c1c;
    --shadow-sm: 0 1px 2px rgba(0,0,0,.2);
    --shadow-md: 0 4px 16px rgba(0,0,0,.3);
  }
}

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

html { scroll-behavior: smooth; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

::selection { background: var(--accent-mid); color: var(--accent); }

/* ── Layout ── */
.site { max-width: 720px; margin: 0 auto; padding: 0 1.5rem; min-height: 100vh; display: flex; flex-direction: column; }
main { flex: 1; }

/* ── Header ── */
.site-header {
  padding: 3rem 0 2.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.site-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.brand { display: flex; align-items: center; gap: 0.85rem; text-decoration: none; }
.brand-icon {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #ea580c, #c2410c);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.7rem; letter-spacing: 0.05em;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(194,65,12,.25);
}
.brand-text h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.35rem; font-weight: 700; letter-spacing: -0.03em;
  color: var(--text); line-height: 1.2;
}
.brand-text p { font-size: 0.8rem; color: var(--muted); margin-top: 0.1rem; }
.header-actions { display: flex; gap: 0.5rem; }
.btn-rss {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface);
  color: var(--text-3); font-size: 0.78rem; font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
}
.btn-rss:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }
.btn-rss svg { width: 14px; height: 14px; }

/* ── Brief List ── */
.brief-count {
  font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--muted);
  margin-bottom: 1rem;
}
.brief-list { list-style: none; }
.brief-card {
  display: block;
  text-decoration: none; color: inherit;
  padding: 1.5rem;
  margin: 0 -1.5rem;
  border-radius: var(--radius);
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
.brief-card:hover {
  background: var(--surface);
  border-color: var(--border);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.brief-item + .brief-item { border-top: 1px solid var(--border-light); }
.brief-item + .brief-item .brief-card { margin-top: 0; }
.brief-card:hover + .brief-item, .brief-item:has(.brief-card:hover) { border-top-color: transparent; }
.card-meta {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.75rem; color: var(--muted); font-weight: 500;
  margin-bottom: 0.65rem;
}
.card-meta .dot { opacity: 0.4; }
.card-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.25rem; font-weight: 600; line-height: 1.35;
  letter-spacing: -0.02em; color: var(--text);
  margin-bottom: 0.5rem;
  transition: color 0.15s ease;
}
.brief-card:hover .card-title { color: var(--accent); }
.card-excerpt { font-size: 0.9rem; color: var(--text-2); line-height: 1.65; }
.card-bottom { display: flex; align-items: center; justify-content: space-between; margin-top: 1rem; }
.tags { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.tag {
  font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.2em 0.6em; border-radius: 5px;
  background: var(--accent-light); color: var(--accent);
  border: 1px solid var(--accent-mid);
}
.card-arrow {
  font-size: 0.8rem; color: var(--accent); font-weight: 500;
  display: inline-flex; align-items: center; gap: 0.25rem;
  opacity: 0; transform: translateX(-6px);
  transition: all 0.2s ease;
}
.card-arrow svg { width: 14px; height: 14px; }
.brief-card:hover .card-arrow { opacity: 1; transform: translateX(0); }

/* ── Article Detail ── */
.back { display: inline-flex; align-items: center; gap: 0.3rem; color: var(--muted); text-decoration: none; font-size: 0.82rem; font-weight: 500; margin-bottom: 2rem; transition: color 0.15s; }
.back:hover { color: var(--accent); }
.back svg { width: 16px; height: 16px; }

.article-header { margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border); }
.article-header .meta { font-size: 0.78rem; color: var(--accent); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.article-header h1 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 2.1rem; font-weight: 700; letter-spacing: -0.03em;
  line-height: 1.25; margin-top: 0.75rem; color: var(--text);
}
.article-header .tags { margin-top: 1rem; }

/* ── Article Content ── */
.article-body { font-size: 1rem; line-height: 1.85; color: var(--text); }
.article-body h2 {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.35rem; font-weight: 600; letter-spacing: -0.02em;
  margin: 2.5rem 0 0.85rem; color: var(--text);
  padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-light);
}
.article-body h3 { font-size: 1.05rem; font-weight: 600; margin: 1.75rem 0 0.5rem; color: var(--text); }
.article-body p { margin-bottom: 1.15rem; color: var(--text-2); }
.article-body ul, .article-body ol { margin: 0.75rem 0 1.25rem 1.25rem; color: var(--text-2); }
.article-body li { margin-bottom: 0.45rem; padding-left: 0.25rem; }
.article-body li::marker { color: var(--accent); }
.article-body a { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1.5px; text-decoration-color: var(--accent-mid); transition: text-decoration-color 0.15s; }
.article-body a:hover { text-decoration-color: var(--accent); }
.article-body strong { font-weight: 600; color: var(--text); }
.article-body em { font-family: 'Fraunces', Georgia, serif; font-style: italic; color: var(--text-3); }
.article-body blockquote { border-left: 3px solid var(--accent); background: var(--accent-light); padding: 1rem 1.25rem; margin: 1.5rem 0; border-radius: 0 8px 8px 0; color: var(--text-3); font-style: italic; }
.article-body blockquote p { margin: 0; }
.article-body code { background: var(--border-light); color: var(--accent); padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.87em; font-family: 'SF Mono', 'Fira Code', monospace; }
.article-body pre { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; overflow-x: auto; margin: 1.5rem 0; }
.article-body pre code { background: none; padding: 0; font-size: 0.85rem; color: var(--text-2); }
.article-body hr { border: none; height: 1px; background: var(--border); margin: 2.5rem 0; }

/* ── Article Nav ── */
.article-nav { display: flex; justify-content: space-between; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); }
.article-nav a { color: var(--text-3); text-decoration: none; font-size: 0.82rem; font-weight: 500; display: inline-flex; align-items: center; gap: 0.3rem; transition: color 0.15s; }
.article-nav a:hover { color: var(--accent); }
.article-nav svg { width: 14px; height: 14px; }

/* ── Footer ── */
.site-footer { margin-top: 3rem; padding: 2rem 0; border-top: 1px solid var(--border); text-align: center; }
.site-footer p { font-size: 0.78rem; color: var(--muted); }
.site-footer .cowork { font-weight: 600; color: var(--text-3); }

/* ── Empty ── */
.empty { text-align: center; padding: 5rem 0; color: var(--muted); }
.empty-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.4; }

/* ── Animation ── */
@keyframes fadeUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
.brief-item { animation: fadeUp 0.35s ease both; }
.brief-item:nth-child(1) { animation-delay: .04s; }
.brief-item:nth-child(2) { animation-delay: .08s; }
.brief-item:nth-child(3) { animation-delay: .12s; }
.brief-item:nth-child(4) { animation-delay: .16s; }
.brief-item:nth-child(5) { animation-delay: .20s; }
.brief-item:nth-child(6) { animation-delay: .24s; }
.brief-item:nth-child(7) { animation-delay: .28s; }
article { animation: fadeUp 0.3s ease both; }

/* ── Responsive ── */
@media (max-width: 640px) {
  .site { padding: 0 1.15rem; }
  .site-header { padding: 2rem 0 2rem; }
  .brand-text h1 { font-size: 1.15rem; }
  .card-title { font-size: 1.1rem; }
  .article-header h1 { font-size: 1.65rem; }
  .brief-card { padding: 1.25rem 0; margin: 0; border-radius: 0; }
  .brief-card:hover { border-color: transparent; box-shadow: none; transform: none; background: transparent; }
  .brief-card:hover .card-title { color: var(--accent); }
  .card-arrow { opacity: 1; transform: translateX(0); }
}
'''

# ── SVG Icons ──

ICON_RSS = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>'
ICON_LEFT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>'
ICON_RIGHT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>'


# ── Markdown to HTML ──

def md_to_html(md):
    lines = md.split('\n')
    out = []
    in_ul = in_ol = in_code = in_bq = False

    for line in lines:
        s = line.strip()

        if s.startswith('```'):
            if in_code: out.append('</code></pre>'); in_code = False
            else: out.append('<pre><code>'); in_code = True
            continue
        if in_code: out.append(esc(line)); continue

        if in_ul and not s.startswith('- ') and not s.startswith('* '): out.append('</ul>'); in_ul = False
        if in_ol and not re.match(r'^\d+\.\s', s): out.append('</ol>'); in_ol = False

        if s.startswith('> '):
            if not in_bq: out.append('<blockquote>'); in_bq = True
            out.append(f'<p>{inl(s[2:])}</p>'); continue
        elif in_bq: out.append('</blockquote>'); in_bq = False

        if s in ('---','***','___'): out.append('<hr>'); continue

        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m: out.append(f'<h{len(m[1])}>{inl(m[2])}</h{len(m[1])}>'); continue

        if s.startswith('- ') or s.startswith('* '):
            if not in_ul: out.append('<ul>'); in_ul = True
            out.append(f'<li>{inl(s[2:])}</li>'); continue

        m = re.match(r'^(\d+)\.\s+(.*)', s)
        if m:
            if not in_ol: out.append('<ol>'); in_ol = True
            out.append(f'<li>{inl(m[2])}</li>'); continue

        if s: out.append(f'<p>{inl(s)}</p>')
        else: out.append('')

    if in_ul: out.append('</ul>')
    if in_ol: out.append('</ol>')
    if in_bq: out.append('</blockquote>')
    if in_code: out.append('</code></pre>')
    return '\n'.join(out)

def inl(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')


# ── Front matter ──

def parse_brief(fp):
    raw = fp.read_text('utf-8')
    attrs, body = {}, raw
    if raw.startswith('---'):
        parts = raw.split('---', 2)
        if len(parts) >= 3:
            body = parts[2].strip()
            for ln in parts[1].strip().split('\n'):
                ln = ln.strip()
                if ':' in ln:
                    k, v = ln.split(':', 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if v.startswith('[') and v.endswith(']'):
                        v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(',')]
                    attrs[k] = v
    wc = len(body.split())
    return dict(slug=fp.stem, title=attrs.get('title', fp.stem), date=attrs.get('date', fp.stem),
                excerpt=attrs.get('excerpt',''), tags=attrs.get('tags',[]),
                html=md_to_html(body), read_time=max(1, round(wc/200)))


# ── Templates ──

def page(title, body_html, is_article=False):
    header = ''
    if not is_article:
        header = f'''
    <header class="site-header">
      <div class="site-header-top">
        <a href="./" class="brand">
          <div class="brand-icon">AI</div>
          <div class="brand-text">
            <h1>{SITE_TITLE}</h1>
            <p>{SITE_SUBTITLE}</p>
          </div>
        </a>
        <div class="header-actions">
          <a href="./feed.xml" class="btn-rss">{ICON_RSS} RSS</a>
        </div>
      </div>
    </header>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{SITE_SUBTITLE}">
  <link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="./feed.xml">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1F4E1;</text></svg>">
  <style>{CSS}</style>
</head>
<body>
  <div class="site">
    {header}
    <main>{body_html}</main>
    <footer class="site-footer">
      <p>Auto-published by <span class="cowork">Cowork</span> &middot; Nghi Duong</p>
    </footer>
  </div>
</body>
</html>'''

def fmt_date(s):
    try: return datetime.strptime(s, '%Y-%m-%d').strftime('%b %d, %Y')
    except: return s

def fmt_short(s):
    try: return datetime.strptime(s, '%Y-%m-%d').strftime('%a, %b %d')
    except: return s


# ── Build ──

def build():
    shutil.rmtree(DIST_DIR, ignore_errors=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Copy public assets (if any non-CSS files)
    if PUBLIC_DIR.exists():
        for f in PUBLIC_DIR.iterdir():
            if f.is_file() and f.suffix != '.css':
                shutil.copy2(f, DIST_DIR / f.name)

    briefs = []
    if BRIEFS_DIR.exists():
        for f in BRIEFS_DIR.glob('*.md'):
            briefs.append(parse_brief(f))
    briefs.sort(key=lambda b: b['date'], reverse=True)

    # ── Index ──
    if not briefs:
        content = '<div class="empty"><div class="empty-icon">&#x1F4E1;</div><p>No briefs yet.<br>Check back tomorrow morning.</p></div>'
    else:
        cards = []
        for b in briefs:
            tags = ''.join(f'<span class="tag">{t}</span>' for t in b['tags'])
            tags_html = f'<div class="tags">{tags}</div>' if b['tags'] else ''
            cards.append(f'''
      <li class="brief-item">
        <a href="./{b["slug"]}.html" class="brief-card">
          <div class="card-meta">
            <span>{fmt_short(b["date"])}</span>
            <span class="dot">&middot;</span>
            <span>{b["read_time"]} min read</span>
          </div>
          <h2 class="card-title">{b["title"]}</h2>
          <p class="card-excerpt">{b["excerpt"]}</p>
          <div class="card-bottom">
            {tags_html}
            <span class="card-arrow">Read {ICON_RIGHT}</span>
          </div>
        </a>
      </li>''')

        content = f'<div class="brief-count">{len(briefs)} brief{"s" if len(briefs)!=1 else ""}</div>\n<ul class="brief-list">{"".join(cards)}</ul>'

    (DIST_DIR / 'index.html').write_text(page(SITE_TITLE, content))

    # ── Detail pages ──
    for i, b in enumerate(briefs):
        tags = ''.join(f'<span class="tag">{t}</span>' for t in b['tags'])
        tags_html = f'<div class="tags">{tags}</div>' if b['tags'] else ''

        nav = '<div class="article-nav">'
        if i < len(briefs)-1:
            p = briefs[i+1]
            nav += f'<a href="./{p["slug"]}.html">{ICON_LEFT} {fmt_short(p["date"])}</a>'
        else:
            nav += '<span></span>'
        if i > 0:
            n = briefs[i-1]
            nav += f'<a href="./{n["slug"]}.html">{fmt_short(n["date"])} {ICON_RIGHT}</a>'
        else:
            nav += '<span></span>'
        nav += '</div>'

        detail = f'''
    <a href="./" class="back">{ICON_LEFT} All briefs</a>
    <article>
      <div class="article-header">
        <div class="meta">{fmt_date(b["date"])} &middot; {b["read_time"]} min read</div>
        <h1>{b["title"]}</h1>
        {tags_html}
      </div>
      <div class="article-body">{b["html"]}</div>
      {nav}
    </article>'''

        (DIST_DIR / f'{b["slug"]}.html').write_text(page(b['title'], detail, True))

    # ── RSS ──
    items = '\n'.join(f'''    <item>
      <title>{esc(b["title"])}</title>
      <link>{SITE_URL}/{b["slug"]}.html</link>
      <description>{esc(b["excerpt"])}</description>
      <pubDate>{datetime.strptime(b["date"],"%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 GMT")}</pubDate>
      <guid>{SITE_URL}/{b["slug"]}.html</guid>
    </item>''' for b in briefs[:20])

    (DIST_DIR / 'feed.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_SUBTITLE}</description>
    <language>en</language>
{items}
  </channel>
</rss>''')

    print(f'✓ Built {len(briefs)} brief(s) → dist/')

if __name__ == '__main__':
    build()
