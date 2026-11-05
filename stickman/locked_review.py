"""Run the repository's real Remotion renderer as an immutable silent review."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
from .beats_data import BEATS
from visual_contract import load_template,validate_hook,validate_accent
ROOT=Path(__file__).resolve().parents[1]
def props(duration):
 t=load_template();hook=validate_hook(BEATS[0]['hook_line'],max_words=t['hook']['max_words'],profile='stickman');scenes=[];captions=[]
 for i,b in enumerate(BEATS):
  validate_accent(b['title'],b['title_accent_word']);start=i*duration/len(BEATS);end=(i+1)*duration/len(BEATS)
  scenes.append({'id':str(i),'label':b['title'],'title_accent_word':b['title_accent_word'],'narration':b['hook_line'],'start':start,'end':end,'kind':'whatif','scenario':'gravity','pose':b['pose']})
  captions.append({'text':hook if i==0 else b['subtitle'],'start':start,'end':min(end,start+2.5)})
 return {'episode':{'profile':'stickman','series':t['display_name'],'title':BEATS[0]['title'],'title_accent_word':BEATS[0]['title_accent_word'],'hook_line':hook,'duration':duration,'scenes':scenes,'caption_groups':captions,'review_only':True,'timing_basis':'silent visual review; no measured narration or timing claim'}}
def render(output,duration,fps):
 t=load_template();output=Path(output).absolute()
 if not 90<duration<180:raise ValueError('Duration must be strictly 90 < duration < 180')
 if output.exists() or output.with_suffix('.json').exists():raise FileExistsError('Candidate outputs are immutable')
 if fps!=t['canvas']['fps']:raise ValueError('Locked canvas requires 30 fps')
 output.parent.mkdir(parents=True,exist_ok=True);folder=output.with_name(output.stem+'-review')
 data=props(duration);p=output.with_suffix('.props.json')
 with p.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2)
 subprocess.run(['node',str(ROOT/'remotion_motion/review.mjs'),'--props',str(p),'--output-dir',str(folder),'--silent-review'],cwd=ROOT,check=True)
 source=folder/'review.mp4'
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(source),'-f','null','-'],check=True)
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]))
 video=next(s for s in metadata['streams'] if s['codec_type']=='video')
 if (video['width'],video['height'])!=(t['canvas']['w'],t['canvas']['h']) or abs(float(metadata['format']['duration'])-duration)>.05 or any(s['codec_type']=='audio' for s in metadata['streams']):raise ValueError('Silent review media contract failed')
 output.hardlink_to(source)
 report={'publishable':False,'review_only':True,'visual_review':True,'duration':duration,'fps':fps,'width':t['canvas']['w'],'height':t['canvas']['h'],'narration_present':False,'hook_line':data['episode']['hook_line'],'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'full_decode_verified':True,'reason':'Silent review only; no frame-zero speech or measured alignment claim','audit_manifest':str(folder/'audit/manifest.json')}
 with output.with_suffix('.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 return report
