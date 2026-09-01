#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WAL-47 — dò sprite trên mascot sheet, xuất CHIP TRÒN production-usable.
Chip tròn thay alpha-cut: nền sheet gradient mờ, chroma-key local sẽ lem —
chip viền mềm dùng được trên MỌI nền (pattern avatar). Alpha thật = residual
cho design pass. Tất định."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

SHEET = Path('concept/mascote-transparent.png')
OUT = Path('assets/mascot')

def find_sprites(im, cell=8, thresh_sat=60, thresh_dark=90):
    small = im.convert('RGB').resize((im.width // cell, im.height // cell))
    w, h = small.size
    px = small.load()
    def is_fg(x, y):
        r, g, b = px[x, y]
        mx, mn = max(r, g, b), min(r, g, b)
        return (mx - mn) > thresh_sat or mx < thresh_dark
    seen = [[False]*h for _ in range(w)]
    boxes = []
    for x in range(w):
        for y in range(h):
            if seen[x][y] or not is_fg(x, y):
                continue
            stack = [(x, y)]; minx=maxx=x; miny=maxy=y; n=0
            while stack:
                cx, cy = stack.pop()
                if cx<0 or cy<0 or cx>=w or cy>=h or seen[cx][cy] or not is_fg(cx,cy):
                    continue
                seen[cx][cy]=True; n+=1
                minx=min(minx,cx); maxx=max(maxx,cx); miny=min(miny,cy); maxy=max(maxy,cy)
                stack += [(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1),
                          (cx+1,cy+1),(cx-1,cy-1),(cx+1,cy-1),(cx-1,cy+1)]
            bw, bh = maxx-minx+1, maxy-miny+1
            if n > 40 and bw > 5 and bh > 5:
                boxes.append((minx*cell, miny*cell, (maxx+1)*cell, (maxy+1)*cell, n*cell*cell))
    boxes.sort(key=lambda b: -b[4])
    return boxes

def make_chip(im, box, size=256, ring=(124, 77, 255), bg=(243, 238, 255)):
    x0, y0, x1, y1, _ = box
    cx, cy = (x0+x1)//2, (y0+y1)//2
    half = int(max(x1-x0, y1-y0) * 0.62)
    crop = im.convert('RGB').crop((max(cx-half,0), max(cy-half,0),
                                   min(cx+half, im.width), min(cy+half, im.height)))
    crop = crop.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
    chip = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    base = Image.new('RGB', (size, size), bg)
    base.paste(crop, (0, 0))
    chip.paste(base, (0, 0), mask)
    ImageDraw.Draw(chip).ellipse((1, 1, size-2, size-2), outline=ring + (255,), width=6)
    return chip

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SHEET)
    boxes = find_sprites(im)
    print(f'dò được {len(boxes)} cụm sprite')
    for i, box in enumerate(boxes[:24]):
        make_chip(im, box).save(OUT / f'cand-{i:02d}.png')
        print(f'cand-{i:02d}: box={box[:4]}')
    dark = Image.new('RGB', (1700, 300), (45, 45, 58))
    for i in range(12):
        p = OUT / f'cand-{i:02d}.png'
        if p.exists():
            c = Image.open(p).resize((128, 128))
            dark.paste(c, (20 + i*140, 40), c)
    dark.save(OUT / '_proof-dark.png')
    print('OK — assets/mascot/_proof-dark.png')
