"""Convert generated English glyphs into native battle-label sprites."""
import argparse,json
import numpy as np
from PIL import Image
from sn3_archive import ROOT,parse_v4,parse_index,child,GameSource
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import sha
F=ROOT/'work/ui/battle_ui_0.1.25'
Y=[85,240,395,550,705,860,1015,1170]
LABELS=['Move','Attack','Summon','Special','Items','Swap Weapon','Stance','Next']

def glyph(n,size):
 sheet=Image.open(F/'buttons_generated.png').convert('RGBA');assert sheet.size==(1112,1414)
 im=sheet.crop((620,Y[n]+15,1040,Y[n]+95));arr=np.array(im)
 mask=((arr[:,:,0]>220)&(arr[:,:,1]>190)&(arr[:,:,2]>120))|((arr[:,:,0]<100)&(arr[:,:,1]<70)&(arr[:,:,2]<55))
 arr[:,:,3]=np.where(mask,arr[:,:,3],0)
 im=Image.fromarray(arr);box=im.getbbox();assert box;im=im.crop(box)
 im.thumbnail((size[0]-2,size[1]-2),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',size);out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return out

def prepare(source):
 original=source.resource('01.DAT',105);idx=parse_v4(original);replacements={};images=[];records=[]
 for n,k in enumerate(range(3,10)):
  data=child(original,idx,k);rows=texture_records(data);assert len(rows)==1
  old=decode_texture(data,rows[0]);assert old.size==(64,16)
  art=glyph(n,old.size);packed,native,changed=encode_texture(data,rows[0],art)
  assert len(packed)==len(data);replacements[k]=packed;images.append((f'command_{k}.png',native))
  records.append(dict(label=LABELS[n],bank='01.DAT',path=[105,k],texture=0,source_sha256=sha(data),output_sha256=sha(packed),changed_pixels=changed))
 output=repack(original,replacements);oi=parse_v4(output)
 for k in range(idx['count']):
  if k not in replacements:assert child(original,idx,k)==child(output,oi,k)
 tutorial=source.resource('02.DAT',3889);ti=parse_index(tutorial,len(tutorial));data=child(tutorial,ti,1)
 assert sha(data)=='ed92b4b773983257e78860e54bde37127c9984dd45f8d3a8ec8891f1b282038a'
 rows=texture_records(data);assert len(rows)==1
 old=decode_texture(data,rows[0]);assert old.size==(288,208)
 generated=Image.open(F/'next_generated.png').convert('RGBA').resize(old.size,Image.Resampling.LANCZOS)
 roi=(247,177,287,197);art=old.copy();art.paste(generated.crop(roi),roi)
 packed,native,changed=encode_texture(data,rows[0],art)
 mask=np.ones((208,288),dtype=bool);mask[177:197,247:287]=False
 assert np.array_equal(np.asarray(native)[mask],np.asarray(old)[mask])
 patched=repack(tutorial,{1:packed});pi=parse_index(patched,len(patched))
 assert all(child(tutorial,ti,k)==child(patched,pi,k) for k in (0,2))
 images.append(('next.png',native.crop(roi)))
 records.append(dict(label='Next',bank='02.DAT',path=[3889,1],texture=0,roi=roi,source_sha256=sha(data),output_sha256=sha(packed),changed_pixels=changed,outside_roi_unchanged=True))
 return {3889:patched},{105:output},images,dict(records=records,untouched_children_verified=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 with GameSource(ROOT/'work/output/0.1.24/Summon_Night_3_EN_0.1.24.iso') as source:_,_,images,r=prepare(source)
 print(json.dumps(r,indent=2))
 if a.write:
  folder=F/'native';folder.mkdir(exist_ok=True)
  for n,im in images:im.save(folder/n)
  sheet=Image.new('RGBA',(256,len(images)*64))
  for n,(_,im) in enumerate(images):sheet.alpha_composite(im.resize((256,64),Image.Resampling.NEAREST),(0,n*64))
  sheet.save(F/'native_preview.png');(F/'graphics.report.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
