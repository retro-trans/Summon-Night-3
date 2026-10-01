"""Load only source-verified, independently reviewed new battle targets."""
import copy,json,re
from battle_pass_055 import FOLDER,scope,draft_targets,groups
from battle_source_024 import sha,ROOT,source_text
from story_source_054 import target_text
from dialogue_encoding import control_tokens,encode_dialogue

def validate_review(d,start,drafts):
    allrows=scope();end=min(start+80,len(allrows))
    assert d['semantic_complete'] is True and not d.get('blockers')
    assert d['reviewer'] in ('independent_agent','independent_agent_b','independent_agent_c')
    assert d['reviewed_range_inclusive']==[start,end-1] and d['rows_in_slice']==end-start
    seen=set()
    for a,b in d['source_ranges_examined']:
        assert isinstance(a,int) and isinstance(b,int) and 0<=a<=b<len(allrows)
        seen.update(range(a,b+1))
    assert len(seen)==d['rows_examined']
    required=set(range(max(0,start-1),min(len(allrows),end+1)))
    reverse={(r['resource'],r['resource_row']):r['ordered_index'] for r in allrows}
    for number in {r['resource'] for r in allrows[start:end]}:
        for g in groups(number):
            indices={reverse[number,n] for n in g['rows']}
            if indices & set(range(start,end)):required.update(indices)
    assert required<=seen
    bindings=d['draft_inputs_sha256']
    for slice_start in {n//80*80 for n in required}:
        name=f'work/translation/en/battle_0.1.55/slice_{slice_start:04d}.targets.json'
        assert name in bindings,('missing review input',name)
    for name,h in bindings.items():
        path=(ROOT/name).resolve()
        assert path.parent==FOLDER.resolve() and path.name.startswith('slice_') and path.name.endswith('.targets.json')
        assert sha(path.read_bytes())==h,('stale review',name)
    fixes={}
    for fix in d.get('corrections',[]):
        index=fix['ordered_index'];assert start<=index<end and index not in fixes
        row=allrows[index]
        assert (fix['resource'],fix['resource_row'])==(row['resource'],row['resource_row'])
        if 'source_sha256' in fix:assert fix['source_sha256']==row['source_sha256']
        else:
            assert fix['id']==row['id'] and fix['before']==drafts[row['id']]['text']
        fixes[index]=fix['text'] if 'text' in fix else fix['after']
    return fixes

def targets(number,rows,data,reviewed=True):
    drafts,inputs=draft_targets();selected=[r for r in scope() if r['resource']==number]
    assert len(selected)==len(rows)
    result={}
    for r in selected:
        t=copy.deepcopy(drafts[r['id']]);n=r['resource_row']
        for k in ('id','source_offset','source_sha256','source_byte_length','reference_instructions'):
            assert t[k]==rows[n][k],(number,n,k)
        result[n]=t
    if reviewed:
        relevant={r['ordered_index']//80*80 for r in selected}
        for start in sorted(relevant):
            path=FOLDER/f'review_{start:04d}.json';d=json.loads(path.read_text('utf8'))
            fixes=validate_review(d,start,drafts)
            inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
            for index,text in fixes.items():
                row=scope()[index]
                if row['resource']==number:result[row['resource_row']]['text']=text
    aliases=json.loads((ROOT/'work/glossary/battle_0.1.24.json').read_text())['aliases']
    for n,t in result.items():
        text=t['text'].replace('Mr. Whiskers','Beardy')
        for old,new in aliases.items():text=re.sub(r'(?<![A-Za-z])'+re.escape(old)+r'(?![A-Za-z])',new,text)
        t['text']=target_text(text)
        assert t['text'].strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff]',t['text'])
        original=source_text(rows[n],data)
        assert control_tokens(t['text'])==control_tokens(original)
        encode_dialogue(t['text'],original)
    for name in ('work/glossary/story_additions_0.1.54.json','work/glossary/battle_0.1.55.json','work/glossary/battle_0.1.24.json','work/glossary/character_reference_sn6_vita.json','work/glossary/terminology_preferences.json','tools/battle_accept_055.py','tools/battle_pass_055.py','tools/battle_source_024.py','tools/battle_compiler_055.py'):
        inputs[name]=sha((ROOT/name).read_bytes())
    return result,inputs
