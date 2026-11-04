import unittest
from unittest.mock import patch
from remotion_factory import author
class ResumeTopicIdentity(unittest.TestCase):
 def test_current_retained_topic_is_not_a_previous_episode(self):
  episodes={'current':{'canonical_subject':'same-topic','source':{'url':'https://example.org/current'}},'old':{'canonical_subject':'old-topic','source':'https://example.org/old'}}
  with patch.object(author,'local',return_value={'episodes':episodes}),patch.object(author.Path,'exists',return_value=False):
   urls,topics=author.prior_identifiers(author.used('current'))
  self.assertEqual(topics,{'old-topic'});self.assertEqual(urls,{'https://example.org/old'})
