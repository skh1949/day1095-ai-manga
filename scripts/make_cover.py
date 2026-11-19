# -*- coding: utf-8 -*-
"""生成发布封面：取第17镜视觉 + 标题副标，零成本本地绘制。"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "images", "shot_17.jpg")
OUT = os.path.join(ROOT, "output", "封面_第1095天.png")
FONT_BD = "/c/Windows/Fonts/msyhbd.ttc"
FONT = "/c/Windows/Fonts/msyh.ttc"

img = Image.open(SRC).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")
W, H = img.size

# 顶部渐暗，提升标题可读性
d.rectangle([0, 0, W, 320], fill=(8, 10, 14, 120))
f_title = ImageFont.truetype(FONT_BD, 96)
f_sub = ImageFont.truetype(FONT, 34)

title = "第1095天"
tw = d.textlength(title, font=f_title)
x = (W - tw) / 2
for dx in (-3, 0, 3):
    for dy in (-3, 0, 3):
        d.text((x + dx, 90 + dy), title, font=f_title, fill=(0, 0, 0, 200))
d.text((x, 90), title, font=f_title, fill=(242, 232, 220, 255))

sub = "她等的人，从未离开"
sw = d.textlength(sub, font=f_sub)
d.text(((W - sw) / 2, 220), sub, font=f_sub, fill=(217, 142, 91, 255))

img.save(OUT)
print(f"COVER saved -> {OUT}  {W}x{H}")
