"""Verbatim dialogue turns and actor cues bound to independently recognized speech."""
import copy,re
from .alignment import anchor_chain,recognized_key,norm
from .narration_style import validate_unnamed_story
DIALOGUE_DIRECTION='''الحلقة حوار طبيعي بين شخصيتين بلا أسماء منطوقة، وليست راويا يصف قام وفعل. الشخصية a فضولية ومندفعة، والشخصية b هادئة بردود مصرية ساخرة قصيرة؛ يتعاونان ويختلفان داخل نفس فرضية ماذا لو. ابدأ بالموقف الغريب أو سؤال مباشر فورًا. لكل مشهد3–5 أدوار حوارية قصيرة،4–16 كلمة للدور، ويتكلم الاثنان في كل مشهد. speaker هو a أو b في البيانات فقط؛ لا تكتب الأول قال أو الثاني رد أو اسم الشخصية داخل text. اجعل مجموع كلام المشاهد الثمانية270–340 كلمة دون حشو أو موعظة. narration يجب أن يكون ضم نصوص الأدوار بالترتيب نفسه، بلا أسماء أو تعليمات أداء منطوقة. الأحداث تتغير بصريًا مع الحوار، والكوميديا تأتي من المحاولة والنتيجة ورد الفعل. يمكنك استخدام أنا وإنت وإحنا بشكل طبيعي، ولا تكرر كلمة صاحبنا أو بطلنا. حافظ على ترتيب مراحل فرضية الحلقة والاشياء التي يستطيع الرسام إظهارها.'''
def schema_for(base):
 schema=copy.deepcopy(base);scene=schema['properties']['scenes']['items']
 scene['properties']['turns']={'type':'ARRAY','minItems':3,'maxItems':5,'items':{'type':'OBJECT','properties':{'speaker':{'type':'STRING','enum':['a','b']},'text':{'type':'STRING','description':'4–16 Arabic words; literal spoken dialogue only, no speaker labels or stage directions'}},'required':['speaker','text']}}
 scene['required'].append('turns');return schema
def prepare_draft(draft):
 story=copy.deepcopy(draft)
 for scene in story.get('scenes',[]):
  turns=scene.get('turns',[])
  if not 3<=len(turns)<=5 or {t.get('speaker') for t in turns}!={'a','b'}:raise ValueError('Each scene requires a real exchange between two unnamed speakers')
  for t in turns:
   t['text']=' '.join(t.get('text','').split())
   if not 3<=len(t.get('text','').split())<=20 or re.search(r'^(?:الأول|الثاني|الشخصية|Speaker|a:|b:)\s*[:：]?',t['text'],re.I):raise ValueError('Dialogue must contain literal concise speech, without spoken role labels')
  # The exact chosen turns are authoritative. Keep the untouched provider draft separately.
  scene['narration']=' '.join(' '.join(t['text'].split()) for t in turns)
 story['dialogue_enabled']=True;story['dialogue_audio_policy']='two distinct Gemini voices; speaker IDs are unspoken metadata'
 validate_unnamed_story(story);return story
def flatten(story):return [dict(t) for scene in story['scenes'] for t in scene.get('turns',[])]
def attach_timing(story,timing,transcripts):
 expected=' '.join(s['narration'] for s in story['scenes']).split();duration=timing['duration']
 anchors,_=anchor_chain(expected,duration,transcripts,recognized_key,join=True)
 # ASR may split Arabic clitics. Recover literal character anchors, never estimated durations.
 if len(anchors)/len(expected)<.9:
  from difflib import SequenceMatcher
  pieces=[recognized_key(w) for w in expected];script=''.join(pieces);ranges=[];pos=0
  for token in pieces:ranges.append((pos,pos+len(token)));pos+=len(token)
  for model,raw in transcripts:
   actual='';owners=[]
   for i,w in enumerate(raw):
    token=recognized_key(w['text']);actual+=token;owners.extend([i]*len(token))
   mapping={}
   for block in SequenceMatcher(None,script,actual,autojunk=False).get_matching_blocks():
    if block.size<4:continue
    for i in range(block.size):mapping[block.a+i]=owners[block.b+i]
   for i,(a,b) in enumerate(ranges):
    if i in anchors or b<=a:continue
    indices=sorted({mapping[k] for k in range(a,b) if k in mapping})
    if sum(k in mapping for k in range(a,b))/(b-a)<.85 or not indices or indices[-1]-indices[0]>5:continue
    first,last=raw[indices[0]],raw[indices[-1]]
    if 0<=first['start']<last['end']<=duration+.1:anchors[i]={'start':first['start'],'end':last['end']}
 cursor=0;turns=[];captions=[]
 for scene_index,scene in enumerate(story['scenes']):
  measured=[]
  for turn in scene['turns']:
   words=turn['text'].split();stop=cursor+len(words);first=[anchors[i] for i in range(cursor,min(cursor+4,stop)) if i in anchors];last=[anchors[i] for i in range(max(cursor,stop-4),stop) if i in anchors]
   if not first or not last:raise ValueError('Dialogue turn has no independently measured speech boundary; retained voice must not be regenerated')
   item={**turn,'start':min(w['start'] for w in first),'end':max(w['end'] for w in last),'timing_method':'independent ASR anchors, not phoneme synchronization'}
   if turns and item['start']<turns[-1]['start']:raise ValueError('Dialogue speaker order conflicts with actual recognized speech')
   measured.append(item);turns.append(item)
   for start in range(cursor,stop,6):
    end=min(start+6,stop);points=[anchors[i] for i in range(start,end) if i in anchors]
    if not points:raise ValueError('Dialogue caption has no measured speech')
    captions.append({'speaker':turn['speaker'],'text':' '.join(expected[start:end]),'start':min(w['start'] for w in points),'end':max(w['end'] for w in points)})
   cursor=stop
  timing['scenes'][scene_index]['dialogue_turns']=measured
 for a,b in zip(turns,turns[1:]):
  if a['end']>b['start']:a['end']=b['start']
 if any(t['end']<=t['start'] for t in turns):raise ValueError('Dialogue turns overlap without an audible boundary')
 for a,b in zip(captions,captions[1:]):
  if a['end']>b['start']:a['end']=b['start']
 timing['dialogue_turns']=turns;timing['caption_groups']=captions;timing['dialogue_timing_verified']=True
 return timing
