#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Weijie Zhang
"""Render the 20 s vertical FindNet ad (1080x1920, 30 fps) as PNG frames.
Usage: python3 render_zh.py [first_frame last_frame]"""
import os
from PIL import Image, ImageDraw, ImageFont

S      = 2
W, H   = 1080*S, 1920*S
FPS    = 30
FRAMES = 600
HERE   = os.path.dirname(os.path.abspath(__file__))
FD     = os.environ.get("FONT_DIR", os.path.join(HERE, "fonts"))          # Outfit-Bold.ttf
NOTO   = os.environ.get("NOTO_DIR", "/usr/share/fonts/opentype/noto")     # NotoSansCJK-*.ttc
OUTDIR = os.path.join(HERE, "build", "frames")

INK   = (19, 28, 26)
CREAM = (250, 244, 233)
TEAL  = (13, 107, 93)
CORAL = (240, 101, 59)
SKY   = (210, 228, 224)
SAGE  = (176, 209, 195)
GREY  = (120, 132, 129)
WHITE = (255, 255, 255)

FONTS = {
    "cjk":  (f"{NOTO}/NotoSansCJK-Bold.ttc", 2),
    "cjkm": (f"{NOTO}/NotoSansCJK-Medium.ttc", 2),
    "cjkr": (f"{NOTO}/NotoSansCJK-Regular.ttc", 2),
    "lat":  (f"{FD}/Outfit-Bold.ttf", 0),
}
LH = 1.30   # CJK line height

def u(v): return int(round(v*S))
def c01(x): return max(0.0, min(1.0, x))
def eoc(x): x=c01(x); return 1-(1-x)**3
def eob(x):
    x=c01(x); c1=1.70158; c3=c1+1
    return 1 + c3*(x-1)**3 + c1*(x-1)**2
def fade(t, start, dur=0.45): return eoc(c01((t-start)/dur))

_fc = {}
def font(key, size):
    k=(key,size)
    if k not in _fc:
        p,i = FONTS[key]
        _fc[k]=ImageFont.truetype(p, u(size), index=i)
    return _fc[k]

def tw(f, s):
    b=f.getbbox(s); return (b[2]-b[0])/S

def fit_block(key, lines, max_w, size, min_size=20):
    while size > min_size:
        f = font(key, size)
        if all(tw(f,l) <= max_w for l in lines): return f, size
        size -= 2
    return font(key, min_size), min_size

def text(d, x, y, s, f, col, a=1.0, anchor="mm"):
    if a <= 0.004: return
    d.text((u(x), u(y)), s, font=f, fill=col+(int(255*c01(a)),), anchor=anchor)

def rrect(d, x0,y0,x1,y1, r, col, a=1.0):
    if a <= 0.004: return
    d.rounded_rectangle([u(x0),u(y0),u(x1),u(y1)], radius=u(r), fill=col+(int(255*c01(a)),))

def circ(d, cx,cy,r, col, a=1.0):
    if a <= 0.004 or r <= 0: return
    d.ellipse([u(cx-r),u(cy-r),u(cx+r),u(cy+r)], fill=col+(int(255*c01(a)),))

def block(d, lines, cx, y_top, f, size, col, a, rise=30.0, lh_mul=LH):
    lh = size*lh_mul
    off = (1-a)*rise
    for i,l in enumerate(lines):
        text(d, cx, y_top + i*lh + off, l, f, col, a)
    return lh

def pin(d, cx, cy, r, col, sc=1.0, a=1.0):
    if a <= 0.004 or sc <= 0.02: return
    r = r*sc; cyc = cy - r*1.25; A = int(255*c01(a))
    d.ellipse([u(cx-r),u(cyc-r),u(cx+r),u(cyc+r)], fill=col+(A,))
    d.polygon([(u(cx-r*0.70),u(cyc+r*0.60)),(u(cx+r*0.70),u(cyc+r*0.60)),(u(cx),u(cy))], fill=col+(A,))
    d.ellipse([u(cx-r*0.34),u(cyc-r*0.34),u(cx+r*0.34),u(cyc+r*0.34)], fill=(255,255,255,A))

