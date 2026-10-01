"""Apply a reviewed meaning correction, followed by name normalization; dry-run default."""
import argparse,json
from pathlib import Path
from story_source_054 import target_text,FOLDER
from stages_patch import sha
from dialogue_encoding import control_tokens
from sn3_archive import ROOT

def apply(path,write=False):
    review=json.loads(path.read_text('utf8'))
    target=ROOT/review['target_file']
    assert target.resolve().is_relative_to(FOLDER.resolve())
    raw=target.read_bytes();assert sha(raw)==review['target_file_sha256'],'Stale target review'
    doc=json.loads(raw);lookup={t['resource_row']:t for t in doc['translations'].values()}
    lo,hi=review['reviewed_rows']['range_inclusive'];changes=[]
    for fix in review['corrections']:
        n=fix['resource_row'];assert lo<=n<=hi
        t=lookup[n];assert t['source_sha256']==fix['source_sha256']
        text=target_text(fix['text']);assert control_tokens(text)==control_tokens(t['text'])
        changes.append(dict(resource_row=n,before=t['text'],after=text,reason=fix['reason']))
        t['text']=text
    out=(json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    receipt=target.parent/(path.stem.replace('review_meaning_','applied_review_')+'.json')
    record=dict(review_file=str(path.relative_to(ROOT)).replace('\\','/'),review_sha256=sha(path.read_bytes()),target_file=review['target_file'],target_before_sha256=sha(raw),target_after_sha256=sha(out),reviewed_rows=review['reviewed_rows'],corrections_applied=changes,remaining_uncertainties=review['uncertainties'],status='Reviewer corrections applied; names normalized afterward. Whole-resource acceptance pending.')
    print(json.dumps(dict(mode='write' if write else 'dry-run',target=review['target_file'],changes=changes,remaining_uncertainties=review['uncertainties']),ensure_ascii=False,indent=2))
    if write:
        assert not receipt.exists()
        target.write_bytes(out);receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('review');p.add_argument('--write',action='store_true');a=p.parse_args()
    apply((ROOT/a.review).resolve(),a.write)
