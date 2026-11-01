"""Read-only own-repository publishing connection discovery; never creates posts."""
import json,os,re
from pathlib import Path
from production_v2.export_review import context,StatusStore
def norm(value):return re.sub(r'[^a-z0-9\u0621-\u064a]','',str(value).lower()).translate(str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ة':'ه','ى':'ي'}))
def main():
 repository,run,attempt,source=context('stickman')
 report={'profile':'stickman','repository':repository,'run_id':run,'run_attempt':attempt,'source_commit':source,'stage':'success','kind':'publishing_connection_discovery','no_posts_created':True,'read_only':True,'ready':False,'credential_present':bool(os.getenv('BUFFER_API_KEY','').strip())}
 if report['credential_present']:
  import requests
  def query(text):
   r=requests.post('https://api.buffer.com',headers={'Authorization':'Bearer '+os.environ['BUFFER_API_KEY']},json={'query':text},timeout=45)
   if r.status_code!=200:raise RuntimeError('Publishing connection HTTP '+str(r.status_code))
   data=r.json()
   if data.get('errors'):raise RuntimeError('Publishing connection query rejected')
   return data['data']
  try:
   orgs=query('query { account { organizations { id } } }')['account']['organizations']
   matches=[];available=[]
   for org in orgs:
    rows=query('query { channels(input: {organizationId: '+json.dumps(org['id'])+'}) { id name displayName service isQueuePaused } }')['channels']
    for row in rows:
     available.append(row)
     if any(norm('افترض كده') in norm(row.get(k,'')) for k in ('name','displayName')):matches.append(row)
   config=Path('config/professional_destinations.json')
   if config.is_file():
    expected=json.loads(config.read_text()).get('buffer_channel_ids',{})
    matches=[r for r in available if r['id'] in expected.values()]
   report['matching_channels']=matches
   report['available_channels']=available
   report['ready']=len(matches)>=1 and len({r['service'] for r in matches})==3 and all(r.get('isQueuePaused') is False for r in matches)
  except Exception as error:report['error_class']=type(error).__name__
 else:report['problem']='Existing fifth-repository BUFFER_API_KEY is not configured'
 Path('work').mkdir(exist_ok=True);Path('work/publishing-connection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 report['status_commit']=StatusStore('.', 'codex/production-v2-audit-status').save(run,attempt,report)
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
