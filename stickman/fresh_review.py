"""Fresh, narrated, review-only orbital cabin film. Never posts to social accounts."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid
import wave
from .orbital_story import story as authored_story
from .alignment import measured_timing
from .candidate import render,validate_timing


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2))

def align(story,wav,out):
    from faster_whisper import WhisperModel
    with wave.open(str(wav)) as audio:duration=audio.getnframes()/audio.getframerate()
    if not 120<=duration<180:raise ValueError('Measured narration must be120 to under180 seconds; no padding or speed changes')
    transcripts=[]
    for name in ('small','medium'):
        model=WhisperModel(name,device='cpu',compute_type='int8',cpu_threads=2)
        segments,_=model.transcribe(str(wav),language='ar',word_timestamps=True,beam_size=5,vad_filter=False)
        words=[{'text':w.word.strip(),'start':float(w.start),'end':float(w.end)} for segment in segments for w in segment.words or []]
        transcripts.append((name,words));write(out/('asr-'+name+'.json'),{'recognized_words':words});del model
        try:
            timing=measured_timing(story,duration,transcripts)
            if timing['coverage']<.9:raise ValueError('Measured speech coverage below90percent')
            break
        except ValueError:
            if name=='medium':raise
    timing.update(profile='stickman',topic_key=story['topic_key'],audio_sha256=sha(wav),
                  story_sha256=hashlib.sha256(json.dumps(story,ensure_ascii=False,sort_keys=True).encode()).hexdigest())
    return timing


def mix_film(rendered,wav,timing,out):
    from .score import build
    duration=timing['duration']
    build(duration,[scene['start'] for scene in timing['scenes']],out,'stickman')
    def ff(*args):subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-y',*map(str,args)],check=True)
    ff('-i',wav,'-af','loudnorm=I=-16:TP=-2:LRA=7,aresample=48000',out/'voice.wav')
    ff('-i',out/'score.wav','-af','loudnorm=I=-30:TP=-5:LRA=9,aresample=48000',out/'music.wav')
    graph=('[1:a]aformat=channel_layouts=stereo,asplit=2[v][control];'
           '[2:a][control]sidechaincompress=threshold=.035:ratio=5:attack=12:release=250[ducked];'
           '[3:a]volume=.4[fx];[v][ducked][fx]amix=inputs=3:duration=first:normalize=0,alimiter=limit=.88:latency=1[mix]')
    film=out/'candidate-review.mp4'
    if film.exists():raise FileExistsError('Existing completed candidate is retained')
    ff('-i',rendered,'-i',out/'voice.wav','-i',out/'music.wav','-i',out/'sfx.wav','-filter_complex',graph,
       '-map','0:v:0','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','192k','-t',duration,'-movflags','+faststart',film)
    return film

def run(run_dir,ledger_path,*,git_state=False,tts=None,asr=None,renderer=None,mixer=None,verifier=None):
    # Existing secret of THIS repository only. Nothing is created before this check.
    if not (os.getenv('GEMINI_TTS_API_KEY') or os.getenv('GEMINI_API_KEY')):raise RuntimeError('Existing fifth-repository Gemini TTS secret is required')
    repo=Path(__file__).resolve().parents[1]
    if os.getenv('GITHUB_REPOSITORY') not in (None,'ahmedalsharqwi2-gif/stickman-what-if-shorts'):
        raise PermissionError('Do not use another repository credentials for this channel')
    out=Path(run_dir).resolve();ledger_path=Path(ledger_path).resolve()
    if out.exists() and any(out.iterdir()):raise FileExistsError('Existing candidate output is retained')
    if out==repo or any(out.is_relative_to(repo/name) for name in ('stickman','config','state','assets')):
        raise ValueError('Use a fresh isolated review directory')
    if ledger_path.is_relative_to(out):raise ValueError('The shared ledger must be outside the run directory')
    from production_v2.ledger import Ledger
    from production_v2.media import verify
    persist=None
    if git_state:
        from production_v2.durable import GitLedgerStore
        store=GitLedgerStore(repo)
        with store.restore(ledger_path):pass
        persist=store.checkpoint
    if tts is None:
        from voice_provider.client import generate
        tts=generate
    asr=asr or align;renderer=renderer or render;mixer=mixer or mix_film;verifier=verifier or verify
    out.mkdir(parents=True,exist_ok=True);delivery=out/'professional_motion/delivery';delivery.mkdir(parents=True)
    output=out/'output';output.mkdir()
    story=authored_story();slot='candidate-stickman-'+uuid.uuid4().hex
    storyfile=delivery/'story.json';write(storyfile,story)
    # Canonical story bytes for renderer/ASR; file hash separately proves artifact identity.
    due=datetime.now(timezone.utc).isoformat()
    with Ledger(ledger_path) as ledger:
        ledger.import_legacy(repo)
        ledger.reserve(slot,story['topic_key'],due,story)
        with ledger.transaction():ledger.event('candidate_story',{'slot':slot,'profile':'stickman','story':story,'run_dir':str(out)})
        if persist:persist(ledger)
        try:
            wav=delivery/'narration.wav';tts(' '.join(s['narration'] for s in story['scenes']),str(wav))
            timing=asr(story,wav,delivery);validate_timing(story,timing,timing['duration'],wav);write(delivery/'timing.json',timing)
            rendered=output/'rendered-review.mp4'
            renderer(rendered,duration=timing['duration'],fps=24,narration=wav,visual_review=False,story=story,timing=timing)
            film=mixer(rendered,wav,timing,output)
            evidence=verifier(film)
            evidence.update(profile='stickman',topic_key=story['topic_key'],pipeline='v2',review_only=True,publishable=False,
                fresh_topic_verified=True,story_sha256=sha(storyfile),narration_sha256=sha(wav),measured_caption_coverage=timing['coverage'],
                artistic_review='Technical ASR/media checks passed; actual visual/listening review remains required')
            write(output/'candidate-verification.json',evidence)
            result={'slot':slot,'profile':'stickman','topic_key':story['topic_key'],'duration':timing['duration'],'story_sha256':sha(storyfile),'audio_sha256':sha(wav),'generated_in_isolation':True,'fresh_topic_verified':True,'publishable':False}
            write(out/'generation-verification.json',result)
            with ledger.transaction():ledger.event('candidate_generated',result)
            if persist:persist(ledger)
            return result
        except BaseException as error:
            failure={'slot':slot,'profile':'stickman','error_class':type(error).__name__,'reservation_retained':True,'publishable':False}
            write(out/'generation-failure.json',failure)
            with ledger.transaction():ledger.event('candidate_generation_failed',failure)
            if persist:persist(ledger)
            raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-dir',required=True);p.add_argument('--ledger',required=True);p.add_argument('--git-state',action='store_true');a=p.parse_args()
    print(json.dumps(run(a.run_dir,a.ledger,git_state=a.git_state),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
