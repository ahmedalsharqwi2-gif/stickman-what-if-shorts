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

if __name__=='__main__':unittest.main()
