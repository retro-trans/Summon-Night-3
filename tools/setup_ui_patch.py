"""Render reviewed setup labels and re-encode bounded native indexed textures."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sn3_archive import ROOT, GameSource, parse_index, child
from sn3_codec import decompress, compress
from sn3_repack import repack
from sn3_ui_textures import texture_records, decode_texture

OUT = ROOT / 'work/ui/setup_0.1.6_r2'
FONT = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')
NARROW = Path('C:/Windows/Fonts/ARIALNB.TTF')
CREAM=(254,242,214,255)
BROWN=(73,43,1,255)


def sha(data):return hashlib.sha256(data).hexdigest()


def render_text(image, text, rect, maximum=16, minimum=8, fill=CREAM, outline=BROWN, stroke=1, font_path=BOLD, align='center', leading=2):
    x,y,w,h=rect
    for size in range(maximum,minimum-1,-1):
        font=ImageFont.truetype(str(font_path),size)
        draw=ImageDraw.Draw(image)
        lines=[]
        for para in text.split('\n'):
            line=''
            for word in para.split(' '):
                trial=line+' '+word if line else word
                if draw.textlength(trial,font=font)+stroke*2 <= w:
                    line=trial
                else:
                    if not line:break
                    lines.append(line);line=word
            else:
                lines.append(line);continue
            break
        else:
            line_height=size+leading
            if len(lines)*line_height<=h and all(draw.textlength(t,font=font)+stroke*2<=w for t in lines):
                yy=y+(h-len(lines)*line_height)//2
                for line in lines:
                    width=draw.textlength(line,font=font)
                    xx=x+(w-width)/2 if align=='center' else x+stroke
                    draw.text((xx,yy),line,font=font,fill=fill,stroke_width=stroke,stroke_fill=outline,anchor='lt')
                    yy+=line_height
                assert ' '.join(lines)==' '.join(text.split())
                return {'text':text,'lines':lines,'font':font_path.name,'size':size,'rect':rect}
    raise ValueError('Full text cannot fit readable bounds: '+text)


def blank_banner(image, box):
    # Horizontal wood grain: replicate a text-free strip at the same Y coordinate.
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        for x in range(x0,x1):image.putpixel((x,y),image.getpixel((8+(x%10),y)))


def pixels_linear(data,row):
    bpp=1 if row['format']==5 else .5
    row_bytes=int(row['pitch']*bpp)
    height=row['data_size']//row_bytes
    raw=data[row['data_offset']:row['data_offset']+row['data_size']]
    if row['swizzled']:
        linear=bytearray(len(raw))
        for y in range(height):
            for x in range(0,row_bytes,16):
                off=((y//8)*(row_bytes//16)+x//16)*128+(y%8)*16
                linear[y*row_bytes+x:y*row_bytes+x+16]=raw[off:off+16]
        return linear,row_bytes,height
    return bytearray(raw),row_bytes,height


def encode_texture(data,row,image):
    """Keep the palette/geometry and untouched indices; invert the verified swizzle."""
    before=decode_texture(data,row)
    old=np.asarray(before);new=np.asarray(image)
    changed=np.any(old!=new,axis=2)
    pal=row['palette_base'];offset,size,fmt,count=struct.unpack_from('<4I',data,pal+4)
    assert fmt==3 and count in (16,256)
    palette=np.frombuffer(data[pal+offset:pal+offset+size],dtype=np.uint8).reshape(count,4)
    # Premultiplied color distance respects transparent palette entries.
    def metric(rgba):
        a=rgba.astype(np.float32)
        a[:,:3]*=a[:,3:4]/255
        return a
    p=metric(palette)
    wanted=new[changed]
    nearest=[]
    for start in range(0,len(wanted),1024):
        block=metric(wanted[start:start+1024])
        nearest.extend(np.square(block[:,None,:]-p[None,:,:]).sum(axis=2).argmin(axis=1).tolist())
    linear,row_bytes,height=pixels_linear(data,row)
    for (y,x),index in zip(np.argwhere(changed),nearest):
        if row['format']==5:linear[y*row_bytes+x]=index
        else:
            n=y*row_bytes+x//2;shift=4*(x%2)
            linear[n]=(linear[n]&~(15<<shift))|(index<<shift)
    if row['swizzled']:
        encoded=bytearray(len(linear))
        for y in range(height):
            for x in range(0,row_bytes,16):
                off=((y//8)*(row_bytes//16)+x//16)*128+(y%8)*16
                encoded[off:off+16]=linear[y*row_bytes+x:y*row_bytes+x+16]
    else:encoded=linear
    out=bytearray(data);a=row['data_offset'];out[a:a+len(encoded)]=encoded
    decoded=decode_texture(bytes(out),row)
    assert np.array_equal(np.asarray(decoded)[~changed],old[~changed])
    expected=new.copy();expected[changed]=palette[nearest]
    assert np.array_equal(np.asarray(decoded),expected)
    return bytes(out),decoded,int(changed.sum())


def prepare():
    path=ROOT/'work/translation/en/setup_ui.targets.json'
    catalog=json.loads(path.read_text(encoding='utf-8'))
    for item in catalog['inputs']:
        assert sha((ROOT/item['path']).read_bytes())==item['sha256']
    review_path=ROOT/'work/translation/en/setup_ui.compact_review.json'
    review=json.loads(review_path.read_text(encoding='utf-8'))
    texts={e['id']:e['target_full'] for e in catalog['entries'] if e['meaning_status']=='meaning_reviewed'}
    replacements={};records=[];images=[]
    labels={5:'Delete',6:'Auto-Name',7:'Confirm',8:'Hira',9:'Kata',10:'ABC\n123',11:'Sym.',12:'Kanji'}
    with GameSource() as source:
        for pack_number in (28,29,30,31,32):
            raw=source.resource('02.DAT',pack_number)
            try:
                index=parse_index(raw,len(raw));decoded=raw;was_compressed=False
            except ValueError:
                decoded,used=decompress(raw,0x9831,16*1024*1024)
                assert not any(raw[used:])
                index=parse_index(decoded,len(decoded));was_compressed=True
            new_children={}
            children=(1,8,9,10,11,12) if pack_number in (28,29) else (1,2,3)
            for ci in children:
                original=child(decoded,index,ci);out=original
                for row in texture_records(original):
                    n=row['number'];im=decode_texture(original,row);before=im.copy();layout=[];tag=None
                    if pack_number in (28,29):
                        if ci==1 and n in (0,1):
                            if n==0:
                                blank_banner(im,(28,29,210,50))
                                layout.append(render_text(im,texts['setup.select_prompt'],(25,30,188,20),13,11,font_path=NARROW))
                            else:
                                blank_banner(im,(25,6,215,51))
                                layout.append(render_text(im,texts['select.affinity'],(22,7,192,44),14,11,font_path=NARROW))
                            tag='select_heading'
                        elif ci==1 and n==4:
                            for yy in range(14,43):
                                samples=[im.getpixel((xx,yy)) for xx in range(44,94)]
                                samples=[p for p in samples if p[0]>180 and 100<p[1]<210 and 65<p[2]<175]
                                color=tuple(int(v) for v in np.median(samples,axis=0))
                                for xx in range(44,94):im.putpixel((xx,yy),color)
                            layout.append(render_text(im,'Confirm',(42,17,51,22),12,10,font_path=NARROW));tag='confirm_button'
                        elif ci==8:
                            im=Image.new('RGBA',im.size);tag='affinity_heading_moved_to_description'
                        elif ci in (9,10,11,12) and n==0:
                            affinity=['machine','yokai','spirit','beast'][ci-9]
                            im=Image.new('RGBA',im.size)
                            layout.append(render_text(im,texts['affinity.'+affinity]+' Affinity',(1,0,198,20),16,14))
                            layout.append(render_text(im,texts['description.'+affinity],(1,21,198,114),11,9,font_path=FONT,leading=1))
                            tag='description.'+affinity
                    else:
                        if ci==1 and n in labels:
                            im=Image.new('RGBA',im.size)
                            layout.append(render_text(im,labels[n],(0,0,im.width,im.height),10 if n!=10 else 7,7,
                                                      font_path=NARROW,stroke=0,leading=0,fill=(253,233,157,255)))
                            tag='name_label_'+str(n)
                        elif ci==1 and n in (1,42):
                            ranges=[(95,0,127,24,'Delete'),(146,0,220,24,'Auto-Name')] if n==1 else [(23,0,55,24,'Delete'),(74,0,134,24,'Auto-Name')]
                            for x0,y0,x1,y1,label in ranges:
                                ImageDraw.Draw(im).rectangle((x0,y0,x1-1,y1-1),fill=(0,0,0,0))
                                layout.append(render_text(im,label,(x0,y0,x1-x0,y1-y0),11,9,font_path=NARROW,outline=(130,33,2,255)))
                            tag='name_footer'
                        elif ci==1 and n==2:
                            ImageDraw.Draw(im).rectangle((30,0,63,15),fill=(0,0,0,0))
                            layout.append(render_text(im,'Confirm',(30,0,34,16),10,8,font_path=NARROW,outline=(130,33,2,255)));tag='start_confirm'
                        elif ci==2 and n in (0,1):
                            blank_banner(im,(33,7,196,49))
                            target=texts['name.protagonist_heading' if n==0 else 'name.summon_heading']
                            layout.append(render_text(im,target,(18,8,185,40),17,12,font_path=NARROW));tag='name_heading'
                        elif ci==3 and n==0:
                            specs=[(216,13,30,18,'Delete'),(246,13,58,18,'Auto-Name'),(304,13,39,36,'Confirm'),
                                   (155,31,30,17,'Hira'),(185,31,30,17,'Kata'),(215,31,30,17,'ABC\n123'),
                                   (245,31,30,17,'Sym.'),(275,31,30,17,'Kanji')]
                            draw=ImageDraw.Draw(im)
                            for x,y,w,h,label in specs:
                                draw.rectangle((x+3,y+3,x+w-4,y+h-4),fill=(62,37,0,255))
                                layout.append(render_text(im,label,(x+2,y+2,w-4,h-4),9 if '\n' not in label else 6,6,
                                                          font_path=NARROW,fill=(151,110,49,255),stroke=0,leading=0))
                            tag='name_background_labels'
                    if not tag:continue
                    # Inversion identity check, including guard rows and nibble ordering.
                    identity,_,_=encode_texture(original,row,before)
                    assert identity==original
                    out,result,changed=encode_texture(out,row,im)
                    name=f'02_{pack_number:05d}_{ci:05d}_sprite_{n:03d}.png'
                    records.append({'sprite_id':f'02:{pack_number:05d}/{ci:05d}:sprite:{n:03d}',
                                    'tag':tag,'image_file':name,'source_resource_sha256':sha(original),
                                    'width':im.width,'height':im.height,'changed_pixels':changed,'layout':layout,
                                    'decoded_rgba_sha256':sha(result.tobytes())})
                    images.append((name,result))
                if out!=original:new_children[ci]=out
            packed=repack(decoded,new_children)
            compressed=compress(packed,0x9831) if was_compressed else packed
            assert (decompress(compressed,0x9831)[0] if was_compressed else compressed)==packed
            new_index=parse_index(packed,len(packed))
            for e in index['entries']:
                if e['id'] not in new_children:assert child(decoded,index,e['id'])==child(packed,new_index,e['id'])
            replacements[pack_number]=compressed
    report={'schema_version':1,'version':'0.1.6','scope':'Character selection, all affinities and name-entry graphics for both protagonists and naming variants.',
            'inputs_sha256':{str(path.relative_to(ROOT)).replace('\\','/'):sha(path.read_bytes()),
                            str(review_path.relative_to(ROOT)).replace('\\','/'):sha(review_path.read_bytes()),
                            'tools/setup_ui_patch.py':sha(Path(__file__).read_bytes())},
            'font_inputs_sha256':{str(p):sha(p.read_bytes()) for p in (FONT,BOLD,NARROW)},
            'sprite_count':len(records),'records':records,
            'packs':[{'number':n,'sha256':sha(b),'bytes':len(b)} for n,b in replacements.items()],
            'native_palette_and_dimensions_preserved':True,'unchanged_pixels_preserved':True,'roundtrip_verified':True,
            'runtime_verified':False}
    return replacements,report,images


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    replacements,report,images=prepare()
    print(json.dumps({'mode':'write' if args.write else 'dry run','destination':str(OUT),
                      'sprite_count':report['sprite_count'],'packs':report['packs'],
                      'samples':[r for r in report['records'] if r['sprite_id'].startswith(('02:00028/00010','02:00030/00003','02:00028/00001'))]},indent=2))
    if args.write:
        OUT.mkdir(parents=True,exist_ok=False)
        for name,im in images:im.save(OUT/name)
        for n,data in replacements.items():(OUT/f'pack_{n:05d}.bin').write_bytes(data)
        (OUT/'index.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
