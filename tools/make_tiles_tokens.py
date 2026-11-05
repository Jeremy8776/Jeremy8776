"""Builds the README quick-link thumbnails and the tool tokens.

  assets/tile-<name>.webp  screenshot thumbnail, Reel-style shade + captions
  assets/tok-<name>.svg    pill token: official mono logo + label

Usage: make_tiles_tokens.py <shots dir> <output dir>
Shots dir holds the screenshots and an icons/ folder of logo SVGs
(Simple Icons, CC0; ComfyUI mark from Comfy-Org/ComfyUI_frontend).
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SHOTS, OUT = Path(sys.argv[1]), Path(sys.argv[2])
A = OUT / "assets"
A.mkdir(parents=True, exist_ok=True)
INK = (242, 240, 236)
SANS = "C:/Windows/Fonts/arial.ttf"   # shortcut: same Gill Sans stand-in as the banner
MONO = "C:/Windows/Fonts/consola.ttf"
TW, TH = 960, 600

# (file stem, screenshot, title, caption, vertical crop anchor 0=top 0.5=centre)
TILES = [
    ("craft", "craft.png", "Craft", "CONTRIBUTOR \u00b7 CREATIVE APP SUITE IN RUST", 0.0),
    ("armoze", "armoze.webp", "ARMOZE", "MAP ZONE EDITOR \u00b7 ARMA REFORGER", 0.4),
    ("dram", "dram.png", "DRAM", "LOCAL-FIRST AI DESKTOP", 0.5),
    ("aimodeldb", "aimodeldb-p.webp", "AIModelDB", "TRACK AND VALIDATE AI MODELS", 0.3),
]


def spaced(d, xy, text, font, sp, fill):
    x, y = xy
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + sp


def tile(shot, title, cap, anchor):
    im = Image.open(SHOTS / shot).convert("RGB")
    s = max(TW / im.width, TH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = (im.width - TW) // 2
    y0 = round((im.height - TH) * anchor)
    im = im.crop((x0, y0, x0 + TW, y0 + TH)).convert("RGBA")
    shade = Image.new("RGBA", (TW, TH))
    sd = ImageDraw.Draw(shade)
    for y in range(TH):
        f = max(0.0, (y / TH - 0.45) / 0.55)
        sd.line([(0, y), (TW, y)], fill=(0, 0, 0, int(225 * f)))
    im = Image.alpha_composite(im, shade)
    d = ImageDraw.Draw(im)
    d.text((40, TH - 118), title, font=ImageFont.truetype(SANS, 60), fill=INK)
    spaced(d, (42, TH - 46), cap, ImageFont.truetype(MONO, 18), 2.4, INK + (200,))
    # Up-right arrow drawn as lines: neither stand-in font has the glyph.
    ax, ay = TW - 52, TH - 30
    d.line([(ax, ay), (ax + 13, ay - 13)], fill=INK, width=2)
    d.line([(ax + 4, ay - 13), (ax + 13, ay - 13), (ax + 13, ay - 4)], fill=INK, width=2)
    return im.convert("RGB")


for stem, shot, title, cap, anc in TILES:
    tile(shot, title, cap, anc).save(A / f"tile-{stem}.webp", "WEBP", quality=82, method=6)

# Filmstrip under the banner: one small linked thumbnail per reel slide,
# because an animated image can only carry a single link.
SW, SH = 480, 240
STRIP = [("reel-1.webp", "01", "ABOUT"), ("reel-2.webp", "02", "PANDORA"),
         ("reel-3.webp", "03", "LU"), ("reel-4.webp", "04", "SPORTS")]


def strip_thumb(shot, num, label):
    im = Image.open(SHOTS / shot).convert("RGB")
    s = max(SW / im.width, SH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = (im.width - SW) // 2, (im.height - SH) // 2
    im = im.crop((x0, y0, x0 + SW, y0 + SH)).convert("RGBA")
    shade = Image.new("RGBA", (SW, SH))
    sd = ImageDraw.Draw(shade)
    for y in range(SH):
        f = max(0.0, (y / SH - 0.35) / 0.65)
        sd.line([(0, y), (SW, y)], fill=(0, 0, 0, int(215 * f)))
    im = Image.alpha_composite(im, shade)
    d = ImageDraw.Draw(im)
    mono = ImageFont.truetype(MONO, 22)
    spaced(d, (24, SH - 48), f"{num}  {label}", mono, 3, INK)
    ax, ay = SW - 36, SH - 26
    d.line([(ax, ay), (ax + 12, ay - 12)], fill=INK, width=2)
    d.line([(ax + 4, ay - 12), (ax + 12, ay - 12), (ax + 12, ay - 4)], fill=INK, width=2)
    return im.convert("RGB")


for shot, num, label in STRIP:
    strip_thumb(shot, num, label).save(A / f"slide-{num}.webp", "WEBP", quality=80, method=6)

# (stem, icon file, label)
TOKENS = [
    ("rust", "rust.svg", "Rust"),
    ("typescript", "typescript.svg", "TypeScript"),
    ("python", "python.svg", "Python"),
    ("comfyui", "comfyui.svg", "ComfyUI"),
    ("threejs", "threedotjs.svg", "Three.js"),
    ("blender", "blender.svg", "Blender"),
]


def token(icon, label):
    src = (SHOTS / "icons" / icon).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([^"]+)"', src).group(1).split()
    vw, vh = float(vb[2]), float(vb[3])
    paths = "".join(re.findall(r"<path[^>]*/>|<path[^>]*>.*?</path>", src, re.S))
    paths = re.sub(r'\sfill="[^"]*"', "", paths)  # recolour to ink
    size = 18
    sc = size / max(vw, vh)
    # width estimate for the mono label: Consolas advance is ~0.55em
    w = 14 + size + 9 + round(len(label) * 13 * 0.55 + len(label) * 1.2) + 14
    h = 34
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="17" fill="#000" stroke="#F2F0EC" stroke-opacity=".25"/>
<g transform="translate(14 {(h - vh * sc) / 2:.2f}) scale({sc:.4f})" fill="#F2F0EC">{paths}</g>
<text x="{14 + size + 9}" y="21.5" font-family="ui-monospace,'SF Mono',Menlo,Consolas,monospace" font-size="13" letter-spacing="1.2" fill="#F2F0EC">{label.upper()}</text>
</svg>"""


