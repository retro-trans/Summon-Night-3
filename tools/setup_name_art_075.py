"""English fixed nameplate targets; lookup by native texture hash covers copies."""
import json
from sn3_archive import ROOT
NIGHT=['Nup','Belfraw','Alieze','Will','Ardylia','Kyuuma','Falzen','Fariel','Yafha','Kyle','Sonolar','Scarrel','Yard','Kunon','Misumi','Subaru','Phlaiz','Marurur','Azlier']
PORTRAITS={1069:'Rexx',1072:'Aty',1086:'Nup',1087:'Belfraw',1088:'Alieze',1089:'Will',1094:'Ardylia',1095:'Kyuuma',1096:'Falzen',1097:'Yafha',1100:'Scarrel',1102:'Marurur',1103:'Kunon',1104:'Var-Xe-LD',1105:'Misumi',1106:'Subaru',1107:'Phlaiz',1108:'Azlier',1109:'Galeor',1114:"Kyle's Crew",1115:'Toris',1116:'Guard',1117:'Leolord',1118:'Hasaha',1119:'Valrel',1120:'Resi',1121:'Nesty',1122:'Amer',1123:'Forte',1124:'Keina',1125:'Rocca',1126:'Ryug',1127:'Morin',1128:'Minis',1129:'Kelma',1130:'Paffel',1133:'Jakini',1134:'Ohkini',1180:'Meimei',1199:'R',1221:'Onibi',1243:'Quiupy',1265:'Teco',1289:'Vijue',1292:'Vizel',1293:'Hazel',1294:'Ordreik',1295:'Zeline',1297:'Ishlar',1302:'Dielgo',1331:'Fariel'}
def main():
 entries=[dict(bank='02.DAT',path=[89,n],sprite=0,text=name,kind='nameplate') for n,name in enumerate(NIGHT,45)]
 for root,text in PORTRAITS.items():
  for n in [1,2]:entries.append(dict(bank='02.DAT',path=[root,n],sprite=0,text=text,kind='nameplate'))
 dest=ROOT/'work/translation/en/menus_0.1.75/nameplates.json';dest.write_text(json.dumps(dict(version='0.1.75',entries=entries),indent=2)+'\n',encoding='utf8')
 labels=list(dict.fromkeys(e['text'] for e in entries));batches=[labels[i:i+24] for i in range(0,len(labels),24)]
 (ROOT/'work/scratch/menus075-name-labels.json').write_text(json.dumps(batches),encoding='utf8');print(len(entries),len(labels))
if __name__=='__main__':main()
