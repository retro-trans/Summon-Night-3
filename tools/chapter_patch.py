"""Compile reviewed Chapter 2/3 dialogue and night conversations without byte budgets."""
import argparse, copy, json, re, struct
from pathlib import Path
from chapter_source import chapter_source
from sn3_archive import ROOT
from sn3_codec import compress, decompress
from sn3_vm import instructions
from script_strings import parse_pool
from script_repack import relocate_script
from dialogue_layout import operand_instruction, verify_layout, latin_width
from dialogue_encoding import encode_dialogue, control_tokens
from font_metrics import collect
from stages_patch import sha, read, punctuation, wrap, units

FOLDER=ROOT/'work/translation/en/chapters_0.1.12'
MAIN=(88,111)
NIGHT=(89,90,91,92,93,99,100,101,102,112,113,114,115,116,122,123,124,125)
RESOURCES=(88,)+NIGHT[:9]+(111,)+NIGHT[9:]
DIRECT={88:set(range(994,999))|set(range(1061,1064))|set(range(1160,1165))|set(range(1227,1230)),
        111:set(range(434,437))|set(range(732,735))|set(range(817,821))|set(range(1499,1503))|set(range(2110,2118))|set(range(565,569))}
PROFILES={2030:(208,1),2044:(208,1),2058:(208,1),2259:(208,1),2273:(208,1),2287:(208,1),2128:(448,0),2141:(448,0),2180:(448,0),2193:(448,0)}
PROFILES.update({2100:(208,1),2114:(208,1),2206:(208,0)})

def expected_rows(number,rows):
    return set(range(0 if number in MAIN else 11,len(rows)))

