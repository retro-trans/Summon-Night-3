"""Make audit contact sheets for unique generated encounter-art previews."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
PREVIEWS=ROOT/'work/ui/battle_0.1.13/encounter_generated/previews'
GENERATED=ROOT/'work/ui/battle_0.1.13/encounter_generated/index.json'
FONT=Path('C:/Windows/Fonts/arialbd.ttf')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 report=json.loads((PREVIEWS/'index.json').read_text(encoding='utf8'))
 catalog=json.loads(GENERATED.read_text(encoding='utf8'))
 texts={e['key']:e['target_text'] for e in catalog['entries']}
 rows={}
 variants={}
 for r in report['records']:
  rows.setdefault(r['key'],r)
  variants.setdefault(r['key'],set()).add(r['decoded_rgba_sha256'])
 if set(rows)!=set(texts): raise ValueError('key mismatch '+repr(sorted(set(rows)^set(texts))))
 if len(rows)!=51: raise ValueError('expected 51 unique generated keys')
 for key,r in rows.items():
  im=Image.open(PREVIEWS/r['preview']).convert('RGBA')
  al=im.getchannel('A').getextrema()
  if al!=(0,255): raise ValueError('alpha extrema failed: '+key+repr(al))
 ordered=sorted(rows)
 summaries=[]
 for page,start in enumerate(range(0,len(ordered),27)):
  keys=ordered[start:start+27]; canvas=Image.new('RGB',(1440,1620),(42,42,48));draw=ImageDraw.Draw(canvas)
  for i,key in enumerate(keys):
   x=(i%3)*480;y=(i//3)*180
   draw.rectangle((x+2,y+2,x+477,y+177),outline=(130,130,140),width=2)
   draw.text((x+10,y+8),f'{key}: {texts[key].replace(chr(10)," / ")}',font=ImageFont.truetype(str(FONT),16),fill=(255,255,255))
   im=Image.open(PREVIEWS/rows[key]['preview']).convert('RGBA');im.thumbnail((450,145),Image.Resampling.NEAREST)
   canvas.paste(im,(x+(480-im.width)//2,y+30+(145-im.height)//2),im)
  name=f'contact_{page:02d}.png'; summaries.append({'file':name,'keys':keys,'sha256':None if not a.write else None})
  if a.write: canvas.save(PREVIEWS/name)
 if a.write:
  for row in summaries: row['sha256']=sha(PREVIEWS/row['file'])
  (PREVIEWS/'contact.index.json').write_text(json.dumps({'unique_key_count':len(rows),'record_count':len(report['records']),'sheets':summaries,'all_alpha_extrema':[0,255],'palette_quantized_variants':{k:len(v) for k,v in variants.items()}},indent=2)+'\n',encoding='utf8')
 print(json.dumps({'mode':'write' if a.write else 'dry-run','unique_key_count':len(rows),'record_count':len(report['records']),'sheets':[{k:v for k,v in s.items() if k!='sha256'} for s in summaries],'alpha_extrema_verified':True,'keys_with_palette_variants':sum(len(v)>1 for v in variants.values())},indent=2))
if __name__=='__main__':main()
