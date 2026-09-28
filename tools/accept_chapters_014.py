"""Bind completed meaning-review records to exact drafts; preview by default."""
import argparse,json
from pathlib import Path
from chapter_patch_014 import source,targets,FOLDER
from chapter_source_014 import MAIN_TAIL_START
from stages_patch import sha
from sn3_archive import ROOT
from build_chapters_014 import RESOURCES

def mapped(number,folder,n):
    if folder.name=='common_0180':
        if number in (134,157):return n if n<464 else n-2149 if n>=2613 else None
        if number in (180,203,226):return n
        return n if n<11 else None
    return n+MAIN_TAIL_START.get(number,0)

def prepare_review(number):
    _,rows,data=source(number)
    selected,all_inputs=targets(number,rows,data,False,False)
    drafts={p:h for p,h in all_inputs.items() if Path(p).name.startswith('slice_') and p.endswith('.targets.json')}
    own=FOLDER/f'{number:04d}';common=FOLDER/'common_0180'
    records=[];independent=set();self_checked=set();fixes={};inputs={};notes=[];historical={}
    for folder in (own,common):
        paths=sorted(folder.glob('translator_self_review*.json'))
        if folder==own:
            paths+=sorted(folder.glob('review_meaning_*.json'))
            if (folder/'independent_review.json').exists():paths.append(folder/'independent_review.json')
        for path in paths:
            doc=json.loads(path.read_text(encoding='utf8'))
            is_independent=doc.get('review_type')=='independent_meaning_review'
            if is_independent:assert doc['semantic_complete']
            else:assert 'self' in str(doc.get('review_status',doc.get('review_type',doc.get('status','')))),path
            hashes=dict(doc.get('draft_inputs_sha256',{}))
            for s in doc.get('reviewed_slices',[]):hashes[s['target_file']]=s['target_file_sha256']
            assert hashes,('review has no bindings',path)
            coverage=set()
            for name,h in hashes.items():
                input_path=ROOT/name
                if not input_path.name.startswith('slice_') or not input_path.name.endswith('.targets.json'):
                    historical.setdefault(str(path.relative_to(ROOT)).replace('\\','/'),{})[name]=h
                    continue
                assert sha(input_path.read_bytes())==h,('stale semantic draft review',path,name)
                assert input_path.parent==folder,(path,name)
                inputs[name]=h
                for t in json.loads(input_path.read_text(encoding='utf8'))['translations'].values():
                    n=mapped(number,folder,t['resource_row'])
                    if n is not None:coverage.add(n)
            assert coverage<=set(selected)
            (independent if is_independent else self_checked).update(coverage)
            for fix in doc.get('corrections',[]):
                n=mapped(number,folder,fix['resource_row'])
                if n is None:continue
                assert n in coverage and fix['source_sha256']==rows[n]['source_sha256']
                assert n not in fixes or fixes[n]['text']==fix['text'],('conflicting reviews',number,n)
                fixes[n]=dict(fix,resource_row=n)
            name=str(path.relative_to(ROOT)).replace('\\','/');inputs[name]=sha(path.read_bytes())
            records.append(dict(path=name,independent=is_independent,covered_rows=len(coverage)))
            notes.extend(doc.get('uncertainties',doc.get('remaining_uncertainties',[])))
    assert independent|self_checked==set(selected),('unreviewed rows',number,sorted(set(selected)-independent-self_checked)[:20])
    # Old machine drafts may only pass through an independent meaning review.
    for name in drafts:
        path=ROOT/name;doc=json.loads(path.read_text(encoding='utf8'))
        if 'machine' in str(doc.get('status','')).lower():
            for t in doc['translations'].values():
                n=mapped(number,path.parent,t['resource_row'])
                if n is not None:assert n in independent,(number,n,'unreviewed machine draft')
    return dict(version='0.1.14',resource_id=f'00:{number:05d}',review_type='mixed_independent_and_author_meaning_checks',reviewed_rows=sorted(selected),independently_reviewed_rows=sorted(independent),author_only_rows=sorted(self_checked-independent),draft_inputs_sha256=drafts,review_inputs_sha256=inputs,corrections=[fixes[n] for n in sorted(fixes)],review_records=records,historical_validation_inputs_not_reused=historical,remaining_uncertainties=notes,limitations=['Author self-check is not an independent second pass.','Structural and source-binding checks do not prove in-game playthrough correctness.','Earlier author compiler checks are historical; final build reruns and binds the current compiler separately.'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resources',type=int,nargs='*');p.add_argument('--write',action='store_true');a=p.parse_args()
    results=[]
    for n in a.resources or RESOURCES:
        d=prepare_review(n);results.append((n,d))
        print(json.dumps(dict(mode='write' if a.write else 'dry-run',resource=n,rows=len(d['reviewed_rows']),independent=len(d['independently_reviewed_rows']),author_only=len(d['author_only_rows']),corrections=len(d['corrections']),sample=d['corrections'][:2]),ensure_ascii=False),flush=True)
    if a.write:
        for n,d in results:(FOLDER/f'{n:04d}'/'accepted_review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
