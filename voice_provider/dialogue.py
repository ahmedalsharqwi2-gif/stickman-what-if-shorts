"""Two real voices in one own-key Gemini interaction; no label text is spoken."""
import base64,hashlib,json,os,tempfile,time,urllib.request,urllib.error
from pathlib import Path
from api_budget import reserve
from .client import config,_wave_info
def payload(turns,base,policy):
 mapping=policy['voices']
 if mapping!={'a':'Charon','b':'Puck'}:raise ValueError('Approved two-character voice mapping changed')
 if not turns or {t['speaker'] for t in turns}!={'a','b'}:raise ValueError('Two actual speaking parts required')
 return {'model':base['model'],'input':[{'type':'user_input','content':[{'type':'text','text':t['text'],'annotations':[{'type':'speech_metadata','speaker':t['speaker'],'style':base['style']+' '+policy['styles'][t['speaker']]+' Speak only this exact Egyptian Arabic text. Do not read any speaker name or metadata.'}]} for t in turns]}],'response_format':{'type':'audio'},'generation_config':{'speech_config':{'speakers':[{'speaker':s,'voice':v} for s,v in mapping.items()]}}}
def generate(turns,path):
 base=config();policy=json.loads(Path('config/stickman_dialogue.json').read_text());key=(os.getenv('GEMINI_TTS_API_KEY') or os.getenv('GEMINI_API_KEY') or '').strip()
 if not key:raise ValueError('Own repository TTS credential missing')
 body=payload(turns,base,policy);text=' '.join(t['text'] for t in turns);fingerprint=hashlib.sha256((hashlib.sha256(key.encode()).hexdigest()+json.dumps(body,ensure_ascii=False,sort_keys=True)).encode()).hexdigest();cache=Path(os.getenv('VOICE_CACHE_DIR','.voice_cache'));cache.mkdir(parents=True,exist_ok=True);wav=cache/(fingerprint+'.wav');meta=wav.with_suffix('.json');hit=wav.exists() and meta.exists()
 if hit:
  data=wav.read_bytes();report=json.loads(meta.read_text())
  if hashlib.sha256(data).hexdigest()!=report['sha256']:raise ValueError('Dialogue cache fingerprint changed')
 else:
  reserve('tts',base['model'],key);request=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',data=json.dumps(body).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(request,timeout=240) as response:raw=json.load(response)
  except (urllib.error.URLError,TimeoutError):raise RuntimeError('Dialogue TTS unavailable; retained intent blocks another uncertain generation') from None
  blocks=[b for step in raw.get('steps',[]) if step.get('type')=='model_output' for b in step.get('content',[]) if b.get('type')=='audio' and b.get('data')]
  if not blocks:raise RuntimeError('No complete dialogue audio returned; no substitute voices or repeated request')
  data=base64.b64decode(blocks[-1]['data'],validate=True);info=_wave_info(data);report={'provider':'Gemini TTS','model':base['model'],'voice':'Charon+Puck','speakers':policy['voices'],'text':text,'turns':turns,'interaction_id':raw.get('id'),**info,'sha256':hashlib.sha256(data).hexdigest(),'newly_synthesized':True,'fallback_used':False,'provider_requests':1,'speaker_names_spoken':False}
  with tempfile.NamedTemporaryFile(dir=cache,delete=False) as f:f.write(data);temporary=Path(f.name)
  temporary.replace(wav);meta.write_text(json.dumps(report,ensure_ascii=False,indent=2))
 target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.with_suffix('.source.json').write_text(json.dumps({**report,'cache_hit':hit,'output_sha256':hashlib.sha256(data).hexdigest()},ensure_ascii=False,indent=2)+'\n');return target
