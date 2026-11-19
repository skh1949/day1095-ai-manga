# -*- coding: utf-8 -*-
"""批量出图：Pollinations 免 key 端点（零成本），固定 seed + 统一风格前缀。"""
import json, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, "创作圣经", "storyboard.json")
OUT = os.path.join(ROOT, "assets", "images")
os.makedirs(OUT, exist_ok=True)

with open(SB, "r", encoding="utf-8") as f:
    sb = json.load(f)

style = sb["style_prefix"]
seed = sb["seed"]
w, h = 576, 1024
UA = {"User-Agent": "Mozilla/5.0 (zero-cost-manju-sample)"}

def jpeg_ok(path):
    try:
        with open(path, "rb") as fh:
            return fh.read(2) == b"\xff\xd8"
    except Exception:
        return False

def download(shot, attempt=1):
    full_prompt = style + "，" + shot["prompt"]
    enc = urllib.parse.quote(full_prompt, safe="")
    url = f"https://image.pollinations.ai/prompt/{enc}?width={w}&height={h}&seed={seed}&nologo=true"
    dest = os.path.join(OUT, f"shot_{shot['id']:02d}.jpg")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
        if not data.startswith(b"\xff\xd8"):
            raise ValueError(f"not jpeg, content-type={ct}")
        with open(dest, "wb") as fh:
            fh.write(data)
        return True, f"shot_{shot['id']:02d}.jpg  {len(data)} bytes  ct={ct}"
    except Exception as e:
        if attempt < 3:
            time.sleep(2 * attempt)
            return download(shot, attempt + 1)
        return False, f"shot_{shot['id']:02d}.jpg  FAILED: {e}"

results = []
for shot in sb["shots"]:
    ok, msg = download(shot)
    results.append({"id": shot["id"], "ok": ok, "msg": msg})
    print(("OK  " if ok else "ERR ") + msg, flush=True)

with open(os.path.join(OUT, "download_log.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

ok_n = sum(1 for r in results if r["ok"])
print(f"\nDONE {ok_n}/{len(results)} images downloaded.")
sys.exit(0 if ok_n == len(results) else 1)
