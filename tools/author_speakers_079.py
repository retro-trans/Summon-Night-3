"""Add untouched story and selection nameplates; preserve mystery-name graphics."""
import json
from sn3_archive import ROOT
N={895:'Rexx',896:'Rexx',897:'Rexx',898:'Aty',899:'Aty',900:'Aty',905:'R',906:'Onibi',907:'Quiupy',908:'Teco',909:'Ardylia',910:'Kyuuma',911:'Falzen',912:'Fariel',913:'Yafha',916:'Scarrel',918:'Kunon',919:'Var-Xe-LD',920:'Misumi',921:'Subaru',922:'Phlaiz',923:'Marurur',924:'Genji',925:'Panache',926:'Meimei',927:'Azlier',928:'Galeor',929:'Vijue',930:'Ishlar',931:'Jakini',932:'Ohkini',933:'Pirate',934:'Ordreik',935:'Zeline',936:'Vizel',937:'Hazel',939:'Rexx',940:'Rexx',941:'Shingen',942:'Faceless Soldier',943:'Rexx',944:'Shaomei',945:'Rexx',946:'Takeshi',947:'Shiari',948:'Beko',954:'Toris',955:'Leolord',956:'Hasaha',957:'Valrel',958:'Resi',959:'Nesty',960:'Amer',961:'Forte',962:'Keina',963:'Minis',964:'Rocca',965:'Ryug',966:'Morin',967:'Kelma',968:'Paffel',969:'Ishlar',970:'Ghost Soldier',971:'Imperial Soldier',972:'Leolord',973:'Hasaha',974:'Valrel',975:'Resi',976:'Hainel',977:'Mimic Master',978:'Mimic Master',979:'Nesty',980:'Amer',982:'Belfraw',983:'Alieze',984:'Will',985:'Ohkini',986:'Jakini',987:'Dielgo',988:'Rexx',989:'Aty',991:'Aty',1049:'Nup',1050:'Belfraw',1051:'Alieze',1052:'Will',1053:'Ardylia',1054:'Fariel',1055:'Fariel',1057:'Yafha',1058:'Kyle',1059:'Sonolar',1060:'Scarrel',1061:'Yard',1062:'Kunon',1063:'Misumi',1064:'Subaru',1065:'Phlaiz',1066:'Marurur',1067:'Azlier',1070:'Rexx',1074:'Rexx',1078:'Rexx',1082:'Rexx',1131:'Hasaha',1132:'Valrel',1135:'Amer',1183:'Kunon',1184:'Marurur'}
N.update({n:'Rexx' for n in range(990,1026) if n!=991})
def main():
 f=ROOT/'work/translation/en/ui_0.1.79/graphics.json';cfg=json.loads(f.read_text());found=json.loads((ROOT/'work/scratch/ui079-speakers/unknown.json').read_text());names=[]
 for e in found:
  root,n=e['path']
  if 350<=root<=379:e.update(text='Starting Beach',kind='location_entry')
  elif root in N and not (root==933 and n==2):e['text']=N[root];names.append(e['text'])
  else:continue
  e.pop('file',None)
  if not any(x['path']==e['path'] and x['sprite']==e['sprite'] and x['bank']==e['bank'] for x in cfg['entries']):cfg['entries'].append(e)
 f.write_text(json.dumps(cfg,indent=2)+'\n')
 old=json.loads((ROOT/'work/ui/menus_0.1.75/atlas_spec.json').read_text());missing=sorted(set(names)-set(sum(old['names'],[])))
 p=ROOT/'work/ui/ui_0.1.79/atlas_spec.json';spec=json.loads(p.read_text());spec['speakers']=missing;p.write_text(json.dumps(spec,indent=2)+'\n')
 print(json.dumps(dict(entries=len(cfg['entries']),new_names=missing),indent=2))
if __name__=='__main__':main()
