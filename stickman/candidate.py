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

from visual_contract import load_template
TEMPLATE=load_template()
W,H=TEMPLATE['canvas']['w'],TEMPLATE['canvas']['h']
from .beats_data import BEATS
FONT=Path(__file__).resolve().parents[1]/TEMPLATE['font']['bold']
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

def frame(t,duration=120,width=W,height=H,visual_review=True,story=None,timing=None,review_label=None):
    from .locked_frame import frame as locked_frame
    return locked_frame(t,duration,width,height,visual_review,story,timing,review_label)

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

def render(output,duration=120,fps=30,narration=None,visual_review=False,story=None,timing=None,review_label=None):
    if not 90<duration<180: raise ValueError('A full candidate must be strictly 90 < duration < 180 seconds')
    if visual_review and narration is None and story is None:
        from .locked_review import render as locked_render
        return locked_render(output,duration,fps)
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
        for n in range(round(duration*fps)):process.stdin.write(frame(n/fps,duration,visual_review=visual_review,story=story,timing=timing,review_label=review_label).tobytes())
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
    manifest={'schema':1,'pipeline':'stickman-candidate-v2','duration':duration,'fps':fps,'width':W,'height':H,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'visual_review':visual_review,'narration_present':bool(narration),'narration_semantics_verified':bool(timing),'measured_captions':bool(timing),'channel_name':CHANNEL_NAME,'review_label':review_label,'publishable':False,'reason':'Candidate review only; narration semantics, measured captions and channel publishing must be verified before cutover','full_decode_verified':True}
    with output.with_suffix('.json').open('x',encoding='utf8') as receipt:
        receipt.write(json.dumps(manifest,ensure_ascii=False,indent=2))
    return manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='reviews/locked-visual-review-'+__import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.mp4');parser.add_argument('--duration',type=float,default=120);parser.add_argument('--fps',type=int,default=30);parser.add_argument('--narration',type=Path);parser.add_argument('--visual-review',action='store_true');args=parser.parse_args()
    print(json.dumps(render(args.output,args.duration,args.fps,args.narration,args.visual_review),ensure_ascii=False,indent=2))
if __name__=='__main__':main()

