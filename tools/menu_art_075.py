"""Import generated English art, preserving native geometry, palettes and codecs."""
import json,hashlib
from collections import defaultdict
import numpy as np
from PIL import Image
from sn3_archive import ROOT,parse_index,parse_v4,child
from sn3_repack import repack
from sn3_codec import decompress,compress,decoded_size
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
FOLDER=ROOT/'work/ui/menus_0.1.75'
def sha(b):return hashlib.sha256(b).hexdigest()
def unpack(data):
 for parser in (lambda d:parse_index(d,len(d)),parse_v4):
  try:return data,parser(data),None
  except ValueError:pass
 for key in (0x9831,0x1731,0xa695):
  try:
   if not 8<=decoded_size(data,key)<=6000000:continue
   raw,used=decompress(data,key,max_output=6000000)
   if any(data[used:]):continue
   for parser in (lambda d:parse_index(d,len(d)),parse_v4):
    try:return raw,parser(raw),key
    except ValueError:pass
  except ValueError:pass
 raise ValueError('Unknown container')
def descend(data,path):
 for n in path:
  raw,ix,_=unpack(data);data=child(raw,ix,n)
 return data
def replace_tree(data,targets):
 raw,ix,key=unpack(data);changes={}
 for n in {p[0] for p in targets}:
  group={p[1:]:v for p,v in targets.items() if p[0]==n}
  changes[n]=group[()] if () in group else replace_tree(child(raw,ix,n),group)
 out=repack(raw,changes)
 if key is not None:
  out=compress(out,key);check,used=decompress(out,key);assert check==repack(raw,changes) and used==len(out)
 return out
def tiles(name,labels,cols=2):
 im=Image.open(FOLDER/'generated'/f'{name}.png').convert('RGBA');a=np.asarray(im)[:,:,3];result={}
 for col in range(cols):
  left=col*im.width//cols;right=(col+1)*im.width//cols;on=(a[:,left:right]>200).sum(axis=1)>3
  bands=[];start=None
  for y,v in enumerate(list(on)+[False]):
   if v and start is None:start=y
   if not v and start is not None:
    if y-start>=5:bands.append((start,y))
    start=None
  # Letters with detached dots may produce tiny bands; join nearby pieces.
  merged=[]
  for lo,hi in bands:
   if merged and lo-merged[-1][1]<(0 if name.startswith('shop_') else 14):merged[-1]=(merged[-1][0],hi)
   else:merged.append((lo,hi))
  wanted=labels[col::cols];assert len(merged)>=len(wanted),(name,col,merged,len(wanted))
  assert len(merged)==len(wanted),(name,col,'extra rows',merged)
  for label,(lo,hi) in zip(wanted,merged):
   crop=im.crop((left,max(0,lo-3),right,min(im.height,hi+3)))
   mask=crop.getchannel('A').point(lambda x:255 if x>200 else 0);box=mask.getbbox();assert box
   result[label]=crop.crop(box)
 return result
