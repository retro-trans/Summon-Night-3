"""Check actual translated tables through the emitted help staging code."""
import argparse,json,struct,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from skills_064 import BASE,TEXT,prepare_names,prepare_elf
from menu_hotfix_017 import lines_at
from verify_guards_049 import AliasCPU,stage
def verify(elf,static):
 assert elf==prepare_elf()[0]
 spec=json.loads(TEXT.read_text(encoding='utf8'));metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];ix=parse_index(static,len(static));c=AliasCPU(elf,static);results=[]
 for r in spec['skills']:
  table=child(static,ix,r['table']);base=4+r['record']*48
  def read(slot):return lines_at(table,struct.unpack_from('<I',table,base+slot*4)[0])[0]
  name=unicodedata.normalize('NFKC',read(8)[0].decode('cp932'));assert name==r['name'][1]
  width=sum(metrics[ch]['proposed_advance_pixels'] for ch in name)*.875;assert width<=108
  assert struct.unpack_from('<I',elf,0x146fcc+192)[0]==3<<26|0x347b5c>>2
  body,master=read(9),read(10);lines=body+master;lengths=[len(b)//2 for b in lines]
  assert len(lines)<=3 and max(lengths)<=27 and sum(lengths)<=54
  assert [unicodedata.normalize('NFKC',b.decode('cp932')) for b in lines]==r['help']+r['master']
  payload=b''.join(b+b'\0\0' for b in lines)+b'\0\0';result=stage(c,payload)
  assert result['glyphs']==sum(lengths) and result['rows']==len(lines) and result['max_slot']<54,(r,result)
  results.append(dict(table=r['table'],record=r['record'],name=name,name_pixels=width,help=r['help'],master=r['master'],lengths=lengths,staging=result))
 return dict(passed=True,skills=results,executable_unchanged=True,exact_learn_skills_screen_verified=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--build');p.add_argument('--report');a=p.parse_args();elf=prepare_elf()[0]
 if a.build:
  folder=ROOT/a.build;m=json.loads((folder/'manifest.json').read_text());elf=(folder/'EBOOT.elf').read_bytes()
  with GameSource(folder/m['output_iso']) as src:r=verify(elf,src.resource('02.DAT',3))
 else:
  with GameSource(next(BASE.glob('*.iso'))) as src:tables,_=prepare_names(src);r=verify(elf,tables[3])
 print(json.dumps(r,indent=2),flush=True)
 if a.report:
  assert a.build;(ROOT/a.report).write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
