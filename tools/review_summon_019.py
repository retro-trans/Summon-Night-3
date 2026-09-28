"""Correct source-aligned summon-name decisions; preview before --write."""
import argparse,json
from sn3_archive import ROOT
F=ROOT/'work/translation/en/summon_0.1.19'
FIX={
7:('Bezsou','Bezsou'),34:('Oni Wisdom King Goen','Wisdom King'),50:('Haunted Captain','Haunted Captain'),
72:('Fierce Demon Beast Remies','Demon Remies'),73:('Fang King Aegis','Fang King Aegis'),
74:('Lord Tauros','Lord Tauros'),75:('Twin Tyrant Dragon Blisgore','Blisgore'),
76:('Summon Material','Summon Material'),77:('Stonework Base','Stonework Base'),
78:('Colossus Fist','Colossus Fist'),79:('Wood Table','Wood Table'),80:('Gourmet Cart','Gourmet Cart'),
81:('Memory Desk','Memory Desk'),82:('Resist Panel','Resist Panel'),83:('Masked Statue','Masked Statue'),
84:('Shine Saber','Shine Saber'),85:('Dark Bringer','Dark Bringer'),86:('Anti-Magic Crystal','Anti-Magic'),87:('Falzen','Falzen')}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 path=F/'names.targets.json';d=json.loads(path.read_text());out=[]
 for ident,r in d['translations'].items():
  if r['record'] in FIX:
   text,compact=FIX[r['record']];r.update(text=text,compact=compact,review='Corrected against exact source ID after independent meaning review');out.append((r['record'],ident,text))
  assert len(r['compact'])<=15 and r['compact'].isascii()
 print(json.dumps({'mode':'write' if a.write else 'dry-run','corrections':out},indent=2))
 if a.write:
  path.write_text(json.dumps(d,indent=2)+'\n')
  (F/'independent.review.json').write_text(json.dumps(dict(accepted_base_names=87,corrected_records=sorted(FIX),note='Rejected offset-shifted draft names in records 72–87 before insertion. Root compared all 87 exact source records. Proper-name romanizations remain provisional outside glossary locks.',excluded=['All long descriptions','Remaining unreviewed form aliases']),indent=2)+'\n')
if __name__=='__main__':main()
