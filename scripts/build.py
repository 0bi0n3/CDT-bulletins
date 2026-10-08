#!/usr/bin/env python3
"""Build the deployable site into _site/: copies static files, adds slugs to
bulletins.json, and generates feed.xml, archive.html and story/<slug>.html.

  python3 scripts/build.py [--site-url https://user.github.io/repo]

The site URL defaults to the GitHub Pages URL derived from $GITHUB_REPOSITORY.
"""
import argparse, datetime, email.utils, html, json, os, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
STATIC = ["index.html", "style.css", "app.js", ".nojekyll"]
TITLE = "AI for Digital Media Inclusion"
DESC = "News from the Centre for Doctoral Training in AI for Digital Media Inclusion, University of Surrey and Royal Holloway."

e = html.escape


def slugify(b, used):
    base = re.sub(r"[^a-z0-9]+", "-", b["title"].lower()).strip("-")[:60].strip("-") or "story"
    slug = f'{b["date"][:10]}-{base}'
    n, s = 2, slug
    while s in used:
        s, n = f"{slug}-{n}", n + 1
    used.add(s)
    return s


def http_url(u):
    return u if u and re.match(r"https?://", u) else None


def parse_date(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def page(title, body, depth=0):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | {TITLE}</title>
<link rel="stylesheet" href="{up}style.css">
<link rel="alternate" type="application/rss+xml" href="{up}feed.xml" title="{TITLE}">
</head><body>
<header class="masthead"><p class="kicker">Centre for Doctoral Training in</p>
<h1><a href="{up}index.html" style="text-decoration:none">{TITLE}</a></h1></header>
<main>{body}</main>
<footer><p><a href="{up}index.html">Front page</a> &middot; <a href="{up}archive.html">Archive</a> &middot; <a href="{up}feed.xml">RSS</a></p></footer>
</body></html>
"""


def story_html(b):
    paras = "".join(f"<p>{e(p)}</p>" for p in (b.get("body") or "").split("\n\n") if p.strip())
    link = http_url(b.get("link"))
    when = parse_date(b["date"]).strftime("%-d %B %Y, %H:%M UTC")
    return (f'<article id="lead" style="border:0"><div class="tag">{"<span class=flash>Breaking</span>" if b.get("breaking") else ""}{e(b.get("category", "News"))}</div>'
            f'<h2>{e(b["title"])}</h2><p class="summary">{e(b.get("summary", ""))}</p>{paras}'
            f'<div class="meta">The Editors &middot; {when}</div>'
            + (f'<p><a class="read" href="{e(link)}" rel="noopener">Read more &rarr;</a></p>' if link else "")
            + "</article>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-url")
    a = ap.parse_args()
    site = a.site_url
    if not site and os.environ.get("GITHUB_REPOSITORY"):
        owner, repo = os.environ["GITHUB_REPOSITORY"].split("/")
        site = f"https://{owner.lower()}.github.io/{repo}"
    site = (site or "http://localhost:8000").rstrip("/")

    data = json.loads((ROOT / "bulletins.json").read_text())
    items = sorted(data["bulletins"], key=lambda b: b["date"], reverse=True)
    used = set()
    for b in items:
        b["slug"] = slugify(b, used)

    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "story").mkdir(parents=True)
    for f in STATIC:
        shutil.copy(ROOT / f, OUT / f)
    data["bulletins"] = items
    (OUT / "bulletins.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

    for b in items:
        (OUT / "story" / f'{b["slug"]}.html').write_text(page(b["title"], story_html(b), 1))

    # Archive: grouped by month.
    months, body = {}, ["<h2>Archive</h2>"]
    for b in items:
        months.setdefault(parse_date(b["date"]).strftime("%B %Y"), []).append(b)
    for m, bs in months.items():
        body.append(f"<h3>{e(m)}</h3><ul>")
        for b in bs:
            body.append(f'<li><a href="story/{b["slug"]}.html">{e(b["title"])}</a> '
                        f'<span class="meta">{e(b.get("category", ""))} &middot; {b["date"][:10]}</span></li>')
        body.append("</ul>")
    (OUT / "archive.html").write_text(page("Archive", "".join(body)))

    # RSS 2.0
    rows = []
    for b in items[:50]:
        url = f'{site}/story/{b["slug"]}.html'
        rows.append(
            f"<item><title>{e(b['title'])}</title><link>{e(url)}</link><guid isPermaLink=\"true\">{e(url)}</guid>"
            f"<pubDate>{email.utils.format_datetime(parse_date(b['date']))}</pubDate>"
            f"<category>{e(b.get('category', 'News'))}</category>"
            f"<description>{e(b.get('summary', ''))}</description></item>")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>{TITLE}</title><link>{e(site)}/</link><description>{e(DESC)}</description><language>en-GB</language>
<atom:link href="{e(site)}/feed.xml" rel="self" type="application/rss+xml"/>
<lastBuildDate>{email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc))}</lastBuildDate>
{chr(10).join(rows)}
</channel></rss>
"""
    (OUT / "feed.xml").write_text(feed)
    print(f"Built {len(items)} stories -> {OUT} (site {site})")


if __name__ == "__main__":
    main()
