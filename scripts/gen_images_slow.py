# -*- coding: utf-8 -*-
"""慢速补图：针对 Pollinations 间歇性 402 限流，只补缺失镜头，连续失败则提前停止。"""
import json, os, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, "创作圣经", "storyboard.json")
OUT = os.path.join(ROOT, "assets", "images")
os.makedirs(OUT, exist_ok=True)
with open(SB, "r", encoding="utf-8") as f:
    sb = json.load(f)

style, seed = sb["style_prefix"], sb["seed"]
w, h = 576, 1024
UA = {"User-Agent": "Mozilla/5.0 (zero-cost-manju-sample)"}

def valid(path):
    if not os.path.exists(path):
        return False
    with open(path, "rb") as fh:
        return fh.read(2) == b"\xff\xd8" and os.path.getsize(path) > 8000

def fetch(shot):
    full = style + "，" + shot["prompt"]
    enc = urllib.parse.quote(full, safe="")
    url = f"https://image.pollinations.ai/prompt/{enc}?width={w}&height={h}&seed={seed}&nologo=true"
    dest = os.path.join(OUT, f"shot_{shot['id']:02d}.jpg")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not jpeg")
    with open(dest, "wb") as fh:
        fh.write(data)
    return len(data)

missing = [s for s in sb["shots"] if not valid(os.path.join(OUT, f"shot_{s['id']:02d}.jpg"))]
print(f"missing={len(missing)}", flush=True)
streak = 0
for shot in missing:
    ok = False
    for attempt in range(1, 4):
        try:
            n = fetch(shot)
            print(f"OK  shot_{shot['id']:02d}.jpg  {n} bytes", flush=True)
            ok = True
            streak = 0
            break
        except Exception as e:
            print(f"  attempt{attempt} shot_{shot['id']:02d}: {e}", flush=True)
            if attempt < 3:
                time.sleep(6 * attempt)
    if not ok:
        streak += 1
        if streak >= 3:
            print("STOP: 连续3镜失败，端点不可用，切换降级路径。", flush=True)
            break
    time.sleep(6)

have = sum(1 for s in sb["shots"] if valid(os.path.join(OUT, f"shot_{s['id']:02d}.jpg")))
print(f"\nTOTAL VALID {have}/{len(sb['shots'])}")
