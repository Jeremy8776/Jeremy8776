# Rebuilding the profile assets

Everything in `assets/` is built by the two scripts here. Nothing runs on a
timer. Rebuild by hand, commit and push.

Needs Python 3.11 with Pillow, and ffmpeg built with `libwebp_anim`. On
Jeremy's PC use the Hermes venv:
`C:\Users\jerem\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`

Font paths are Windows ones (Arial as a stand-in for the portfolio's Gill
Sans, Consolas for captions). Change `SANS` and `MONO` at the top of each
script if you have a Gill Sans `.ttf`.

## Banner: `assets/reel.webp`

```
python tools/make_reel_video.py <clips dir> .
```

`<clips dir>` holds `c1.mp4` to `c4.mp4`, in the same order as the
portfolio reel. Get the current list from
`https://jeremywalderwillows.co.uk/api/projects/reel` (each slide's `src`).
Titles and captions are in `SLIDES` near the top of the script. If the reel
order changes, update the filmstrip under the banner to match: its
thumbnails (`assets/slide-*.webp`, from `STRIP` in `make_tiles_tokens.py`)
and their links in `README.md` (each slide's `cta.href` in the same API
response).

GitHub strips `<video>` from READMEs, so the banner is an animated WebP.
Keep it under about 5 MB: lower `-q:v`, `FPS` or `W`/`H` if it grows.

## Thumbnails and tokens: `assets/tile-*.webp`, `assets/tok-*.svg`

```
python tools/make_tiles_tokens.py <shots dir> .
```

`<shots dir>` holds:

| File | Source |
|------|--------|
| `craft.png` | `storytold/craft-launcher`, `docs/screenshots/artcraft-launcher-grid.png` |
| `armoze.webp` | portfolio, ARMOZE project, first image |
| `dram.png` | `Jeremy8776/DRAM`, `docs/screenshots/Canvas-render.png` |
| `aimodeldb-p.webp` | portfolio, AI Model Database project, first image |
| `reel-1.webp` to `reel-4.webp` | portfolio reel, each slide's `poster` |
| `icons/*.svg` | Simple Icons (CC0) for rust, typescript, python, threedotjs, blender; ComfyUI mark from `Comfy-Org/ComfyUI_frontend`, `packages/design-system/src/icons/comfy-c.svg` |

Portfolio project images are listed at
`https://jeremywalderwillows.co.uk/api/projects`.

Tiles are set in `TILES` (file, title, caption, crop anchor) and tokens in
`TOKENS`. Token width is estimated from label length, so check a new
label still fits its pill.

## Streak card

Not built here. It is a live image from `streak-stats.demolab.com`, set
straight in `README.md`. If that service goes down the image breaks; remove
the line or swap the service.
