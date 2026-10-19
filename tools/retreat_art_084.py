"""Use the neighboring native wooden button for both Retreat states."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from sn3_archive import ROOT,GameSource
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import descend,replace_tree,sha

def prepare(source,write=False):
 catalog=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text('utf8'));targets={};reports=[];previews=[]
 with GameSource() as original:
  for state,(leaf,reference) in enumerate([(73,15),(74,16)]):
   ref=descend(source.resource('02.DAT',1333),[10,reference]);row=texture_records(ref)[0];before=decode_texture(ref,row);art=before.copy()
   # Only the center text area changes. Keep every edge/frame pixel and alpha
   # from Load, including the selected state's highlight and wooden ornament.
   for y in range(3,21):
    left=np.array(before.getpixel((24,y)),dtype=float);right=np.array(before.getpixel((100,y)),dtype=float)
    for x in range(25,100):art.putpixel((x,y),tuple(np.rint(left+(right-left)*(x-24)/76).astype('uint8')))
   font=ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf',20);word=Image.new('RGBA',(100,30));draw=ImageDraw.Draw(word)
   draw.text((3,2),'Retreat',font=font,fill=(59,31,2,255) if state==0 else (248,212,143,255),stroke_width=1,stroke_fill=(255,230,176,255) if state==0 else (124,65,22,255))
   word=word.crop(word.getbbox()).resize((47,18),Image.Resampling.LANCZOS);art.alpha_composite(word,((112-word.width)//2,(24-word.height)//2))
   art.putalpha(before.getchannel('A'));packed,native,changed=encode_texture(ref,row,art)
   src=descend(original.resource('02.DAT',1333),[10,leaf]);group=next(g for g in catalog['resources'] if g['source_sha256']==sha(src));current=descend(source.resource('02.DAT',1333),[10,leaf]);uses=[]
   for o in group['occurrences']:
    assert o['bank']=='02.DAT';p=tuple(o['path']);assert descend(source.resource('02.DAT',p[0]),p[1:])==current
    targets[p]=packed;uses.append(list(p))
   old=decode_texture(current,texture_records(current)[0]);previews.append((old,before,native));reports.append(dict(state=state,reference=[1333,10,reference],occurrences=uses,width=112,height=24,changed_pixels=changed,source_sha256=sha(current),output_sha256=sha(packed),frame_and_palette_from_neighbor=True))
 packs={n:replace_tree(source.resource('02.DAT',n),{p[1:]:v for p,v in targets.items() if p[0]==n}) for n in {p[0] for p in targets}}
 if write:
  dest=ROOT/'work/ui/ui_0.1.84';dest.mkdir(parents=True,exist_ok=True);sheet=Image.new('RGBA',(336,48))
  for y,row in enumerate(previews):
   for x,im in enumerate(row):sheet.alpha_composite(im,(x*112,y*24))
  sheet.resize((1344,192),Image.Resampling.NEAREST).save(dest/'retreat-comparison.png')
 return packs,dict(states=reports,occurrences=len(targets),changed_packs=sorted(packs))
