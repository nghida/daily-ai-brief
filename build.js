const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const fm = require('front-matter');

const BRIEFS_DIR = path.join(__dirname, 'briefs');
const DIST_DIR = path.join(__dirname, 'dist');
const PUBLIC_DIR = path.join(__dirname, 'public');

// Ensure dist exists
if (fs.existsSync(DIST_DIR)) fs.rmSync(DIST_DIR, { recursive: true });
fs.mkdirSync(DIST_DIR, { recursive: true });

// Copy public assets
if (fs.existsSync(PUBLIC_DIR)) {
  for (const file of fs.readdirSync(PUBLIC_DIR)) {
    fs.copyFileSync(path.join(PUBLIC_DIR, file), path.join(DIST_DIR, file));
  }
}

// Read all briefs
const briefs = fs.readdirSync(BRIEFS_DIR)
  .filter(f => f.endsWith('.md'))
  .map(filename => {
    const raw = fs.readFileSync(path.join(BRIEFS_DIR, filename), 'utf-8');
    const { attributes, body } = fm(raw);
    const slug = filename.replace('.md', '');
    return {
      slug,
      title: attributes.title || slug,
      date: attributes.date || slug,
      excerpt: attributes.excerpt || '',
      tags: attributes.tags || [],
      html: marked(body),
    };
  })
  .sort((a, b) => b.date.localeCompare(a.date));

// HTML shell
function shell(title, content, isDetail = false) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <link rel="stylesheet" href="/style.css">
  <link rel="alternate" type="application/rss+xml" title="Daily AI Brief" href="/feed.xml">
</head>
<body>
  <div class="container">
    ${isDetail ? '' : `
    <header>
      <div class="header-row">
        <div>
          <h1>Daily AI Brief</h1>
          <p>Enterprise AI insights, curated daily by Cowork</p>
        </div>
        <a href="/feed.xml" class="rss-link">RSS</a>
      </div>
    </header>`}
    <main>
      ${content}
    </main>
    <footer>
      <p>Auto-published by Cowork &middot; Nghi Duong</p>
    </footer>
  </div>
</body>
</html>`;
}

// Generate index page
const briefListHTML = briefs.length === 0
  ? '<div class="empty-state"><p>No briefs yet. Check back tomorrow.</p></div>'
  : `<ul class="brief-list">${briefs.map(b => `
    <li class="brief-item">
      <span class="brief-date">${formatDate(b.date)}</span>
      <h2 class="brief-title"><a href="/${b.slug}.html">${b.title}</a></h2>
      <p class="brief-excerpt">${b.excerpt}</p>
      ${b.tags.length ? `<div class="tags">${b.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
    </li>`).join('')}
  </ul>`;

fs.writeFileSync(
  path.join(DIST_DIR, 'index.html'),
  shell('Daily AI Brief', briefListHTML)
);

// Generate individual brief pages
for (const brief of briefs) {
  const detailHTML = `
    <a href="/" class="back-link">&larr; All briefs</a>
    <article>
      <div class="brief-header">
        <span class="date">${formatDate(brief.date)}</span>
        <h1>${brief.title}</h1>
        ${brief.tags.length ? `<div class="tags">${brief.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
      </div>
      <div class="brief-content">
        ${brief.html}
      </div>
    </article>`;

  fs.writeFileSync(
    path.join(DIST_DIR, `${brief.slug}.html`),
    shell(brief.title, detailHTML, true)
  );
}

// Generate RSS feed
const rssItems = briefs.slice(0, 20).map(b => `
  <item>
    <title>${escapeXml(b.title)}</title>
    <link>https://daily-ai-brief.vercel.app/${b.slug}.html</link>
    <description>${escapeXml(b.excerpt)}</description>
    <pubDate>${new Date(b.date).toUTCString()}</pubDate>
    <guid>https://daily-ai-brief.vercel.app/${b.slug}.html</guid>
  </item>`).join('');

const rssFeed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Daily AI Brief</title>
    <link>https://daily-ai-brief.vercel.app</link>
    <description>Enterprise AI insights, curated daily by Cowork</description>
    <language>en</language>
    ${rssItems}
  </channel>
</rss>`;

fs.writeFileSync(path.join(DIST_DIR, 'feed.xml'), rssFeed);

// Helpers
function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
}

function escapeXml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

console.log(`✓ Built ${briefs.length} brief(s) → dist/`);
