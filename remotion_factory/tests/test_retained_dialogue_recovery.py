import copy,json,unittest
from pathlib import Path
from remotion_factory.dialogue import attach_timing
from remotion_factory.speech_characters import character_timing
from remotion_factory.speech_lexicon import recognized_key
class RetainedDialogueRecovery(unittest.TestCase):
 def fixture(self):
  data=json.loads((Path(__file__).parent/'fixtures/retained-dialogue-boundary.json').read_text())
  rows=[(name,[{'text':t,'start':a,'end':b} for t,a,b in words]) for name,words in data['transcripts'].items()]
  timing=character_timing(data['story'],data['duration'],rows,recognized_key)
  return data,rows,timing
 def test_retained_real_asr_omission_never_gets_synthetic_captions(self):
  data,rows,timing=self.fixture();original=copy.deepcopy(data['story'])
  result=attach_timing(data['story'],timing,rows)
  self.assertEqual(data['story'],original);self.assertGreaterEqual(result['coverage'],.9)
  self.assertEqual(len(result['dialogue_omissions']),1)
  self.assertEqual(result['dialogue_omissions'][0]['word_count'],7)
  self.assertEqual(len(result['dialogue_omissions'][0]['confirming_asr_models']),3)
  self.assertFalse(result['dialogue_full_script_spoken'])
  self.assertNotIn('بالضبط', ' '.join(c['text'] for c in result['caption_groups']))
  self.assertEqual(len(result['dialogue_turns']),31)
  self.assertTrue(all(a['end']<=b['start'] for a,b in zip(result['dialogue_turns'],result['dialogue_turns'][1:])))
 def test_long_unrecognized_audio_cannot_be_treated_as_omitted_speech(self):
  data,rows,timing=self.fixture()
  expected=' '.join(s['narration'] for s in data['story']['scenes']).split()
  cursor=sum(len(t['text'].split()) for s in data['story']['scenes'][:4] for t in s['turns'])+sum(len(t['text'].split()) for t in data['story']['scenes'][4]['turns'][:3])
  keys=[int(k) for k in timing['script_word_anchors'] if int(k)<cursor]
  timing['script_word_anchors'][max(keys)]['end']-=3
  with self.assertRaises(ValueError):attach_timing(data['story'],timing,rows)

