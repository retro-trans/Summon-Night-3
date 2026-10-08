"""Import English location and speaker labels into fixed native texture records."""
import json
from collections import defaultdict
from PIL import Image
import numpy as np
from sn3_archive import ROOT
from menu_art_075 import descend,replace_tree,tiles,fit,sha
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
F=ROOT/'work/ui/ui_0.1.79'
def new_tiles(file,labels,row_edges=None):
 im=Image.open(file).convert('RGBA');result={};height=len(labels)//2
 # Generated atlas is column-major; row silhouettes are detected from alpha.
 for col in range(2):
  x0=col*im.width//2;x1=(col+1)*im.width//2
  mask=np.asarray(im.getchannel('A'))[:,x0:x1]>200;on=mask.sum(axis=1)>3;bands=[];start=None
  for y,v in enumerate(list(on)+[False]):
   if v and start is None:start=y
   if not v and start is not None:
    if y-start>=5:bands.append((start,y))
    start=None
  merged=[]
  for lo,hi in bands:
   if merged and lo-merged[-1][1]<12:merged[-1]=(merged[-1][0],hi)
   else:merged.append((lo,hi))
  if row_edges:
   assert len(row_edges)==height+1
   merged=list(zip(row_edges,row_edges[1:]))
  assert len(merged)==height,(file,col,merged,height)
  for label,(lo,hi) in zip(labels[col*height:(col+1)*height],merged):
   crop=im.crop((x0,max(0,lo-3),x1,min(im.height,hi+3)))
   alpha=crop.getchannel('A').point(lambda a:255 if a>200 else 0);box=alpha.getbbox();assert box
   crop.putalpha(alpha);result[label]=crop.crop(box)
 return result

def prepare(source,write=False):
 spec=json.loads((F/'atlas_spec.json').read_text());old=json.loads((ROOT/'work/ui/menus_0.1.75/atlas_spec.json').read_text());art={};names={}
 for n,labels in enumerate(old['labels']):art.update(tiles(f'labels_{n}',labels))
 art.update(tiles('corrections',old['corrections']))
 for n,labels in enumerate(old['names']):names.update(tiles(f'names_{n}',labels))
 # Reviewed fixed rows keep descenders separate from the following label.
 names.update(new_tiles(F/'generated/speakers.png',spec['speakers']+['Guard'],[40,180,300,430,550,680,805,940]))
 for n,labels in enumerate(spec['labels']):
  edges=[12,103,187,275,362,448,536,622,709,797,886,974] if n>=2 else None
  art.update(new_tiles(F/'generated'/f'locations_{n}.png',labels,edges))
 cfg=json.loads((ROOT/'work/translation/en/ui_0.1.79/graphics.json').read_text());groups=defaultdict(list)
 for e in cfg['entries']:groups[(e['bank'],tuple(e['path']))].append(e)
 catalog=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());copies=defaultdict(set)
 for g in catalog['resources']:
  for o in g['occurrences']:copies[(o['bank'],g['source_sha256'])].add(tuple(o['path']))
 replacements=defaultdict(dict);reports=[]
 if write:(F/'native').mkdir(exist_ok=True)
 for (bank,path),entries in groups.items():
  before=descend(source.resource(bank,path[0]),path[1:]);data=before;rows=texture_records(before);changed=set()
  for e in entries:
   assert sha(before)==e['source_sha256']
   row=rows[e['sprite']];original=decode_texture(before,row)
   label=names[e['text']] if e['kind']=='nameplate' else art[e['text']]
   native=fit(label,original.size,'nameplate')
   data,decoded,pixels=encode_texture(data,row,native);assert len(data)==len(before) and texture_records(data)==rows
   changed.add(e['sprite']);id=bank[:2]+'_'+'_'.join(map(str,path))+'_'+str(e['sprite'])
   if write:decoded.save(F/'native'/(id+'.png'))
   reports.append(dict(e,id=id,native_size=original.size,changed_pixels=pixels))
  for r in rows:
   if r['number'] not in changed:assert decode_texture(before,r).tobytes()==decode_texture(data,r).tobytes()
  for p in copies[(bank,sha(before))]|{path}:
   if descend(source.resource(bank,p[0]),p[1:])==before:replacements[bank][p]=data
 packs={bank:{root:replace_tree(source.resource(bank,root),{p[1:]:v for p,v in paths.items() if p[0]==root}) for root in {p[0] for p in paths}} for bank,paths in replacements.items()}
 return packs,dict(entries=reports,translated_sprites=len(reports),leaf_occurrences=sum(map(len,replacements.values())),geometry_palette_codecs_preserved=True)
