"""Finish the 641-row opening scope with explicit special-style reflow."""
import argparse,copy,json,hashlib,struct
from pathlib import Path
from sn3_archive import ROOT,GameSource
from sn3_codec import decompress,compress
from prepare_harbor_context import opening_source
from script_strings import parse_pool
from script_repack import relocate_script
from dialogue_layout import operand_instruction,wrap_pixels,verify_layout,latin_width
from dialogue_encoding import encode_dialogue
from verify_dialogue_layout import simulate_group
from sn3_vm import instructions
from font_metrics import collect,MAP_VA,ELF_SEGMENT_OFFSET

PRIOR=ROOT/'work/output/0.1.10'
REVIEW='work/translation/en/harbor_remaining_0.1.11.meaning_review.json'
TARGET='work/translation/en/opening_harbor_0.1.11.targets.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()

def prepare(source):
    manifest=read(PRIOR/'manifest.json');report=copy.deepcopy(manifest['script_changes'][0])
    before=decompress(source.resource('00.DAT',65),0xa695)[0];assert sha(before)==report['decoded_sha256']
    resource,rows,original=opening_source();review=read(ROOT/REVIEW)
    assert review['accepted_count']==17 and not review['unresolved_rows'] and sha(original)==review['source_decoded_sha256']
    selection=read(ROOT/'work/translation/en/opening_harbor_0.1.10.targets.json')
    metrics=copy.deepcopy(collect()[0]['characters'])
    # The current spacing hooks leave unlisted Japanese/music symbols at 16px.
    # Verify that the retained music note maps to a real, nonempty native glyph.
    elf=(ROOT/'work/source/EBOOT.elf').read_bytes();a,b='\u266a'.encode('cp932')
    page=struct.unpack_from('<I',elf,ELF_SEGMENT_OFFSET+MAP_VA+(a-0x80)*4)[0]
    glyph=struct.unpack_from('<H',elf,ELF_SEGMENT_OFFSET+page+(b-0x40)*2)[0]
    with GameSource() as original_source:font=original_source.read('02.DAT',456704,473088)
    bitmap=font[28+(glyph-1)*128:28+glyph*128];assert 1<=glyph<=3680 and any(bitmap)
    metrics['\u266a']={'proposed_advance_pixels':16}
    prior_pool=parse_pool(before)['pool_offset'];delta=prior_pool-parse_pool(original)['pool_offset']
    targets={};identity={}
    for item in review['items']:
        r=rows[item['opening_row']];assert r['id']==item['id'] and r['source_sha256']==item['source_sha256']
        t=dict(source_offset=r['source_offset'],source_sha256=r['source_sha256'],text=item['reviewed_text'],status='meaning_reviewed',encoding_profile='dialogue_fullwidth_cp932')
        assert r['id'] not in selection['translations'];selection['translations'][r['id']]=t
        current=r['source_offset']+delta;targets[current]=t;identity[current]=r
    moved,changes=relocate_script(before,targets)
    code=instructions(before);at={i['offset']:i for i in code};destinations={i['target_word']*2 for i in code if 'target_word' in i}
    plans=[]
    for group in review['groups']:
        ns=group['opening_rows'];positions=[rows[n]['reference_instructions'][0] for n in ns]
        start=positions[0];assert positions==list(range(start,start+8*len(ns),8))
        tail_start=positions[-1]+8;end=tail_start
        while at[end]['opcode']==5:end+=at[end]['size']
        helper=at[end]['target_word'];assert helper in (2030,2058) and at[end]['mode']==1
        end+=4;assert not any(start<x<end for x in destinations)
        # All these helpers call native0x3052 with the same eight parameters.
        # 2058 differs from2030 only in style2, kept in every emitted page.
        lines=wrap_pixels(group['reviewed_text'],208,31,metrics);pages=[lines[i:i+3] for i in range(0,len(lines),3)]
        tail=before[tail_start:end]
        plans.append(dict(id='harbor_complete_'+'_'.join(map(str,ns)),opening_rows=ns,source_offsets=[rows[n]['source_offset'] for n in ns],
            original_span=[start,end],original_span_sha256=sha(before[start:end]),tail=tail,display_helper_word=helper,
            text=group['reviewed_text'],page_texts=pages,code_size=sum(8*len(p)+len(tail) for p in pages)+4))
    growth=sum(p['code_size'] for p in plans);new_pool=prior_pool+growth
    out=bytearray(moved[:prior_pool]+bytes(growth)+moved[prior_pool:]);struct.pack_into('<I',out,20,new_pool//2)
    # Every prior string moves with the pool; relative VM string operands stay valid.
    for c in report['changes']:c['new_offset']+=growth
    for g in report['layout_groups']:
        for p in g['pages']:
            for c in p:c['new_offset']+=growth
    for c in changes:
        r=identity[c['old_offset']];c.update(id=r['id'],prior_build_source_offset=c['old_offset'],old_offset=r['source_offset'],new_offset=c['new_offset']+growth)
    cursor=prior_pool;groups=[]
    for plan in plans:
        emitted=bytearray();pages=[]
        for pi,texts in enumerate(plan['page_texts']):
            fragments=[]
            for li,text in enumerate(texts):
                encoded,display=encode_dialogue(text,'');offset=len(out);word=(offset-new_pool)//2;ref=cursor+len(emitted)
                out.extend(encoded+b'\0\0');emitted.extend(operand_instruction(5,4,word)+operand_instruction(7,1,2003))
                fragments.append(dict(id=f"{plan['id']}:page:{pi}:line:{li}",text=text,display_text=display,new_offset=offset,new_byte_length=len(encoded),pool_word_offset=word,reference_instructions=[ref]))
            emitted.extend(plan['tail']);pages.append(fragments)
        start,end=plan['original_span'];emitted.extend(operand_instruction(10,0,end//2));assert len(emitted)==plan['code_size']
        out[cursor:cursor+len(emitted)]=emitted;out[start:end]=operand_instruction(10,0,cursor//2)+bytes(end-start-4)
        for c in changes:
            if c['old_offset'] in plan['source_offsets']:
                c['original_reference_instructions']=c['reference_instructions'];c['reference_instructions']=[];c['layout_group_id']=plan['id']
        group={k:v for k,v in plan.items() if k not in ('tail','page_texts')}
        group.update(trampoline_offset=cursor,return_instruction=end,pages=pages,max_display_units=31,max_lines_per_page=3,
            layout_profile='opening_special_style_and_music_v1',measured_pixel_limit=208,maximum_measured_pixels=max(latin_width(r['text'],metrics) for p in pages for r in p))
        groups.append(group);cursor+=len(emitted)
    assert out[new_pool:new_pool+len(before)-prior_pool]==before[prior_pool:]
    allowed=set(range(20,24))|{i for g in plans for i in range(*g['original_span'])}
    assert all(before[i]==out[i] for i in range(prior_pool) if i not in allowed)
    report['changes'].extend(changes);report['layout_groups'].extend(groups)
    verify_layout(bytes(out),report['changes'],report['layout_groups'])
    for g in groups:
        old=simulate_group(before,*g['original_span']);new=simulate_group(out,*g['original_span']);assert len(old)==1
        assert len(new)==len(g['pages'])
        for page,expected in zip(new,g['pages']):
            assert page['helper']==old[0]['helper'] and page['args']==old[0]['args'] and page['lines']==[r['display_text'] for r in expected]
    # Exhaustive opening-scope coverage: every one of the641 source references
    # is translated directly or owned by a complete verified reflow group.
    assert {rows[n]['id'] for n in range(641)}==set(selection['translations'])
    assert {c['id'] for c in report['changes']}==set(selection['translations'])
    parsed=parse_pool(out);assert len(out)<0x78000
    packed=compress(bytes(out),0xa695);assert decompress(packed,0xa695)[0]==out
    report.update(decoded_size=len(out),encoded_size=len(packed),decoded_sha256=sha(out),runtime_allocation_verified=False)
    selection.update(scope='Complete641-row opening/harbor source scope including alternate branches; later script text remains untranslated.',excluded_groups=[])
    for g in selection.get('incremental_layout_groups',[]):
        for p in g['pages']:
            for c in p:c['new_offset']+=growth
    selection.setdefault('incremental_layout_groups',[]).extend(groups)
    for p in (REVIEW,'tools/harbor_complete_patch.py'):
        selection['review_inputs_sha256'][p]=sha((ROOT/p).read_bytes())
    checks=dict(added_source_rows=review['target_rows'],covered_source_rows=641,remaining_in_scope=0,new_reflow_groups=len(groups),
        new_code_bytes=growth,new_pages=sum(len(g['pages']) for g in groups),decoded_script_bytes=len(out),
        helper2058=dict(native_call='0x3052',argument_count=8,difference_from2030='style argument2 rather than0; all original helper calls retained'),
        music_note=dict(glyph_index=glyph,glyph_sha256=sha(bitmap),native_fallback_advance=16),
        samples=[dict(rows=g['opening_rows'],helper=g['display_helper_word'],pages=[[r['text'] for r in p] for p in g['pages']]) for g in groups],
        prior_translations_preserved=True,source_pool_preserved=True,all_group_calls_simulated=True,coverage='Source-reference order includes branches;641 fragments is not641 sequential dialogue boxes.')
    return packed,report,selection,checks

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    with GameSource(PRIOR/'Summon_Night_3_EN_0.1.10.iso') as source:_,report,selection,checks=prepare(source)
    print(json.dumps(dict(mode='write' if a.write else 'dry run',**checks),indent=2))
    if a.write:
        (ROOT/TARGET).write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
        (ROOT/'docs/harbor_complete_static_0.1.11.json').write_text(json.dumps(checks,indent=2)+'\n')

if __name__=='__main__':main()
