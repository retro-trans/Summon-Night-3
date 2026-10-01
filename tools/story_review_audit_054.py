"""Audit independent review proof; never marks a translation accepted."""
import json
from collections import defaultdict,Counter
from pathlib import Path
from story_source_054 import FOLDER
from stages_patch import sha
from sn3_archive import ROOT

def audit(number=None):
    counts=Counter(); errors=[]; details=[]
    for folder in sorted(FOLDER.iterdir()):
        if not folder.is_dir() or not folder.name.isdigit(): continue
        if number is not None and int(folder.name) != number: continue
        edges=defaultdict(lambda:defaultdict(set)); applied={}; covered=set(); pending=set()
        for p in folder.glob('applied_review_*.json'):
            r=json.loads(p.read_text('utf8')); proof=ROOT/r['review_file']
            if not proof.exists() or sha(proof.read_bytes())!=r['review_sha256']:
                errors.append(f'{p.name}: review proof changed');continue
            review=json.loads(proof.read_text('utf8'))
            if review['target_file_sha256']!=r['target_before_sha256'] or review['target_file']!=r['target_file']:
                errors.append(f'{p.name}: receipt binding mismatch');continue
            edges[r['target_file']][r['target_before_sha256']].add(r['target_after_sha256'])
            applied[r['review_sha256']]=r
        normal=folder/'name_normalization.json'
        if normal.exists():
            record=json.loads(normal.read_text('utf8'))
            for name,h in record['glossary_inputs_sha256'].items():
                if sha((ROOT/name).read_bytes())!=h:errors.append(f'{normal}: glossary input changed: {name}')
            for item in record['files']:
                edges[item['target_file']][item['target_before_sha256']].add(item['target_after_sha256'])
        for p in sorted(folder.glob('review_meaning_*.json')):
            raw=p.read_bytes(); r=json.loads(raw); target=ROOT/r['target_file']
            if not target.exists():errors.append(f'{p}: missing target');continue
            current=sha(target.read_bytes()); doc=json.loads(target.read_text('utf8'))
            reachable={r['target_file_sha256']}; todo=list(reachable)
            while todo:
                for h in edges[r['target_file']].get(todo.pop(),set())-reachable:
                    reachable.add(h);todo.append(h)
            lo,hi=r['reviewed_rows']['range_inclusive']; selected=set(range(lo,hi+1))
            lookup={t['resource_row']:t for t in doc['translations'].values()}
            valid=current in reachable and r['source_sha256']==doc['source_sha256'] and selected<=lookup.keys() and len(selected)==r['reviewed_rows']['count']
            for fix in r.get('corrections',[]):
                valid=valid and fix['resource_row'] in selected and lookup.get(fix['resource_row'],{}).get('source_sha256')==fix['source_sha256']
            if not valid: errors.append(f'{p.relative_to(FOLDER)}: stale or invalid binding');continue
            counts['valid_review_files']+=1
            counts['reported_uncertainties']+=len(r.get('uncertainties',[]))
            if r.get('semantic_complete') is not True:
                counts['review_files_pending_semantic_completion']+=1
                pending.update(selected)
                continue
            if r.get('corrections') and sha(raw) not in applied:
                pending.update(selected);counts['review_files_with_unapplied_fixes']+=1
            else:covered.update(selected)
        # A newer unresolved correction cannot be hidden by overlapping clean proof.
        covered-=pending
        if covered or pending:details.append(dict(resource=int(folder.name),reviewed_rows_with_current_proof=len(covered),rows_awaiting_correction=len(pending-covered)))
        counts['reviewed_rows_with_current_proof']+=len(covered)
        counts['rows_awaiting_correction']+=len(pending-covered)
    return dict(status='Proof integrity and coverage only; does not replace semantic acceptance or gameplay testing',counts=dict(counts),errors=errors,resources=details)
if __name__=='__main__':print(json.dumps(audit(),indent=2))
