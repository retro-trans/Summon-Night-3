"""Bind independent meaning reviews to complete chapter source coverage."""
import argparse,json
from chapter_patch import FOLDER,expected_rows,read,sha,ROOT
from chapter_source import chapter_source

def prepare(number):
    folder=FOLDER/f'{number:04d}';_,rows,_=chapter_source(number)
    covered=set();inputs={};reviews={};fixes={};notes=[]
    def draft(name,digest,span=None):
        path=folder/name.replace('\\','/').rsplit('/',1)[-1]
        assert sha(path.read_bytes())==digest,('stale review',path)
        inputs[str(path.relative_to(ROOT)).replace('\\','/')]=digest
        doc=read(path);actual={t['resource_row'] for t in doc['translations'].values()}
        reviewed=set(range(span[0],span[1]+1)) if span is not None else actual
        assert reviewed <= actual, ('review range outside draft',path,span)
        covered.update(reviewed)
    def fix(n,text,reason,name):
        n=int(n);r=rows[n];item=dict(resource_row=n,id=r['id'],source_sha256=r['source_sha256'],text=text,reason=reason,review=name)
        if n in fixes:assert fixes[n]['text']==text,('conflicting reviews',n,fixes[n],item)
        fixes[n]=item
    for path in sorted(folder.glob('review_*.json')):
        doc=read(path);assert doc['resource_id']==f'00:{number:05d}'
        if doc.get('review_type')=='structural_only' or doc.get('semantic_complete') is False:continue
        reviews[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        if 'relevant_draft' in doc:
            f=doc['relevant_draft']
            assert sha((folder/f['target_file']).read_bytes())==f['target_file_sha256'],('stale addendum',path)
        for key in ('reviewed_slices','reviewed_targets','reviewed_files'):
            for f in doc.get(key,[]):draft(f.get('target_file',f.get('path')),f.get('target_sha256',f.get('target_file_sha256',f.get('sha256'))),f.get('assigned_range'))
        for name,digest in doc.get('target_files_sha256',{}).items():draft(name,digest)
        for name,digest in doc.get('reviewed_target_file_hashes',{}).items():
            assert sha((folder/name).read_bytes())==digest
        for key in ('required_corrections','required_fixes','corrections','meaning_corrections'):
            items=doc.get(key,[]);items=items.values() if isinstance(items,dict) else items
            for f in items:
                n=f['resource_row'];r=rows[n]
                assert f.get('source_id',r['id'])==r['id'] and f.get('source_sha256',r['source_sha256'])==r['source_sha256']
                if 'suggested_group_replacements' in f:
                    for n,text in f['suggested_group_replacements'].items():fix(n,text,f['rationale'],path.name)
                else:fix(n,f.get('replacement_text',f.get('suggested_text',f.get('text'))),f.get('reason',f.get('rationale')),path.name)
        notes.extend(doc.get('uncertainties',[]))
    assert covered==expected_rows(number,rows),('unreviewed',number,sorted(expected_rows(number,rows)-covered))
    assert inputs=={str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for p in folder.glob('slice_*.targets.json')}
    return dict(resource_id=f'00:{number:05d}',reviewed_rows=sorted(covered),draft_inputs_sha256=inputs,review_inputs_sha256=reviews,corrections=list(fixes.values()),uncertainties=notes,order='Independent meaning corrections first, locked glossary spelling normalization second.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resources',type=int,nargs='+');p.add_argument('--write',action='store_true');a=p.parse_args()
    for number in a.resources:
        d=prepare(number);print(json.dumps(dict(mode='write' if a.write else 'dry run',resource=number,rows=len(d['reviewed_rows']),corrections=d['corrections'],uncertainties=d['uncertainties']),indent=2))
        if a.write:(FOLDER/f'{number:04d}'/'accepted_review.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
