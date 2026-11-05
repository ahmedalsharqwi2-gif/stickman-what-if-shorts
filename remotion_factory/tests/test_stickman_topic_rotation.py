import unittest
from remotion_factory.stickman_topics import seed_anchor,template,ordered
from remotion_factory.author import prior_identifiers
class HypothesisRotation(unittest.TestCase):
 def test_a_seed_is_used_even_when_the_writer_chose_a_more_specific_episode_id(self):
  _,topics=prior_identifiers([{'canonical_subject':'earth-stop-inertia-at-equator','source_selection':{'canonical_subject':'stickman-whatif-earth-stop-consequences'}}]);self.assertIn('earth-stop-inertia-at-equator',topics);self.assertIn('stickman-whatif-earth-stop-consequences',topics)
 def test_creative_world_is_not_a_finite_episode_reservation(self):
  self.assertIsNone(seed_anchor({'source_selection':{'canonical_subject':'creative-environment-phone'}}));self.assertTrue(template({'canonical_subject':'creative-environment-phone'}))
 def test_a_recent_world_does_not_dominate_other_available_worlds(self):
  rows=[{'canonical_subject':'creative-environment-phone','scenario':'phone'},{'canonical_subject':'creative-environment-gravity','scenario':'gravity'}];history=[{'source_selection':{'scenario':'phone'}}];self.assertEqual(ordered(rows,history)[0]['scenario'],'gravity')
