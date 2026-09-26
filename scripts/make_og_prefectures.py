#!/usr/bin/env python3
"""Image de partage de la rubrique /prefectures/ (img/og/prefectures.png, 1200 x 630).

Meme gabarit que les autres images OG du site (fond blanc, marque en haut,
titre, domaine, liseré en bas), avec la carte des plateformes a droite, lue
dans prefectures/index.html (lancer build_prefectures.py avant).

    /usr/bin/python3 scripts/make_og_prefectures.py   # Pillow est dans le python3 du systeme
"""

import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = pathlib.Path("/System/Library/Fonts/Supplemental")
COLORS = ["#7c9cf0", "#f39aa2", "#8fd3b6", "#f5c778", "#b9a3ec", "#7fcbe0", "#e7b198", "#c2d67f"]
S = 2  # rendu en 2x puis réduit, pour des bords nets


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size * S)


def polygons(d):
    for m in re.finditer(r"M(-?\d+) (-?\d+)((?:l-?\d+ -?\d+)*)z", d):
        x, y = int(m.group(1)), int(m.group(2))
        pts = [(x, y)]
        for dx, dy in re.findall(r"l(-?\d+) (-?\d+)", m.group(3)):
            x += int(dx)
            y += int(dy)
            pts.append((x, y))
        yield pts


def main():
    hub = (ROOT / "prefectures" / "index.html").read_text(encoding="utf-8")
    svg = re.search(r'<figure class="pf-map pf-map-hub">(.*?)</figure>', hub, re.S).group(1)
    shapes = re.findall(r'<path d="([^"]+)" class="c(\d)">', svg)
    dots = [(int(x), int(y)) for x, y in re.findall(r'<circle cx="(\d+)" cy="(\d+)"', svg)]

    W, H = 1200 * S, 630 * S
    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)
    # disque pâle à droite, comme les autres images
    dr.ellipse((690 * S, -60 * S, 1260 * S, 520 * S), fill="#eaf0ff")
    # carte : viewBox 1000 x 963 → boîte de 450 px de haut, Corse comprise
    k = 450 * S / 963
    ox, oy = 700 * S, 72 * S
    for d, c in shapes:
        for poly in polygons(d):
            pts = [(ox + x * k, oy + y * k) for x, y in poly]
            dr.polygon(pts, fill=COLORS[int(c)], outline="white")
    for x, y in dots:
        cx, cy, r = ox + x * k, oy + y * k, 5 * S
        dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#0a0f2c", outline="white", width=2 * S)

    ink, grey, red, blue = "#0a0f2c", "#5a6378", "#ed2939", "#002395"
    f_brand = font("Arial Bold.ttf", 30)
    dr.text((72 * S, 54 * S), "Naturalisation", font=f_brand, fill=ink)
    w = dr.textlength("Naturalisation ", font=f_brand)
    dr.text((72 * S + w, 54 * S), "France Facile", font=f_brand, fill=red)
    dr.text((72 * S, 205 * S), "101 DÉPARTEMENTS · 36 PLATEFORMES", font=font("Arial Bold.ttf", 23), fill=blue)
    f_title = font("Arial Black.ttf", 62)
    dr.text((68 * S, 248 * S), "Où déposer", font=f_title, fill=ink)
    dr.text((68 * S, 322 * S), "votre dossier ?", font=f_title, fill=ink)
    dr.text((72 * S, 420 * S), "La plateforme de votre département :", font=font("Arial Bold.ttf", 25), fill=grey)
    dr.text((72 * S, 454 * S), "adresse, courriel, rendez-vous", font=font("Arial Bold.ttf", 25), fill=grey)
    dr.text((72 * S, 566 * S), "naturalisationfrancefacile.fr", font=font("Arial Bold.ttf", 24), fill="#8a93a6")
    dr.rectangle((0, H - 12 * S, W, H), fill=blue)
    im = im.resize((1200, 630), Image.LANCZOS)
    out = ROOT / "img" / "og" / "prefectures.png"
    im.save(out, optimize=True)
    print(out, out.stat().st_size // 1024, "Ko")


if __name__ == "__main__":
    main()
