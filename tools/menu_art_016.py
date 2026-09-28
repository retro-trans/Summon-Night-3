"""Convert generated menu sprites and options labels; fixed native footprints."""
import argparse,json
from collections import defaultdict
import numpy as np
from PIL import Image
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import descend,replace_tree,sha
F=ROOT/'work/ui/menu_0.1.16'
ROWS=[('Win/Lose',[1333,10,5],[1333,10,6]),('Support Skills',[1333,10,65],[1333,10,66]),
 ('Brave Goals',[1333,10,67],[1333,10,68]),('Train Summons',[1333,10,69],[1333,10,70]),
 ('Retreat',[1333,10,73],[1333,10,74]),('Suspend Data',[1333,10,81],[1333,10,82]),
 ('Game Data',[1333,10,83],[1333,10,84]),('System',[1334,10,39],[1334,10,40]),
 ('Buy',[1332,1],[1332,2]),('Sell',[1332,3],[1332,4])]
Y=[(48,147),(180,278),(316,414),(453,550),(591,688),(726,825),(864,961),(999,1097),(1138,1234),(1270,1368)]
LABEL_Y=[(23,103),(126,201),(227,301),(329,398),(430,498),(535,603),(634,710),
 (735,817),(844,915),(948,1019),(1053,1127),(1155,1230),(1265,1342),(1378,1454)]
def glyph(row,state):
 atlas=Image.open(F/'labels_atlas.png').convert('RGBA')
 im=atlas.crop((0 if state==0 else 520,LABEL_Y[row][0],510 if state==0 else 1024,LABEL_Y[row][1]))
 # Mechanical matte extraction: generated glyphs are ivory or deep brown;
 # midtone backdrop is excluded before native-palette conversion.
 arr=np.array(im);mask=((arr[:,:,0]>220)&(arr[:,:,1]>195)&(arr[:,:,2]>145))|((arr[:,:,0]<90)&(arr[:,:,1]<60)&(arr[:,:,2]<45))
 arr[:,:,3]=mask.astype('uint8')*255
 out=Image.fromarray(arr);box=out.getbbox();assert box;return out.crop(box)