def wordmark(d, cx, cy, size, a=1.0):
    f = font("lat", size); label = "FindNet"
    lw = tw(f, label); m = size*1.02; gap = size*0.26
    x0 = cx - (m + gap + lw)/2
    rrect(d, x0, cy-m/2, x0+m, cy+m/2, m*0.29, TEAL, a)
    pin(d, x0+m/2, cy+m*0.30, m*0.21, CREAM, 1.0, a)
    text(d, x0+m+gap, cy+size*0.015, label, f, INK, a, anchor="lm")

# ---------------------------------------------------------------- scenes

def s1(d, t):
    l1 = ["一个人没劲"]
    l2 = ["一起才带劲"]
    f, sz = fit_block("cjk", l1+l2, 920, 134)
    a1 = fade(t, 0.15)
    block(d, l1, 540, 800, f, sz, INK, a1)
    a2 = fade(t, 1.30)
    top2 = 800 + sz*LH + 70
    block(d, l2, 540, top2, f, sz, INK, a2)
    p = eoc(c01((t-1.95)/0.55))
    if p > 0:
        wline = tw(f, l2[0]); x0 = 540 - wline/2
        y = top2 + sz*0.60
        rrect(d, x0, y, x0+wline*p, y+15, 8, CORAL, 1.0)

def s2(d, t):
    lines = ["出门走走", "有人等你"]
    f, sz = fit_block("cjk", lines, 880, 196)
    a = fade(t, 0.30)
    lh = block(d, lines, 540, 830, f, sz, CREAM, a)
    p = eoc(c01((t-1.15)/0.55))
    if p > 0:
        rrect(d, 540-85*p, 830+lh+150, 540+85*p, 830+lh+162, 6, CORAL, 1.0)

def s3(d, t):
    wordmark(d, 540, 318, 60, fade(t, 0.28))
    fs, _ = fit_block("cjkm", ["附近谁在动，打开就知道"], 900, 56)
    text(d, 540, 452, "附近谁在动，打开就知道", fs, GREY, fade(t, 0.45))

    ap = fade(t, 0.50, 0.55)
    if ap > 0.004:
        slide = (1-ap)*40
        px0, py0, px1, py1 = 240, 540+slide, 840, 1660+slide
        rrect(d, px0, py0, px1, py1, 62, INK, ap)
        sx0, sy0, sx1, sy1 = px0+14, py0+14, px1-14, py1-14
        rrect(d, sx0, sy0, sx1, sy1, 50, SKY, ap)
        rrect(d, sx0+36,  sy0+90,  sx0+250, sy0+300, 40, SAGE, ap)
        rrect(d, sx0+300, sy0+420, sx1-40,  sy0+660, 40, SAGE, ap)
        rrect(d, sx0+40,  sy0+700, sx0+230, sy0+880, 36, SAGE, ap)
        for y in (sy0+340, sy0+700):
            rrect(d, sx0, y, sx1, y+16, 8, CREAM, ap)
        for x in (sx0+270, sx0+470):
            rrect(d, x, sy0, x+16, sy1-230, 8, CREAM, ap)
        pins = [(360, 820, CORAL, 1.00), (640, 746, TEAL, 1.30),
                (742, 1026, CORAL, 1.60), (430, 1120, TEAL, 1.90)]
        for (x, y, col, st) in pins:
            pin(d, x, y+slide, 30, col, eob(c01((t-st)/0.45)), ap)
        yd = eoc(c01((t-2.15)/0.4))
        if yd > 0:
            circ(d, 540, 1270+slide, 36*yd, CREAM, ap)
            circ(d, 540, 1270+slide, 22*yd, TEAL, ap)
        rp = c01((t-2.45)/0.6)
        if rp > 0:
            ax, ay, bx, by = 540, 1270+slide, 640, 766+slide
            n = 14
            for i in range(n):
                if i/n > rp: break
                if i % 2: continue
                m = (i+0.5)/n
                circ(d, ax+(bx-ax)*m, ay+(by-ay)*m, 7, CORAL, ap)
        ac = fade(t, 2.55, 0.5)
        if ac > 0.004:
            cy0 = 1408 + (1-ac)*26 + slide
            rrect(d, 288, cy0, 792, cy0+200, 30, WHITE, ap*ac)
            f1, _ = fit_block("cjk",  ["晨间散步 · 8:00"], 318, 32)
            f2, _ = fit_block("cjkr", ["滨江公园 · 4人参加"], 318, 27)
            text(d, 318, cy0+74,  "晨间散步 · 8:00", f1, INK,  ap*ac, anchor="lm")
            text(d, 318, cy0+132, "滨江公园 · 4人参加", f2, GREY, ap*ac, anchor="lm")
            rrect(d, 648, cy0+56, 764, cy0+144, 44, CORAL, ap*ac)
            fj, _ = fit_block("cjk", ["加入"], 96, 32)
            text(d, 706, cy0+100, "加入", fj, CREAM, ap*ac)

