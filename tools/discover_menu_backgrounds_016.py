import argparse,json
from sn3_ui_textures import collect
from sn3_archive import ROOT
import discover_battle_intro_graphics as exp
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();images=[]
 for n in range(1332,1342):
  try:r,im=collect([n])
  except ValueError:continue
  for rec,i in im:
   if i.height>64:images.append((rec,i))
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',count=len(images),samples=[r['id'] for r,i in images[:4]])))
 if a.write:
  exp.OUT=ROOT/'work/ui/menu_0.1.16/backgrounds';exp.write({'candidates':[r for r,i in images]},images)
if __name__=='__main__':main()