for stem, icon, label in TOKENS:
    (A / f"tok-{stem}.svg").write_text(token(icon, label), encoding="utf-8")

# Footer link buttons: bigger than the tokens, solid ink fill so they read
# as the page's call to action. jww.svg is the portfolio's own favicon.
LINKS = [("site", "jww.svg", "jeremywalderwillows.co.uk"), ("instagram", "instagram.svg", "Instagram")]


def link_btn(icon, label):
    src = (SHOTS / "icons" / icon).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([^"]+)"', src).group(1).split()
    vw, vh = float(vb[2]), float(vb[3])
    paths = "".join(re.findall(r"<path[^>]*/>|<path[^>]*>.*?</path>", src, re.S))
    paths = re.sub(r'\sfill="[^"]*"', "", paths)
    h, size, fs = 48, 22, 15
    sc = size / max(vw, vh)
    text_w = round(len(label) * fs * 0.55 + len(label) * 1.6)
    w = 20 + size + 12 + text_w + 14 + 12 + 20
    ax, ay = w - 20 - 12, h / 2 + 6
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<rect width="{w}" height="{h}" rx="24" fill="#F2F0EC"/>
<g transform="translate(20 {(h - vh * sc) / 2:.2f}) scale({sc:.4f})" fill="#000">{paths}</g>
<text x="{20 + size + 12}" y="{h / 2 + 5}" font-family="ui-monospace,'SF Mono',Menlo,Consolas,monospace" font-size="{fs}" letter-spacing="1.6" fill="#000">{label.upper()}</text>
<path d="M{ax} {ay}l12 -12M{ax + 4} {ay - 12}h8v8" stroke="#000" stroke-width="2" fill="none"/>
</svg>"""


for stem, icon, label in LINKS:
    (A / f"link-{stem}.svg").write_text(link_btn(icon, label), encoding="utf-8")

for p in sorted(A.glob("t*")):
    print(f"{p.stat().st_size:>8}  {p.name}")