def s4(d, t):
    rows = [("1", "找到朋友",     TEAL,  0.30),
            ("2", "看他们在哪动",  CORAL, 1.15),
            ("3", "约上就出发",    TEAL,  2.00)]
    f, sz = fit_block("cjk", [r[1] for r in rows], 690, 92)
    fn = font("lat", 48)
    y0, gap = 700, 260
    for i, (num, label, col, st) in enumerate(rows):
        a = fade(t, st)
        if a <= 0.004: continue
        y = y0 + i*gap + (1-a)*26
        circ(d, 226, y, 62, col, a)
        text(d, 226, y+3, num, fn, CREAM, a)
        text(d, 326, y, label, f, INK, a, anchor="lm")

def s5(d, t):
    lines = ["他们都在动", "就差你一个"]
    f, sz = fit_block("cjk", lines, 880, 196)
    block(d, lines, 540, 830, f, sz, CREAM, fade(t, 0.30))

def s6(d, t):
    wordmark(d, 540, 700, 92, fade(t, 0.25))
    ft, _ = fit_block("cjk", ["有伴才有劲"], 820, 78)
    text(d, 540, 895, "有伴才有劲", ft, TEAL, fade(t, 0.55))
    ac = fade(t, 0.90)
    if ac > 0.004:
        yo = (1-ac)*22
        rrect(d, 300, 1085+yo, 780, 1245+yo, 80, CORAL, ac)
        fb, _ = fit_block("cjk", ["免费下载"], 400, 62)
        text(d, 540, 1165+yo, "免费下载", fb, CREAM, ac)

SCENES = [
    (  0,  95, s1, CREAM,  0),
    ( 95, 180, s2, TEAL,   1),
    (180, 315, s3, CREAM, -1),
    (315, 435, s4, CREAM,  0),
    (435, 525, s5, TEAL,   1),
    (525, 600, s6, CREAM, -1),
]

os.makedirs(OUTDIR, exist_ok=True)
WIPE = 0.34
import sys
F0 = int(sys.argv[1]) if len(sys.argv) > 1 else 0
F1 = int(sys.argv[2]) if len(sys.argv) > 2 else FRAMES
for i in range(F0, F1):
    for k, (f0, f1, fn, bg, wd) in enumerate(SCENES):
        if f0 <= i < f1: break
    t = (i - f0) / FPS
    prev_bg = SCENES[k-1][3] if k > 0 else bg
    img = Image.new("RGBA", (W, H), prev_bg + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    p = eoc(c01(t / WIPE)) if wd != 0 else 1.0
    if p >= 1.0:       d.rectangle([0,0,W,H], fill=bg+(255,))
    elif wd == 1:      d.rectangle([0,int(H*(1-p)),W,H], fill=bg+(255,))
    else:              d.rectangle([0,0,W,int(H*p)], fill=bg+(255,))
    fn(d, t)
    img.convert("RGB").resize((1080,1920), Image.LANCZOS).save(f"{OUTDIR}/f{i:04d}.png")
print("rendered", FRAMES, "zh frames")
