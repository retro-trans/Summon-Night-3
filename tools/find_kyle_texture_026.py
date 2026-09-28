"""Rank small UI textures by their nameplate alpha shape; dry-run before --write."""
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_codec import decompress,decoded_size
from sn3_ui_textures import texture_records,decode_texture

def shape(im):
 a=im.getchannel('A');box=a.point(lambda v:255 if v>100 else 0).getbbox()
 if not box:return None
 a=a.crop(box)
 if not 2<a.width/a.height<5:return None
 return np.asarray(a.resize((64,24),Image.Resampling.BILINEAR)).astype(float)/255

ref=shape(Image.open(ROOT/'work/ui/nameplates_0.1.10/packs_870-1080_names/02_00914_00003_000.png'))
matches=[];seen=set()
def scan(d,path,depth=0):
 try:
  for r in texture_records(d):
   if not (r['height']<=40 and 40<=r['width']<=256):continue
   try:im=decode_texture(d,r)
   except ValueError:continue
   h=hashlib.sha256(im.tobytes()).hexdigest()
   if h in seen:continue
   seen.add(h);a=shape(im)
   if a is not None:matches.append((float(np.mean(abs(a-ref))),dict(path=path,sprite=r['number'],width=r['width'],height=r['height'],sha256=hashlib.sha256(d).hexdigest()),im))
  return
 except ValueError:pass
 if depth>=2:return
 try:
  ix=parse_index(d,len(d))
  for e in ix['entries']:scan(child(d,ix,e['id']),path+[e['id']],depth+1)
 except ValueError:pass

with GameSource(ROOT/'work/output/0.1.25/Summon_Night_3_EN_0.1.25.iso') as s:
 for bank in ['01.DAT','02.DAT']:
  for e in s.indexes[bank]['entries']:
   n=e['id'];raw=s.resource(bank,n);scan(raw,[bank,n])
   if len(raw)<5:continue
   for k in [0x1700+(raw[0]^raw[3]),0x9831]:
    try:
     if not 5000<=decoded_size(raw,k)<=1500000:continue
     d,u=decompress(raw,k,1500000)
     if not any(raw[u:]):scan(d,[bank,n,'key'+hex(k)])
    except ValueError:pass
matches.sort(key=lambda v:v[0]);top=matches[:24]
print(json.dumps([dict(score=s,**r) for s,r,_ in top],indent=2))
if '--write' in sys.argv:
 folder=ROOT/'work/ui/ui_fixes_0.1.26/kyle_discovery';folder.mkdir(exist_ok=True)
 sheet=Image.new('RGB',(800,12*65),'#657078');draw=ImageDraw.Draw(sheet)
 for i,(score,r,im) in enumerate(top):
  x=(i%2)*400;y=(i//2)*65
  draw.text((x,y),str(r['path'])+' #'+str(r['sprite']),fill='white');sheet.paste(im,(x,y+20),im)
 sheet.save(folder/'ranked.png');(folder/'ranked.json').write_text(json.dumps([dict(score=s,**r) for s,r,_ in top],indent=2)+'\n')
