"""Author remaining optional-battle title translations; no dialogue export."""
import json,hashlib,shutil
from sn3_archive import ROOT,GameSource,parse_v4,child
from sn3_ui_textures import decode_texture,texture_records
from battle_art_077 import F,T
sha=lambda b:hashlib.sha256(b).hexdigest()
T.mkdir(parents=True,exist_ok=True);(F/'generated').mkdir(parents=True,exist_ok=True)
atlas=F/'generated/title_atlas.png'
assert not atlas.exists()
shutil.copyfile('C:/Users/Binh/.codex/generated_images/01a0db63-acc7-7ff0-b061-538dd1602405/exec-f4473abe-f717-4183-814d-7002b2429a53.png',atlas)
groups=[([65,70],0,'Rogue Demon Beasts'),([66,67,68,69],None,'Rogue Summon Beasts'),([71],1,'Malevolent Spirits'),([72],2,'Rampaging Machines'),([73],3,'Rogue Yokai'),([74,75,76,77],4,'Colorless Spirits'),([83,88,93,98],5,'Phantom Warriors'),([84,89,94],6,"Loreilal's Mechanical Soldiers"),([85,90],7,"Silturn's Oni & Yokai"),([86],8,"Sapureth's Ghosts"),([87,92],9,"Maetropa's Summon Beasts"),([91],10,"Sapureth's Magic Soldiers"),([95],11,"Silturn's Evil Oni"),([96],12,"Sapureth's Holy Spirits"),([97],13,"Maetropa's Demon Beasts")]
rows=[]
with GameSource(ROOT/'work/output/0.1.76/Summon_Night_3_EN_0.1.76.iso') as s:
 for numbers,cell,english in groups:
  for n in numbers:
   b=s.resource('01.DAT',n);ix=parse_v4(b);leaf=child(b,ix,4);im=decode_texture(leaf,texture_records(leaf)[0])
   rows.append(dict(resource=n,child=4,texture=0,source_sha256=sha(leaf),english='VS '+english,atlas_cell=cell,native_size=im.size))
(T/'titles.json').write_text(json.dumps(dict(version='0.1.77',category='Remaining optional-battle encounter headings, full family through 01:98',atlas_sha256=sha(atlas.read_bytes()),method='Built-in imagegen atlas; transparent crop, resize and native palette import only',entries=rows),indent=2)+'\n')
print('Titles',len(rows),'unique labels',len(groups))
