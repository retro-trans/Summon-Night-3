"""Remaining battle-event translation: source-bound slices, no saved Japanese."""
import argparse, collections, copy, json, re, struct
from functools import lru_cache
from battle_source_024 import load, source_text, sha, ROOT, catalog
from dialogue_encoding import control_tokens, encode_dialogue
from story_source_054 import target_text
from sn3_vm import instructions

FOLDER=ROOT/'work/translation/en/battle_0.1.55'

@lru_cache(None)
def scope():
    m=json.loads((ROOT/'work/output/0.1.54/manifest.json').read_text('utf8'))
    covered={r['index'] for r in m['battle024']}
    rows=[]
    for r in catalog()['resources']:
        if r['bank']!='01.DAT' or not r['strings'] or r['path'][0] in covered:continue
        number=r['path'][0]
        for n,row in enumerate(sorted(r['strings'],key=lambda x:min(x['reference_instructions']))):
            rows.append(dict(row,resource=number,resource_row=n,ordered_index=len(rows)))
    assert len(rows)==642 and len({r['resource'] for r in rows})==27
    return rows

@lru_cache(None)
def source(number):return load(number)

def groups(number):
    _,rows,data=source(number);code=instructions(data);at={i['offset']:i for i in code}
    destinations={i['target_word']*2 for i in code if 'target_word' in i}|{struct.unpack_from('<I',data,16)[0]*2}
    done=set()
    for n,row in enumerate(rows):
        if n in done:continue
        start=row['reference_instructions'][0];ns=[n]
        while ns[-1]+1<len(rows) and rows[ns[-1]+1]['reference_instructions']==[start+8*len(ns)] and start+8*len(ns) not in destinations:ns.append(ns[-1]+1)
        for k in ns:
            p=rows[k]['reference_instructions'][0]
            assert at[p+4]['opcode']==8 and at[p+4]['operands']==[0x20c7]
        tail=at[start+8*len(ns)]
        done.update(ns)
        yield dict(rows=ns,speaker_operand=dict(mode=tail['mode'],high=tail['high'],operands=tail['operands']))

def preview(start,count=80,context=8):
    allrows=scope();lo=max(0,start-context);hi=min(len(allrows),start+count+context)
    selected={r['resource'] for r in allrows[lo:hi]}
    reverse={(r['resource'],r['resource_row']):r for r in allrows}
    for number in sorted(selected):
        for g in groups(number):
            indices=[reverse[number,n]['ordered_index'] for n in g['rows']]
            if max(indices)<lo or min(indices)>=hi:continue
            print(json.dumps(dict(resource=number,indices=indices,speaker_operand=g['speaker_operand'],
                source=[source_text(reverse[number,n],source(number)[2]) for n in g['rows']]),ensure_ascii=False))

def save(start,lines,examined,*,uncertainties,omissions,notes='',write=False):
    allrows=scope();end=start+len(lines)
    assert start%80==0 and (len(lines)==80 or end==len(allrows))
    seen={n for a,b in examined for n in range(a,b+1)}
    assert set(range(max(0,start-1),min(len(allrows),end+1)))<=seen
    translations={}
    for r,t in zip(allrows[start:end],lines):
        assert isinstance(t,str) and t.strip(), ('keep nonempty fragments for original battle compiler',r['ordered_index'])
        t=target_text(t);original=source_text(r,source(r['resource'])[2])
        assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',t)
        assert control_tokens(t)==control_tokens(original),(r['ordered_index'],'control mismatch')
        encode_dialogue(t,original)
        translations[r['id']]=dict(r,text=t)
    doc=dict(version='0.1.55',range_inclusive=[start,end-1],rows_in_slice=len(lines),
             source_ranges_examined=examined,rows_examined=len(seen),notes=notes,
             uncertainties=uncertainties,preserved_source_omissions=omissions,
             review_status='author draft; independent review pending',translations=translations)
    path=FOLDER/f'slice_{start:04d}.targets.json'
    print(json.dumps(dict(mode='write' if write else 'dry-run',path=str(path),range=doc['range_inclusive'],
                         rows_examined=len(seen),samples=[translations[allrows[n]['id']]['text'] for n in sorted({start,(start+end-1)//2,end-1})],uncertainties=uncertainties),ensure_ascii=False,indent=2))
    if write:
        assert not path.exists();FOLDER.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return doc

def draft_targets():
    result={};inputs={}
    for path in sorted(FOLDER.glob('slice_*.targets.json')):
        d=json.loads(path.read_text('utf8'));inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        for identity,t in d['translations'].items():
            assert identity not in result;result[identity]=t
    return result,inputs

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--start',type=int);p.add_argument('--count',type=int,default=80);p.add_argument('--context',type=int,default=8);a=p.parse_args()
    if a.start is None:print(json.dumps(dict(rows=len(scope()),resources=dict(collections.Counter(r['resource'] for r in scope()))),indent=2))
    else:preview(a.start,a.count,a.context)
