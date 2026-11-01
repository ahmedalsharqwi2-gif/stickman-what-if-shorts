"""Opt-in cinematic stickman candidate; never a social publishing entry point.

A silent visual review is explicitly incomplete. Real narration is required for
an eligible production candidate. Existing prototypes and outputs are untouched.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
from .character import character

W,H=1080,1920
BEATS=(
 ('تخيل لو الجاذبية اختفت؟','العالم ده تجربة خيالية، مش توقع علمي','surprised'),
 ('السرير بدأ يطلع!','كل حاجة سايبة بتتحرك بعيد عن الأرض','surprised'),
 ('الموبايل طاير هو كمان','محتاج نقطة ثابتة عشان أتحرك','neutral'),
 ('الدفع بيغيّر الاتجاه','دفعة صغيرة، ورد فعل في الاتجاه العكسي','surprised'),
 ('مش وقت الجري','من غير احتكاك ثابت، الحركة مختلفة','neutral'),
 ('صاحبي معاه حبل','هنمسك بعض ونفكر بهدوء','happy'),
 ('خطة الرجوع','الحبل مربوط في نقطة ثابتة في المشهد الخيالي','neutral'),
 ('الحل مش في القوة','التخيل ممتع، والعلم يساعدنا نفهم الحركة','happy'),
)
FONT=Path(__file__).resolve().parents[1]/'assets/fonts/NotoSansArabic-Bold.ttf'
CHANNEL_NAME=json.loads((Path(__file__).resolve().parents[1]/'config/channel.json').read_text())['channel_name']

def ease(value):
    value=max(0,min(1,value))
    return value*value*(3-2*value)

def scene_at(t,duration,timing=None):
    if timing:
        scenes=timing["scenes"]
        index=max(i for i,scene in enumerate(scenes) if scene["start"]<=max(0,min(t,duration)))
        scene=scenes[index]
        return index,ease((t-scene["start"])/max(.001,scene["end"]-scene["start"]))
    index=min(len(BEATS)-1,max(0,int(t/duration*len(BEATS))))
    return index,(t-index*duration/len(BEATS))/(duration/len(BEATS))

def frame(t,duration=120,width=W,height=H,visual_review=True,story=None,timing=None):
    """Layered room, perspective floor, independent acting and slow camera drift."""
    index,progress=scene_at(t,duration,timing)
    title,line,mood=BEATS[index]
    if story:
        scene=story["scenes"][index];title=scene["label"];line=scene.get("caption","");mood=scene.get("mood","neutral")
    if timing:
        line=next((group["text"] for group in timing["caption_groups"] if group["start"]<=t<group["end"]),"")
    im=Image.new('RGB',(W,H),'#091525'); d=ImageDraw.Draw(im)
    # A slowly changing light gradient preserves readable silhouettes.
    for y in range(0,H,12):
        gain=max(0,1-abs(y-650)/1500)
        d.rectangle((0,y,W,y+12),fill=(int(8+10*gain),int(19+18*gain),int(33+26*gain)))
    camera=math.sin(t*.12)*28+18*(ease(progress)-.5)
    # Background window and distant skyline: one quarter of camera displacement.
    for n in range(7):
        x=n*180-camera*.25
        d.rectangle((x,560+(n%3)*55,x+120,1050),fill='#172c43')
        for row in range(3): d.rectangle((x+20,650+row*90,x+36,674+row*90),fill='#4c7f8b')
    d.rounded_rectangle((125-camera*.4,310,950-camera*.4,1000),radius=30,outline='#426875',width=8)
    # Floor converges at the vanishing point; foreground travels farther.
    d.polygon(((0,1320),(W,1320),(W,H),(0,H)),fill='#20384b')
    for n in range(-5,8):
        d.line((540+(n-1)*65-camera*.45,1320,540+(n-1)*420-camera*1.7,H),fill='#345164',width=3)
    for y in (1360,1425,1530,1690,1900): d.line((0,y,W,y),fill='#345164',width=3)
    floating=index in (1,2,3,4)
    local=t-(timing["scenes"][index]["start"] if timing else index*duration/8)
    x=580-camera+math.sin(local*.5)*55
    y=1130-(150+70*math.sin(local*.8) if floating else 0)
    # Soft contact shadow changes size as the character leaves the floor.
    shadow=Image.new('RGBA',(W,H)); sd=ImageDraw.Draw(shadow)
    for r in range(12,0,-1):
        spread=r*5
        sd.ellipse((x-120-spread,1440-spread*.15,x+120+spread,1470+spread*.15),fill=(0,0,0,5))
    im=Image.alpha_composite(im.convert('RGBA'),shadow).convert('RGB'); d=ImageDraw.Draw(im)
    if index<5:
        by=1190-(160+25*math.sin(t) if floating else 0)
        d.polygon(((190-camera,by),(795-camera,by-60),(905-camera,by+65),(275-camera,by+130)),fill='#49688d',outline='#9caec9')
        d.polygon(((275-camera,by+130),(905-camera,by+65),(905-camera,by+115),(275-camera,by+175)),fill='#2c4667')
    if index==2:
        px=740-camera+50*math.sin(t*1.4);py=700+65*math.cos(t)
        d.rounded_rectangle((px,py,px+58,py+114),radius=9,fill='#080f1b',outline='#edc46d',width=5)
    if index>=5:
        character(d,235-camera*.75,1160,scale=1.18,phase=t+1,mood='happy',accent='#8ad6cd')
        d.line((235-camera*.75,1070,x,1030),fill='#dbad73',width=7)
        d.ellipse((90,1240,120,1270),outline='#dbad73',width=5)
    character(d,x,y,scale=1.8+ease(progress)*.08,phase=t,mood=mood,accent='#f4ce79')
    # Occluding foreground rail and plants provide depth without covering text.
    for side in (-1,1):
        base=30 if side<0 else 1040
        offset=camera*1.8
        for n in range(4):
            d.line((base-offset,1630,base+side*(30+n*18)-offset,1440-n*32),fill='#244d53',width=18)
    d.rounded_rectangle((70,95,1010,238),radius=25,fill='#142c40',outline='#3c6577',width=2)
    font=ImageFont.truetype(str(FONT),48); small=ImageFont.truetype(str(FONT),31)
    d.text((970,120),title,font=font,fill='#f1d69b',anchor='ra',direction='rtl')
    d.text((970,190),f'{CHANNEL_NAME} • المشهد {index+1} من 8',font=small,fill='#b7d6dc',anchor='ra',direction='rtl')
    d.rounded_rectangle((90,1515,990,1655),radius=22,fill='#142b3e')
    d.text((945,1540),line,font=small,fill='#f0f0e6',anchor='ra',direction='rtl')
    if visual_review:
        d.text((540,1710),'مراجعة حركة فقط، بدون تعليق صوتي',font=small,fill='#efc87b',anchor='ma',direction='rtl')
    d.rectangle((95,1775,985,1780),fill='#315261'); d.rectangle((95,1775,95+890*min(1,t/duration),1780),fill='#88c9c0')
    return im if (width,height)==(W,H) else im.resize((width,height),Image.Resampling.LANCZOS)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

def validate_timing(story,timing,duration,narration):
    if not narration or story.get('profile')!='stickman' or len(story.get('scenes',[]))!=8 or len(timing.get('scenes',[]))!=8:
        raise ValueError('Eight authored and measured stickman scenes and narration are required')
    if abs(float(timing['duration'])-duration)>.05 or not .9<=float(timing.get('coverage',0))<=1:
        raise ValueError('Complete measured speech coverage is required')
    if timing.get('audio_sha256')!=hashlib.sha256(Path(narration).read_bytes()).hexdigest():raise ValueError('Narration changed after alignment')
    digest=hashlib.sha256(json.dumps(story,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    if timing.get('story_sha256')!=digest:raise ValueError('Story changed after alignment')
    prior=0
    for index,(authored,measured) in enumerate(zip(story['scenes'],timing['scenes'])):
        start,end=float(measured['start']),float(measured['end'])
        if measured['id']!=authored['id'] or not all(math.isfinite(v) for v in (start,end)) or abs(start-prior)>.05 or not start<end<=duration+.001:
            raise ValueError('Measured scenes must cover the complete film without gaps')
        prior=end
    if abs(prior-duration)>.05:raise ValueError('Final measured scene must reach film end')
    groups=timing.get('caption_groups',[])
    if not groups:raise ValueError('Measured captions required')
    previous=0
    for group in groups:
        start,end=float(group['start']),float(group['end'])
        if not all(math.isfinite(v) for v in (start,end)) or not 0<=start<end<=duration+.1 or start<previous-.03:
            raise ValueError('Measured captions are unordered or outside narration')
        previous=end

def render(output,duration=120,fps=24,narration=None,visual_review=False,story=None,timing=None):
    if not 120<=duration<180: raise ValueError('A full candidate must be 120 to less than 180 seconds')
    if not 12<=fps<=30: raise ValueError('Frame rate must be 12..30')
    if not visual_review and narration is None: raise ValueError('Original Arabic narration is required; use --visual-review for an incomplete silent review')
    if narration:
        evidence=probe(narration)
        if not any(s['codec_type']=='audio' for s in evidence['streams']): raise ValueError('Narration has no audio stream')
        audio_duration=float(evidence['format']['duration'])
        if abs(audio_duration-duration)>.5: raise ValueError('Narration duration must match requested film duration within 0.5 second')
    if (story is None)!=(timing is None): raise ValueError('Authored story and measured timing must be supplied together')
    if timing:
        validate_timing(story,timing,duration,narration)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists() or output.with_suffix('.json').exists(): raise FileExistsError('Candidate outputs are immutable: choose a new output path')
    temporary=output.with_name(output.stem+'.partial.mp4')
    if temporary.exists():raise FileExistsError(temporary)
    command=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-']
    if narration: command+=['-i',str(narration),'-map','0:v','-map','1:a','-c:a','aac']
    else:command+=['-an']
    command+=['-t',str(duration),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(temporary)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for n in range(round(duration*fps)):process.stdin.write(frame(n/fps,duration,visual_review=visual_review,story=story,timing=timing).tobytes())
        process.stdin.close()
        if process.wait(): raise RuntimeError('FFmpeg encoding failed')
    except BaseException:
        process.kill();process.wait();temporary.unlink(missing_ok=True);raise
    try:
        media=probe(temporary);video=next(s for s in media['streams'] if s['codec_type']=='video')
        if (video['width'],video['height'])!=(W,H) or abs(float(media['format']['duration'])-duration)>.1:raise ValueError('Encoded film dimensions/duration mismatch')
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(temporary),'-f','null','-'],check=True)
        output.hardlink_to(temporary)  # atomic refusal if another run reserved this final path
        temporary.unlink()
    except BaseException:temporary.unlink(missing_ok=True);raise
    manifest={'schema':1,'pipeline':'stickman-candidate-v2','duration':duration,'fps':fps,'width':W,'height':H,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'visual_review':visual_review,'narration_present':bool(narration),'narration_semantics_verified':bool(timing),'measured_captions':bool(timing),'channel_name':CHANNEL_NAME,'publishable':False,'reason':'Candidate review only; narration semantics, measured captions and channel publishing must be verified before cutover','full_decode_verified':True}
    with output.with_suffix('.json').open('x',encoding='utf8') as receipt:
        receipt.write(json.dumps(manifest,ensure_ascii=False,indent=2))
    return manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--duration',type=float,default=120);parser.add_argument('--fps',type=int,default=24);parser.add_argument('--narration',type=Path);parser.add_argument('--visual-review',action='store_true');args=parser.parse_args()
    print(json.dumps(render(args.output,args.duration,args.fps,args.narration,args.visual_review),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
