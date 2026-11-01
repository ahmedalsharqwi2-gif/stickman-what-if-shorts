import os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from stickman.alignment import measured_timing
from voice_provider.client import generate

class ResumeRegressionTests(unittest.TestCase):
 def test_pronunciation_anchors_are_tried_between_85_and_90_percent(self):
  letters='ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
  tokens=['هذا' if i%9==0 else 'كلمة'+letters[i%len(letters)]+letters[i//len(letters)] for i in range(96)]
  story={'scenes':[{'id':str(i),'narration':' '.join(tokens[i*12:(i+1)*12])} for i in range(8)]}
  actual=[{'text':token.replace('ذ','ز'),'start':i,'end':i+.8} for i,token in enumerate(tokens)]
  timing=measured_timing(story,96,[('measured',actual)])
  self.assertGreaterEqual(timing['exact_token_coverage'],.85)
  self.assertLess(timing['exact_token_coverage'],.9)
  self.assertEqual(timing['coverage'],1)
  self.assertTrue(timing['known_name_and_egyptian_normalization_applied'])
 def test_missing_reserved_voice_cache_never_calls_provider(self):
  with tempfile.TemporaryDirectory() as temp:
   with patch.dict(os.environ,{'GEMINI_TTS_API_KEY':'test-only','VOICE_CACHE_DIR':temp},clear=True):
    with patch('voice_provider.client._synthesize') as synth:
     with self.assertRaisesRegex(RuntimeError,'refusing duplicate'):
      generate('نص محجوز',str(Path(temp)/'output.wav'),cache_only=True)
     synth.assert_not_called()
if __name__=='__main__':unittest.main()
