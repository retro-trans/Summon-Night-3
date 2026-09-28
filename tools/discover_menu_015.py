"""Export existing menu sprites for inspection; dry-run by default."""
import argparse,json
from discover_battle_intro_graphics import sha,write
import discover_battle_intro_graphics as exporter
from sn3_archive import ROOT,GameSource
from sn3_ui_textures import decode_texture

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 index=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());images=[];report={'candidates':[],'rejected':[]}
 with GameSource() as source:
  for group in index['resources']:
   o=next((o for o in group['occurrences'] if o['bank']=='02.DAT' and o['path'][0] in (1332,1333) and len(o['path'])>=2),None)
   if not o:continue
   data=source.read(o['bank'],o['offset'],o['size']);assert sha(data)==o['sha256']
   for row in group['textures']:
    if not (row['width']>=80 and row['height']<=48):continue
    try:im=decode_texture(data,row)
    except ValueError as e:report['rejected'].append(str(e));continue
    r=dict(id=o['id']+':sprite:%03d'%row['number'],source_sha256=o['sha256'],path=o['path'],width=im.width,height=im.height)
    report['candidates'].append(r);images.append((r,im))
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',count=len(images),sample=report['candidates'][:3])))
 if a.write:
  exporter.OUT=ROOT/'work/ui/menu_0.1.15/source';write(report,images)
if __name__=='__main__':main()
