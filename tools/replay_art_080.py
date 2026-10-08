"""Translate Replay chapter-marker image glyphs with fixed native geometry."""
import json,hashlib
from PIL import Image
from sn3_archive import ROOT
from menu_art_075 import descend,replace_tree
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture

FOLDER=ROOT/'work/ui/ui_0.1.80/replay'
SPEC=ROOT/'work/translation/en/ui_0.1.80/replay-graphics.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare(source):
 spec=json.loads(SPEC.read_text());original=source.resource('02.DAT',1341);before=descend(original,[16]);assert sha(before)==spec['source_leaf_sha256'];rows=texture_records(before);out=before;report=[]
 for e in spec['entries']:
  p=FOLDER/e['image'];assert sha(p.read_bytes())==e['image_sha256'];im=Image.open(p).convert('RGBA');r=rows[e['sprite']];assert list(im.size)==e['size'];assert sha(decode_texture(before,r).tobytes())==e['source_rgba_sha256']
  out,native,_=encode_texture(out,r,im);report.append(dict(e,decoded_rgba_sha256=sha(native.tobytes())))
 changed={e['sprite'] for e in spec['entries']}
 for r in rows:
  if r['number'] not in changed:assert decode_texture(before,r).tobytes()==decode_texture(out,r).tobytes()
 return {1341:replace_tree(original,{(16,):out})},report

def author():
 from pathlib import Path
 from PIL import ImageDraw,ImageFont
 from sn3_archive import GameSource
 fontpath=Path('C:/Windows/Fonts/georgiab.ttf');FOLDER.mkdir(parents=True,exist_ok=True);entries=[]
 with GameSource(ROOT/'work/output/0.1.79/Summon_Night_3_EN_0.1.79.iso') as source:
  before=descend(source.resource('02.DAT',1341),[16]);rows=texture_records(before)
  for n,text in [(4,'Ch'),(5,''),(9,'Extra'),(13,'Halls')]:
   old=decode_texture(before,rows[n]);im=Image.new('RGBA',old.size)
   if text:
    for size in range(16,10,-1):
     font=ImageFont.truetype(str(fontpath),size);box=font.getbbox(text,stroke_width=1)
     if box[2]-box[0]<=old.width-2:break
    d=ImageDraw.Draw(im);x=(old.width-(box[2]-box[0]))//2-box[0];y=6-box[1]
    d.text((x,y),text,font=font,fill=(255,243,204,255),stroke_width=1,stroke_fill=(175,85,7,255))
   name=f'marker_{n}.png';p=FOLDER/name;im.save(p);_,native,_=encode_texture(before,rows[n],im);native.save(FOLDER/f'marker_{n}_native.png')
   entries.append(dict(sprite=n,text=text,image=name,size=list(old.size),image_sha256=sha(p.read_bytes()),source_rgba_sha256=sha(old.tobytes())))
  SPEC.write_text(json.dumps(dict(version='0.1.80',path=[1341,16],source_leaf_sha256=sha(before),font=fontpath.name,font_sha256=sha(fontpath.read_bytes()),entries=entries),indent=2)+'\n')
 print(json.dumps(dict(translated_marker_sprites=len(entries))))

if __name__=='__main__':author()
