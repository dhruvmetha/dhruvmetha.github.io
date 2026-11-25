#!/usr/bin/env python3
"""Build index.html and sitemap.xml from _templates/index.html and _data/*.yml.

    python3 build.py          write index.html and sitemap.xml
    python3 build.py --check  exit 1 if either file is out of date (run before committing)

The site is served as plain files (.nojekyll), so GitHub Pages serves exactly what
is committed. Edit the template or the YAML, run this script, commit both.
Needs PyYAML. On this machine /usr/bin/python3 has it; elsewhere: pip install pyyaml
"""
import argparse
import datetime
import html
import re
import struct
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing. Run with /usr/bin/python3, or: python3 -m pip install pyyaml")

ROOT = Path(__file__).resolve().parent
SITE = "https://dhruvmetha.github.io"
# Pages listed in sitemap.xml. The project pages live in their own repos but share this host.
SITEMAP_URLS = [f"{SITE}/", f"{SITE}/legged-probe/", f"{SITE}/insert/"]
PLACEHOLDER = re.compile(r"\[[A-Z ]*\]")

errors = []


def esc(s):
    return html.escape(str(s), quote=True)


def jpeg_size(path):
    """Width and height of a baseline or progressive JPEG, without Pillow."""
    data = path.read_bytes()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise ValueError(f"no size marker in {path}")


def need(path):
    p = ROOT / path
    if not p.is_file():
        errors.append(f"missing file: {path}")
    return p


def media_html(p):
    alt = esc(p.get("media_alt") or p["title"])
    if p.get("teaser"):
        poster = re.sub(r"\.mp4$", ".jpg", p["teaser"])
        need(p["teaser"])
        w, h = jpeg_size(need(poster))
        return (
            f'          <video class="teaser" autoplay muted loop playsinline preload="metadata" '
            f'poster="{esc(poster)}" width="{w}" height="{h}" style="--ar: {w / h:.3f}" aria-label="{alt}" tabindex="0" '
            f'title="Click to pause or play">\n'
            f'            <source src="{esc(p["teaser"])}" type="video/mp4">\n'
            f"          </video>"
        )
    if p.get("image"):
        w, h = jpeg_size(need(p["image"]))
        return (f'          <img src="{esc(p["image"])}" alt="{alt}" width="{w}" height="{h}" '
                f'style="--ar: {w / h:.3f}" loading="lazy">')
    return ""


def info_html(p, indent):
    links = p.get("links") or {}
    pad = " " * indent
    title_url = links.get("project page") or next(iter(links.values()), None)
    if title_url:
        title = f'<a href="{esc(title_url)}" class="papertitle">{esc(p["title"])}</a>'
    else:
        title = f'<span class="papertitle">{esc(p["title"])}</span>'
    link_row = " / ".join(f'<a href="{esc(u)}">{esc(label)}</a>' for label, u in links.items())
    lines = [
        title,
        f'<div class="paper-authors">{p["authors"]}</div>',
        f'<div class="paper-venue"><em>{esc(p["venue"])}</em></div>',
    ]
    if link_row:
        lines.append(f'<div class="paper-links">{link_row}</div>')
    if p.get("blurb"):
        lines.append(f'<p class="paper-desc">{" ".join(p["blurb"].split())}</p>')
    return "\n".join(pad + line for line in lines)


def paper_html(p):
    for field in ("key", "title", "authors", "venue"):
        if not p.get(field):
            errors.append(f"paper {p.get('key', '?')}: missing {field}")
    return (
        f'      <article class="paper" id="{esc(p["key"])}">\n'
        f'        <div class="paper-media">\n{media_html(p)}\n        </div>\n'
        f'        <div class="paper-info">\n{info_html(p, 10)}\n        </div>\n'
        f"      </article>"
    )


def compact_html(p):
    return (f'        <div class="paper-info" id="{esc(p["key"])}">\n'
            f"{info_html(p, 10)}\n        </div>")


def news_html(news):
    out = ['        <ul class="news">']
    for item in news["items"][: news.get("show", 5)]:
        d = datetime.datetime.strptime(str(item["date"]), "%Y-%m")
        out.append(f'          <li><span class="news-date">{d.strftime("%b %Y")}</span>'
                   f'<span>{" ".join(item["text"].split())}</span></li>')
    out.append("        </ul>")
    return "\n".join(out)


def render():
    pubs = yaml.safe_load((ROOT / "_data/publications.yml").read_text())
    news = yaml.safe_load((ROOT / "_data/news.yml").read_text())
    page = (ROOT / "_templates/index.html").read_text()
    parts = {
        "news": news_html(news),
        "selected": "\n".join(paper_html(p) for p in pubs if p.get("selected")),
        "other": "\n".join(compact_html(p) for p in pubs if not p.get("selected")),
    }
    for name, value in parts.items():
        page = page.replace("{{ " + name + " }}", value)
    leftover = re.findall(r"\{\{.*?\}\}", page)
    if leftover:
        errors.append(f"unfilled template markers: {leftover}")
    banner = ("<!-- Generated by build.py from _templates/index.html and _data/*.yml. "
              "Edit those, then run: python3 build.py -->\n")
    index = page.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + banner, 1)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url><loc>{u}</loc></url>\n" for u in SITEMAP_URLS)
               + "</urlset>\n")
    return {"index.html": index, "sitemap.xml": sitemap}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if the committed output is stale")
    args = ap.parse_args()

    outputs = render()
    for name, text in outputs.items():
        for line_no, line in enumerate(text.splitlines(), 1):
            for m in PLACEHOLDER.findall(line):
                errors.append(f"{name}:{line_no}: placeholder {m} would show on the site")
    if errors:
        sys.exit("build.py found problems:\n  " + "\n  ".join(errors))

    # Files the page links to but that are added by hand outside this script.
    for linked in ("pdfs/Dhruv-Metha-Ramesh-CV.pdf",):
        if not (ROOT / linked).is_file():
            print(f"warning: {linked} is missing, so the CV link will 404 until it is added",
                  file=sys.stderr)

    stale = [n for n, t in outputs.items()
             if not (ROOT / n).is_file() or (ROOT / n).read_text() != t]
    if args.check:
        if stale:
            sys.exit(f"out of date: {', '.join(stale)}. Run: python3 build.py")
        print("index.html and sitemap.xml are up to date")
        return
    for name in stale:
        (ROOT / name).write_text(outputs[name])
    print(f"wrote {', '.join(stale)}" if stale else "nothing to do, output already up to date")


if __name__ == "__main__":
    main()
