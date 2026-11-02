import copy,unittest
from production_v2.publish_completed_stickman import publish_one
DUE='2026-11-02T15:00:00Z'
class PublishOnceTests(unittest.TestCase):
 def setUp(self):
  self.record={};self.snapshots=[];self.calls=[];self.post={'id':'accepted','channelId':'owned-channel','status':'scheduled','dueAt':DUE,'assets':[{'source':'same-full-film.mp4'}]}
 def persist(self):self.snapshots.append(copy.deepcopy(self.record))
 def call(self,query,variables):
  self.assertEqual(self.snapshots[-1]['phase'],'intent')
  self.calls.append(variables);return {'createPost':{'post':{'id':'accepted','dueAt':DUE}}}
 def run_case(self,queue=None,read=None,call=None):
  return publish_one('youtube',{'channel':'owned-channel','organization':'own-org'},DUE,'same-full-film.mp4','title','caption',self.record,self.persist,read_queue=lambda *a:queue or [],read_post=read or (lambda id:copy.deepcopy(self.post)),call=call or self.call)
 def test_new_post_records_intent_before_one_submission_and_receipt_after_lookup(self):
  self.run_case();self.assertEqual(len(self.calls),1);self.assertEqual(self.record['id'],'accepted');self.assertEqual(self.record['phase'],'verified')
 def test_saved_accepted_id_is_never_submitted_again(self):
  self.record={'id':'accepted','phase':'acknowledged'};self.run_case();self.assertEqual(self.calls,[])
 def test_timed_out_submission_with_one_matching_provider_post_is_reconciled(self):
  self.record={'phase':'uncertain'};self.run_case(queue=[self.post]);self.assertEqual(self.calls,[]);self.assertEqual(self.record['id'],'accepted')
 def test_timed_out_submission_without_match_blocks_new_post(self):
  self.record={'phase':'uncertain'}
  with self.assertRaises(ValueError):self.run_case()
  self.assertEqual(self.calls,[])
 def test_another_film_in_target_slot_blocks_new_post(self):
  other={**self.post,'id':'other','assets':[{'source':'different-film.mp4'}]}
  with self.assertRaises(ValueError):self.run_case(queue=[other])
  self.assertEqual(self.calls,[])
