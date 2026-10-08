"""Read-only discovery of remaining encounter sprites and crafting prompts."""
import json,struct
from PIL import Image,ImageDraw
from sn3_archive import ROOT,GameSource,parse_v4,child
from sn3_ui_textures import texture_records,decode_texture
from battle_elf_refs import references
from menu_hotfix_017 import lines_at
from stat_spacing_026 import _file_offset_for_va
F=ROOT/'work/ui/battle_0.1.77/discovery'
F.mkdir(parents=True,exist_ok=True)
with GameSource(ROOT/'work/output/0.1.76/Summon_Night_3_EN_0.1.76.iso') as s:
 images=[];catalog=[]
 for n in range(4,105):
  b=s.resource('01.DAT',n)
  try:ix=parse_v4(b)
  except ValueError:continue
  if ix['count']!=6:continue
  for c in range(1,ix['count']):
   data=child(b,ix,c)
   for t in texture_records(data):
    if c!=4:continue
    im=decode_texture(data,t);name=f'{n}_{c}_{t["number"]}.png';im.save(F/name)
    images.append((name,im));catalog.append(dict(resource=n,child=c,texture=t['number'],file=name,size=im.size))
 for start in range(0,len(images),40):
  batch=images[start:start+40];page=Image.new('RGB',(1000,((len(batch)+3)//4)*100),'#808080');draw=ImageDraw.Draw(page)
  for i,(name,im) in enumerate(batch):
   x=i%4*250;y=i//4*100;draw.text((x+3,y),name,fill='white');im.thumbnail((246,76));page.paste(im,(x+2,y+20),im)
  page.save(F/f'contact{start//40}.png')
 (F/'index.json').write_text(json.dumps(catalog,indent=2)+'\n')
 print('Encounter titles',len(images),'contact pages',(len(images)+39)//40)
b=(ROOT/'work/output/0.1.76/EBOOT.elf').read_bytes();refs,users,_=references(b)
for va in sorted(v for v in refs if 0x21a330<=v<=0x21a530):
 raw=lines_at(b,_file_offset_for_va(b,va))[0]
 print(hex(va),[x.decode('cp932','replace') for x in raw],refs[va])
