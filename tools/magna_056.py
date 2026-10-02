"""Import Magna lettering into original layers; relocate exact backlog labels."""
import argparse,json,struct,hashlib
import numpy as np
from PIL import Image
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_codec import decompress,compress
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from dialogue_encoding import encode_dialogue
ART=ROOT/'work/ui/magna_0.1.56'
TARGETS=ROOT/'work/translation/en/magna_0.1.56/targets.json'
def sha(b):return hashlib.sha256(b).hexdigest()

def identify(write=False):
 m=json.loads((ROOT/'work/output/0.1.55/manifest.json').read_text())
 assets=[]
 with GameSource(ROOT/'work/output/0.1.55'/m['output_iso']) as s:
  for n,key,layers in [(953,0x1731,[3,4]),(1113,0x9831,[1,2])]:
   raw=s.resource('02.DAT',n);d,u=decompress(raw,key);assert not any(raw[u:]);ix=parse_index(d,len(d))
   t=texture_records(child(d,ix,layers[0]))[0];w,h=t['width'],t['height']
   assets.append(dict(resource=n,key=key,layers=layers,width=w,height=h,ink_width=112 if w==144 else 76,ink_height=20 if h==32 else 16,y=6 if h==32 else 3,source_sha256=sha(raw),layer_sha256={str(i):sha(child(d,ix,i)) for i in layers}))
 spec=dict(version='0.1.56',source_label='マグナ',target='Magna',reference='work/glossary/cameo_nameplates_0.1.56.json',assets=assets)
 print(json.dumps({'mode':'write targets' if write else 'preview','spec':spec},indent=2,ensure_ascii=False),flush=True)
 if write:TARGETS.write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 return spec

def prepare_names(source,write_assets=False):
 spec=json.loads(TARGETS.read_text(encoding='utf8'));glossary=json.loads((ROOT/spec['reference']).read_text(encoding='utf8'))
 assert spec['target']=='Magna' and glossary['entries'][0]['short_name']=='Magna'
 im=Image.open(ART/'magna_generated.png').convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
 box=im.getchannel('A').point(lambda v:255 if v>=12 else 0).getbbox();assert box
 cut=im.crop(box);replacements={};reports=[]
 for asset in spec['assets']:
  n=asset['resource'];raw=source.resource('02.DAT',n);assert sha(raw)==asset['source_sha256']
  data,used=decompress(raw,asset['key']);assert not any(raw[used:]);idx=parse_index(data,len(data))
  scale=min(asset['ink_height']/cut.height,asset['ink_width']/cut.width);size=(round(cut.width*scale),round(cut.height*scale))
  native=Image.new('RGBA',(asset['width'],asset['height']));native.alpha_composite(cut.resize(size,Image.Resampling.LANCZOS),((asset['width']-size[0])//2,asset['y']))
  changes={};layers=[]
  for li,ci in enumerate(asset['layers']):
   old=child(data,idx,ci);assert sha(old)==asset['layer_sha256'][str(ci)]
   rows=texture_records(old);assert len(rows)==1;row=rows[0];assert (row['width'],row['height'])==native.size
   wanted=native
   if li:
    pixels=np.asarray(decode_texture(old,row));colors,counts=np.unique(pixels[pixels[:,:,3]>200,:3],axis=0,return_counts=True)
    color=tuple(int(v) for v in colors[counts.argmax()]);wanted=Image.new('RGBA',native.size,color+(0,));wanted.putalpha(native.getchannel('A'))
   patched,preview,changed=encode_texture(old,row,wanted);changes[ci]=patched
   if write_assets:preview.save(ART/f'magna_{n}_{ci}_native.png')
   assert preview.getbbox() and preview.getbbox()[3]<=asset['height']
   # Native palette, descriptors, offsets, and sprite allocation stay byte-identical.
   assert old[:row['data_offset']]==patched[:row['data_offset']]
   assert old[row['data_offset']+row['data_size']:]==patched[row['data_offset']+row['data_size']:]
   layers.append(dict(child=ci,source_sha256=sha(old),output_sha256=sha(patched),changed_pixels=changed,ink_bounds=preview.getbbox()))
  out=repack(data,changes);ni=parse_index(out,len(out))
  assert all(child(out,ni,e['id'])==changes.get(e['id'],child(data,idx,e['id'])) for e in idx['entries'])
  packed=compress(out,asset['key']);assert decompress(packed,asset['key'])[0]==out
  replacements[n]=packed;reports.append(dict(resource=n,target='Magna',layers=layers,source_sha256=sha(raw),output_sha256=sha(packed),other_children_unchanged=True))
 for n in [85,86,87]:
  raw=source.resource('02.DAT',n);data,used=decompress(raw,0x9831);assert not any(raw[used:]);idx=parse_index(data,len(data))
  table=child(data,idx,22);count=struct.unpack_from('<I',table)[0];assert count==255;out=bytearray(table);changes=[]
  for field in range(4,4+count*8,4):
   ptr=struct.unpack_from('<I',table,field)[0]
   if not ptr:continue
   assert 4+count*8<=ptr<len(table) and ptr%2==0
   end=ptr
   while table[end:end+2]!=b'\0\0':end+=2;assert end<len(table)
   label=table[ptr:end].decode('cp932')
   if label!=spec['source_label']:continue
   encoded,display=encode_dialogue('Magna',label);new=len(out);out.extend(encoded+b'\0\0');struct.pack_into('<I',out,field,new)
   changes.append(dict(field=field,old_offset=ptr,new_offset=new,text='Magna',display_text=display))
  assert changes,('Missing Magna backlog label',n)
  data2=repack(data,{22:bytes(out)});ix2=parse_index(data2,len(data2));assert all(child(data,idx,e['id'])==child(data2,ix2,e['id']) for e in idx['entries'] if e['id']!=22)
  for c in changes:
   ptr=struct.unpack_from('<I',out,c['field'])[0];assert out[ptr:ptr+len(c['display_text'])*2].decode('cp932')==c['display_text']
  packed=compress(data2,0x9831);assert decompress(packed,0x9831)[0]==data2
  replacements[n]=packed;reports.append(dict(resource=n,kind='backlog label',changes=changes,source_sha256=sha(raw),output_sha256=sha(packed),other_children_unchanged=True))
 return replacements,reports

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--identify',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.identify:identify(a.write)
 else:
  m=json.loads((ROOT/'work/output/0.1.55/manifest.json').read_text())
  with GameSource(ROOT/'work/output/0.1.55'/m['output_iso']) as source:r,reports=prepare_names(source,a.write)
  print(json.dumps(dict(mode='write preview sprites' if a.write else 'preview',replacements=sorted(r),reports=reports),indent=2),flush=True)
  if a.write:(ART/'import-validation.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf8')
