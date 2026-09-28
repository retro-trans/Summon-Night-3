"""Import the generated Night Talk lettering into original 120x24 palettes."""
import json
from PIL import Image
from sn3_archive import ROOT,parse_index,child
from sn3_codec import decompress,compress
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from stages_patch import sha
NAMES=['Nup','Belfraw','Alieze','Will','Ardylia','Kyuuma','Falzen','Fariel','Yafha','Kyle','Sonolar','Scarrel','Yard','Kunon','Misumi','Subaru','Phlaiz','Marurur','Azlier']
ART=ROOT/'work/ui/night_talk_0.1.37'

def prepare_names(source):
    sheet=Image.open(ART/'names_generated.png').convert('RGBA')
    assert sheet.size==(1536,1024) and sheet.getchannel('A').getextrema()[0]==0
    glossary=json.loads((ROOT/'work/glossary/character_reference_sn6_vita.json').read_text(encoding='utf8'))
    assert set(NAMES)<={r['short_name'] for r in glossary['entries']}
    replacements={};report=[]
    for i,name in enumerate(NAMES):
        n=1028+i;raw=source.resource('02.DAT',n);d,used=decompress(raw,0x1731);assert not any(raw[used:])
        ix=parse_index(d,len(d));old=child(d,ix,3);rows=texture_records(old)
        assert len(rows)==1 and (rows[0]['width'],rows[0]['height'])==(120,24)
        x=i%4*384;y=round(i//4*1024/5);bottom=round((i//4+1)*1024/5)
        im=sheet.crop((x,y,x+384,bottom));box=im.getchannel('A').point(lambda a:255 if a>=12 else 0).getbbox();assert box
        im=im.crop(box);im.thumbnail((102,17),Image.Resampling.LANCZOS)
        wanted=Image.new('RGBA',(120,24));wanted.alpha_composite(im,((120-im.width)//2,3))
        updated,native,_=encode_texture(old,rows[0],wanted);native.save(ART/(name.lower()+'_native.png'))
        assert native.getbbox() and native.getbbox()[2]<=114 and native.getbbox()[3]<=21
        out=repack(d,{3:updated});oi=parse_index(out,len(out))
        for e in ix['entries']:
            if e['id']!=3:assert child(d,ix,e['id'])==child(out,oi,e['id'])
        packed=compress(out,0x1731);assert decompress(packed,0x1731)[0]==out
        replacements[n]=packed
        report.append(dict(resource=n,child=3,name=name,source_sha256=sha(raw),output_sha256=sha(packed),original_name_texture_sha256=sha(old),name_texture_sha256=sha(updated),native_ink_bounds=native.getbbox(),portrait_children_unchanged=True))
    return replacements,report
