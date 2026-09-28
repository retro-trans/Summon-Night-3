"""Read-only texture discovery; --write exports a labeled contact sheet."""
import sys,json,argparse
from PIL import Image,ImageDraw
from sn3_archive import ROOT,GameSource
from sn3_ui_textures import decode_texture
from menu_art_015 import descend
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
x=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());items=[]
with GameSource() as s:
 for g in x['resources']:
  o=next((o for o in g['occurrences'] if o['bank']=='01.DAT' and o['path'][0]==105),None)
  if not o:continue
  d=s.read(o['bank'],o['offset'],o['size'])
  for t in g['textures']:
   if 32<=t['width']<=256 and t['height']<=64:
    try:items.append((o,t,decode_texture(d,t)))
    except ValueError as e:print(o['id'],t['number'],str(e))
print(len(items))
if a.write:
 for page in range((len(items)+149)//150):
  chunk=items[page*150:(page+1)*150];im=Image.new('RGB',(1200,((len(chunk)+5)//6)*65),(65,75,85));dr=ImageDraw.Draw(im)
  for n,(o,t,tile) in enumerate(chunk):
   xx=n%6*200;yy=n//6*65;dr.text((xx,yy),o['bank'][:2]+':'+ '/'.join(map(str,o['path']))+':'+str(t['number']),fill='white');tile.thumbnail((190,44));im.paste(tile,(xx,yy+17),tile)
  im.save(ROOT/f'work/ui/battle_ui_0.1.25/discovery_105_{page}.png')


