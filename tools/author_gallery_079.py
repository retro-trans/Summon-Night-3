"""Keep every translated gallery title within the real 256-pixel cache strip."""
import json,struct
from sn3_archive import ROOT,GameSource
from menu_art_075 import descend
from menu_hotfix_017 import lines_at
from ui_fix_079 import sha
from dialogue_encoding import encode_dialogue
FIX={'The Bounds of an Organization':"An Organization's Bounds",'Thunder General, Wind Princess':'Thunder Gen., Wind Princess'}
F=ROOT/'work/translation/en/ui_0.1.79'
def main():
 cfg=json.loads((ROOT/'work/translation/en/menus_0.1.76/gallery_captions.json').read_text());changes=[]
 with GameSource(ROOT/'work/output/0.1.78/Summon_Night_3_EN_0.1.78.iso') as s:
  for e in cfg['entries']:
   if e['english'][0] not in FIX:continue
   b=descend(s.resource('02.DAT',e['path'][0]),e['path'][1:]);ps={struct.unpack_from('<I',b,f)[0] for f in e['pointer_fields']};assert len(ps)==1
   p=ps.pop();raw=lines_at(b,p)[0][0];assert raw==encode_dialogue(e['english'][0],'')[0]
   changes.append(dict(path=e['path'],source_offset=p,source_sha256=sha(raw),pointer_fields=e['pointer_fields'],english=[FIX[e['english'][0]]]))
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 names={'Rexx','Aty'}
 for filename in ('titles.json','gallery_captions.json'):
  names.update(FIX.get(e['english'][0],e['english'][0]) for e in json.loads((ROOT/'work/translation/en/menus_0.1.76'/filename).read_text())['entries'])
 for e in cfg['entries']:
  title=FIX.get(e['english'][0],e['english'][0]);assert sum(metrics[c]['proposed_advance_pixels'] for c in title)<=256,title
 (F/'gallery.json').write_text(json.dumps(dict(version='0.1.79',entries=changes,match_names=sorted(names),cache_pixels=256,blank_title_cause='Measured Latin advance exceeded the 256-pixel native strip; fallback could not allocate a longer cache entry.'),indent=2)+'\n')
 print('Gallery corrections:',len(changes))
if __name__=='__main__':main()
