"""Append reviewed harbor gaps and import generated native nameplate layers."""
import argparse,copy,hashlib,json,re,struct,shutil
from pathlib import Path
from PIL import Image
import numpy as np
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_codec import compress,decompress
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from prepare_harbor_context import opening_source
from script_strings import parse_pool
from script_repack import relocate_script
from dialogue_encoding import encode_dialogue
from dialogue_layout import operand_instruction,verify_layout
from verify_dialogue_layout import simulate_group

ASSETS=ROOT/'work/ui/nameplates_0.1.10'
REVIEW='work/translation/en/harbor_gaps_0.1.10.meaning_review.json'
TARGET='work/translation/en/opening_harbor_0.1.10.targets.json'
PRIOR=ROOT/'work/output/0.1.9'
NAMES={'Nup':901,'Belfrau':902,'Alieze':903,'Will':904,'Salome':938}
def sha(d):return hashlib.sha256(d).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def script_patch(source):
    previous=read(PRIOR/'manifest.json');report=copy.deepcopy(previous['script_changes'][0])
    before=decompress(source.resource('00.DAT',65),0xa695)[0]
    assert sha(before)==report['decoded_sha256']
    resource,rows,original=opening_source();review=read(ROOT/REVIEW)
    assert sha(original)==review['source_decoded_sha256']
    selection=read(ROOT/'work/translation/en/opening_harbor_0.1.5.targets.json')
    selection['scope']='0.1.9 content plus reviewed harbor choices and measured six-glyph player-name introduction; built incrementally by build_harbor_gaps.py.'
    shift=parse_pool(before)['pool_offset']-parse_pool(original)['pool_offset']
    preferred={r['opening_row']:r['text'] for r in review['preferred_menu_targets_if_native_280px_confirmed']}
    targets={};numbers=review['target_rows'];by_current={}
    for item in review['items']:
        n=item['opening_row'];r=rows[n]
        assert r['id']==item['id'] and r['source_sha256']==item['source_sha256']
        text=preferred.get(n,item['reviewed_catalog_text'])
        target=dict(source_offset=r['source_offset'],source_sha256=r['source_sha256'],text=text,
                    status='meaning_reviewed',encoding_profile='dialogue_fullwidth_cp932')
        assert r['id'] not in selection['translations']
        selection['translations'][r['id']]=target
        current=r['source_offset']+shift;targets[current]=target;by_current[current]=r
    moved,changes=relocate_script(before,targets);out=bytearray(moved);pool=parse_pool(before)['pool_offset']
    for c in changes:
        r=by_current[c['old_offset']];c['prior_build_source_offset']=c['old_offset'];c['old_offset']=r['source_offset'];c['id']=r['id']
    # Two physical lines retain the original three logical source identities.
    encoded,display=encode_dialogue('My name is \u25cf.','\u25cf');offset=len(out)
    out.extend(encoded+b'\0\0');word=(offset-pool)//2
    out[85288:85292]=operand_instruction(5,4,word)
    out[85296:85304]=operand_instruction(10,0,85304//2)+bytes(4)
    group_id='harbor_player_introduction_0.1.10'
    for c in changes:
        if c['id'] in (rows[331]['id'],rows[332]['id']):
            c['original_reference_instructions']=c['reference_instructions'];c['reference_instructions']=[];c['layout_group_id']=group_id
    first=next(c for c in changes if c['id']==rows[330]['id'])
    fragment=dict(id=group_id+':page:0:line:1',text='My name is \u25cf.',display_text=display,new_offset=offset,
                  new_byte_length=len(encoded),pool_word_offset=word,reference_instructions=[85288])
    group=dict(id=group_id,source_offsets=[rows[n]['source_offset'] for n in (330,331,332)],
               original_span=[85280,85312],original_span_sha256=sha(before[85280:85312]),
               layout_profile='opening_player_name_six_glyphs_v1',max_display_units=31,max_lines_per_page=3,
               max_expanded_pixel_width=208,max_player_name_glyphs=6,worst_case_expanded_pixels=197,
               text='Ah, yes. My name is \u25cf.',pages=[[copy.deepcopy(first),fragment]],display_helper_word=2030)
    old=simulate_group(before,85280,85312);new=simulate_group(out,85280,85312)
    assert len(old)==len(new)==1 and old[0]['helper']==new[0]['helper']==2030 and old[0]['args']==new[0]['args']
    assert new[0]['lines']==[first['display_text'],display]
    assert ''.join(old[0]['lines']).count('\u25cf')==''.join(new[0]['lines']).count('\u25cf')==1
    allowed={x for c in changes for p in c.get('original_reference_instructions',c['reference_instructions']) for x in range(p,p+4)}|set(range(85296,85304))
    assert all(before[i]==out[i] for i in range(len(before)) if i not in allowed)
    report['changes'].extend(changes);report['layout_groups'].append(group)
    verify_layout(bytes(out),report['changes'],report['layout_groups'])
    assert len(out)<0x78000 and len(report['changes'])==624
    packed=compress(bytes(out),0xa695);assert decompress(packed,0xa695)[0]==out
    report.update(decoded_size=len(out),encoded_size=len(packed),decoded_sha256=sha(out),runtime_allocation_verified=False)
    selection['excluded_groups']=[g for g in selection['excluded_groups'] if not set(g['opening_rows'])&set(numbers)]
    selection['incremental_layout_groups']=[group]
    selection['menu_layout_evidence'].append(dict(version='0.1.10',max_measured_advance=251,available_pixels=280,
         basis='Centered choice window from user capture, pending live validation; original indentation and one-line choices retained.'))
    for p in (REVIEW,'tools/harbor_gap_patch.py'):
        selection['review_inputs_sha256'][p]=sha((ROOT/p).read_bytes())
    return packed,report,selection,dict(added_source_rows=numbers,added_fragments=len(changes),
        unchanged_prior_bytes_except_declared_vm_operands=True,introduction_helper_and_arguments_preserved=True,
        dynamic_name_tokens_preserved=True,menu_max_units=31,menu_max_pixels=251,script_size=len(out),allocation_bound=0x78000)

def nameplates(source):
    ix=read(ASSETS/'packs_870-1080_names/index.json');generation=read(ASSETS/'generation.json')
    packs={};images={};reports=[];copies=[]
    for name,n in NAMES.items():
        gen=next(g for g in generation['images'] if g['name']==name)
        path=Path(re.search(r'as (C:.*?\.png) by default',gen['output_hint']).group(1))
        original_image=Image.open(path).convert('RGBA');alpha=original_image.getchannel('A')
        assert alpha.getextrema()==(0,255),'Image generation must supply real transparency'
        bbox=alpha.point(lambda v:255 if v>=12 else 0).getbbox();cut=original_image.crop(bbox)
        scale=min(20/cut.height,122/cut.width);size=(round(cut.width*scale),round(cut.height*scale))
        native=Image.new('RGBA',(144,32));native.paste(cut.resize(size,Image.Resampling.LANCZOS),((144-size[0])//2,6))
        images[name+'_import.png']=native;copies.append((path,ASSETS/'generated'/f'{name}.png'))
        for ci in (3,4):
            rec=next(r for r in ix['textures'] if r['id']==f'02:{n:05d}/{ci:05d}:0')
            for occurrence in rec['occurrences']:
                pack=occurrence['pack']
                if pack not in packs:
                    raw=source.resource('02.DAT',pack);d,used=decompress(raw,0x1731)
                    assert not any(raw[used:]);packs[pack]=dict(raw=raw,decoded=d,index=parse_index(d,len(d)),children={})
                p=packs[pack];data=child(p['decoded'],p['index'],ci)
                assert sha(data)==occurrence['source_sha256']
                row=texture_records(data)[0];wanted=native
                if ci==4:
                    old=np.asarray(decode_texture(data,row));colors,count=np.unique(old[old[:,:,3]>200,:3],axis=0,return_counts=True)
                    rgb=tuple(int(v) for v in colors[count.argmax()]);wanted=Image.new('RGBA',native.size,rgb+(0,));wanted.putalpha(native.getchannel('A'))
                patched,preview,pixels=encode_texture(data,row,wanted);p['children'][ci]=patched
                images[f'{name}_native_{ci}.png']=preview
                reports.append(dict(name=name,pack=pack,child=ci,source_sha256=sha(data),patched_sha256=sha(patched),
                                    changed_pixels=pixels,width=144,height=32,ink_bounds=preview.getbbox()))
    replacements={}
    for n,p in packs.items():
        d=repack(p['decoded'],p['children']);idx=parse_index(d,len(d))
        for e in idx['entries']:
            assert child(d,idx,e['id'])==p['children'].get(e['id'],child(p['decoded'],p['index'],e['id']))
        raw=compress(d,0x1731);assert decompress(raw,0x1731)[0]==d;replacements[n]=raw
    return replacements,dict(names=list(NAMES),pack_count=len(packs),layers=reports,
        method='Generated transparent lettering; aspect-preserving crop/downsample to native geometry and original-palette quantization. Matching alpha masks replace shadow layers. All other portrait layers unchanged.'),images,copies

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    prior=read(PRIOR/'manifest.json')
    with GameSource(PRIOR/prior['output_iso']) as source:
        _,script,selection,checks=script_patch(source);_,names,images,copies=nameplates(source)
    print(json.dumps(dict(mode='write' if a.write else 'dry run',checks=checks,names=names,
        targets=[dict(id=k,text=v['text']) for k,v in selection['translations'].items() if k not in read(ROOT/'work/translation/en/opening_harbor_0.1.5.targets.json')['translations']]),indent=2),flush=True)
    if not a.write:return
    (ASSETS/'generated').mkdir(exist_ok=True);(ASSETS/'native').mkdir(exist_ok=True)
    for src,dst in copies:shutil.copyfile(src,dst)
    for name,im in images.items():im.save(ASSETS/'native'/name)
    (ROOT/TARGET).write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
    (ASSETS/'import_report.json').write_text(json.dumps(names,indent=2)+'\n')
    (ROOT/'docs/harbor_gap_static_0.1.10.json').write_text(json.dumps(checks,indent=2)+'\n')

if __name__=='__main__':main()
