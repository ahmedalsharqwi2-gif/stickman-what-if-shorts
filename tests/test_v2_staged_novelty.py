import unittest
from copy import deepcopy
from production_v2.general_editorial import require_novel_story
class StagedNoveltyTests(unittest.TestCase):
 def story(self):
  return {'visual_plan':{'world':'procedural_story'},'scenes':[{'environment':'workshop','objects':[{'kind':'stickman','motion':'none'},{'kind':'gear','motion':'spin'}]} for _ in range(8)]}
 def test_same_hero_with_four_distinct_prop_actions_is_new(self):
  old=self.story();new=deepcopy(old)
  for s in new['scenes'][:4]:s['objects'][1]={'kind':'door','motion':'open'}
  self.assertTrue(require_novel_story(new,[old]))
 def test_titles_colors_cameras_and_positions_cannot_disguise_repetition(self):
  old=self.story();new=deepcopy(old);new['title']='another'
  for s in new['scenes']:
   s.update(camera_start=[2,3,12],narration='other')
   for o in s['objects']:o.update(color='#ff0000',position=[1,2,3])
  with self.assertRaises(ValueError):require_novel_story(new,[old])
 def test_only_three_changed_beats_are_insufficient(self):
  old=self.story();new=deepcopy(old)
  for s in new['scenes'][:3]:s['objects'][1]={'kind':'door','motion':'open'}
  with self.assertRaises(ValueError):require_novel_story(new,[old])
