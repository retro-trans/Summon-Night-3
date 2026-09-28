"""Preview/export bounded remaining menu sprites from original source."""
import argparse,json
from discover_battle_intro_graphics import sha,write
import discover_battle_intro_graphics as exporter
from sn3_archive import ROOT,GameSource
from sn3_ui_textures import decode_texture
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--extra',action='store_true');p.add_argument('--roots');a=p.parse_args()
 roots=set(map(int,a.roots.split(','))) if a.roots else None
 index=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());images=[];report={'candidates':[],'rejected':[]}
 with GameSource() as s:
  for g in index['resources']:
   o=next((o for o in g['occurrences'] if o['bank']=='02.DAT' and (o['path'][0] in roots if roots else o['path'][0] in (34,35,36,37,1346) if a.extra else 1334<=o['path'][0]<=1345)),None)
   if not o:continue
   data=s.read(o['bank'],o['offset'],o['size']);assert sha(data)==o['sha256']
   for row in g['textures']:
    if row['height']>64 or (roots and row['width']<48):continue
    try:im=decode_texture(data,row)
    except ValueError:continue
    r=dict(id=o['id']+':sprite:%03d'%row['number'],source_sha256=o['sha256'],path=o['path'],width=im.width,height=im.height)
    report['candidates'].append(r);images.append((r,im))
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',count=len(images),samples=report['candidates'][:2])))
 if a.write:
  exporter.OUT=ROOT/('work/ui/menu_0.1.16/source_roots' if roots else 'work/ui/menu_0.1.16/source_extra' if a.extra else 'work/ui/menu_0.1.16/source');write(report,images)
if __name__=='__main__':main()
