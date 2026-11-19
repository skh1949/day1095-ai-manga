# -*- coding: utf-8 -*-
"""合成 9:16 竖屏样片：图片片段按音频实际时长对轨，无 BGM，导出 MP4。"""
import json, os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.join(ROOT, "创作圣经", "storyboard.json")
IMG = os.path.join(ROOT, "assets", "images_burned")
AUDIO = os.path.join(ROOT, "assets", "audio")
OUTMP4 = os.path.join(ROOT, "output", "第1095天_样片_60s.mp4")
os.makedirs(os.path.dirname(OUTMP4), exist_ok=True)
with open(SB, "r", encoding="utf-8") as f:
    sb = json.load(f)

clips = []
durations = []
for shot in sb["shots"]:
    i = shot["id"]
    imgp = os.path.join(IMG, f"shot_{i:02d}.jpg")
    audp = os.path.join(AUDIO, f"shot_{i:02d}.mp3")
    audio = AudioFileClip(audp)
    # 尾部留 0.25s 呼吸，保证下一镜字幕不突兀
    dur = audio.duration + 0.25
    v = ImageClip(imgp).with_duration(dur).with_audio(audio)
    v = v.resized((576, 1024))
    clips.append(v)
    durations.append(dur)
    print(f"shot_{i:02d}  dur={dur:.2f}s", flush=True)

final = concatenate_videoclips(clips, method="chain")
print(f"\nTOTAL DURATION {final.duration:.2f}s", flush=True)
final.write_videofile(OUTMP4, fps=24, codec="libx264", audio_codec="aac",
                      ffmpeg_params=["-pix_fmt", "yuv420p"], logger="bar")
print(f"EXPORTED {OUTMP4}")
with open(os.path.join(ROOT, "output", "compose_meta.json"), "w", encoding="utf-8") as f:
    json.dump({"total_duration": final.duration, "shots": len(clips),
               "per_shot_duration": durations, "output": OUTMP4}, f, ensure_ascii=False, indent=2)
