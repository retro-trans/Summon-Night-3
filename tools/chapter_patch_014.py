"""Chapter 4-8 adapter for the verified relocation compiler; dry-run by default.

Keeps published compiler inputs immutable. Unsupported branching groups retain
their original flow and must fit the conservative original single-line limit.
No semantic review is inferred from a structural check.
"""
import argparse, copy, json, re, struct
from pathlib import Path
import chapter_compiler_014 as compiler
from chapter_source_014 import load, MAIN_TAIL_START
from dialogue_encoding import control_tokens, encode_dialogue
from sn3_archive import ROOT
from sn3_vm import instructions
from stages_patch import sha, punctuation, units
from dialogue_layout import latin_width
from font_metrics_014 import collect

FOLDER = ROOT/'work/translation/en/chapters_0.1.14'
GLOSSARY = ROOT/'work/glossary/character_reference_sn6_vita.json'
PROFILES = dict(compiler.PROFILES, **{})
PROFILES[2301] = (208, 1)
PROFILES[-0x3052] = (208, 8)
BASE_PREPARE = compiler.prepare

def source(number):
    resource, rows, data = load(number)
    return resource,rows,data

def normalize(text):
    text = punctuation(text)
    prefix = '　' if text.startswith('　') else ''
    text = prefix + ' '.join(text.replace('　',' ').split())
    mappings = {}
    for e in json.loads(GLOSSARY.read_text(encoding='utf-8'))['entries']:
        for old in e['gallery_aliases'] + e['previous_project_spellings']:
            mappings[old] = e['target_name'] if ' ' in old else e['short_name']
            if ' ' in old and ' ' in e['target_name']:
                mappings[old.split()[0]]=e['short_name']
    for old,new in sorted(mappings.items(),key=lambda x:-len(x[0])):
        text = re.sub(r'(?<![A-Za-z])'+re.escape(old)+r'(?![A-Za-z])',new,text)
    return text

def targets(number, rows, data, reviewed=True, partial=False):
    result={}; inputs={}; folders=[(FOLDER/f'{number:04d}',MAIN_TAIL_START.get(number,0),number)]
    folders.append((FOLDER/'common_0180',0,180))
    for folder,shift,canonical in folders:
        canonical_rows = load(canonical)[1] if canonical != number else None
        for path in sorted(folder.glob('slice_*.targets.json')):
            doc=json.loads(path.read_text(encoding='utf-8')); inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
            for identity,t in doc['translations'].items():
                cn=t['resource_row']
                if folder.name=='common_0180':
                    if number in (134,157):
                        if 464<=cn<2613:continue
                        n=cn if cn<464 else cn-2149
                    elif number in (180,203,226):n=cn
                    else:
                        if cn>=11:continue
                        n=cn
                else:n=cn+shift
                r=rows[n]
                original_row=canonical_rows[cn] if canonical_rows else r
                assert identity==original_row['id'] and n not in result,(number,n,identity)
                for key in ('source_sha256','source_offset','source_byte_length','reference_instructions'):
                    assert t[key]==original_row[key],(number,n,key)
                assert original_row['source_sha256']==r['source_sha256']
                result[n]=dict(t, resource_row=n, **{k:r[k] for k in ('source_sha256','source_offset','source_byte_length','reference_instructions')})
    expected=set(range(len(rows)))
    if not partial: assert set(result)==expected,('coverage',number,len(result),len(expected),sorted(expected-set(result))[:10])
    assert set(result)<=expected and result
    if not reviewed:
        folder=FOLDER/f'{number:04d}'
        paths=sorted(folder.glob('review_meaning_*.json'))
        if (folder/'independent_review.json').exists():paths.append(folder/'independent_review.json')
        for path in paths:
            doc=json.loads(path.read_text(encoding='utf-8'))
            assert doc['semantic_complete']
            for s in doc['reviewed_slices']:
                assert sha((ROOT/s['target_file']).read_bytes())==s['target_file_sha256'],s['target_file']
            for fix in doc['corrections']:
                n=fix['resource_row']+MAIN_TAIL_START.get(number,0)
                assert fix['source_sha256']==rows[n]['source_sha256'] and n in result
                result[n]['text']=fix['text']
            inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
    if reviewed:
        review_path=FOLDER/f'{number:04d}'/'accepted_review.json'
        review=json.loads(review_path.read_text(encoding='utf-8'))
        assert review['reviewed_rows']==sorted(result)
        assert review['draft_inputs_sha256']==inputs
        for name,h in review['review_inputs_sha256'].items():
            assert sha((ROOT/name).read_bytes())==h
            inputs[name]=h
        inputs[str(review_path.relative_to(ROOT)).replace('\\','/')]=sha(review_path.read_bytes())
        for fix in review['corrections']:
            n=fix['resource_row'];assert fix['source_sha256']==rows[n]['source_sha256']
            result[n]['text']=fix['text']
    for n,t in result.items():
        r=rows[n];original=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
        t['text']=normalize(t['text'])
        assert control_tokens(t['text'])==control_tokens(original),(number,n,'controls')
        assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',t['text']),(number,n,'Japanese')
        if original.count('♪')==1 and '♪' not in t['text']:t['text']+=' ♪'
        if t['text']:encode_dialogue(t['text'],original)
    for p in (GLOSSARY,Path(__file__),ROOT/'tools/chapter_source_014.py',ROOT/'tools/script_compact_014.py',ROOT/'tools/chapter_compiler_014.py',ROOT/'tools/chapter_patch.py',ROOT/'tools/font_metrics_014.py'):
        inputs[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p.read_bytes())
    return result,inputs