def fit(im,size,kind):
 if kind=='shop':return im.resize(size,Image.Resampling.LANCZOS)
 if kind in ('frame','page'):return im.resize(size,Image.Resampling.LANCZOS)
 w,h=size;maxh=max(8,h-2);maxw=max(8,w-4)
 factor=min(maxw/im.width,maxh/im.height)
 scaled=im.resize((max(1,round(im.width*factor)),max(1,round(im.height*factor))),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',size);out.alpha_composite(scaled,((w-scaled.width)//2,(h-scaled.height)//2));return out
def prepare(source,write=False):
 spec=json.loads((FOLDER/'atlas_spec.json').read_text());art={};shops={};names={};mini={};slots={}
 for n,labels in enumerate(spec['labels']):art.update(tiles(f'labels_{n}',labels))
 art.update(tiles('corrections',spec['corrections']))
 # Selected and unselected button columns use the same label sequence.
 im=Image.open(FOLDER/'generated/shop.png').convert('RGBA')
 for col,state in enumerate(('selected','unselected')):
  half=im.crop((col*im.width//2,0,(col+1)*im.width//2,im.height));tmp=FOLDER/'generated'/f'shop_{state}.png';half.save(tmp)
  shops[state]=tiles(f'shop_{state}',spec['shop'],1)
 for n,labels in enumerate(spec['names']):names.update(tiles(f'names_{n}',labels))
 mini=tiles('mini_labels',spec['mini_labels']);slots=tiles('slot_labels',spec['slot_labels'])
 entries=[]
 for cfg in ('graphics','minigames','nameplates'):entries+=json.loads((ROOT/f'work/translation/en/menus_0.1.75/{cfg}.json').read_text())['entries']
 groups=defaultdict(list)
 for e in entries:groups[(e['bank'],tuple(e['path']))].append(e)
 # Native leaf hashes identify exact duplicates, including compressed portraits.
 catalog=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());copies=defaultdict(set)
 for g in catalog['resources']:
  for o in g['occurrences']:copies[(o['bank'],g['source_sha256'])].add(tuple(o['path']))
 for root in [89]+list(range(1069,1332)):
  try:
   raw,ix,_=unpack(source.resource('02.DAT',root))
   for n in (1,2) if root!=89 else range(ix['count']):
    d=child(raw,ix,n);copies[('02.DAT',sha(d))].add((root,n))
  except ValueError:pass
 replacements=defaultdict(dict);report=[];folder=FOLDER/'native'
 if write:folder.mkdir(exist_ok=True)
 for (bank,path),rows in groups.items():
  print('Import',bank,path,flush=True)
  data=descend(source.resource(bank,path[0]),path[1:]);original=data;descs=texture_records(data)
  for e in rows:
   row=next(r for r in descs if r['number']==e['sprite']);old=decode_texture(data,row);same,_,_=encode_texture(data,row,old);assert same==data
   kind=e['kind'];text=e['text']
   if kind=='shop':generated=shops[e.get('state','unselected')][text]
   elif kind=='nameplate':generated=names[text]
   elif kind=='mini_label':generated=mini[text]
   elif kind=='slot_label':generated=slots[text]
   elif kind in ('page','frame'):
    generated=Image.open(FOLDER/'generated'/f'{text}.png').convert('RGBA')
    if text=='night_prompt':generated=generated.crop(generated.getchannel('A').point(lambda x:255 if x>200 else 0).getbbox())
   else:generated=art[text]
   native=fit(generated,old.size,kind)
   if kind=='shop':native.putalpha(old.getchannel('A'))
   before=data;data,decoded,changed=encode_texture(data,row,native);assert len(data)==len(before) and texture_records(data)==descs
   ident=bank[:2]+'_'+'_'.join(map(str,path))+'_'+str(e['sprite'])
   if write:decoded.save(folder/(ident+'.png'))
   report.append(dict(e,id=ident,native_size=list(old.size),changed_pixels=changed,source_sha256=sha(original)))
  occurrences=copies[(bank,sha(original))]|{path}
  for p in occurrences:
   current=descend(source.resource(bank,p[0]),p[1:])
   if current!=original:continue # Earlier English copies are immutable inputs.
   if p in replacements[bank]:assert replacements[bank][p]==data
   replacements[bank][p]=data
 packs={bank:{root:replace_tree(source.resource(bank,root),{p[1:]:v for p,v in paths.items() if p[0]==root}) for root in {p[0] for p in paths}} for bank,paths in replacements.items()}
 result=dict(entries=report,translated_sprites=len(report),leaf_occurrences=sum(map(len,replacements.values())),codec_palette_geometry_preserved=True)
 if write:(folder/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 return packs,result
if __name__=='__main__':
 from sn3_archive import GameSource
 with GameSource(ROOT/'work/output/0.1.74/Summon_Night_3_EN_0.1.74.iso') as s:
  p,r=prepare(s,True);print(json.dumps({k:len(v) for k,v in p.items()}));print(r['translated_sprites'],r['leaf_occurrences'])
