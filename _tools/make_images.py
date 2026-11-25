#!/usr/bin/env python3
"""Make the favicon set and the 1200x630 link-preview image (images/og.jpg).

Run from the repo root after changing images/profile.jpg or a teaser poster:
    python3 _tools/make_images.py
Needs Pillow and the Lato font (Ubuntu package fonts-lato).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ACCENT = (23, 114, 208)  # #1772d0, the link color in stylesheet.css
FONT_DIRS = [Path("/usr/share/fonts/truetype/lato"), Path.home() / ".fonts"]


def font(name, size):
    for d in FONT_DIRS:
        p = d / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def favicons():
    big = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, 511, 511], radius=96, fill=ACCENT)
    f = font("Lato-Bold.ttf", 270)
    d.text((256, 262), "DM", font=f, fill="white", anchor="mm")
    big.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    big.resize((32, 32), Image.LANCZOS).save(ROOT / "images/favicon-32x32.png")
    touch = Image.new("RGB", (180, 180), ACCENT)
    touch.paste(big.resize((180, 180), Image.LANCZOS), (0, 0), big.resize((180, 180), Image.LANCZOS))
    touch.save(ROOT / "images/apple-touch-icon.png")


def cover(img, w, h):
    return ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.5))


def og_image():
    W, H = 1200, 630
    og = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(og)

    # Left: circular photo, name, one line of description.
    photo = cover(Image.open(ROOT / "images/profile.jpg").convert("RGB"), 280, 280)
    mask = Image.new("L", (280, 280), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 279, 279], fill=255)
    og.paste(photo, (160, 60), mask)
    d.text((300, 400), "Dhruv Metha Ramesh", font=font("Lato-Bold.ttf", 50), fill="black", anchor="mm")
    d.text((300, 462), "PhD student in robot learning", font=font("Lato-Regular.ttf", 30), fill=(60, 60, 60), anchor="mm")
    d.text((300, 504), "Rutgers University", font=font("Lato-Regular.ttf", 30), fill=(60, 60, 60), anchor="mm")
    d.text((300, 566), "dhruvmetha.github.io", font=font("Lato-Regular.ttf", 28), fill=ACCENT, anchor="mm")

    # Right: two real-robot stills from the homepage teaser posters.
    probe = Image.open(ROOT / "videos/legged_probe.jpg").convert("RGB")
    probe = probe.crop((0, 0, probe.width, probe.height // 2))  # top half is the camera view
    insert = Image.open(ROOT / "videos/insert.jpg").convert("RGB")
    insert = insert.crop((0, int(insert.height * 0.47), insert.width, int(insert.height * 0.47) + insert.width * 264 // 540))
    og.paste(cover(probe, 540, 264), (620, 40))
    og.paste(cover(insert, 540, 264), (620, 326))
    og.save(ROOT / "images/og.jpg", quality=85, optimize=True, progressive=True)


if __name__ == "__main__":
    favicons()
    og_image()
    print("wrote favicon.ico, images/favicon-32x32.png, images/apple-touch-icon.png, images/og.jpg")
