"""Schedule verified complete stickman productions once, preserving every accepted ID."""
import copy,hashlib,json,math,os,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from .media import verify
from .review import bundle

STATE=Path('state/stickman_publications.json')
def now():return datetime.now(timezone.utc).isoformat()
def instant(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('Aware exact publication time required')
    return result.astimezone(timezone.utc)
def checkpoint(data):
    STATE.parent.mkdir(exist_ok=True);STATE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['git','config','user.name','stickman-publication-bot'],check=True)
    subprocess.run(['git','config','user.email','stickman-publication-bot@users.noreply.github.com'],check=True)
    subprocess.run(['git','add',str(STATE)],check=True)
    if subprocess.run(['git','diff','--cached','--quiet']).returncode:
        subprocess.run(['git','commit','-m','Preserve exact stickman publication intent and receipts [skip ci]'],check=True,stdout=subprocess.DEVNULL)
        for _ in range(3):
            pulled=subprocess.run(['git','pull','--rebase','--autostash','origin','main'],stdout=subprocess.DEVNULL).returncode==0
            if pulled and subprocess.run(['git','push','origin','HEAD:refs/heads/main'],stdout=subprocess.DEVNULL).returncode==0:break
        else:raise RuntimeError('Could not persist publication intent; stop without submitting')
def query(text,variables=None):
    import requests
    key=os.environ['BUFFER_API_KEY'].strip()
    response=requests.post('https://api.buffer.com',headers={'Authorization':'Bearer '+key},json={'query':text,**({'variables':variables} if variables is not None else {})},timeout=45)
    response.raise_for_status();data=response.json()
    if data.get('errors'):raise RuntimeError('Buffer query rejected; credentials and response omitted')
    return data['data']
FIELDS='id channelId status dueAt assets {source}'
def lookup(identifier):return query('query { post(input:{id:'+json.dumps(identifier)+'}) {'+FIELDS+'} }')['post']
def matches(post,channel,due,url):
    return post.get('channelId')==channel and post.get('status')=='scheduled' and instant(post['dueAt'])==instant(due) and url in [a.get('source') for a in post.get('assets',[])]
def live_channels(bindings):
    selected={}
    for org in query('query {account {organizations {id}}}')['account']['organizations']:
        rows=query('query {channels(input:{organizationId:'+json.dumps(org['id'])+'}) {id service isQueuePaused}}')['channels']
        for row in rows:
            service=row['service'].lower()
            if bindings.get(service)==row['id']:
                if row.get('isQueuePaused'):raise ValueError('Existing destination queue is paused')
                selected[service]={'channel':row['id'],'organization':org['id']}
    if set(selected)!=set(bindings):raise ValueError('Every existing confirmed destination must be live')
    return selected
def queued(destination,due):
    start=(instant(due)-timedelta(seconds=1)).isoformat();end=(instant(due)+timedelta(seconds=1)).isoformat();rows=[];cursor=None
    for _ in range(20):
        after=',after:'+json.dumps(cursor) if cursor else ''
        result=query('query {posts(first:100'+after+',input:{organizationId:'+json.dumps(destination['organization'])+',filter:{channelIds:['+json.dumps(destination['channel'])+'],dueAt:{start:'+json.dumps(start)+',end:'+json.dumps(end)+'},status:[scheduled,sending,sent]}}){edges{node{'+FIELDS+'}} pageInfo{hasNextPage endCursor}}}')['posts']
        rows.extend(e['node'] for e in result['edges'] or [])
        if not result['pageInfo']['hasNextPage']:return rows
        cursor=result['pageInfo']['endCursor']
    raise ValueError('Bounded queue inspection incomplete')
def publish_one(service,destination,due,url,title,caption,record,persist,read_queue=queued,read_post=lookup,call=query):
    channel=destination['channel']
    if not record.get('id'):
        existing=read_queue(destination,due)
        matching=[p for p in existing if matches(p,channel,due,url)]
        if len(matching)==1:
            record.update(id=matching[0]['id'],phase='reconciled');persist()
        elif existing:raise ValueError('Another or ambiguous post occupies the channel/time; no new submission')
        elif record.get('phase') in ('intent','uncertain'):
            raise ValueError('Unacknowledged previous submission; reconcile instead of sending again')
        else:
            record.update(phase='intent',channel_id=channel,due_at=due,media_url=url,created_at=now());persist()
            metadata={'youtube':{'title':title[:100],'categoryId':'27','privacy':'public','madeForKids':False,'notifySubscribers':False},'facebook':{'type':'post'},'instagram':{'type':'reel','shouldShareToFeed':True}}
            payload={'channelId':channel,'text':caption,'mode':'customScheduled','schedulingType':'automatic','dueAt':due,'assets':[{'video':{'url':url}}],'metadata':{service:metadata[service]}}
            try:
                result=call('mutation CreateCompleteStickman($input:CreatePostInput!){createPost(input:$input){... on PostActionSuccess{post{id dueAt}} ... on MutationError{message}}}',{'input':payload})['createPost']
                if not result.get('post',{}).get('id'):raise RuntimeError('Provider did not acknowledge the complete-film post')
                record.update(id=result['post']['id'],phase='acknowledged',accepted_at=now());persist()
            except Exception:
                record['phase']='uncertain';persist();raise
    actual=read_post(record['id'])
    if actual.get('id')!=record['id'] or not matches(actual,channel,due,url):raise ValueError('Independent same-ID publication lookup failed')
    record.update(phase='verified',status=actual['status'],scheduled_at=actual['dueAt'],verified_at=now());persist()
    return record
