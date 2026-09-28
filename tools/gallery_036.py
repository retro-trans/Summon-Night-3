"""Gallery labels and bounded tutorial titles, based on immutable 0.1.35."""
import hashlib,json,struct,unicodedata
from PIL import Image
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from menu_art_015 import descend,replace_tree
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from dialogue_encoding import encode_dialogue
BASE=ROOT/'work/output/0.1.35'
ART=ROOT/'work/ui/gallery_0.1.36'
sha=lambda data:hashlib.sha256(data).hexdigest()

def prepare_elf():
    data=(BASE/'EBOOT.elf').read_bytes()
    return data,dict(entries=[],executable_unchanged=True,patched_elf_sha256=sha(data))

def prepare_tables(source):
    pack=source.resource('02.DAT',3)
    changes={};reports=[]
    metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
    with GameSource(ROOT/'work/source/original.iso') as original:
        for table,records,slot,stride,target in [(19,range(140,162),0,24,'Review Basics'),(38,[3],6,28,'Weapons & Range')]:
            old=descend(pack,[table]);out=bytearray(old);fields=set();rows=[]
            orig=descend(original.resource('02.DAT',3),[table])
            encoded=encode_dialogue(target,'')[0]
            width=sum(metrics[c]['proposed_advance_pixels'] for c in target)*.875
            assert width <= (116 if table==19 else 148)
            out.extend(bytes(-len(out)%2));new=len(out);out.extend(encoded+b'\0\0')
            for record in records:
                field=4+record*stride+slot*4
                before=struct.unpack_from('<I',old,field)[0]
                srcpos=struct.unpack_from('<I',orig,field)[0];end=orig.find(b'\0',srcpos)
                if table==19:assert orig[srcpos:end].decode('cp932')=='基礎知識の確認'
                else:assert orig[srcpos:end].decode('cp932')=='攻撃範囲と武器'
                struct.pack_into('<I',out,field,new);fields.update(range(field,field+4))
                rows.append(dict(record=record,slot=slot,source_offset=srcpos,source_sha256=sha(orig[srcpos:end]),previous_offset=before,new_offset=new,target=target,width_pixels=width))
            assert all(a==b for i,(a,b) in enumerate(zip(old,out)) if i not in fields)
            assert out[new:new+len(encoded)+2]==encoded+b'\0\0'
            changes[table]=bytes(out);reports.append(dict(table=table,changes=rows,unselected_bytes_unchanged=True))
    newpack=repack(pack,changes)
    master=source.resource('00.DAT',44);assert descend(master,[7])==pack
    master=repack(master,{7:newpack})
    # The generated image supplies the translated footer; all other frame pixels
    # are preserved exactly before native palette quantization.
    gallery=source.resource('02.DAT',3570);frame=descend(gallery,[2]);fr=texture_records(frame)[0]
    oldframe=decode_texture(frame,fr);art=Image.open(ART/'frame_generated.png').convert('RGBA')
    art=art.crop(art.getbbox()).resize((432,244),Image.Resampling.LANCZOS)
    replacement=oldframe.copy();box=(65,220,367,240);replacement.paste(art.crop(box),box)
    packedframe,decoded,_=encode_texture(frame,fr,replacement)
    for y in range(oldframe.height):
        for x in range(oldframe.width):
            if not (box[0]<=x<box[2] and box[1]<=y<box[3]):assert decoded.getpixel((x,y))==oldframe.getpixel((x,y))
    decoded.save(ART/'frame_native.png')
    data=descend(gallery,[3]);rows=texture_records(data);old=data
    sheet=Image.open(ART/'headings_generated.png').convert('RGBA')
    heading_reports=[]
    for n,half,label in [(25,0,'Illustrations'),(26,1,'Sound')]:
        im=sheet.crop((0,half*sheet.height//2,sheet.width,(half+1)*sheet.height//2));im=im.crop(im.getbbox())
        im.thumbnail((78,21),Image.Resampling.LANCZOS);native=Image.new('RGBA',(80,24));native.alpha_composite(im,((80-im.width)//2,(24-im.height)//2))
        data,out,_=encode_texture(data,rows[n],native);out.save(ART/f'heading_{n}_native.png');heading_reports.append(dict(sprite=n,text=label,rgba_sha256=sha(out.tobytes())))
    modes=Image.open(ART/'modes_generated.png').convert('RGBA')
    for n,half,label,width in [(21,0,'Play',32),(20,1,'Artwork',64)]:
        im=modes.crop((0,half*modes.height//2,modes.width,(half+1)*modes.height//2))
        im=im.crop(im.getbbox());im.thumbnail((54 if n==20 else 28,11),Image.Resampling.LANCZOS)
        # Opaque native overlays replace the shared View/Sound text. The blank
        # background strip comes from the generated footer, with matching rows.
        native=art.crop((40,221,41,237)).resize((width,16))
        native.alpha_composite(im,(4 if n==20 else (width-im.width)//2,0))
        if n==20:native.paste(art.crop((236,221,244,237)),(56,0))
        data,out,_=encode_texture(data,rows[n],native);out.save(ART/f'mode_{n}_native.png')
        heading_reports.append(dict(sprite=n,text=label,rgba_sha256=sha(out.tobytes())))
    for r in rows:
        if r['number'] not in (20,21,25,26):assert decode_texture(data,r).tobytes()==decode_texture(old,r).tobytes()
    updated=replace_tree(gallery,{(2,):packedframe,(3,):data})
    return {3:newpack,3570:updated},{},master,dict(tables=reports,units=[],graphics=dict(resource=3570,footer_box=list(box),footer_labels=['View','Sound Mode','Exit'],headings=heading_reports,unselected_pixels_unchanged=True))

if __name__=='__main__':
    with GameSource(BASE/'Summon_Night_3_EN_0.1.35.iso') as source:
        _,_,_,report=prepare_tables(source)
    print(json.dumps(report,indent=2))
