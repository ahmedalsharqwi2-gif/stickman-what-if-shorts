import hashlib,json,os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave
from stickman.candidate import frame,scene_at,validate_timing
from stickman.fresh_review import run
from stickman.orbital_story import story

class FreshReviewTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.out=self.root/'run';self.ledger=self.root/'ledger.sqlite3';self.calls=[]
 def tts(self,text,path):
  self.calls.append('tts')
  with wave.open(path,'wb') as w:w.setparams((1,2,100,0,'NONE','PCM'));w.writeframes(b'\0\0'*12000)
 def timing(self,authored,wav,out):
  return {'duration':120,'coverage':1,'scenes':[{'id':row['id'],'start':i*15,'end':(i+1)*15} for i,row in enumerate(authored['scenes'])],
    'caption_groups':[{'text':'تعليق مقاس','start':0,'end':120}], 'audio_sha256':hashlib.sha256(Path(wav).read_bytes()).hexdigest(),
    'story_sha256':hashlib.sha256(json.dumps(authored,ensure_ascii=False,sort_keys=True).encode()).hexdigest()}
 def renderer(self,path,**kwargs):self.calls.append('render');Path(path).write_bytes(b'fake render used only in provider-mocked test')
 def mixer(self,rendered,wav,timing,out):
  final=out/'candidate-review.mp4';final.write_bytes(b'mocked final');return final
 def verify(self,path):return {'validated':True,'decode':'PASS','duration':120,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}
 def test_missing_fifth_key_leaves_no_partial_files(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaises(RuntimeError):run(self.out,self.ledger)
  self.assertFalse(self.out.exists());self.assertFalse(self.ledger.exists())
 def test_fresh_generation_uses_original_script_and_measured_captions(self):
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   result=run(self.out,self.ledger,tts=self.tts,asr=self.timing,renderer=self.renderer,mixer=self.mixer,verifier=self.verify)
  self.assertEqual(self.calls,['tts','render']);self.assertFalse(result['publishable']);self.assertEqual(result['profile'],'stickman')
  self.assertTrue((self.out/'output/candidate-verification.json').exists())
 def test_failed_tts_retains_topic_and_blocks_repeated_generation(self):
  from production_v2.ledger import Conflict
  def failed(*args):raise ConnectionError('mock provider unavailable')
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   with self.assertRaises(ConnectionError):run(self.out,self.ledger,tts=failed)
   self.assertTrue((self.out/'generation-failure.json').exists())
   with self.assertRaises(Conflict):run(self.root/'retry',self.ledger,tts=self.tts)
  self.assertEqual(self.calls,[])
 def test_scene_switches_follow_measured_not_uniform_timing(self):
  timing={'scenes':[{'start':start,'end':end} for start,end in [(0,5),(5,25),(25,45),(45,60),(60,75),(75,90),(90,105),(105,120)]]}
  self.assertEqual(scene_at(6,120,timing)[0],1)
  self.assertEqual(scene_at(24,120,timing)[0],1)
 def test_changed_audio_rejected_before_rendering(self):
  wav=self.root/'voice.wav';self.tts('mock',str(wav));authored=story();timing=self.timing(authored,wav,self.root);wav.write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'Narration changed'):validate_timing(authored,timing,120,wav)
 def test_story_distinguishes_weightlessness_from_absent_gravity(self):
  authored=story();text=' '.join(s['narration'] for s in authored['scenes'])
  self.assertIn('الجاذبية ما اختفتش',text);self.assertIn('سقوط حر',text);self.assertTrue(authored['fiction'])

 def test_explicit_resume_keeps_original_slot_and_script_without_new_reservation(self):
  from production_v2.ledger import Ledger
  captured=[]
  def failed(text,path):captured.append(text);raise ConnectionError('mock provider unavailable')
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   with self.assertRaises(ConnectionError):run(self.out,self.ledger,tts=failed)
   failure=json.loads((self.out/'generation-failure.json').read_text());slot=failure['slot']
   def same_text(text,path):captured.append(text);self.tts(text,path)
   result=run(self.root/'explicit-resume',self.ledger,resume_slot=slot,tts=same_text,asr=self.timing,renderer=self.renderer,mixer=self.mixer,verifier=self.verify)
  self.assertEqual(result['slot'],slot);self.assertTrue(result['resumed']);self.assertEqual(captured[0],captured[1])
  with Ledger(self.ledger) as ledger:
   self.assertEqual(ledger.db.execute('SELECT count(*) FROM reservations').fetchone()[0],1)
   kinds=[row[0] for row in ledger.db.execute('SELECT kind FROM events ORDER BY sequence')]
   self.assertIn('candidate_generation_failed',kinds);self.assertIn('candidate_resumed',kinds);self.assertIn('candidate_generated',kinds)
 def test_resume_rejects_changed_story_and_missing_reservation(self):
  from production_v2.ledger import Conflict
  def failed(*args):raise ConnectionError('mock provider unavailable')
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   with self.assertRaises(ConnectionError):run(self.out,self.ledger,tts=failed)
   slot=json.loads((self.out/'generation-failure.json').read_text())['slot']
   changed=story();changed['scenes'][0]['narration']='Replacement story is not authorized by resume'
   with patch('stickman.fresh_review.authored_story',return_value=changed):
    with self.assertRaisesRegex(Conflict,'story'):
     run(self.root/'changed',self.ledger,resume_slot=slot,tts=self.tts)
   with self.assertRaisesRegex(Conflict,'reservation'):
    run(self.root/'missing',self.ledger,resume_slot='candidate-does-not-exist',tts=self.tts)
  self.assertEqual(self.calls,[])
 def test_resume_failure_appends_attempt_without_erasing_previous_failure(self):
  from production_v2.ledger import Ledger
  def failed(*args):raise ConnectionError('mock provider unavailable')
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   with self.assertRaises(ConnectionError):run(self.out,self.ledger,tts=failed)
   slot=json.loads((self.out/'generation-failure.json').read_text())['slot']
   with self.assertRaises(ConnectionError):run(self.root/'resumed-failure',self.ledger,resume_slot=slot,tts=failed)
  with Ledger(self.ledger) as ledger:
   self.assertEqual(ledger.db.execute("SELECT count(*) FROM events WHERE kind='candidate_generation_failed'").fetchone()[0],2)
   self.assertEqual(ledger.db.execute('SELECT count(*) FROM reservations').fetchone()[0],1)
 def test_protected_ledger_path_is_rejected_before_creating_run(self):
  repo=Path(__file__).resolve().parents[1]
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   with self.assertRaisesRegex(ValueError,'protected'):
    run(self.out,repo/'state/must-not-create.sqlite3',tts=self.tts)
  self.assertFalse(self.out.exists());self.assertFalse((repo/'state/must-not-create.sqlite3').exists())
 def test_resume_reuses_provider_voice_cache_without_another_synthesis(self):
  import io
  from voice_provider.client import generate
  data=io.BytesIO()
  with wave.open(data,'wb') as audio:audio.setparams((1,2,100,0,'NONE','PCM'));audio.writeframes(b'\0\0'*12000)
  def failed_asr(*args):raise ValueError('Mock alignment interrupted after cached voice')
  env={'GEMINI_API_KEY':'mock-only','VOICE_CACHE_DIR':str(self.root/'voice-cache')}
  with patch.dict(os.environ,env,clear=True),patch('voice_provider.client._synthesize',return_value=(data.getvalue(),'mock-interaction',{'duration':120,'sample_rate':100,'channels':1})) as synth:
   with self.assertRaises(ValueError):run(self.out,self.ledger,tts=generate,asr=failed_asr)
   slot=json.loads((self.out/'generation-failure.json').read_text())['slot']
   resumed=self.root/'cached-resume'
   run(resumed,self.ledger,resume_slot=slot,tts=generate,asr=self.timing,renderer=self.renderer,mixer=self.mixer,verifier=self.verify)
   self.assertEqual(synth.call_count,1)
  source=json.loads((resumed/'professional_motion/delivery/narration.source.json').read_text())
  self.assertTrue(source['cache_hit']);self.assertEqual(source['interaction_id'],'mock-interaction')
 def test_resume_refuses_candidate_with_any_publication_intent(self):
  from production_v2.ledger import Ledger,Conflict
  def failed(*args):raise ConnectionError('mock provider unavailable')
  with patch.dict(os.environ,{'GEMINI_API_KEY':'mock-only'},clear=True):
   with self.assertRaises(ConnectionError):run(self.out,self.ledger,tts=failed)
   slot=json.loads((self.out/'generation-failure.json').read_text())['slot']
   with Ledger(self.ledger) as ledger:
    due=ledger.db.execute('SELECT due FROM reservations WHERE slot=?',(slot,)).fetchone()[0]
    ledger.register_video(slot,{'sha256':'c'*64,'decode':'PASS','validated':True})
    ledger.begin_submission(slot,'youtube','retained-channel',due,'https://example.test/existing.mp4')
   with self.assertRaisesRegex(Conflict,'Publication'):
    run(self.root/'forbidden-resume',self.ledger,resume_slot=slot,tts=self.tts)
  self.assertEqual(self.calls,[])
 def test_displayed_arabic_characters_have_real_font_glyphs(self):
  from PIL import ImageFont
  from stickman.candidate import FONT,CHANNEL_NAME,BEATS
  from stickman.fresh_review import FRESH_REVIEW_LABEL
  font=ImageFont.truetype(str(FONT),31);missing=bytes(font.getmask('\U0010ffff'))
  text=CHANNEL_NAME+'، المشهد 12345678 من '+FRESH_REVIEW_LABEL+' '.join(' '.join(beat[:2]) for beat in BEATS)
  text+=' '.join(scene['label']+' '+scene['caption']+' '+scene['narration'] for scene in story()['scenes'])
  self.assertNotIn('•',text)
  unsupported=[char for char in set(text) if not char.isspace() and bytes(font.getmask(char))==missing]
  self.assertEqual(unsupported,[])

if __name__=='__main__':unittest.main()