def main():
    if os.getenv('GITHUB_REPOSITORY')!='ahmedalsharqwi2-gif/stickman-what-if-shorts' or os.getenv('GITHUB_REF_NAME')!='main':raise ValueError('Only this repository main may schedule its own completed film')
    request=json.loads(Path('.github/publish-completed-stickman.json').read_text());due=request['due_at']
    local=instant(due).astimezone(ZoneInfo('Africa/Cairo'))
    if instant(due)<=datetime.now(timezone.utc) or (local.hour,local.minute,local.second)!=(17,0,0):raise ValueError('Explicit17:00 slot expired; never roll over')
    films=list(Path('work/completed').rglob('candidate-review.mp4'))
    if len(films)!=1:raise ValueError('One complete retained film required')
    film=films[0];output=film.parent;run_dir=output.parent;delivery=run_dir/'professional_motion/delivery'
    if hashlib.sha256(film.read_bytes()).hexdigest()!=request['video_sha256']:raise ValueError('Retained video fingerprint differs')
    story,timing=bundle(delivery,'stickman')
    render=json.loads((output/'render.json').read_text())
    if render.get('review') is not False or render.get('pipeline')!='v2' or render.get('errors') or render.get('start_frame')!=0 or render.get('end_frame')!=math.ceil(timing['duration']*30):raise ValueError('Review samples or partial renders cannot be published')
    evidence=verify(film,profile='stickman')
    if timing['coverage']<.9:raise ValueError('Original narration speech evidence is incomplete')
    bindings=json.loads(Path('config/professional_destinations.json').read_text())
    if bindings.get('profile')!='stickman' or bindings.get('existing_bindings_confirmed_by_user') is not True:raise ValueError('Owner-confirmed existing destinations required')
    destinations=live_channels(bindings['buffer_channel_ids'])
    if set(destinations)!={'youtube','facebook','instagram'}:raise ValueError('Exactly the existing three stickman destinations required')
    data=json.loads(STATE.read_text()) if STATE.exists() else {'episodes':{}}
    key='publication-'+local.date().isoformat();row=data['episodes'].setdefault(key,{'topic_key':story['topic_key'],'story':story,'source_run':request['source_run'],'source_slot':request['source_slot'],'video_sha256':evidence['sha256'],'due_at':due,'posts':{},'accepted_duration_policy':'strictly over90seconds','technical_evidence':evidence})
    if row['video_sha256']!=evidence['sha256'] or row['due_at']!=due:raise ValueError('Existing target is bound to another movie or time')
    checkpoint(data)
    if not row.get('media_url'):
        from .production_release_media import ProductionReleaseUploader
        previous=os.environ.get('PRODUCTION_MEDIA_ID');os.environ['PRODUCTION_MEDIA_ID']='stickman-'+local.date().isoformat()
        try:row['media_url']=ProductionReleaseUploader()._release_asset_url(film)
        finally:
            if previous is None:os.environ.pop('PRODUCTION_MEDIA_ID',None)
            else:os.environ['PRODUCTION_MEDIA_ID']=previous
        checkpoint(data)
    title=story['title'];tags=' '.join('#'+str(t).lstrip('#') for t in story.get('hashtags',[]))
    caption='إفترض كده | '+title+'\n\nقصة افتراضية برسوم متحركة.\n'+tags
    for service,destination in destinations.items():
        for post in queued(destination,due):
            if not matches(post,destination['channel'],due,row['media_url']):raise ValueError('Another video occupies an existing channel/time; no duplicate submission')
    for service,destination in destinations.items():
        record=row['posts'].setdefault(service,{})
        publish_one(service,destination,due,row['media_url'],title,caption,record,lambda:checkpoint(data))
    row.update(status='scheduled',complete=True,verified_at=now());checkpoint(data)
    Path('work/stickman-publication-result.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'scheduled':True,'due_at':due,'movie_url':row['media_url'],'posts':row['posts']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
