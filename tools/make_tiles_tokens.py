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

for p in sorted(A.glob("t*")):
    print(f"{p.stat().st_size:>8}  {p.name}")
