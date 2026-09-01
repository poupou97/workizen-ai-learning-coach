#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WAL-47 — 13 chip trạng thái sư phạm của SAM, box TAY-CHỌN từ lưới toạ độ.
Chip tròn nền lavender viền tím (dùng trên mọi nền); 2 state thiếu = sprite
gần nghĩa + BADGE lập trình (giải pháp TẠM có ghi nhận — art cuối cho design pass)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SHEET = Image.open('concept/mascote-transparent.png').convert('RGB')
OUT = Path('assets/mascot'); OUT.mkdir(parents=True, exist_ok=True)

# state → (x0,y0,x1,y1, badge)
STATES = {
 'hello':               (355, 15, 505, 198, None),   # vẫy cánh
 'listen':              (1015, 10, 1235, 198, None), # tai nghe (tạm — audit đã ghi)
 'think':               (660, 192, 872, 378, None),  # cánh chống cằm + "?"
 'probe':               (715, 508, 885, 692, None),  # chỉ tay + bong bóng ý
 'hint':                (1015, 198, 1255, 378, None),# bóng đèn 💡 + laptop
 'your-turn':           (478, 508, 662, 692, None),  # nháy mắt mời lượt
 'step-back':           (1262, 192, 1412, 378, None),# đeo balo bước đi — SAM lùi lại
 'try-again':           (1122, 378, 1275, 505, None),# mặt hiền ấm (không dùng mặt khóc)
 'explain':             (718, 502, 1045, 692, None), # bảng xanh + que chỉ
 'admit-uncertainty':   (855, 688, 1018, 808, None), # đầu + bong bóng "?"
 'celebrate-independence': (1222, 12, 1428, 198, None), # cúp + confetti
 'camera-scan':         (852, 192, 1038, 378, 'camera'), # kính lúp + badge camera
 'review-due':          (338, 192, 508, 378, 'clock'),   # đọc sách + badge đồng hồ
}

def chip(box, size=256, ring=(124,77,255), bg=(243,238,255), fit=False):
    x0,y0,x1,y1 = box
    if fit:
        # sprite BỀ NGANG kẹp giữa hai hàng: crop ĐÚNG box, letterbox trên nền
        # BLUR của chính nó — không lẹm hàng xóm, không ô trắng.
        exact = SHEET.crop(box).copy()
        backdrop = exact.resize((size, size), Image.Resampling.LANCZOS)\
                        .filter(ImageFilter.GaussianBlur(24))
        fg = exact.copy()
        fg.thumbnail((int(size*0.94), int(size*0.94)), Image.Resampling.LANCZOS)
        backdrop.paste(fg, ((size-fg.width)//2, (size-fg.height)//2))
        crop = backdrop
    else:
        cx, cy = (x0+x1)//2, (y0+y1)//2
        half = int(max(x1-x0, y1-y0) * 0.54)
        crop = SHEET.crop((max(cx-half,0), max(cy-half,0),
                           min(cx+half, SHEET.width), min(cy+half, SHEET.height)))
        crop = crop.resize((size,size), Image.Resampling.LANCZOS)
    mask = Image.new('L',(size,size),0)
    ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1),fill=255)
    out = Image.new('RGBA',(size,size),(0,0,0,0))
    base = Image.new('RGB',(size,size),bg); base.paste(crop,(0,0))
    out.paste(base,(0,0),mask)
    ImageDraw.Draw(out).ellipse((1,1,size-2,size-2),outline=ring+(255,),width=6)
    return out

def badge(img, kind):
    s = img.size[0]; b = s//3
    bd = Image.new('RGBA',(b,b),(0,0,0,0)); d = ImageDraw.Draw(bd)
    d.ellipse((0,0,b-1,b-1), fill=(124,77,255,255))
    d.ellipse((0,0,b-1,b-1), outline=(255,255,255,255), width=3)
    w = max(4,b//14)
    if kind=='camera':
        d.rounded_rectangle((b*0.20,b*0.34,b*0.80,b*0.74), radius=b//9, outline=(255,255,255,255), width=w)
        d.ellipse((b*0.38,b*0.42,b*0.62,b*0.66), outline=(255,255,255,255), width=w)
        d.rounded_rectangle((b*0.38,b*0.24,b*0.62,b*0.36), radius=b//20, fill=(255,255,255,255))
    else:  # clock
        d.ellipse((b*0.18,b*0.18,b*0.82,b*0.82), outline=(255,255,255,255), width=w)
        d.line((b*0.5,b*0.5,b*0.5,b*0.30), fill=(255,255,255,255), width=w)
        d.line((b*0.5,b*0.5,b*0.66,b*0.58), fill=(255,255,255,255), width=w)
    out = img.copy(); out.paste(bd,(s-b-2,s-b-2),bd); return out

for name,(x0,y0,x1,y1,bk) in STATES.items():
    c = chip((x0,y0,x1,y1), fit=(name=='explain'))
    if bk: c = badge(c, bk)
    c.save(OUT/f'sam-{name}.png')
    # bản 64px cho UI nhỏ
    c.resize((64,64), Image.Resampling.LANCZOS).save(OUT/f'sam-{name}@64.png')

# proof: nền tối + nền sáng
names = list(STATES)
for bgc, fn in [((45,45,58),'_proof-dark.png'), ((247,247,252),'_proof-light.png')]:
    board = Image.new('RGB',(20+7*150, 40+2*160), bgc)
    for i,n in enumerate(names):
        c = Image.open(OUT/f'sam-{n}.png').resize((128,128))
        board.paste(c,(20+(i%7)*150, 20+(i//7)*160), c)
    board.save(OUT/fn)
print(f'OK — {len(STATES)} state chips + proofs')
