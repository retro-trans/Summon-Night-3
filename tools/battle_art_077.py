"""Mechanically crop generated encounter lettering and import native textures."""
import json,hashlib
from PIL import Image,ImageOps
from sn3_archive import ROOT,parse_v4,child
from sn3_ui_textures import texture_records,decode_texture
from sn3_repack import repack
from setup_ui_patch import encode_texture
F=ROOT/'work/ui/battle_0.1.77'
T=ROOT/'work/translation/en/battle_0.1.77'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare(source,write_assets=False):
 cfg=json.loads((T/'titles.json').read_text());atlas=F/'generated/title_atlas.png'
 assert sha(atlas.read_bytes())==cfg['atlas_sha256']
 sheet=Image.open(atlas).convert('RGBA');assert sheet.size==(1535,1025)
 out={};rows=[];images=[]
 for e in cfg['entries']:
  top=e['resource'];b=source.resource('01.DAT',top);ix=parse_v4(b);leaf=child(b,ix,4)
  assert sha(leaf)==e['source_sha256'];textures=texture_records(leaf);assert len(textures)==1
  old=decode_texture(leaf,textures[0]);assert old.size==tuple(e['native_size'])
  if e['atlas_cell'] is None:
   prior=source.resource('01.DAT',43);pi=parse_v4(prior);pd=child(prior,pi,4)
   im=decode_texture(pd,texture_records(pd)[0])
  else:
   i=e['atlas_cell'];col=i%4;row=i//4;im=sheet.crop((round(col*sheet.width/4),round(row*sheet.height/4),round((col+1)*sheet.width/4),round((row+1)*sheet.height/4)))
   box=im.getchannel('A').point(lambda v:255 if v>=32 else 0).getbbox();assert box
   im=ImageOps.expand(im.crop(box),border=3,fill=(0,0,0,0))
  im=im.resize(old.size,Image.Resampling.LANCZOS)
  assert im.getchannel('A').getextrema()==(0,255)
  same,_,_=encode_texture(leaf,textures[0],old);assert same==leaf
  packed,native,changed=encode_texture(leaf,textures[0],im);assert changed and len(packed)==len(leaf)
  patched=repack(b,{4:packed});ni=parse_v4(patched)
  assert all(child(b,ix,k)==child(patched,ni,k) for k in range(ix['count']) if k!=4)
  out[top]=patched;images.append((top,native));rows.append(dict(e,output_sha256=sha(packed),changed_pixels=changed,other_children_unchanged=True))
 if write_assets:
  (F/'native').mkdir(exist_ok=True)
  for n,im in images:im.save(F/'native'/f'title_{n}.png')
  w=max(im.width for _,im in images)+8;h=max(im.height for _,im in images)+8
  page=Image.new('RGBA',(w*2,((len(images)+1)//2)*h),(110,110,110,255))
  for i,(n,im) in enumerate(images):page.alpha_composite(im,(i%2*w,i//2*h))
  page.save(F/'native/contact.png')
 report=dict(entries=rows,translated_sprites=len(rows),full_remaining_encounter_title_category=True,native_geometry_codec_palette_preserved=True)
 return {'01.DAT':out},report
