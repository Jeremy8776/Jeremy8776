"""Builds assets/reel.webp: the profile banner as an animated WebP cut from
the real showreel clips, so the video actually plays on GitHub.

Why WebP: GitHub READMEs strip <video>; only animated images autoplay and
loop. Animated WebP is far smaller than GIF at the same quality.

Usage: make_reel_video.py <clips dir> <output dir>
Clips: c1.mp4..c4.mp4 in reel order. Overlays (shade, captions, counter,
header) are drawn with PIL and composited by ffmpeg.
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIPS, OUT = Path(sys.argv[1]), Path(sys.argv[2])
TMP = OUT / "_overlays"
W, H, FPS = 960, 420, 15
SEG, FADE, START = 4.6, 0.6, 1.0  # seconds per clip, crossfade, offset into clip
INK = (242, 240, 236, 255)
# shortcut: Arial stands in for the site's Gill Sans stack (not installed on
# this PC, and it is what the site falls back to here). Swap in a Gill Sans
# .ttf path if one becomes available.
SANS = "C:/Windows/Fonts/arial.ttf"
MONO = "C:/Windows/Fonts/consola.ttf"

SLIDES = [
    ("About", ""),
    ("Pandora Celebration Collection", "MAISON META \u00b7 SNR AI STRATEGIST & ART DIRECTOR \u00b7 2023"),
    ("Lu: Synthetic Character Study", "INDEPENDENT \u00b7 CREATIVE DIRECTOR \u00b7 2026"),
    ("White Label Sports Imagery", "OPTIKKA \u00b7 DIRECTOR OF AI STRATEGY & INNOVATION \u00b7 2025"),
]
N = len(SLIDES)


def spaced(draw, xy, text, font, spacing, anchor_right=False, fill=INK):
    """Draw text with letter spacing (PIL has none built in)."""
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    if anchor_right:
        x -= total
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += w + spacing


def shade():
    im = Image.new("RGBA", (W, H))
    px = im.load()
    for y in range(H):
        f = y / H
        a = 0.45 * max(0, 1 - f / 0.35) + 0.8 * max(0, (f - 0.6) / 0.4)
        for x in range(W):
            px[x, y] = (0, 0, 0, int(255 * min(a, 1)))
    return im


def slide_overlay(i, title, cap, base):
    im = base.copy()
    d = ImageDraw.Draw(im)
    d.text((30, H - 100), title, font=ImageFont.truetype(SANS, 44), fill=INK)
    mono = ImageFont.truetype(MONO, 12)
    spaced(d, (31, H - 44), cap, mono, 1.6, fill=(242, 240, 236, 190))
    spaced(d, (W - 30, H - 44), f"0{i + 1} / 0{N}", mono, 1.6, anchor_right=True)
    return im


def header():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    spaced(d, (30, 30), "JEREMY8776", ImageFont.truetype(SANS, 15), 4.5)
    mono = ImageFont.truetype(MONO, 10)
    spaced(d, (31, 54), "AI \u00b7 CREATIVE DIRECTION \u00b7 OPEN SOURCE", mono, 1.4, fill=(242, 240, 236, 190))
    spaced(d, (W - 30, 32), "WORK \u00b7 SITE \u00b7 SPONSOR", ImageFont.truetype(MONO, 11), 1.4, anchor_right=True)
    d.rectangle((0, H - 2, W, H), fill=(242, 240, 236, 40))
    return im


TMP.mkdir(parents=True, exist_ok=True)
base = shade()
for i, (t, c) in enumerate(SLIDES):
    slide_overlay(i, t, c, base).save(TMP / f"o{i}.png")
header().save(TMP / "header.png")
Image.new("RGBA", (W, 2), INK).save(TMP / "bar.png")

inputs, f = [], []
for i in range(N):
    inputs += ["-ss", str(START), "-t", str(SEG), "-i", str(CLIPS / f"c{i + 1}.mp4")]
for i in range(N):
    inputs += ["-loop", "1", "-i", str(TMP / f"o{i}.png")]
inputs += ["-loop", "1", "-i", str(TMP / "header.png"), "-loop", "1", "-i", str(TMP / "bar.png")]

for i in range(N):
    f.append(f"[{i}:v]fps={FPS},scale={W}:-2,crop={W}:{H},setsar=1,format=rgba[v{i}]")
    f.append(f"[v{i}][{N + i}:v]overlay=shortest=1,format=yuv420p[s{i}]")
prev, step = "s0", SEG - FADE
for i in range(1, N):
    f.append(f"[{prev}][s{i}]xfade=transition=fade:duration={FADE}:offset={step * i:.2f}[x{i}]")
    prev = f"x{i}"
total = SEG * N - FADE * (N - 1)
f.append(f"[{prev}][{2 * N}:v]overlay=shortest=1[h]")
f.append(f"[h][{2 * N + 1}:v]overlay=x='-{W}+{W}*mod(t+{FADE},{step})/{step}':y={H - 2}:shortest=1[out]")

webp = OUT / "assets" / "reel.webp"
webp.parent.mkdir(parents=True, exist_ok=True)
cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(f), "-map", "[out]",
       "-t", f"{total:.2f}", "-c:v", "libwebp_anim", "-lossless", "0", "-q:v", "72",
       "-compression_level", "6", "-loop", "0", "-an", str(webp)]
subprocess.run(cmd, check=True)
print(f"{webp.stat().st_size / 1e6:.2f} MB  {webp}  ({total:.1f}s at {FPS}fps, {W}x{H})")