def direct_rows(rows,data,selected,profiles=None):
    profiles=PROFILES if profiles is None else profiles
    at={i['offset']:i for i in instructions(data)}
    destinations={i['target_word']*2 for i in at.values() if 'target_word' in i}|{struct.unpack_from('<I',data,16)[0]*2}
    done=set();direct=set()
    for n in sorted(selected):
        if n in done:continue
        r=rows[n];assert len(r['reference_instructions'])==1
        start=r['reference_instructions'][0];ns=[n]
        if at.get(start+4,{}).get('target_word')!=2003:
            direct.add(n);done.add(n);continue
        while ns[-1]+1 in selected:
            nxt=ns[-1]+1;p=start+8*len(ns)
            if rows[nxt]['reference_instructions']!=[p] or p in destinations or at.get(p+4,{}).get('target_word')!=2003:break
            ns.append(nxt)
        end=start+8*len(ns);argc=0
        while at[end]['opcode']==5:
            if at[end]['mode'] not in (2,5,9,10):break
            argc+=1;end+=at[end]['size']
        inst=at[end];helper=inst.get('target_word',-0x3052 if inst['opcode']==8 and inst['operands']==[0x3052] else None)
        good=(inst['opcode']==7 or helper==-0x3052) and helper in profiles and inst['mode']==argc==profiles[helper][1]
        if good:good=not any(start<x<end+inst['size'] for x in destinations)
        if not good:direct.update(ns)
        done.update(ns)
    return direct

def prepare(number,reviewed=True,partial=False):
    resource,rows,data=source(number)
    translated,inputs=targets(number,rows,data,reviewed,partial)
    direct=direct_rows(rows,data,translated)
    metrics=copy.deepcopy(collect()[0]['characters'])
    for c,advance in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:metrics[c]={'proposed_advance_pixels':advance}
    for n in direct:
        text=translated[n]['text']
        assert text and units(text)<=31 and latin_width(text,metrics)<=208,('conditional/menu text too wide',number,n,text,units(text),latin_width(text,metrics))
    saved={k:getattr(compiler,k) for k in ('chapter_source','load_targets','DIRECT','PROFILES')}
    try:
        compiler.chapter_source=lambda _: (resource,rows,data)
        compiler.load_targets=lambda *args:(translated,inputs)
        compiler.DIRECT={number:direct};compiler.PROFILES=PROFILES
        packed,report,selection,checks=BASE_PREPARE(number,reviewed)
    finally:
        for k,v in saved.items():setattr(compiler,k,v)
    checks.update(partial_preview=partial,meaning_review_verified=reviewed,conditional_or_menu_rows=len(direct))
    if partial:checks['remaining_in_scope']=len(rows)-len(translated)
    return packed,report,selection,checks

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resources',type=int,nargs='+');p.add_argument('--draft-preview',action='store_true');p.add_argument('--partial',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    assert not(a.write and (a.draft_preview or a.partial))
    for n in a.resources:
        packed,report,selection,checks=prepare(n,not a.draft_preview,a.partial)
        print(json.dumps(dict(mode='write' if a.write else 'dry-run',**checks),ensure_ascii=False,indent=2),flush=True)
        if a.write:
            (FOLDER/f'{n:04d}'/'compiled.targets.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
            (ROOT/'docs'/f'chapter_{n:04d}_static_0.1.14.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
