"""Expressive stickman character primitives for richer scenes."""
import math
from PIL import ImageDraw

def character(draw, x, y, scale=1.0, phase=0.0, mood="surprised", accent="#141d35"):
    s=scale
    sway=math.sin(phase*3)*7*s
    head_y=y-130*s+sway
    r=42*s
    w=max(3,int(8*s))
    draw.ellipse((x-r,head_y-r,x+r,head_y+r),fill="#fff7e8",outline=accent,width=w)
    eye_y=head_y-10*s
    if mood=="surprised":
        for dx in (-15,15):
            draw.ellipse((x+(dx-5)*s,eye_y-6*s,x+(dx+5)*s,eye_y+6*s),fill=accent)
        draw.ellipse((x-9*s,head_y+9*s,x+9*s,head_y+31*s),outline=accent,width=max(2,int(4*s)))
        draw.arc((x-30*s,head_y-29*s,x-7*s,head_y-9*s),190,345,fill=accent,width=3)
        draw.arc((x+7*s,head_y-29*s,x+30*s,head_y-9*s),195,350,fill=accent,width=3)
    elif mood=="happy":
        for dx in (-16,16):
            draw.arc((x+(dx-8)*s,eye_y-6*s,x+(dx+8)*s,eye_y+9*s),190,350,fill=accent,width=3)
        draw.arc((x-20*s,head_y-1*s,x+20*s,head_y+28*s),5,175,fill=accent,width=4)
    else:
        for dx in (-16,16):
            draw.ellipse((x+(dx-4)*s,eye_y-4*s,x+(dx+4)*s,eye_y+4*s),fill=accent)
        draw.line((x-13*s,head_y+19*s,x+13*s,head_y+19*s),fill=accent,width=4)
    body_top=(x,head_y+r)
    body_bottom=(x+sway*.5,y+85*s)
    draw.line((body_top,body_bottom),fill=accent,width=w)
    arm=math.sin(phase*5)*20*s
    draw.line((x,head_y+70*s,x-76*s,head_y+48*s-arm),fill=accent,width=w)
    draw.line((x,head_y+70*s,x+76*s,head_y+35*s+arm),fill=accent,width=w)
    draw.line((body_bottom,(x-52*s,y+184*s-arm*.3)),fill=accent,width=w)
    draw.line((body_bottom,(x+52*s,y+184*s+arm*.3)),fill=accent,width=w)
    for px,py in ((x-76*s,head_y+48*s-arm),(x+76*s,head_y+35*s+arm)):
        draw.ellipse((px-8*s,py-8*s,px+8*s,py+8*s),fill="#ffcf78",outline=accent,width=3)
