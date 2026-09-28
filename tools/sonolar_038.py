"""Translate Sonolar's ordinary and battle nameplates, preserving native palettes."""
import json
import numpy as np
from PIL import Image
from sn3_archive import ROOT,parse_index,child
from sn3_codec import decompress,compress
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from stages_patch import sha
ART=ROOT/'work/ui/sonolar_0.1.38'
TARGETS=ROOT/'work/translation/en/sonolar_0.1.38/targets.json'

def prepare_names(source):
    spec=json.loads(TARGETS.read_text(encoding='utf8'))
    glossary=json.loads((ROOT/spec['reference']).read_text(encoding='utf8'))
    assert spec['target']=='Sonolar' and any(e['short_name']=='Sonolar' for e in glossary['entries'])
    original=Image.open(ART/'sonolar_generated.png').convert('RGBA')
    assert original.getchannel('A').getextrema()[0]==0
    box=original.getchannel('A').point(lambda v:255 if v>=12 else 0).getbbox();assert box
    cut=original.crop(box);replacements={};reports=[]
    for asset in spec['assets']:
        n=asset['resource'];raw=source.resource('02.DAT',n);assert sha(raw)==asset['source_sha256']
        data,used=decompress(raw,asset['key']);assert not any(raw[used:]);idx=parse_index(data,len(data))
        scale=min(asset['ink_height']/cut.height,asset['ink_width']/cut.width)
        size=(round(cut.width*scale),round(cut.height*scale))
        native=Image.new('RGBA',(asset['width'],asset['height']))
        native.alpha_composite(cut.resize(size,Image.Resampling.LANCZOS),((asset['width']-size[0])//2,asset['y']))
        changes={};layers=[]
        for li,ci in enumerate(asset['layers']):
            old=child(data,idx,ci);assert sha(old)==asset['layer_sha256'][str(ci)]
            rows=texture_records(old);assert len(rows)==1
            row=rows[0];assert (row['width'],row['height'])==native.size
            wanted=native
            if li:
                pixels=np.asarray(decode_texture(old,row));colors,counts=np.unique(pixels[pixels[:,:,3]>200,:3],axis=0,return_counts=True)
                color=tuple(int(v) for v in colors[counts.argmax()]);wanted=Image.new('RGBA',native.size,color+(0,));wanted.putalpha(native.getchannel('A'))
            patched,preview,changed=encode_texture(old,row,wanted);changes[ci]=patched
            preview.save(ART/f'sonolar_{n}_{ci}_native.png')
            assert preview.getbbox() and preview.getbbox()[3]<=asset['height']
            layers.append(dict(child=ci,source_sha256=sha(old),output_sha256=sha(patched),changed_pixels=changed,ink_bounds=preview.getbbox()))
        out=repack(data,changes);ni=parse_index(out,len(out))
        for e in idx['entries']:assert child(out,ni,e['id'])==changes.get(e['id'],child(data,idx,e['id']))
        packed=compress(out,asset['key']);assert decompress(packed,asset['key'])[0]==out
        replacements[n]=packed;reports.append(dict(resource=n,target=spec['target'],layers=layers,source_sha256=sha(raw),output_sha256=sha(packed),other_children_unchanged=True))
    return replacements,reports
