"""Reflow proven Night Talk display modes without recompiling historical inputs."""
import copy,json,struct
from sn3_archive import ROOT,GameSource
from sn3_codec import compress,decompress
from sn3_vm import instructions
from chapter_patch import simulate as legacy_simulate
from chapter_patch_014 import normalize
from dialogue_layout import operand_instruction,latin_width
from dialogue_encoding import encode_dialogue,control_tokens
from stages_patch import wrap,units,sha

BASE=ROOT/'work/output/0.1.36'
WIDTH=368
HELPERS={2100:4,2114:5}

def simulate(data,at,start,stop):
    # The compact compiler pads unused original instructions with VM NOPs.
    # Present each NOP as a jump to the following instruction for the symbolic runner.
    patched=dict(at)
    for offset,row in at.items():
        if row['opcode']==8 and row['operands']==[0x3052]:
            patched[offset]=dict(row,opcode=7,target_word=-0x3052)
        if row['opcode']==0:
            patched[offset]=dict(row,opcode=10,target_word=(offset+row['size'])//2)
    return legacy_simulate(data,patched,start,stop)

def signature(data,at,helper):
    rows=[];pc=helper*2
    assert at[pc]['opcode']==2
    while at[pc]['opcode']!=3:
        rows.append(at[pc]);pc+=at[pc]['size']
    native=[r for r in rows if r['opcode']==8]
    assert len(native)==1 and native[0]['operands']==[0x3052] and native[0]['mode']==8
    pushes=[r for r in rows if r['opcode']==5]
    assert len(pushes)==8 and pushes[1]['mode']==10
    assert pushes[1]['high']-1==HELPERS[helper]
    return sha(data[helper*2:pc+2])

def tail_bytes(data,at,start,stop,helper):
    pc=start;tail=bytearray();steps=0
    while pc!=stop:
        steps+=1;assert steps<2000
        r=at[pc];nxt=pc+r['size']
        if r['opcode']==10:pc=r['target_word']*2;continue
        if r['opcode']==7 and r['target_word']==2003:tail.clear()
        elif r['opcode']==7:
            assert r['target_word']==helper
            tail.extend(data[pc:nxt]);return bytes(tail)
        else:tail.extend(data[pc:nxt])
        pc=nxt
    raise AssertionError('Missing display call')

def prepare_scripts(source):
    manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf8'))
    metrics=copy.deepcopy(json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'])
    for c,a in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:metrics[c]={'proposed_advance_pixels':a}
    replacements={};reports=[]
    for section in ('script_changes','chapters_4_to_8'):
        for record in manifest[section]:
            selected=[g for g in record.get('layout_groups',[]) if g.get('display_helper_word') in HELPERS]
            if not selected:continue
            n=int(record['resource_id'].split(':')[1]);assert n not in replacements
            raw=source.resource('00.DAT',n);before=decompress(raw,0xa695)[0]
            assert sha(before)==record['decoded_sha256'],n
            at={r['offset']:r for r in instructions(before)}
            pool=struct.unpack_from('<I',before,20)[0]*2
            plans=[]
            for g in selected:
                helper=g['display_helper_word'];sig=signature(before,at,helper)
                original=simulate(before,at,*g['original_span'])
                assert all(p['helper']==helper and p['args']==original[0]['args'] for p in original)
                assert [p['lines'] for p in original]==[[l['display_text'] for l in p] for p in g['pages']]
                text=normalize(g['text']);assert control_tokens(text)==control_tokens(g['text'])
                lines=wrap(text,WIDTH,metrics);pages=[lines[i:i+2] for i in range(0,len(lines),2)]
                assert ' '.join(lines)==' '.join(text.split())
                tail=tail_bytes(before,at,*g['original_span'],helper)
                plans.append(dict(group=g,text=text,pages=pages,tail=tail,signature=sig,old_pages=original,size=sum(8*len(p)+len(tail) for p in pages)+4))
            growth=sum(p['size'] for p in plans);newpool=pool+growth
            out=bytearray(before[:pool]+bytes(growth)+before[pool:]);struct.pack_into('<I',out,20,newpool//2)
            cursor=pool;groups=[];allowed=set(range(20,24))
            for p in plans:
                g=p['group'];start,end=g['original_span'];emitted=bytearray();pages=[]
                for texts in p['pages']:
                    page=[]
                    for text in texts:
                        encoded,display=encode_dialogue(text,''.join(control_tokens(text)))
                        offset=len(out);word=(offset-newpool)//2;ref=cursor+len(emitted)
                        out.extend(encoded+b'\0\0');emitted.extend(operand_instruction(5,4,word)+operand_instruction(7,1,2003))
                        assert units(text)<=31 and latin_width(text,metrics)<=WIDTH
                        page.append(dict(text=text,display_text=display,offset=offset,reference=ref,expanded_units=units(text),pixels=latin_width(text,metrics)))
                    emitted.extend(p['tail']);pages.append(page)
                emitted.extend(operand_instruction(10,0,end//2));assert len(emitted)==p['size']
                out[cursor:cursor+len(emitted)]=emitted
                out[start:end]=operand_instruction(10,0,cursor//2)+bytes(end-start-4);allowed.update(range(start,end))
                groups.append(dict(id=g['id'],resource_rows=g['resource_rows'],original_span=g['original_span'],display_helper_word=g['display_helper_word'],native_display_mode=HELPERS[g['display_helper_word']],helper_sha256=p['signature'],text=p['text'],pages=pages,trampoline_offset=cursor,return_instruction=end,old_page_count=len(g['pages']),max_lines_per_page=2,max_expanded_units_per_line=31,pixel_limit=WIDTH))
                cursor+=len(emitted)
            assert cursor==newpool
            assert all(before[i]==out[i] for i in range(pool) if i not in allowed)
            assert out[newpool:newpool+len(before)-pool]==before[pool:]
            after={r['offset']:r for r in instructions(out)}
            starts=set(after)
            for r in after.values():
                if 'target_word' in r:assert r['target_word']*2 in starts
            selected_ids={g['id'] for g in groups}
            for g in record['layout_groups']:
                if g['id'] not in selected_ids:
                    assert simulate(before,at,*g['original_span'])==simulate(out,after,*g['original_span'])
            for g,p in zip(groups,plans):
                actual=simulate(out,after,*g['original_span'])
                assert len(actual)==len(g['pages'])
                for page,want in zip(actual,g['pages']):
                    assert page['helper']==g['display_helper_word'] and page['args']==p['old_pages'][0]['args']
                    assert page['lines']==[r['display_text'] for r in want]
            assert len(out)<0x78000,(n,len(out))
            packed=compress(bytes(out),0xa695);assert decompress(packed,0xa695)[0]==out
            replacements[n]=packed
            reports.append(dict(resource_id=record['resource_id'],source_sha256=sha(raw),prior_decoded_sha256=sha(before),decoded_sha256=sha(out),decoded_size=len(out),groups=groups,untouched_groups=len(record['layout_groups'])-len(groups),all_groups_simulated=True,unrelated_code_and_pool_unchanged=True))
    return replacements,reports

if __name__=='__main__':
    with GameSource(BASE/'Summon_Night_3_EN_0.1.36.iso') as s:_,r=prepare_scripts(s)
    dest=ROOT/'work/translation/en/night_talk_0.1.37';dest.mkdir(parents=True,exist_ok=True)
    (dest/'layout.json').write_bytes((json.dumps(dict(schema_version=1,base='0.1.36',resources=r),indent=2)+'\n').encode())
    print(json.dumps(dict(resources=len(r),groups=sum(len(x['groups']) for x in r),pages=sum(len(g['pages']) for x in r for g in x['groups']),max_decoded_size=max(x['decoded_size'] for x in r))))
