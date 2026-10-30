import argparse
import json
import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw

def make_demo(out="out", width=540, height=960, fps=12, seconds=12):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe required")
    root=Path(out)
    frames=root/"frames"
    frames.mkdir(parents=True,exist_ok=True)
    for i in range(fps*seconds):
        t=i/fps
        im=Image.new("RGB",(width,height),(250,248,241))
        d=ImageDraw.Draw(im)
        cx=width//2+int(math.sin(t*2)*width*.12)
        cy=int(height*.52+math.sin(t*5)*12)
        s=width/540
        r=int(32*s)
        line=max(2,int(7*s))
        d.ellipse((cx-r,cy-145*s-r,cx+r,cy-145*s+r),outline=(20,20,30),width=line)
        d.line([(cx,cy-113*s),(cx,cy+40*s)],fill=(20,20,30),width=line)
        swing=math.sin(t*6)*40*s
        for direction in (-1,1):
            d.line([(cx,cy-65*s),(cx+direction*75*s,cy-10*s+swing*direction)],fill=(20,20,30),width=line)
            d.line([(cx,cy+40*s),(cx+direction*65*s,cy+155*s-swing*direction)],fill=(20,20,30),width=line)
        d.text((width*.1,height*.14),"WHAT IF?",fill=(15,25,50))
        d.text((width*.12,height*.8),"STICKMAN DEMO",fill=(20,20,30))
        im.save(frames/f"{i:05d}.png")
    audio=root/"demo.wav"
    rate=16000
    with wave.open(str(audio),"wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h",int(800*math.sin(2*math.pi*220*j/rate))) for j in range(rate*seconds)))
    video=root/"video.mp4"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-framerate",str(fps),"-i",str(frames/"%05d.png"),"-i",str(audio),"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest",str(video)],check=True)
    result=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(video)],capture_output=True,text=True,check=True)
    duration=float(result.stdout.strip())
    if video.stat().st_size<10000 or duration<seconds-1:
        raise RuntimeError("Output validation failed")
    manifest={"video":str(video),"duration":duration,"width":width,"height":height,"fps":fps,"demo":True,"publishable":False}
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--demo",action="store_true")
    a=p.parse_args()
    if not a.demo:
        raise SystemExit("Production not configured. Use --demo. Never publish demo.")
    print(json.dumps(make_demo(),indent=2))
