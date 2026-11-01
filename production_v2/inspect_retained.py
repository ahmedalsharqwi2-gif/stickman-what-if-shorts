"""Read retained draft evidence; never contacts text, voice or social providers."""
import io,json,os,zipfile
from pathlib import Path,PurePosixPath
from .diagnose import Reader
from .export_review import context,StatusStore
def main():
    request=json.loads(Path('.github/production-v2-inspect-request.json').read_text())
    profile=request['profile'];repository,run,attempt,source=context(profile)
    target=str(int(request['target_run']));reader=Reader(repository,os.environ['GITHUB_TOKEN'])
    matches=[a for a in reader.json('/actions/runs/'+target+'/artifacts').get('artifacts',[]) if a['name']==request['artifact_name'] and not a.get('expired')]
    if len(matches)!=1:raise ValueError('Unique exact retained artifact required')
    evidence={}
    with zipfile.ZipFile(io.BytesIO(reader.archive('/actions/artifacts/'+str(matches[0]['id'])+'/zip'))) as archive:
        for item in archive.infolist():
            path=PurePosixPath(item.filename)
            if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe retained archive')
            if path.name in ('last-draft.json','story.json','narration-continuation.json','generation-failure.json','narration.source.json'):
                if item.file_size>512*1024:raise ValueError('Retained text exceeds limit')
                if path.name in evidence:raise ValueError('Ambiguous retained text')
                evidence[path.name]=json.loads(archive.read(item))
    report={'profile':profile,'stage':'success','kind':'retained_episode_inspection','target_run':target,'provider_requests':0,'posts_created':False,'evidence':evidence}
    StatusStore('.', 'codex/production-v2-diagnostics').save(run,attempt,report)
    print(json.dumps({'stage':'success','retained_names':list(evidence),'provider_requests':0}))
if __name__=='__main__':main()
