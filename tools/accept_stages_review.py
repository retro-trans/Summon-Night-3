"""Bind all independent Terra reviews to source and unchanged draft hashes."""
import argparse,json
from stages_patch import ROOT,FOLDER,read,sha
from prepare_harbor_context import opening_source
def prepare():
    _,rows,_=opening_source();covered=set();inputs={};reviews={};fixes=[];notes=[]
    for name,key,fixkey in [('review_641.json','reviewed_slices','required_corrections'),('review_721.json','reviewed_files','required_corrections'),('review_801.json','reviewed_targets','required_fixes')]:
        path=FOLDER/name;d=read(path);reviews[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        for f in d[key]:
            p=FOLDER/PathName(f['target_file']);digest=sha(p.read_bytes());assert digest==f.get('target_sha256',f.get('target_file_sha256'))
            inputs[str(p.relative_to(ROOT)).replace('\\','/')]=digest;a,b=f['assigned_range'];assert not covered.intersection(range(a,b+1));covered.update(range(a,b+1))
        items=d[fixkey];items=items.values() if isinstance(items,dict) else items
        for f in items:
            n=f['opening_row'];r=rows[n];assert f.get('source_id',r['id'])==r['id']
            assert f.get('source_sha256',r['source_sha256'])==r['source_sha256']
            fixes.append(dict(opening_row=n,id=r['id'],source_sha256=r['source_sha256'],text=f.get('replacement_text',f.get('suggested_text')),reason=f.get('reason',f.get('rationale')),review=name))
        notes.extend(d.get('uncertainties',[]))
    assert covered==set(range(641,1428))
    menu=read(FOLDER/'menu_review.json');assert sha((ROOT/menu['reviewed_target_file']).read_bytes())==menu['reviewed_target_file_sha256']
    reviews['work/translation/en/stages_0.1.12/menu_review.json']=sha((FOLDER/'menu_review.json').read_bytes())
    for identity,f in menu['approved_replacements'].items():
        r=rows[f['opening_row']];assert identity==r['id'] and f['source_sha256']==r['source_sha256']
        fixes.append(dict(opening_row=f['opening_row'],id=identity,source_sha256=r['source_sha256'],text=f['approved_replacement_text'],reason=f['rationale'],review='menu_review.json'))
    for f in fixes:
        if f['opening_row'] in (1213,1215):f['text']='What on earth'
        if f['opening_row'] in (1214,1216):f['text']='is happening...?'
        if f['opening_row'] in range(1213,1217):f['followup']='Independent reviewer terra_cabin_721 confirmed the natural combined wording in follow-up message2026-09-27.'
    assert len({f['opening_row'] for f in fixes})==len(fixes)
    return dict(resource_id='00:00065',reviewed_rows=sorted(covered),draft_inputs_sha256=inputs,review_inputs_sha256=reviews,corrections=fixes,uncertainties=notes,order='Independent meaning corrections first, scripted locked glossary normalization second.',scope='Three complete story sequences through end of Chapter1, all pupil/protagonist branches in main story script.')
def PathName(p):return p.replace('\\','/').rsplit('/',1)[-1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();d=prepare()
    print(json.dumps(dict(mode='write' if a.write else 'dry run',reviewed_count=len(d['reviewed_rows']),corrections=d['corrections'],uncertainties=d['uncertainties']),indent=2))
    if a.write:(FOLDER/'accepted_review.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
