"""Check armor-name bounds and execute symbolic row dispatch after relocation."""
import json,struct,unicodedata
from sn3_archive import ROOT,child,parse_index
from armor_051 import BASE,TARGETS,HOOK,STAT_CELLS,prepare_elf
from verify_equipment_047 import CPU
from verify_guards_050 import GuardCPU
from menu_hotfix_017 import lines_at

def verify(elf,static):
 expected,report=prepare_elf();assert elf==expected,'Unexpected candidate executable'
 cfg=json.loads(TARGETS.read_text());idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());rows=next(t['strings'] for t in idx['tables'] if t['resource_path']==[3,16]);table=child(static,parse_index(static,len(static)),16)
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];names=[];targets={e['id']:e['text'] for e in cfg['entries']}
 for row in rows:
  for ref in row['references']:
   p=struct.unpack_from('<I',table,ref['pointer_field_offset'])[0];raw=lines_at(table,p)[0][0];text=unicodedata.normalize('NFKC',raw.decode('cp932'))
   assert text.isascii() and len(raw)//2<=15,(row['id'],text)
   if row['id'] in targets:assert text==targets[row['id']]
   width=sum(metrics[x]['proposed_advance_pixels'] for x in text)*.875
   if row['id'] in targets:assert width<=130,(text,width)
   names.append(dict(text=text,width=width,new_translation=row['id'] in targets))
 old=(BASE/'EBOOT.elf').read_bytes();prefixes=set();equipment_cases=0
 for kind in range(3):
  c=CPU(elf,static,kind);b=CPU(old,static,kind)
  for rec in range(1,c.count):
   for key in (False,True):
    r=c.run(rec,key);assert r==b.run(rec,key),(kind,rec,key)
    if r['lines']:prefixes.add(c.read(0x5019f0,2))
    equipment_cases+=1
 assert 0xaa84 in prefixes and 0xac84 in prefixes
 dispatch_cases=0;unchanged_cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,report,base);row=0x09400000;callback=base+0x1000;vwf=base+0x347be0
  entry=base+int(report['code_address'],16)+report['labels']['armor_stat_dispatch']
  def run(cell,mode):
   m.store(row+0x34,struct.pack('<I',mode));m.store(row+0x4c,struct.pack('<H',cell))
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[20]=row;m.r[6]=callback;m.r[29]=0x09f00000;m.r[31]=0x08801234
   before=m.r.copy();fp=m.fp.copy();pc=entry
   for _ in range(80):
    if pc in (callback,vwf):break
    pc=m.step(pc)
   else:raise AssertionError('Dispatch budget')
   assert m.r[4:8]==before[4:8] and m.r[16:32]==before[16:32] and m.fp==fp,'Callback ABI changed'
   return pc==callback
  for cell in range(65536):
   native=cell in STAT_CELLS or (cell&255==0x83 and 0x9f<=cell>>8<=0xb6)
   assert run(cell,6)==native,(base,hex(cell))
   dispatch_cases+=1
  for mode in (0,1,2,3,4,5,7,8):
   for cell in prefixes|set(STAT_CELLS)|{0x4081,0x6082,0xffff,0}:
    assert not run(cell,mode),(mode,cell)
    unchanged_cases+=1
 return dict(translated_names=len(targets),armor_name_references=len(names),widest_new_name=max((n for n in names if n['new_translation']),key=lambda x:x['width']),all_armor_names_english=True,equipment_outputs_unchanged=equipment_cases,dispatch_cases=dispatch_cases,non_stat_mode_cases=unchanged_cases,load_bases=2,callback_arguments_registers_and_float_positions_preserved=True)
