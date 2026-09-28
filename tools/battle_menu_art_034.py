"""Convert generated English menu glyphs to the twelve native 64x16 sprites."""
import argparse,json
import numpy as np
from PIL import Image,ImageFilter
from sn3_archive import ROOT,parse_v4,child,GameSource
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import sha
F=ROOT/'work/ui/battle_menu_0.1.34'
LABELS=['End Turn','Battle Info','Unit List','Summon Index','Inventory','Options','Suspend','Retreat','Party Abilities','Support Skills','Brave Goals','Win/Lose']
CHILDREN=[10,11,12,13,14,15,17,16,20,21,19,18]
def glyph(n):
 sheet=Image.open(F/'labels_generated.png').convert('RGBA');assert sheet.size==(1536,1024)
 x=n%3*512;y=n//3*256;im=sheet.crop((x,y,x+512,y+256));arr=np.asarray(im)
 cream=(arr[:,:,0]>220)&(arr[:,:,1]>190)&(arr[:,:,2]>120)
 near=np.asarray(Image.fromarray(cream.astype('uint8')*255).filter(ImageFilter.MaxFilter(21)))>0
 brown=(arr[:,:,0]>40)&(arr[:,:,0]<135)&(arr[:,:,1]<35)&(arr[:,:,2]<30)&(arr[:,:,0]>2.5*arr[:,:,1])
 mask=cream|(near&brown);im.putalpha(Image.fromarray(mask.astype('uint8')*255));box=im.getbbox();assert box
 im=im.crop(box);im.thumbnail((62,14),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(64,16));out.alpha_composite(im,((64-im.width)//2,(16-im.height)//2));return out

def prepare(source):
 original=source.resource('01.DAT',105);idx=parse_v4(original);replacements={};images=[];records=[]
 for n,k in enumerate(CHILDREN):
  data=child(original,idx,k);rows=texture_records(data);assert len(rows)==1
  old=decode_texture(data,rows[0]);assert old.size==(64,16)
  packed,native,changed=encode_texture(data,rows[0],glyph(n));assert len(packed)==len(data)
  replacements[k]=packed;images.append((LABELS[n],native))
  records.append(dict(label=LABELS[n],bank='01.DAT',path=[105,k],source_sha256=sha(data),output_sha256=sha(packed),changed_pixels=changed))
 output=repack(original,replacements);oi=parse_v4(output)
 for k in range(idx['count']):assert child(output,oi,k)==replacements.get(k,child(original,idx,k))
 return {105:output},images,dict(records=records,other_children_unchanged=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write-preview',action='store_true');a=p.parse_args()
 with GameSource(ROOT/'work/output/0.1.33/Summon_Night_3_EN_0.1.33.iso') as source:_,images,r=prepare(source)
 print(json.dumps(r,indent=2))
 if a.write_preview:
  sheet=Image.new('RGBA',(256,12*64),(115,85,65,255))
  for n,(name,im) in enumerate(images):sheet.alpha_composite(im.resize((256,64),Image.Resampling.NEAREST),(0,n*64))
  sheet.save(F/'native_preview.png');(F/'graphics.report.json').write_text(json.dumps(r,indent=2)+'\n')