def load_targets(number,rows,source,reviewed):
    folder=FOLDER/f'{number:04d}';result={};inputs={}
    for path in sorted(folder.glob('slice_*.targets.json')):
        doc=read(path);inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        for identity,t in doc['translations'].items():
            n=t['resource_row'];r=rows[n]
            assert identity==r['id'] and n not in result,(number,n)
            for key in ('source_sha256','source_offset','source_byte_length','reference_instructions'):
                assert t[key]==r[key],(number,n,key)
            original=source[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
            # A review may redistribute merged draft fragments; only reviewed
            # nonempty targets reach relocation below.
            assert control_tokens(t['text'])==control_tokens(original)
            if t['text']:encode_dialogue(punctuation(t['text']),original)
            result[n]=copy.deepcopy(t)
    assert set(result)==expected_rows(number,rows),('coverage',number,sorted(expected_rows(number,rows)-set(result)))
    if reviewed:
        path=folder/'accepted_review.json';accepted=read(path)
        assert accepted['reviewed_rows']==sorted(result)
        assert accepted['draft_inputs_sha256']==inputs
        for fix in accepted['corrections']:
            n=fix['resource_row'];assert fix['source_sha256']==rows[n]['source_sha256']
            result[n]['text']=fix['text']
        for name,digest in accepted['review_inputs_sha256'].items():
            assert sha((ROOT/name).read_bytes())==digest,name
            inputs[name]=digest
        inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
    # Name normalization deliberately follows independent meaning review.
    replacements={'Sonora':'Sonolar','Biju':'Vijue','Bijou':'Vijue','Galeor':'Galleor',
                  'Azuria':'Azlier','Azria':'Azlier','Belfraw':'Belfrau','Alize':'Alieze',
                  'Kunon':'Cunnon','Kyuma':'Kyuuma','Yaffa':'Yafha','Ardyla':'Ardylia','Farzen':'Falzen','Beiger':'Veiger',
                  'Freize':'Phlaiz','Maruru':'Marurur'}
    for n,t in result.items():
        t['text']=punctuation(t['text'])
        prefix='　' if t['text'].startswith('　') else ''
        t['text']=prefix+' '.join(t['text'].replace('　',' ').split())
        for old,new in replacements.items():t['text']=re.sub(r'\b'+old+r'\b',new,t['text'])
        t['text']=t['text'].replace('factory-ship city','shipbuilding city')
        r=rows[n];original=source[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
        if original.count('♪')==1 and '♪' not in t['text']:
            t['text']+=' ♪'
            t.setdefault('normalization_notes',[]).append('Restored the source musical-note expression after meaning review.')
        encode_dialogue(t['text'],original)
        assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',t['text']),('untranslated',number,n)
    return result,inputs

def simulate(data,at,start,stop):
    """Bounded execution of replaced spans, retaining symbolic local arguments."""
    pool=struct.unpack_from('<I',data,20)[0]*2
    pc=start;stack=['sentinel'];pending=[];pages=[];steps=0
    while pc!=stop:
        steps+=1;assert steps<2000
        row=at[pc];pc+=row['size'];op=row['opcode'];mode=row['mode']
        if op==10:pc=row['target_word']*2
        elif op==5:
            if mode==4:
                offset=pool+row['string_word']*2;end=offset
                while data[end:end+2]!=b'\0\0':end+=2
                stack.append(data[offset:end].decode('cp932'))
            elif mode in (5,9):
                value=(row['high']<<16)|row['operands'][0]
                stack.append(value-65536 if mode==9 and value>=32768 else value)
            elif mode==10:stack.append(row['high']-1)
            elif mode==2:stack.append(('local',row['high'],tuple(row['operands'])))
            else:raise AssertionError(('push',row))
        elif op==7:
            args=stack[-mode:] if mode else []
            if mode:del stack[-mode:]
            if row['target_word']==2003:
                assert len(args)==1 and isinstance(args[0],str);pending.append(args[0])
            else:
                assert pending;pages.append(dict(helper=row['target_word'],args=args,lines=pending));pending=[]
        else:raise AssertionError(('opcode',row))
    assert stack==['sentinel'] and not pending
    return pages

def prepare(number,reviewed=True):
    resource,rows,before=chapter_source(number)
    translated,inputs=load_targets(number,rows,before,reviewed)
    metrics=copy.deepcopy(collect()[0]['characters'])
    for c,advance in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:metrics[c]={'proposed_advance_pixels':advance}
    targets={};identity={}
    for n,t in translated.items():
        r=rows[n];targets[r['source_offset']]=dict(source_sha256=r['source_sha256'],text=t['text'],encoding_profile='dialogue_fullwidth_cp932')
        identity[r['source_offset']]=r
    moved,changes=relocate_script(before,targets)
    pool=parse_pool(before)['pool_offset'];code=instructions(before);at={i['offset']:i for i in code}
    destinations={i['target_word']*2 for i in code if 'target_word' in i}
    plans=[];done=set();direct=[];direct_rows=DIRECT.get(number,set())
    for n in sorted(translated):
        if n in done:continue
        r=rows[n];assert len(r['reference_instructions'])==1,(number,n,'shared reference')
        pos=r['reference_instructions'][0]
        if n in direct_rows:
            text=translated[n]['text'];limit=208 if number==111 and n in range(565,569) else 280
            assert units(text)<=31 and latin_width(text,metrics)<=limit,('direct text too wide',number,n,text,units(text),latin_width(text,metrics))
            direct.append(dict(row=n,text=text,reference=pos,pixel_limit=limit));done.add(n);continue
        ns=[n]
        while ns[-1]+1 in translated and ns[-1]+1 not in direct_rows:
            nxt=ns[-1]+1;p=pos+8*len(ns)
            if rows[nxt]['reference_instructions']!=[p] or at.get(p+4,{}).get('target_word')!=2003:break
            ns.append(nxt)
        for k in ns:
            p=rows[k]['reference_instructions'][0]
            assert at[p]['opcode']==5 and at[p]['mode']==4 and at[p+4]['opcode']==7 and at[p+4]['target_word']==2003,(number,k,at[p+4])
        tail_start=pos+8*len(ns);end=tail_start;argc=0
        while at[end]['opcode']==5:
            assert at[end]['mode'] in (2,5,9,10),(number,ns,at[end]);argc+=1;end+=at[end]['size']
        inst=at[end];helper=inst.get('target_word');assert inst['opcode']==7 and helper in PROFILES,(number,ns,inst)
        width,expected_argc=PROFILES[helper];assert inst['mode']==argc==expected_argc
        # Bind helper assumptions to the actual original function body.
        hp=helper*2;assert at[hp]['opcode']==2
        native=[]
        while at[hp]['opcode']!=3:
            if at[hp]['opcode']==8:native.append(at[hp])
            hp+=at[hp]['size']
        assert len(native)==1 and native[0]['mode']==8 and native[0]['operands']==[0x3052]
        end+=inst['size'];assert not any(pos<x<end for x in destinations),(number,ns,'branch into group')
        text=' '.join(translated[k]['text'] for k in ns);lines=wrap(text,width,metrics);pages=[lines[i:i+3] for i in range(0,len(lines),3)]
        for page in pages:assert sum(units(line) for line in page)<=192
        plans.append(dict(id=f'chapter_{number}_'+'_'.join(map(str,ns)),resource_rows=ns,source_offsets=[rows[k]['source_offset'] for k in ns],original_span=[pos,end],original_span_sha256=sha(before[pos:end]),tail=before[tail_start:end],display_helper_word=helper,text=text,page_texts=pages,code_size=sum(8*len(p)+end-tail_start for p in pages)+4,measured_pixel_limit=width))
        done.update(ns)
    assert done==set(translated)
    growth=sum(p['code_size'] for p in plans);new_pool=pool+growth
    out=bytearray(moved[:pool]+bytes(growth)+moved[pool:]);struct.pack_into('<I',out,20,new_pool//2)
    for c in changes:c.update(id=identity[c['old_offset']]['id'],new_offset=c['new_offset']+growth)
    cursor=pool;groups=[]
    for plan in plans:
        emitted=bytearray();pages=[]
        for pi,texts in enumerate(plan['page_texts']):
            fragments=[]
            for li,text in enumerate(texts):
                encoded,display=encode_dialogue(text,''.join(control_tokens(text)));offset=len(out);word=(offset-new_pool)//2;ref=cursor+len(emitted)
                out.extend(encoded+b'\0\0');emitted.extend(operand_instruction(5,4,word)+operand_instruction(7,1,2003))
                fragments.append(dict(id=f"{plan['id']}:page:{pi}:line:{li}",text=text,display_text=display,new_offset=offset,new_byte_length=len(encoded),pool_word_offset=word,reference_instructions=[ref],expanded_units=units(text)))
            emitted.extend(plan['tail']);pages.append(fragments)
        start,end=plan['original_span'];emitted.extend(operand_instruction(10,0,end//2));assert len(emitted)==plan['code_size']
        out[cursor:cursor+len(emitted)]=emitted;out[start:end]=operand_instruction(10,0,cursor//2)+bytes(end-start-4)
        for c in changes:
            if c['old_offset'] in plan['source_offsets']:
                c['original_reference_instructions']=c['reference_instructions'];c['reference_instructions']=[];c['layout_group_id']=plan['id']
        group={k:v for k,v in plan.items() if k not in ('tail','page_texts')}
        group.update(trampoline_offset=cursor,return_instruction=end,pages=pages,max_display_units=31,max_lines_per_page=3,layout_profile='chapters_expanded_tokens_v1',maximum_measured_pixels=max(latin_width(r['text'],metrics) for p in pages for r in p))
        groups.append(group);cursor+=len(emitted)
    assert cursor==new_pool and out[new_pool:new_pool+len(before)-pool]==before[pool:]
    allowed=set(range(20,24))|{i for p in plans for i in range(*p['original_span'])}|{i for d in direct for i in range(d['reference'],d['reference']+4)}
    assert all(before[i]==out[i] for i in range(pool) if i not in allowed)
    verify_layout(bytes(out),changes,groups)
    new_at={i['offset']:i for i in instructions(out)}
    for g in groups:
        old=simulate(before,at,*g['original_span']);new=simulate(out,new_at,*g['original_span']);assert len(old)==1 and len(new)==len(g['pages'])
        for p,expected in zip(new,g['pages']):assert p['helper']==old[0]['helper'] and p['args']==old[0]['args'] and p['lines']==[r['display_text'] for r in expected]
    assert len(out)<0x78000,(number,len(out),'allocation')
    packed=compress(bytes(out),0xa695);assert decompress(packed,0xa695)[0]==out
    report=dict(resource_id=resource['id'],resource=resource['id'],bank='00.DAT',index=number,source_sha256=resource['sha256'],original_decoded_sha256=sha(before),decoded_size=len(out),encoded_size=len(packed),decoded_sha256=sha(out),changes=changes,layout_groups=groups,runtime_allocation_verified=False)
    inputs['tools/chapter_patch.py']=sha(Path(__file__).read_bytes())
    selection=dict(resource_id=resource['id'],translations={rows[n]['id']:t for n,t in translated.items()},review_inputs_sha256=inputs,layout_groups=groups)
    checks=dict(resource_id=resource['id'],covered_source_rows=len(translated),remaining_in_scope=0,excluded_shared_library_rows=len(resource['strings'])-len(translated),groups=len(groups),pages=sum(len(g['pages']) for g in groups),code_growth=growth,decoded_script_bytes=len(out),direct_rows=direct,source_pool_preserved=True,unrelated_code_preserved=True,all_group_calls_simulated=True,reviewed=reviewed,samples=[dict(rows=g['resource_rows'],pages=[[r['text'] for r in p] for p in g['pages']]) for g in groups[:3]])
    return packed,report,selection,checks

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resources',type=int,nargs='*',default=RESOURCES);p.add_argument('--write',action='store_true');p.add_argument('--draft-preview',action='store_true');a=p.parse_args();assert not(a.write and a.draft_preview)
    for number in a.resources:
        _,report,selection,checks=prepare(number,not a.draft_preview)
        print(json.dumps(dict(mode='write' if a.write else 'dry run',**checks),indent=2),flush=True)
        if a.write:
            (FOLDER/f'{number:04d}'/'compiled.targets.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
            (ROOT/'docs'/f'chapter_{number:04d}_static_0.1.12.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
