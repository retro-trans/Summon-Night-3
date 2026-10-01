"""Read-only coverage and draft-discipline audit for remaining story work."""
import json
from collections import Counter
from story_source_054 import FOLDER
from chapter_source_014 import load
from dialogue_encoding import control_tokens

def audit():
    scope=json.loads((FOLDER/'scope.json').read_text('utf8'))
    summary=Counter();details=[]
    for entry in scope['resources']:
        number=entry['resource'];new=entry['new_translation_range_half_open']
        expected=set(range(*new)) if new else set()
        summary['new_fragments_in_scope']+=len(expected)
        summary['shared_occurrences']+=sum(s['end']-s['start'] for s in entry['shared_segments'])
        summary['internal_ascii_rows_preserved']+=len(entry['preserved_internal_ascii_rows'])
        seen={};legacy=[]
        paths=sorted((FOLDER/f'{number:04d}').glob('slice_*.targets.json'))
        if paths:resource,rows,data=load(number)
        for path in paths:
            doc=json.loads(path.read_text('utf8'));selected=doc['translations'];ns=sorted(t['resource_row'] for t in selected.values())
            assert doc['source_sha256']==entry['source_sha256']
            assert set(ns)<=expected and ns==list(range(ns[0],ns[-1]+1)),path
            for identity,t in selected.items():
                n=t['resource_row'];assert n not in seen,(number,n,'overlap')
                r=rows[n];assert identity==r['id']
                for key in ('source_sha256','source_offset','source_byte_length','reference_instructions'):assert t[key]==r[key],(number,n,key)
                original=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
                assert control_tokens(original)==control_tokens(t['text']),(number,n,'controls')
                seen[n]=str(path.name)
            examined=doc['source_ranges_examined']
            context={n for group in examined for n in (range(group[0],group[1]+1) if len(group)==2 else group)}
            compliant=(len(ns)==80 or ns[-1]==entry['source_fragments']-1) and 'uncertainties' in doc and 'preserved_source_omissions' in doc and (ns[0]==0 or ns[0]-1 in context) and (ns[-1]+1==entry['source_fragments'] or ns[-1]+1 in context)
            if not compliant:legacy.append(path.name)
            summary['slices_with_updated_workflow_metadata' if compliant else 'legacy_slices_pending_updated_review']+=1
        summary['new_fragments_drafted']+=len(seen)
        summary['new_fragments_remaining']+=len(expected-set(seen))
        summary['resources_with_drafts']+=bool(seen)
        if seen and set(seen)==expected:summary['resources_with_complete_new_draft']+=1
        if seen:details.append(dict(resource=number,drafted=len(seen),remaining=len(expected-set(seen)),legacy_slices=len(legacy),legacy_examples=legacy[:2]))
    return dict(status='Draft coverage only; independent review and gameplay checks remain',counts=dict(summary),resources=details)
if __name__=='__main__':print(json.dumps(audit(),indent=2))

