"""Read-only correlation search against decoded source graphics; optional evidence export."""
import argparse,json,heapq
import numpy as np
from PIL import Image
from sn3_archive import ROOT,GameSource
from sn3_ui_textures import decode_texture
def norm(im):
 a=np.array(im.convert('RGBA'),dtype=float)
 return np.minimum(a[:,:,1],a[:,:,2])*a[:,:,3]/255
def windows(a,h,w):
 p=np.pad(a,((1,0),(1,0))).cumsum(0).cumsum(1)
 return p[h:,w:]-p[:-h,w:]-p[h:,:-w]+p[:-h,:-w]
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
 shot=Image.open('C:/Users/Binh/AppData/Local/Temp/codex-clipboard-47b84f6b-6586-4915-a9f6-51373ea081c7.png').resize((480,272))
 t=norm(shot.crop((43,10,127,29)));h,w=t.shape;t-=t.mean();tn=np.sqrt((t*t).sum());cache={}
 idx=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());best=[];count=0
 with GameSource() as source:
  for g in idx['resources']:
   rows=[r for r in g['textures'] if w<=r['width']<=512 and h<=r['height']<=512]
   if not rows:continue
   o=g['occurrences'][0];data=source.read(o['bank'],o['offset'],o['size'])
   for r in rows:
    try:im=decode_texture(data,r)
    except ValueError:continue
    a=norm(im);H,W=a.shape;shape=(1<<(H+h-2).bit_length(),1<<(W+w-2).bit_length())
    if shape not in cache:cache[shape]=np.fft.rfft2(t[::-1,::-1],s=shape)
    corr=np.fft.irfft2(np.fft.rfft2(a,s=shape)*cache[shape],s=shape)[h-1:H,w-1:W]
    var=windows(a*a,h,w)-windows(a,h,w)**2/(h*w)
    corr/=tn*np.sqrt(np.maximum(var,1e-8));y,x=np.unravel_index(np.argmax(corr),corr.shape);score=float(corr[y,x]);count+=1
    rec=dict(id=o['id'],number=r['number'],score=score,position=[int(x),int(y)],source=o)
    best.append((score,count,rec,im));best=sorted(best,reverse=True)[:12]
 print(json.dumps(dict(mode='write' if args.write else 'dry-run',count=count,best=[x[2] for x in best]),indent=2),flush=True)
 if args.write:
  folder=ROOT/'work/ui/menu_0.1.16/heading_matches';folder.mkdir(exist_ok=False)
  for i,(_,_,r,im) in enumerate(best):im.save(folder/f'{i:02}.png')
  (folder/'report.json').write_text(json.dumps([x[2] for x in best],indent=2)+'\n')
if __name__=='__main__':main()
