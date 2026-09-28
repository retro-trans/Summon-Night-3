"""Remove the reviewed duplicate at a Chapter 1 translation-batch boundary."""
import copy,json,struct
from sn3_archive import ROOT
from sn3_codec import compress,decompress
from sn3_vm import instructions
from chapter_compiler_014 import simulate
from dialogue_layout import operand_instruction,verify_layout
from script_strings import parse_pool
from dialogue_encoding import control_tokens
from prepare_harbor_context import opening_source
from stages_patch import sha
BASE=ROOT/'work/output/0.1.38'
REVIEW=ROOT/'work/translation/en/repetition_0.1.39/review.json'

def prepare_scripts(source):
    review=json.loads(REVIEW.read_text(encoding='utf8'))
    manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf8'))
    report=copy.deepcopy(next(r for r in manifest['script_changes'] if r['resource_id']==review['resource_id']))
    before=decompress(source.resource('00.DAT',65),0xa695)[0]
    assert sha(before)==report['decoded_sha256']==review['prior_decoded_sha256']
    _,rows,original=opening_source()
    for r in review['source_rows']:
        row=rows[r['row']];assert row['id']==r['id'] and row['source_sha256']==r['sha256']
        assert sha(original[row['source_offset']:row['source_offset']+row['source_byte_length']])==r['sha256']
    group=next(g for g in report['layout_groups'] if g['id']==review['group_id'])
    reference=next(g for g in report['layout_groups'] if g['id']==review['reference_group_id'])
    assert group['text']==review['previous_text'] and reference['text']==review['target']
    assert control_tokens(group['text'])==control_tokens(review['target'])==[]
    assert len(group['pages'])==len(reference['pages'])==1
    assert len(group['pages'][0])==3 and len(reference['pages'][0])==2
    start=group['trampoline_offset'];size=group['code_size'];at={r['offset']:r for r in instructions(before)}
    old_pages=simulate(before,at,*group['original_span'])
    # Reuse already-correct English text only. Retain this branch's own speaker
    # arguments, display call, and return jump rather than copying the other branch.
    oldrefs=[l['reference_instructions'][0] for l in group['pages'][0]]
    assert oldrefs==[start,start+8,start+16]
    tail=before[start+24:start+size]
    assert at[start+size-4]['opcode']==10 and at[start+size-4]['target_word']*2==group['return_instruction']
    assert not any(start<r['target_word']*2<start+size for r in at.values() if 'target_word' in r)
    emitted=bytearray();newpages=copy.deepcopy(reference['pages'])
    for i,line in enumerate(newpages[0]):
        ref=line['reference_instructions'][0]
        assert at[ref]['opcode']==5 and at[ref]['mode']==4 and at[ref+4]['target_word']==2003
        emitted.extend(before[ref:ref+8])
        line['id']=f"{group['id']}:page:0:line:{i}"
    emitted.extend(tail);assert len(emitted)==size-8
    out=bytearray(before);out[start:start+size]=emitted+bytes(size-len(emitted))
    assert out[:start]==before[:start] and out[start+size:]==before[start+size:]
    group.update(text=review['target'],pages=newpages,code_size=len(emitted),reserved_trampoline_bytes=size,repetition039_review=REVIEW.relative_to(ROOT).as_posix())
    parsed=parse_pool(out);by_offset={r['source_offset']:r for r in parsed['strings']}
    for rec in report['changes']+[l for g in report['layout_groups'] for p in g['pages'] for l in p]:
        rec['reference_instructions']=by_offset[rec['new_offset']]['reference_instructions']
    verify_layout(bytes(out),report['changes'],report['layout_groups'])
    after={r['offset']:r for r in instructions(out)};unchanged=0
    for g in report['layout_groups']:
        old=simulate(before,at,*g['original_span']);new=simulate(out,after,*g['original_span'])
        if g['id']!=group['id']:assert old==new;unchanged+=1
        else:
            assert len(old)==len(new)==1
            assert old[0]['helper']==new[0]['helper'] and old[0]['args']==new[0]['args']
            assert new[0]['lines']==[l['display_text'] for l in newpages[0]]
    assert all(r['target_word']*2 in after for r in after.values() if 'target_word' in r)
    packed=compress(bytes(out),0xa695);assert decompress(packed,0xa695)[0]==out
    report.update(decoded_sha256=sha(out),decoded_size=len(out),encoded_size=len(packed))
    checks=dict(resource='00:00065',group_id=group['id'],before=review['previous_text'],after=review['target'],pages=[[l['text'] for l in p] for p in newpages],unchanged_groups_simulated=unchanged,patched_code_range=[start,start+size],decoded_size_unchanged=True,string_pool_unchanged=True,speaker_and_continuation_preserved=True,dialogue_and_backlog_share_corrected_page=True,runtime_scene_verified=False)
    return {65:packed},report,checks

if __name__=='__main__':
    from sn3_archive import GameSource
    with GameSource(BASE/'Summon_Night_3_EN_0.1.38.iso') as source:_,_,checks=prepare_scripts(source)
    print(json.dumps(checks,indent=2))
