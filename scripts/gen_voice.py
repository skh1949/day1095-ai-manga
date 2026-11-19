# -*- coding: utf-8 -*-
"""多角色配音：edge-tts 生成 MP3 + 逐句 SRT 时间戳（零成本，微软在线服务）。"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, "创作圣经", "storyboard.json")
AUDIO = os.path.join(ROOT, "assets", "audio")
SUBS = os.path.join(ROOT, "assets", "subs")
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(SUBS, exist_ok=True)
with open(SB, "r", encoding="utf-8") as f:
    sb = json.load(f)
vm = sb["voice_map"]

meta = []
for shot in sb["shots"]:
    voice = vm[shot["role"]]
    mp3 = os.path.join(AUDIO, f"shot_{shot['id']:02d}.mp3")
    srt = os.path.join(SUBS, f"shot_{shot['id']:02d}.srt")
    cmd = [sys.executable, "-m", "edge_tts", "--voice", voice,
           "--text", shot["line"], "--write-media", mp3, "--write-subtitles", srt]
    ok = False
    for attempt in range(1, 4):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(mp3) and os.path.getsize(mp3) > 1000:
            ok = True
            break
        time.sleep(2 * attempt)
    if not ok:
        print(f"ERR shot_{shot['id']:02d}: {r.stderr[-300:]}", flush=True)
        sys.exit(1)
    print(f"OK  shot_{shot['id']:02d}  [{shot['role']}/{voice}]  {os.path.getsize(mp3)} bytes", flush=True)
    meta.append({"id": shot["id"], "role": shot["role"], "voice": voice,
                 "line": shot["line"], "mp3": os.path.basename(mp3), "srt": os.path.basename(srt)})

with open(os.path.join(AUDIO, "voice_meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print(f"\nDONE {len(meta)} voices generated.")
