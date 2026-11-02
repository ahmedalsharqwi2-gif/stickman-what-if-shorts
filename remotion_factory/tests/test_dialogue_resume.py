import copy,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from remotion_factory import author as editorial
class ResumeOriginalDraft(unittest.TestCase):
 def test_prepared_review_resumes_without_another_writing_call(self):
  if 'exclude_slot' not in editorial.used.__code__.co_varnames:self.skipTest('Run this regression against the stickman production package')
  turns=[{'speaker':'a','text':'تخيل إن البحر اختفى وإحنا واقفين على الشط'}, {'speaker':'b','text':'طب والسفينة دي هتمشي على الرمل ولا هتستنى'}, {'speaker':'a','text':'خلينا نفهم أثر الفرضية من غير أرقام مخترعة'}, {'speaker':'b','text':'أيوه نسأل ونجرب ونشوف نتيجة كل خطوة سوا'}]
  draft={'title':'ماذا لو المحيط اختفى؟','canonical_subject':'what-if-ocean-new-episode','hashtags':['ماذا_لو','محيط','حوار'],'scenes':[{'label':'المحيط اختفى','turns':copy.deepcopy(turns),'narration':'','diagram':'flow','labels':['بحر','سفينة'],'evidence_quote':''} for _ in range(8)]}
  row={'title':'Ocean','scenario':'ocean','publisher':'NOAA'};entry={'status':'review_prepared','canonical_subject':draft['canonical_subject'],'story_document':{'path':'old-story'},'draft_document':{'path':'retained-draft'},'source_document':{'path':'retained-source'},'source_selection':row};state={'episodes':{'slot':entry}}
  def read(ref):return copy.deepcopy(draft) if ref['path']=='retained-draft' else {'text':'An unchanged original source.'}
  def mutate(callback):callback(state);return state
  def ask(prompt,schema,review=False):
   self.assertTrue(review,'A retained draft must not be written again');return {'supported':True,'engaging':True,'novel':True,'visuals_match':True,'issues':[]}
  original=Path.cwd()
  with tempfile.TemporaryDirectory() as folder:
   try:
    os.chdir(folder)
    with patch.object(editorial,'local',return_value=state),patch.object(editorial,'document_read',side_effect=read),patch.object(editorial,'document_write',return_value={'path':'new-story'}),patch.object(editorial,'mutate',side_effect=mutate),patch.object(editorial,'candidates',side_effect=AssertionError('No new topic selection')),patch.object(editorial,'ask_once',side_effect=ask) as request:
     story=editorial.author({'slot':'slot','profile':'stickman'},{})
    self.assertTrue(story['dialogue_enabled']);self.assertEqual(request.call_count,1);self.assertEqual(state['episodes']['slot']['status'],'authored')
   finally:os.chdir(original)
if __name__=='__main__':unittest.main()
