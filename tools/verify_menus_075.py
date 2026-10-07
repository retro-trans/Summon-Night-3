"""Execute new default-name lookup and validate unchanged table/gameplay fields."""
import json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from menus_fix_075 import prepare_elf,prepare_tables,BASE,TEXT
from name_lookup_075 import prepare as prepare_names
from verify_guards_050 import GuardCPU
from dialogue_encoding import encode_dialogue
from font_patch import CODE_VA
def verify(elf,source):
 expected,report=prepare_elf();assert elf==expected
 _,_,pairs=prepare_names(prepare_elf_without_names())
 nr=report['default_name_lookup'];checks=0;width_cases=0;type_cases=0
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,report,base);ptr=0x09800000;stop=0x08801234
  samples=list(metrics)+['Ghost Fossil','A'*32,'','Japanese fallback']
  for text in samples:
   src=b''.join(bytes.fromhex(metrics[c]['cp932_hex']) for c in text) if text!='Japanese fallback' else bytes.fromhex('839a839c83a6')
   wanted=(sum(metrics[c]['proposed_advance_pixels'] for c in text)+15)//16 if text!='Japanese fallback' else 3
   m.store(ptr-8,b'G'*8+src+b'\0\0'+b'G'*8);m.r=[0]*32;m.r[4]=ptr;m.r[29]=0x09f00000;m.r[31]=stop
   for i in range(16,29):m.r[i]=0x12500000+i
   before=m.r.copy();fp=m.fp.copy();pc=base+int(report['code_address'],16)+report['labels']['reward_cells']
   for _ in range(100000):
    if pc==stop:break
    pc=m.step(pc)
   else:raise AssertionError('Reward width budget')
   assert m.r[2]==wanted,(text,m.r[2],wanted)
   assert m.r[16:32]==before[16:32] and m.fp==fp;width_cases+=1
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,nr,base);entry=base+int(nr['code_address'],16)+nr['labels']['default_name'];ptr=0x09800000;stop=0x08801234
  for src,dst in pairs+[(encode_dialogue('My Hero','')[0],None),(b'',None),(encode_dialogue('HazelX','')[0],None)]:
   raw=src+b'\0\0';m.store(ptr-8,b'G'*8+raw+b'G'*8);m.r=[0]*32;m.r[4]=ptr;m.r[29]=0x09f00000;m.r[31]=stop
   for i in range(16,29):m.r[i]=0x12500000+i
   before=m.r.copy();pc=entry
   for _ in range(100000):
    if pc==stop:break
    pc=m.step(pc)
   else:raise AssertionError('Name lookup budget')
   if dst is None:assert m.r[2]==ptr
   else:assert bytes(m.read(m.r[2]+i,1) for i in range(len(dst)+2))==dst+b'\0\0'
   assert m.r[16:32]==before[16:32] and m.r[4]==ptr
   assert bytes(m.read(ptr-8+i,1) for i in range(len(raw)+16))==b'G'*8+raw+b'G'*8;checks+=1
  m.r=[0]*32;m.r[31]=stop;pc=entry
  for _ in range(10):
   if pc==stop:break
   pc=m.step(pc)
  assert pc==stop and m.r[2]==0;checks+=1
  for src,dst in pairs+[(encode_dialogue('My Hero','')[0],None),(encode_dialogue('A'*17,'')[0],None)]:
   raw=src+b'\0\0';m.store(ptr-8,b'G'*8+raw+b'G'*8);m.store(0x09effe00,b'S'*1024)
   m.r=[0]*32;m.r[4:7]=[0x09400000,ptr,1];m.r[29]=0x09f00000;m.r[31]=stop
   for i in range(16,29):m.r[i]=0x12500000+i
   before=m.r.copy();pc=base+nr['type_entry'];seen=[]
   wanted=dst if dst is not None else src
   for _ in range(100000):
    if pc==stop:break
    if pc==base+0x1e4ac8:
     p=m.r[4];n=0
     while m.read(p+n*2,2):n+=1
     m.r[2]=n;pc=m.r[31];continue
    if pc in (base+0x32e060,base+0x1cbdec):
     p=m.r[5];assert bytes(m.read(p+i,1) for i in range(len(wanted)+2))==wanted+b'\0\0'
     assert m.r[4]==before[4] and m.r[6]==(len(wanted)//2 if pc==base+0x32e060 else 1)
     if pc==base+0x32e060:assert m.r[7]==1
     seen.append(pc);m.r[2]=123;pc=m.r[31];continue
    pc=m.step(pc)
   else:raise AssertionError('Name field wrapper budget')
   assert len(seen)==1 and m.r[2]==123 and m.r[4:7]==before[4:7] and m.r[16:32]==before[16:32]
   assert bytes(m.read(ptr-8+i,1) for i in range(len(raw)+16))==b'G'*8+raw+b'G'*8
   assert bytes(m.read(0x09f00000+i,1) for i in range(100))==b'S'*100;type_cases+=1
 p02,p01,master,tr=prepare_tables(source);assert p02[3]==source.resource('02.DAT',3)
 raw=child(p01[1],parse_index(p01[1],len(p01[1])),0)
 for e in tr['units']:
  target=encode_dialogue(e['english'][0],'')[0];assert raw[e['new_offset']:e['new_offset']+len(target)+2]==target+b'\0\0'
  assert sum(metrics[c]['proposed_advance_pixels'] for c in e['english'][0])*.875<=133,e['english']
  for ref in e['references']:assert struct.unpack_from('<I',raw,ref['pointer_field_offset'])[0]==e['new_offset']
 return dict(passed=True,default_name_pairs=len(pairs),name_execution_cases=checks,name_field_wrapper_cases=type_cases,reward_width_cases=width_cases,load_bases=2,translated_labels=tr['entries'],native_messages=len(report['entries']),custom_names_preserved=True,source_pools_and_numeric_fields_unchanged=True,static_tail_unchanged=True)
def prepare_elf_without_names():
 # The helper's inputs depend only on immutable original pools; patched prefix is irrelevant.
 return (BASE/'EBOOT.elf').read_bytes()
if __name__=='__main__':
 elf,_=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.74.iso') as src:r=verify(elf,src)
 p=ROOT/'work/ui/menus_0.1.75/validation.json';p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
