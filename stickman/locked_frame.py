"""Template-bound Pillow inspection frame; the full review uses Remotion."""
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from visual_contract import load_template,validate_accent,assert_in_safe_zone
from .beats_data import BEATS
from .character import character
ROOT=Path(__file__).resolve().parents[1]
def wrap(text,font,width):
 lines=[];line=''
 for word in text.split():
  candidate=(line+' '+word).strip()
  if font.getlength(candidate,direction='rtl')>width:
   if not line:raise ValueError('Word exceeds locked width')
   lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 if len(lines)>2:raise ValueError('Text must be rewritten; no shrink or clip')
 return lines

def render_title(d,text,word,t,font):
 validate_accent(text,word);x=t['safe_zone']['text_x'][1];y=t['title']['y'];lines=wrap(text,font,t['layout']['title_width']);boxes=[]
 for line in lines:
  # Draw connected RTL runs, splitting only at word boundaries.
  parts=line.split(word) if word in line.split() else [line]
  for index,part in enumerate(parts):
   if part:
    box=d.textbbox((x,y),part,font=font,anchor='rt',direction='rtl');assert_in_safe_zone('title',box,template=t);boxes.append(box);d.text((x,y),part,font=font,anchor='rt',direction='rtl',fill=t['palette']['ink']);x-=font.getlength(part,direction='rtl')
   if len(parts)>1 and index==0:
    box=d.textbbox((x,y),word,font=font,anchor='rt',direction='rtl');assert_in_safe_zone('title',box,template=t);boxes.append(box);d.text((x,y),word,font=font,anchor='rt',direction='rtl',fill=t['palette']['accent']);x-=font.getlength(word,direction='rtl')
  y+=round(t['title']['size']*t['layout']['title_line_height']);x=t['safe_zone']['text_x'][1]
 if max(b[3] for b in boxes)>t['layout']['title_bottom']:raise ValueError('Title exceeds locked band')
 return boxes

def frame(time,duration,width,height,visual_review,story,timing,review_label):
 t=load_template();w,h=t['canvas']['w'],t['canvas']['h'];z=t['safe_zone'];index=min(7,int(max(0,time)/duration*8));b=BEATS[index];im=Image.new('RGB',(w,h),t['palette']['bg']);d=ImageDraw.Draw(im);path=ROOT/t['font']['bold'];title=ImageFont.truetype(str(path),t['title']['size']);small=ImageFont.truetype(str(path),t['layout']['brand_size']);caption=ImageFont.truetype(str(path),t['caption']['size'])
 label=b['title'];accent=b['title_accent_word'];line=b['subtitle']
 if story:
  scene=story['scenes'][index];label=scene['label'];accent=scene.get('title_accent_word');line=scene.get('caption','')
 if timing:line=next((c['text'] for c in timing['caption_groups'] if c['start']<=time<c['end']),'')
 render_title(d,label,accent,t,title)
 d.text((z['text_x'][1],t['layout']['brand_y']),t['display_name'],font=small,fill=t['palette']['ink'],anchor='rt',direction='rtl')
 cfg=t['layout']['candidate']
 for i,key in enumerate(('actor_a','actor_b')):
  x,y,scale=cfg[key];character(d,x,y+math.sin(time+i)*cfg['actor_sway'],scale=scale,phase=time+i,mood=b['expression'],accent=t['palette']['ink'])
 x,y,r=cfg['floating_prop'];x+=math.sin(time)*cfg['prop_motion'];y+=math.cos(time)*cfg['prop_motion'];d.rectangle((x-r,y-r,x+r,y+r),outline=t['palette']['ink'],width=cfg['outline_width'])
 if line:
  pad_y,pad_x=t['layout']['caption_padding'];lines=wrap(line,caption,z['caption_max_width']-2*pad_x);line_h=round(t['caption']['size']*t['layout']['caption_line_height']);height_box=len(lines)*line_h+2*pad_y;box=(z['text_x_lower']['x'][0],z['caption_y_bottom']-height_box,z['text_x_lower']['x'][0]+z['caption_max_width'],z['caption_y_bottom']);assert_in_safe_zone('caption',box,template=t)
  if height_box>z['caption_max_height']:raise ValueError('Caption is over two lines')
  d.rounded_rectangle(box,radius=t['layout']['caption_radius'],fill=t['palette']['ink'])
  for n,text in enumerate(lines):d.text((z['caption_center_x'],box[1]+pad_y+n*line_h),text,font=caption,fill=t['palette']['bg'],anchor='mt',direction='rtl')
 if visual_review or review_label:d.text((z['caption_center_x'],t['layout']['review_y']),review_label or 'معاينة بدون صوت',font=small,fill=t['palette']['ink'],anchor='mt',direction='rtl')
 return im if im.size==(width,height) else im.resize((width,height),Image.Resampling.LANCZOS)
