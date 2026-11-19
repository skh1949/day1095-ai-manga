# -*- coding: utf-8 -*-
"""组合C降级：用 8 色色卡程序化生成 17 张 9:16 分镜板（零成本、零依赖、无素材侵权）。"""
import json, os, math
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, "创作圣经", "storyboard.json")
OUT = os.path.join(ROOT, "assets", "images")
os.makedirs(OUT, exist_ok=True)
with open(SB, "r", encoding="utf-8") as f:
    sb = json.load(f)

PAL = {
    "夜蓝": (0x1B, 0x2A, 0x41), "暖米白": (0xF2, 0xE8, 0xDC),
    "褪色青": (0x7C, 0x9A, 0x92), "铁灰": (0x4A, 0x4E, 0x54),
    "暖橙": (0xD9, 0x8E, 0x5B), "暗红": (0x8C, 0x3B, 0x3B),
    "雾白": (0xDD, 0xE3, 0xE6), "墨黑": (0x12, 0x15, 0x1A),
}
# 每镜：主色、辅色、氛围光色、类型(人/空)、人物角色
MOOD = {
    1:  ("暖橙", "雾白", "暖橙", "人", "林知夏"),
    2:  ("铁灰", "夜蓝", "雾白", "空", None),
    3:  ("雾白", "褪色青", "雾白", "人", "林知夏"),
    4:  ("夜蓝", "墨黑", "暖橙", "人", "沈默"),
    5:  ("暖米白", "铁灰", "暖橙", "人", "林知遥"),
    6:  ("暖橙", "墨黑", "暖橙", "人", "林知夏"),
    7:  ("铁灰", "暗红", "暗红", "空", None),
    8:  ("墨黑", "铁灰", "雾白", "人", "林知夏"),
    9:  ("暖米白", "褪色青", "暖橙", "人", "林知遥"),
    10: ("暖米白", "暗红", "暗红", "人", "林知夏"),
    11: ("夜蓝", "暗红", "暗红", "人", "沈默"),
    12: ("暗红", "雾白", "暗红", "空", None),
    13: ("褪色青", "夜蓝", "褪色青", "人", "林知遥"),
    14: ("夜蓝", "墨黑", "褪色青", "空", None),
    15: ("墨黑", "铁灰", "暖橙", "人", "林知夏"),
    16: ("夜蓝", "暖橙", "暖橙", "人", "沈默"),
    17: ("雾白", "暖橙", "暖橙", "人", "林知夏"),
}
W, H = 576, 1024

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def gradient(c1, c2):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(c1, c2, y / H))
    return img

def glow(base, color, cx, cy, r=220, strength=110):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, strength))
    layer = layer.filter(ImageFilter.GaussianBlur(90))
    return Image.alpha_composite(base.convert("RGBA"), layer)

def silhouette(d, cx, cy, role):
    """简洁人物剪影：头+肩+(长发/短发)。"""
    dark = (18, 21, 26, 170)
    fh = 96  # 头高
    d.ellipse([cx - 46, cy - fh, cx + 46, cy + 8], fill=dark)       # 头
    d.polygon([(cx - 120, cy + 250), (cx - 92, cy + 40),
               (cx + 92, cy + 40), (cx + 120, cy + 250)], fill=dark)  # 肩身
    if role == "林知夏":
        d.polygon([(cx - 58, cy - 80), (cx - 78, cy + 120),
                   (cx - 40, cy + 100), (cx - 38, cy - 70)], fill=dark)
        d.polygon([(cx + 58, cy - 80), (cx + 78, cy + 120),
                   (cx + 40, cy + 100), (cx + 38, cy - 70)], fill=dark)
    elif role == "沈默":
        d.ellipse([cx - 50, cy - fh - 14, cx + 50, cy - 30], fill=(18, 21, 26, 210))

def empty_fx(d, kind, color):
    """空镜元素：信纸/雨痕/光斑。"""
    if kind == "letter":
        for i, off in enumerate(range(0, 3)):
            d.polygon([(200 + off * 24, 380 + off * 18), (390 + off * 24, 360 + off * 18),
                       (398 + off * 24, 560 + off * 18), (208 + off * 24, 580 + off * 18)],
                      outline=(*color, 150), width=3)
    elif kind == "rain":
        for i in range(40):
            x = (i * 67) % W
            y = (i * 131) % H
            d.line([(x, y), (x - 14, y + 46)], fill=(*color, 70), width=2)
    else:
        for i in range(9):
            x = 60 + (i * 97) % (W - 120)
            y = 120 + (i * 173) % 500
            r = 6 + (i % 4) * 5
            d.ellipse([x - r, y - r, x + r, y + r], fill=(*color, 90))

empty_kind = {2: "rain", 7: "letter", 12: "letter", 14: "rain"}

saved = []
for shot in sb["shots"]:
    i = shot["id"]
    main, sec, light, typ, role = MOOD[i]
    img = gradient(PAL[main], PAL[sec])
    img = glow(img, PAL[light], W // 2, 380, r=240, strength=120)
    d = ImageDraw.Draw(img, "RGBA")
    if typ == "人":
        silhouette(d, W // 2 + 40, 430, role)
    else:
        empty_fx(d, empty_kind.get(i, "bokeh"), PAL[light])
    # 顶部 8 色色卡签名条
    order = ["夜蓝", "暖米白", "褪色青", "铁灰", "暖橙", "暗红", "雾白", "墨黑"]
    for k, name in enumerate(order):
        d.rectangle([k * (W // 8), 0, (k + 1) * (W // 8), 10], fill=(*PAL[name], 255))
    # 底部字幕安全区暗条（字幕后期叠加，画面不生成文字）
    d.rectangle([0, H - 250, W, H], fill=(10, 12, 16, 70))
    # 镜号角标（几何点，非文字）
    for k in range(3):
        d.ellipse([W - 60 + k * 16, 34, W - 50 + k * 16, 44], fill=(*PAL[light], 180))
    dest = os.path.join(OUT, f"shot_{i:02d}.jpg")
    img.convert("RGB").save(dest, quality=90)
    saved.append(dest)

print(f"GENERATED {len(saved)} storyboard boards -> {OUT}")
