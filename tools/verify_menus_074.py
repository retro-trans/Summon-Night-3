"""Execute stat dispatcher at two load bases; validate every inserted UI field."""
import json,struct,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from menus_fix_074 import BASE,TEXT,prepare_elf,prepare_tables
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from verify_guards_050 import GuardCPU
from verify_equipment_047 import CPU as EquipmentCPU

def verify(elf,source):
 expected,report=prepare_elf();assert elf==expected
 cfg=json.loads(TEXT.read_text());packs02,packs01,_,_=prepare_tables(source)
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];text_checks=[]
 for e in cfg['entries']:
  raw=[encode_dialogue(s,'')[0] for s in e['english']]
  if e['kind']=='name':
   assert len(raw)==1 and len(raw[0])//2<=16
   if e['table']==37:assert sum(metrics[c]['proposed_advance_pixels'] for c in e['english'][0])*.875<=108,e['english']
  else:assert len(raw)<=3 and max(len(x)//2 for x in raw)<=27 and sum(len(x)//2 for x in raw)<=54,(e['records'],e['english'])
  tb=child(packs02[3],parse_index(packs02[3],len(packs02[3])),e['table'])
  for f in e['pointer_fields']:
   p=struct.unpack_from('<I',tb,f)[0];assert lines_at(tb,p)[0]==raw
  text_checks.append(dict(table=e['table'],records=e['records'],cells=[len(x)//2 for x in raw]))
 for e in cfg['labels']:
  tb=child(packs01[1],parse_index(packs01[1],len(packs01[1])),0);raw=encode_dialogue(e['english'][0],'')[0]
  width=sum(metrics[c]['proposed_advance_pixels'] for c in e['english'][0])*.875
  assert width<=133,(e['english'],width)
  for ref in e['references']:
   p=struct.unpack_from('<I',tb,ref['pointer_field_offset'])[0];assert tb[p:p+len(raw)+2]==raw+b'\0\0'
 cases=0
 for e in cfg['menus']:
  if e['source_address'] in (0x21e1e0,0x21e1ec):
   assert max(sum(metrics[c]['proposed_advance_pixels'] for c in s)*.75 for s in e['english'])<=72
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,report,base);owner=0x09400000;cb=base+0x1000;vwf=base+0x347be0;entry=base+int(report['code_address'],16)+report['labels']['stat_dispatch']
  for mode in (2,6,26):
   for rownum in (0,1,2):
    row=owner+rownum*0x3a
    for cell in (0xa383,0xa783,0xab83,0xad83,0xaa84,0xac84,0x6082,0x7282,0x4081,0,0xffff):
     m.store(owner,bytes(0x200));m.store(owner+0x34,struct.pack('<I',mode));m.store(row+0x4c,struct.pack('<H',cell))
     m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[18]=owner;m.r[20]=row;m.r[6]=cb;m.r[29]=0x09f00000;m.r[31]=0x08801234
     before=m.r.copy();fp=m.fp.copy();pc=entry
     for _ in range(100):
      if pc in (cb,vwf):break
      pc=m.step(pc)
     else:raise AssertionError('Dispatch budget')
     native=cell in (0xaa84,0xac84) or (cell&255==0x83 and 0x9f<=cell>>8<=0xb6)
     assert (pc==cb)==native,(mode,rownum,hex(cell))
     assert m.r[4:8]==before[4:8] and m.r[16:32]==before[16:32] and m.fp==fp
     cases+=1
 # Execute the private resident-table copy and unchanged initializer boundary.
 from verify_menu_vwf_020 import CPU as BindCPU
 from font_patch import CODE_VA
 from stages_pupil_names import parse_elf
 assert parse_elf(elf)['phdrs'][3][6]&2, 'Private table buffer must be writable'
 arena_cases=0;full=packs02[3];tail=report['static_tail_offset'];static=full[tail:];size=len(static)
 assert report['static_arena_bytes']==size
 for base in (0x08804000,0x0890c000):
  for iteration in range(2):
   m=BindCPU(elf,report,base);src=0x09400000;labels=0x09200000;dest=base+report['static_arena_address']
   m.store(src-16,b'G'*16+full+b'G'*16);m.store(dest+size,b'G'*16);m.store(0x09efff00,b'G'*0x200)
   m.reg=[0]*32;m.fp=[0]*32;m.set('a0',labels);m.set('a1',src);m.set('sp',0x09f00000)
   for i in range(16,29):m.reg[i]=0x11100000+i
   saved=m.reg[16:30].copy();seen=[]
   def copy(q):
    assert q.reg[4:7]==[dest,src+tail,size];q.store(dest,q.bytes(src+tail,size));seen.append('copy');return {'v0':dest}
   def bind(q):
    assert q.reg[4:6]==[labels,src] and q.bytes(dest,size)==static
    # Event-script writes at the former resident location cannot change this copy.
    q.store(src,bytes(len(full)));assert q.bytes(dest,size)==static;seen.append('initialize');return {'v0':123}
   m.native_handlers={base+0x1c2b80:copy,base+0x197f90:bind}
   m.run(int(report['code_address'],16)-CODE_VA+report['labels']['static_bind'])
   assert m.reg[16:24]+m.reg[26:30]==saved[:8]+saved[10:] and m.reg[2]==123
   assert seen==['copy','initialize'] and m.bytes(src-16,16)==m.bytes(src+len(full),16)==m.bytes(dest+size,16)==b'G'*16
   assert m.bytes(0x09efff00,0xe0)==b'G'*0xe0 and m.bytes(0x09f00000,0x100)==b'G'*0x100
   arena_cases+=1
 child_cases=0
 for base in (0x08804000,0x0890c000):
  for relative in (-16,0,2,size-2,size,size+16):
   m=BindCPU(elf,report,base);old=0x09480000;dest=base+report['static_arena_address'];ctx=base+report['static_arena_context']
   m.store(ctx,struct.pack('<I',old));m.store(0x09efff00,b'G'*0x200)
   m.reg=[0]*32;m.set('sp',0x09f00000);m.set('a0',0x09400000);m.set('a1',40);m.set('a2',0)
   for i in range(16,29):m.reg[i]=0x11100000+i
   saved=m.reg[16:30].copy()
   def lookup(q):
    assert q.reg[4:7]==[0x09400000,40,0];return {'v0':old+relative}
   m.native_handlers={base+0x1e6bd4:lookup}
   m.run(int(report['code_address'],16)-CODE_VA+report['labels']['static_child'])
   assert m.reg[2]==(dest+relative if 0<=relative<size else old+relative)
   assert m.reg[16:24]+m.reg[26:30]==saved[:8]+saved[10:]
   assert m.bytes(0x09efff00,0xe0)==b'G'*0xe0 and m.bytes(0x09f00000,0x100)==b'G'*0x100
   child_cases+=1
 # The rendering repair cannot alter any numeric formatter output.
 previous=(BASE/'EBOOT.elf').read_bytes();equipment_cases=0
 with GameSource(BASE/'Summon_Night_3_EN_0.1.73.iso') as oldsource:
  static=oldsource.resource('02.DAT',3)
 for kind in range(3):
  a=EquipmentCPU(elf,packs02[3],kind);b=EquipmentCPU(previous,static,kind)
  for rec in range(1,a.count):
   for key in (False,True):assert a.run(rec,key)==b.run(rec,key);equipment_cases+=1
 return dict(passed=True,text_fields=len(text_checks),unit_labels=len(cfg['labels']),native_texts=len(cfg['menus']),stat_dispatch_cases=cases,private_static_arena_cases=arena_cases,private_static_arena_bytes=size,private_child_cases=child_cases,load_bases=2,equipment_outputs_unchanged=equipment_cases,callback_abi_preserved=True,original_pools_and_gameplay_fields_preserved=True)

if __name__=='__main__':
 elf,_=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.73.iso') as source:report=verify(elf,source)
 dest=ROOT/'work/ui/menus_0.1.74/validation.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