def label_image(row,state,size):
 out=Image.new('RGBA',size);g=glyph(row,state)
 g.thumbnail((size[0]-2,size[1]-2),Image.Resampling.LANCZOS)
 out.alpha_composite(g,((size[0]-g.width)//2,(size[1]-g.height)//2));return out
def prepare(source):
 catalog=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text())
 targets={};images=[];records=[]
 atlas=Image.open(F/'buttons_final.png').convert('RGBA')
 with GameSource() as original:
  for r,(label,*paths) in enumerate(ROWS):
   for state,path in enumerate(paths):
    olddata=descend(original.resource('02.DAT',path[0]),path[1:]);h=sha(olddata)
    g=next(g for g in catalog['resources'] if g['source_sha256']==h)
    desc=texture_records(olddata);assert len(desc)==1
    old=decode_texture(olddata,desc[0]);assert old.size==(112,24)
    assert encode_texture(olddata,desc[0],old)[0]==olddata
    art=atlas.crop((18 if state==0 else 529,Y[r][0],497 if state==0 else 1008,Y[r][1])).resize(old.size,Image.Resampling.LANCZOS)
    art.putalpha(old.getchannel('A'));packed,native,_=encode_texture(olddata,desc[0],art)
    uses=[]
    for o in g['occurrences']:
     assert o['bank']=='02.DAT'
     p=tuple(o['path']);assert descend(source.resource('02.DAT',p[0]),p[1:])==olddata
     targets[p]=packed;uses.append(o['id'])
    images.append((f'button_{r:02}_{state}.png',native));records.append(dict(label=label,state=state,occurrences=uses,sha256=sha(packed)))
  # Battle Info has additional unselected variants with different palettes.
  for label,n,row in [('Win/Lose',4,0),('Support Skills',10,1),('Brave Goals',12,2),('Party Abilities',2,None)]:
   path=(1341,n);olddata=descend(original.resource('02.DAT',1341),[n])
   if path in targets:continue
   desc=texture_records(olddata);assert len(desc)==1
   old=decode_texture(olddata,desc[0]);assert old.size==(112,24)
   if row is None:art=Image.open(ROOT/'work/ui/menu_0.1.15/native/09_1.png').convert('RGBA')
   else:art=atlas.crop((529,Y[row][0],1008,Y[row][1])).resize(old.size,Image.Resampling.LANCZOS)
   art.putalpha(old.getchannel('A'));packed,native,_=encode_texture(olddata,desc[0],art)
   group=next(g for g in catalog['resources'] if g['source_sha256']==sha(olddata));uses=[]
   for o in group['occurrences']:
    p=tuple(o['path']);current=descend(source.resource('02.DAT',p[0]),p[1:])
    if current!=olddata:continue # Already localized in the previous release.
    targets[p]=packed;uses.append(o['id'])
   images.append((f'variant_{n}.png',native));records.append(dict(label=label,state='alternate unselected',occurrences=uses))
  # All options glyphs share one texture resource. Preserve the original
  # controller icons, thumbnails and frames except the localized footer text.
  data=descend(source.resource('02.DAT',33),[2]);rows=texture_records(data)
  translated={2:(0,0),6:(2,0),11:(2,1),7:(3,0),12:(3,1),8:(4,0),9:(5,0),15:(5,1),10:(1,1),27:(6,0),36:(6,1)}
  opts={n:label_image(r,st,(rows[n]['width'],rows[n]['height'])) for n,(r,st) in translated.items()}
  for ns,row,st in [([3,4],1,0),([13,14],4,1),([31,32],7,0),([37,38],7,1)]:
   width=sum(rows[n]['width'] for n in ns);height=rows[ns[0]]['height'];im=label_image(row,st,(width,height));x=0
   for n in ns:opts[n]=im.crop((x,0,x+rows[n]['width'],height));x+=rows[n]['width']
  for n,im in opts.items():
   data,native,_=encode_texture(data,rows[n],im);images.append((f'options_{n:02}.png',native))
  frame=Image.open(F/'options_frame.png').convert('RGBA')
  oldfooter=decode_texture(data,rows[0])
  footer=frame.crop((180,833,420,935)).resize(oldfooter.size,Image.Resampling.LANCZOS)
  footer.putalpha(oldfooter.getchannel('A'))
  for box in [(40,4,58,24),(99,4,117,24)]:footer.alpha_composite(oldfooter.crop(box),(box[0],box[1]))
  footer.alpha_composite(label_image(8,0,(40,18)),(59,5))
  footer.alpha_composite(label_image(9,0,(65,18)),(120,5))
  data,native,_=encode_texture(data,rows[0],footer);images.append(('options_confirm_cancel.png',native))
  targets[(33,2)]=data
  framedata=descend(source.resource('02.DAT',33),[3]);framerows=texture_records(framedata)
  oldframe=decode_texture(framedata,framerows[5]);assert oldframe.size==(432,256)
  # Import the whole generated frame, keeping its original native alpha shape.
  newframe=frame.resize(oldframe.size,Image.Resampling.LANCZOS);newframe.putalpha(oldframe.getchannel('A'))
  framedata,native,_=encode_texture(framedata,framerows[5],newframe)
  targets[(33,3)]=framedata;images.append(('options_frame.png',native))
  records.append(dict(label='Options label states',sprites=sorted(opts),sha256=sha(data)))
  data=descend(source.resource('02.DAT',2952),[0]);desc=texture_records(data);assert len(desc)==1
  old=decode_texture(data,desc[0]);assert old.size==(480,272)
  art=Image.open(F/'summon_index.png').convert('RGBA').resize(old.size,Image.Resampling.LANCZOS)
  art.putalpha(old.getchannel('A'));data,native,_=encode_texture(data,desc[0],art)
  targets[(2952,0)]=data;images.append(('summon_index.png',native))
  records.append(dict(label='Summon Index background and Affinity label',path=[2952,0],sha256=sha(data)))
 packs={n:replace_tree(source.resource('02.DAT',n),{p[1:]:v for p,v in targets.items() if p[0]==n}) for n in {p[0] for p in targets}}
 return packs,images,dict(records=records,packs=sorted(packs),occurrences=len(targets),sprite_count=len(images))
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 with GameSource(ROOT/'work/output/0.1.15/Summon_Night_3_EN_0.1.15.iso') as s:packs,images,r=prepare(s)
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',**r),indent=2))
 if a.write:
  folder=F/'native_release';folder.mkdir(exist_ok=False)
  for n,im in images:im.save(folder/n)
  (folder/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
