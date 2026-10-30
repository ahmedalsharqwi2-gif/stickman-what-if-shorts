"""Procedural stickman acting demo: joint animation, staging and physical comedy."""
import argparse, math, os, subprocess
from PIL import Image, ImageDraw, ImageFont

W,H=540,960
SCENES=[
 ("النوم الهادئ", "sleep"),("السرير بيطير!", "float"),("فين الموبايل؟", "phone"),
 ("الحقوني!", "panic"),("محاولة هبوط", "fall"),("صاحبنا ظهر", "friend"),
 ("خطة عبقرية", "plan"),("مفاجأة!", "surprise")
]
def point(x,y,r,a): return (x+r*math.cos(a),y+r*math.sin(a))
def character(d,x,y,t,mode,color,scale=1):
    # Per-joint motion and independent head/arm/leg poses.
    bob=math.sin(t*5)*5 if mode in ("panic","friend") else math.sin(t*2)*2
    y+=bob
    swing=math.sin(t*7)*0.7 if mode=="panic" else math.sin(t*3)*0.3
    if mode=="sleep": swing=-0.7
    if mode=="surprise": swing=1.1
    head=(x,y-95*scale); neck=(x,y-64*scale); hip=(x,y+35*scale)
    left=(x-46*scale,y-18*scale-35*scale*swing)
    right=(x+46*scale,y-18*scale+35*scale*swing)
    if mode in ("float","fall"): left=(x-65*scale,y-75*scale);right=(x+65*scale,y-70*scale)
    feet=[(x-30*scale,y+110*scale+18*scale*swing),(x+30*scale,y+110*scale-18*scale*swing)]
    line=lambda a,b,width=9:d.line([a,b],fill=color,width=max(2,int(width*scale)),joint="curve")
    line(neck,hip);line((x,y-45*scale),left);line((x,y-45*scale),right)
    line(hip,feet[0]);line(hip,feet[1])
    r=27*scale;d.ellipse((head[0]-r,head[1]-r,head[0]+r,head[1]+r),fill="#fff8e7",outline=color,width=6)
    eye=6*scale
    for dx in (-10,10):d.ellipse((x+dx*scale-eye/2,head[1]-5*scale,x+dx*scale+eye/2,head[1]+2*scale),fill=color)
    if mode in ("panic","surprise","fall"):
        d.ellipse((x-7*scale,head[1]+8*scale,x+7*scale,head[1]+20*scale),outline=color,width=3)
    else:d.arc((x-11*scale,head[1]+2*scale,x+11*scale,head[1]+18*scale),0,180,fill=color,width=3)

def frame(sec,fps=24):
    idx=min(len(SCENES)-1,int(sec//7.5));title,mode=SCENES[idx];local=sec%7.5
    im=Image.new("RGB",(W,H),"#111a30");d=ImageDraw.Draw(im)
    d.rectangle((0,720,W,H),fill="#263b53")
    d.line((0,720,W,720),fill="#79cbd0",width=5)
    # moving environment objects, not static slideshow frames
    for i in range(6):
        x=(i*130+int(sec*15))%(W+100)-50
        d.ellipse((x,100+i*78,x+8,108+i*78),fill="#526b87")
    if idx==0:
        d.rounded_rectangle((90,570,450,750),radius=25,fill="#5867b3")
        d.rectangle((110,600,440,670),fill="#e2e9f7")
    if idx in (1,2,3,4):
        yy=530-170*min(1,local/5)+15*math.sin(sec*2)
        d.rounded_rectangle((70,yy,470,yy+85),radius=16,fill="#6677bb",outline="#d5dafa",width=4)
    if idx==2:
        px=360+65*math.sin(sec*3);py=380+90*math.cos(sec*2)
        d.rounded_rectangle((px,py,px+35,py+65),radius=5,fill="#111111",outline="#f4ce61",width=5)
    if idx==4:
        d.ellipse((180,700,360,730),fill="#354f62")
    y=520
    if idx in (1,2,3):y=540-150*min(1,local/4)+25*math.sin(sec*2)
    if idx==4:y=300+400*min(1,local/7.5)**2
    character(d,270,y,sec,mode,"#f6c657",1.45)
    if idx in (5,6,7):character(d,110,540,sec+1,"friend","#7be2d0",0.95)
    # typography kept ASCII-safe; Arabic dialogue supplied as scene metadata in README
    d.rounded_rectangle((25,38,515,110),radius=22,fill="#243751")
    d.text((45,59),f"WHAT IF GRAVITY VANISHED?  {idx+1}/8",fill="white")
    d.rounded_rectangle((25,835,515,920),radius=20,fill="#283e58")
    d.text((45,864),f"SCENE {idx+1}  |  {mode.upper()}  |  {int(local*100/7.5)}%",fill="#f6c657")
    return im

def main():
    p=argparse.ArgumentParser();p.add_argument("--seconds",type=float,default=60);p.add_argument("--fps",type=int,default=24);p.add_argument("--output",default="out/acting-demo.mp4");a=p.parse_args()
    os.makedirs(os.path.dirname(a.output) or ".",exist_ok=True)
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(a.fps),"-i","-","-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100","-shortest","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-c:a","aac",a.output]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(int(a.seconds*a.fps)):process.stdin.write(frame(n/a.fps).tobytes())
    except BrokenPipeError:raise RuntimeError("ffmpeg stopped unexpectedly")
    finally:process.stdin.close()
    if process.wait():raise RuntimeError("ffmpeg failed")
    print(a.output)
if __name__=="__main__":main()
