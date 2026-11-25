# dhruvmetha.github.io

Source for https://dhruvmetha.github.io, the homepage of Dhruv Metha Ramesh.
The design comes from [Jon Barron's website](https://github.com/jonbarron/jonbarron.github.io).

GitHub Pages serves this repo as plain files (`.nojekyll`), so what you commit is what goes live.

## Editing

- Papers: `_data/publications.yml`. News: `_data/news.yml`.
- Bio, contact links, reviewing and teaching: `_templates/index.html`.
- Styles: `stylesheet.css`. The upstream part is unchanged; site changes are in the block at the end.

After any edit, rebuild and check the result:

```bash
/usr/bin/python3 build.py           # writes index.html and sitemap.xml (needs PyYAML)
/usr/bin/python3 build.py --check   # fails if index.html is stale; run before committing
python3 -m http.server 8000         # then open http://localhost:8000
```

`build.py` refuses to write a page that still contains an all-caps bracketed placeholder.

## CV

The CV link points at `pdfs/Dhruv-Metha-Ramesh-CV.pdf`. Copy the built PDF there by hand; `build.py` warns while it is missing. Leave the phone number out of the public copy.

## Media

- Teasers go in `videos/` as MP4 (about 480 px wide, under 500 KB) with a `.jpg` poster of the same name. `_tools/media.sh` has the ffmpeg commands.
- `_tools/make_images.py` rebuilds the favicons and the link-preview image `images/og.jpg` from `images/profile.jpg` and the teaser posters.

The project pages `/insert/` and `/legged-probe/` live in their own repos, `dhruvmetha/insert` and `dhruvmetha/legged-probe`.
