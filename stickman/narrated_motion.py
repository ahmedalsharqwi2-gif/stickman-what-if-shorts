"""Bind existing character choreography to measured narration, preserving the reserved script."""
from .story_actions import frame as stage_frame, state_at
# The reserved narration explains freefall, phone drift, wall contact, air-running,
# a friend's rope, a controlled pull, and returning. It is not the silent phone-catch script.
BEATS=(0,0,1,2,3,4,5,7)
def scene_progress(t,duration,timing):
 index=max(i for i,s in enumerate(timing['scenes']) if s['start']<=max(0,min(t,duration)))
 scene=timing['scenes'][index]
 progress=max(0,min(.999999,(t-scene['start'])/(scene['end']-scene['start'])))
 return index,progress
def state(t,duration,timing):
 index,progress=scene_progress(t,duration,timing)
 return state_at('orbital_phone',(BEATS[index]+progress)*4,32)
def frame(t,duration,story,timing):
 if story.get('topic_key')!='orbital-cabin-freefall-v2':
  raise ValueError('No narrated motion contract for this reserved subject')
 index,progress=scene_progress(t,duration,timing)
 return stage_frame('orbital_phone',(BEATS[index]+progress)*4,32,story=story,timing=timing,scene_index=index,actual_time=t)
