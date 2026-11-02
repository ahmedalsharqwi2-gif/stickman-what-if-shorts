import copy,unittest
from remotion_factory.dialogue import prepare_draft,attach_timing,schema_for
class Dialogue(unittest.TestCase):
 def sample(self):return {'scenes':[{'turns':[{'speaker':'a','text':'تخيّل إننا صحينا جوه الموبايل'},{'speaker':'b','text':'طب والبطارية هتكفينا لحد فين'},{'speaker':'a','text':'نلحق الشاحن قبل الشاشة ماتطفي'}]}]}
 def test_verbatim_turns_define_narration_without_spoken_names(self):
  raw=self.sample();before=copy.deepcopy(raw);story=prepare_draft(raw)
  self.assertEqual(raw,before);self.assertTrue(story['dialogue_enabled']);self.assertEqual(story['scenes'][0]['narration'],' '.join(t['text'] for t in raw['scenes'][0]['turns']));self.assertNotIn('speaker',story['scenes'][0]['narration'])
 def test_single_speaker_is_not_a_two_character_conversation(self):
  raw=self.sample()
  for t in raw['scenes'][0]['turns']:t['speaker']='a'
  with self.assertRaises(ValueError):prepare_draft(raw)
 def test_actor_switches_use_recognized_audio_not_evenly_divided_scene(self):
  story=prepare_draft(self.sample());words=story['scenes'][0]['narration'].split();boundary=len(story['scenes'][0]['turns'][0]['text'].split());actual=[{'text':word,'start':(.2+i*.3 if i<boundary else 5+i*.31),'end':(.4+i*.3 if i<boundary else 5.2+i*.31)} for i,word in enumerate(words)];timing={'duration':20,'scenes':[{}]};attach_timing(story,timing,[('independent-asr',actual)])
  self.assertEqual(timing['dialogue_turns'][1]['speaker'],'b');self.assertAlmostEqual(timing['dialogue_turns'][1]['start'],actual[boundary]['start']);self.assertTrue(timing['dialogue_timing_verified']);self.assertTrue(all(c.get('speaker') in ('a','b') for c in timing['caption_groups']))
 def test_missing_recognized_speech_never_invents_actor_timestamps(self):
  with self.assertRaises(ValueError):attach_timing(prepare_draft(self.sample()),{'duration':20,'scenes':[{}]},[('empty',[])])
if __name__=='__main__':unittest.main()
