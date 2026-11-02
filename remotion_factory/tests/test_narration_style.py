import unittest
from remotion_factory.narration_style import validate_unnamed_story
class NaturalStory(unittest.TestCase):
 def test_character_type_is_not_spoken_in_any_common_spelling(self):
  for name in ('ستيكمان','ستيك مان','ستيكي مان','استيكى مان','سْتيكي مان','Stickman','stick man','آرنولد'):
   with self.subTest(name=name),self.assertRaises(ValueError):validate_unnamed_story({'scenes':[{'narration':name+' بيحاول يفتح الباب.'}]})
 def test_direct_whatif_story_uses_no_repeated_subject_name(self):
  validate_unnamed_story({'scenes':[{'narration':'تخيّل إنك صحيت جوه موبايلك. كل إشعار بيقرب، والبطارية بتنقص. هتلحق الشاحن إزاي؟'}]})
 def test_visual_metadata_and_topical_hashtags_are_not_censored(self):
  validate_unnamed_story({'title':'مغامرة ستيكي مان','hashtags':['#ستيك_مان'],'scenes':[{'label':'ستيك مان','narration':'الإشعارات نازلة زي المطر. تجري ناحية الشاحن، لكن الطريق بيتقفل.'}]})
if __name__=='__main__':unittest.main()
