"""Convert generated menu buttons to native palettes and replace exact copies."""
import argparse,hashlib,json
from PIL import Image
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture

FOLDER=ROOT/'work/ui/menu_0.1.15'
ROWS=[('Battle Prep',41,42),('Deployment',1,2),('Battle Info',71,72),
 ('Inventory',7,8),('Summon Index',9,10),('Options',11,12),('Save',13,14),
 ('Load',15,16),('Start Battle',31,32),('Party Abilities',3,4)]
Y=[(106,183),(234,310),(362,439),(490,567),(619,695),(749,828),(878,956),(1007,1085),(1136,1213),(1263,1339)]
def sha(b):return hashlib.sha256(b).hexdigest()
def descend(data,path):
 for n in path:data=child(data,parse_index(data,len(data)),n)
 return data
def replace_tree(data,targets):
 direct={p[0]:v for p,v in targets.items() if len(p)==1}
 for n in {p[0] for p in targets if len(p)>1}:
  assert n not in direct
  direct[n]=replace_tree(descend(data,[n]),{p[1:]:v for p,v in targets.items() if p[0]==n})
 return repack(data,direct)
def prepare(source):
 index=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text())
 atlas=Image.open(FOLDER/'buttons_atlas.png').convert('RGBA');assert atlas.size==(1024,1536)
 replacements={};images=[];report=[]
 with GameSource() as original:
  for row,(label,*children) in enumerate(ROWS):
   for state,n in enumerate(children):
    path=[1333,10,n];data=descend(original.resource('02.DAT',1333),path[1:]);h=sha(data)
    group=next(g for g in index['resources'] if g['source_sha256']==h)
    desc=texture_records(data);assert len(desc)==1
    old=decode_texture(data,desc[0]);assert old.size==(112,24)
    same,_,_=encode_texture(data,desc[0],old);assert same==data
    top,bottom=Y[row];left,right=((59,489),(537,967))[state]
    # Cropping, resampling, original alpha and palette conversion only;
    # the generated atlas supplies all visible English lettering and artwork.
    art=atlas.crop((left,top,right,bottom)).resize(old.size,Image.Resampling.LANCZOS)
    art.putalpha(old.getchannel('A'))
    packed,decoded,changed=encode_texture(data,desc[0],art)
    assert len(data)==len(packed)
    occurrences=[]
    for o in group['occurrences']:
     assert o['bank']=='02.DAT',o
     p=o['path'];current=descend(source.resource(o['bank'],p[0]),p[1:]);assert sha(current)==h,(label,p)
     replacements[tuple(p)]=packed;occurrences.append(o['id'])
    images.append((f'{row:02d}_{state}.png',decoded))
    report.append(dict(label=label,state='selected' if state==0 else 'unselected',source_sha256=h,native_sha256=sha(packed),native_size=list(old.size),atlas_crop=[left,top,right,bottom],occurrences=occurrences,changed_pixels=changed))
 packs={n:replace_tree(source.resource('02.DAT',n),{p[1:]:v for p,v in replacements.items() if p[0]==n}) for n in {p[0] for p in replacements}}
 return packs,images,dict(atlas_sha256=sha((FOLDER/'buttons_atlas.png').read_bytes()),buttons=report,occurrences=len(replacements),packs=sorted(packs))
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 with GameSource(ROOT/'work/output/0.1.14/Summon_Night_3_EN_0.1.14.iso') as source:packs,images,r=prepare(source)
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',**r),indent=2))
 if a.write:
  folder=FOLDER/'native';folder.mkdir(exist_ok=False)
  for n,im in images:im.save(folder/n)
  (folder/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
