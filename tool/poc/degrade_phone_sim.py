#!/usr/bin/env python3
"""WAL-32 proxy — tổng hợp ảnh-giả-điện-thoại từ trang render sạch.

Ba mức, mỗi mức là TỔ HỢP lỗi camera thật gặp:
  L1 nhẹ : nghiêng nhẹ (perspective) + lệch sáng nhẹ + JPEG q75
  L2 vừa : nghiêng rõ + gradient bóng một góc + blur nhẹ + JPEG q55
  L3 nặng: nghiêng mạnh + thiếu sáng + bóng đậm + blur + nhiễu + JPEG q30
Tất định (seed cố định) để tái lập. Đây là PROXY — không thay ảnh thật.
"""
import sys, random
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

random.seed(20260901)

def perspective(im, mag):
    """Nghiêng kiểu cầm tay: co ngẫu nhiên 4 góc theo biên độ mag (tỷ lệ cạnh)."""
    w, h = im.size
    dx, dy = w * mag, h * mag
    # QUAD: 4 góc nguồn (NW, SW, SE, NE) lấy VÀO trong ảnh gốc
    quad = (
        random.uniform(0, dx), random.uniform(0, dy),                 # NW
        random.uniform(0, dx), h - random.uniform(0, dy),             # SW
        w - random.uniform(0, dx), h - random.uniform(0, dy),         # SE
        w - random.uniform(0, dx), random.uniform(0, dy),             # NE
    )
    return im.transform((w, h), Image.Transform.QUAD, quad,
                        resample=Image.Resampling.BICUBIC, fillcolor=(228, 222, 210))

def corner_shadow(im, strength):
    """Bóng tối dần về một góc (tay che sáng)."""
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(mask)
    steps = 60
    for i in range(steps):
        # elip lớn dần từ góc dưới-phải; càng gần góc càng tối
        alpha = int(strength * 255 * (1 - i / steps))
        bbox = [w - w * 1.6 * (i + 1) / steps, h - h * 1.6 * (i + 1) / steps, w * 1.02, h * 1.02]
        d.ellipse(bbox, fill=alpha)
    black = Image.new('RGB', (w, h), (10, 10, 15))
    return Image.composite(black, im, mask.filter(ImageFilter.GaussianBlur(40))) if strength else im

def add_noise(im, sigma):
    if not sigma:
        return im
    noise = Image.effect_noise(im.size, sigma).convert('L')
    return Image.blend(im, Image.merge('RGB', (noise, noise, noise)), 0.18)

LEVELS = {
    'L1': dict(persp=0.015, bright=0.92, shadow=0.0,  blur=0.0, noise=0,  q=75),
    'L2': dict(persp=0.045, bright=0.80, shadow=0.35, blur=1.0, noise=0,  q=55),
    'L3': dict(persp=0.09,  bright=0.62, shadow=0.55, blur=1.6, noise=48, q=30),
}

def degrade(src, outdir):
    im = Image.open(src).convert('RGB')
    outs = []
    for name, p in LEVELS.items():
        random.seed(hash((src.name, name)) % (2**31))  # tất định theo (trang, mức)
        x = perspective(im, p['persp'])
        x = ImageEnhance.Brightness(x).enhance(p['bright'])
        x = corner_shadow(x, p['shadow'])
        if p['blur']:
            x = x.filter(ImageFilter.GaussianBlur(p['blur']))
        x = add_noise(x, p['noise'])
        out = outdir / f"{src.stem}-{name}.jpg"
        x.save(out, 'JPEG', quality=p['q'])
        outs.append(out)
    return outs

if __name__ == '__main__':
    render, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    all_out = []
    for src in sorted(render.glob('*.png')):
        all_out += degrade(src, outdir)
    # Gói mỗi mức thành một PDF để đi qua ocr_pdf.swift không sửa tool
    for lv in LEVELS:
        pages = [Image.open(f).convert('RGB') for f in sorted(outdir.glob(f'*-{lv}.jpg'))]
        pdf = outdir / f'phone-sim-{lv}.pdf'
        pages[0].save(pdf, save_all=True, append_images=pages[1:])
        print(f'{pdf} ← {len(pages)} trang')
