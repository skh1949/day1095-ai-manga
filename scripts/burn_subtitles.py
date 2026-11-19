# -*- coding: utf-8 -*-
"""字幕烧录：按角色配色把台词写进每镜底部字幕安全区，避免错字与字体依赖问题。"""
import json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, "创作圣经", "storyboard.json")
IMG = os.path.join(ROOT, "assets", "images")
OUT = os.path.join(ROOT, "assets", "images_burned")
os.makedirs(OUT, exist_ok=True)
with open(SB, "r", encoding="utf-8") as f:
    sb = json.load(f)

FONT = "/c/Windows/Fonts/msyh.ttc"
FONT_BD = "/c/Windows/Fonts/msyhbd.ttc"
role_color = {
    "林知夏": (242, 232, 220),  # 暖米白
    "沈默": (221, 227, 230),    # 雾白
    "林知遥": (217, 142, 91),   # 暖橙
    "旁白": (200, 210, 220),    # 冷灰
}

def wrap(text, font, draw, max_w):
    lines, cur = [], ""
    punct = "。，、；：！？…,.!?"
    for ch in text:
        t = cur + ch
        # 标点紧跟前文，不单独起行
        if ch in punct and cur:
            cur = t
            continue
        if draw.textlength(t, font=font) > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines

W = 576
for shot in sb["shots"]:
    i = shot["id"]
    src = os.path.join(IMG, f"shot_{i:02d}.jpg")
    img = Image.open(src).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    f_role = ImageFont.truetype(FONT_BD, 26)
    f_line = ImageFont.truetype(FONT, 34)

    # 半透明字幕底板
    d.rectangle([0, 774, W, 1024], fill=(8, 10, 14, 120))
    # 角色名标签
    label = shot["role"]
    lc = role_color.get(label, (240, 240, 240))
    d.rounded_rectangle([36, 792, 36 + 30 + len(label) * 28, 834], radius=8, fill=(16, 18, 24, 200))
    d.text((50, 798), label, font=f_role, fill=(*lc, 255))

    # 台词（自动换行，居中）
    lines = wrap(shot["line"], f_line, d, W - 80)
    y0 = 856
    lh = 46
    for k, ln in enumerate(lines):
        tw = d.textlength(ln, font=f_line)
        x = (W - tw) / 2
        # 描边提升可读性
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                d.text((x + dx, y0 + k * lh + dy), ln, font=f_line, fill=(0, 0, 0, 220))
        d.text((x, y0 + k * lh), ln, font=f_line, fill=(*lc, 255))

    img.convert("RGB").save(os.path.join(OUT, f"shot_{i:02d}.jpg"), quality=92)

print(f"BURNED {len(sb['shots'])} captioned boards -> {OUT}")
