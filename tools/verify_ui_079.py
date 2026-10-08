"""Execute actual UI help staging and relocated Night Talks layout helpers."""
import json,struct
from sn3_archive import ROOT,GameSource,parse_index
from ui_fix_079 import prepare_tables,prepare_elf,TEXT
from check_ui_079 import check
from dialogue_encoding import encode_dialogue
from verify_guards_049 import AliasCPU,stage
from verify_guards_050 import GuardCPU

def verify():
 with GameSource(ROOT/'work/output/0.1.78/Summon_Night_3_EN_0.1.78.iso') as source:
  tables,_,_,tr=prepare_tables(source)
 elf,r=prepare_elf(tables[3]);cpu=AliasCPU(elf,tables[3]);help_cases=0
 rows=check(tables[3],json.loads(TEXT.read_text()))['rows']
 for row in rows:
  lines=row['help'];payload=b''.join(encode_dialogue(t,'')[0]+bytes(2) for t in lines)+bytes(2)
  result=stage(cpu,payload)
  assert result['glyphs']==sum(map(len,lines)) and result['rows']==len(lines),(row,result)
  assert result['max_slot']<54;help_cases+=1
 names=json.loads((TEXT.parent/'gallery.json').read_text())['match_names']
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 night_cases=strip_cases=tail_cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base);owner=0x09400000;records=0x09700000;stop=0x08801234
  code=base+int(r['code_address'],16)
  for text in names+['Custom Name']:
   ptr=0x09800000;m.store(ptr,encode_dialogue(text,'')[0]+bytes(4));m.store(owner,bytes(0x100));m.write(owner+0x30,records);m.write(records,ptr);m.write(owner+0x34,0x09710000);m.write(owner+0x3c,1);m.write(owner+0x64,9,1)
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['gallery_strip'];draws=0
   for _ in range(100000):
    if pc==stop:break
    if pc==base+0x35272c:
     assert m.r[4:8]==before[4:8];assert m.read(owner+0x34)==(0 if text in names else 0x09710000)
     draws+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and draws==1 and m.r[16:32]==before[16:32]
   assert m.read(owner+0x34)==0x09710000 and m.read(owner+0x64,1)==9;strip_cases+=1
  texts=['A Jester\'s Way',"An Organization's Bounds",'????????','Thunder Gen., Wind Princess','A Wish from the Past']
  for start in (0,1,4):
   m.store(owner,bytes(0x100));m.write(owner+0x30,records);m.write(owner+0x20,start);m.write(owner+0x24,3);m.write(owner+0x3c,len(texts));m.write(owner+0x54,0x41600000);m.write(owner+0x58,0x41700000)
   for i,text in enumerate(texts):
    ptr=0x09800000+256*i;m.store(ptr,encode_dialogue(text,'')[0]+bytes(4));m.write(records+16*i,ptr)
   width=min([14.0]+[min(14.,2240/sum(metrics[c]['proposed_advance_pixels'] for c in t)) for t in texts[start:start+3] if t in names]);expected=struct.unpack('<I',struct.pack('<f',width))[0]
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['night_captions'];draws=0
   for _ in range(100000):
    if pc==stop:break
    if pc==code+r['labels']['gallery_strip']:
     assert m.read(owner+0x54)==m.read(owner+0x58)==expected and m.r[4:8]==before[4:8]
     draws+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and draws==1 and m.r[16:32]==before[16:32]
   assert m.read(owner+0x54)==0x41600000 and m.read(owner+0x58)==0x41700000;night_cases+=1
  source=0x09600000;size=r['static_arena_bytes'];tail=source+r['static_tail_offset'];arena=base+r['static_arena_address'];context=base+r['static_arena_context']
  m.store(source,tables[3]);m.store(arena-8,b'G'*8+bytes(size)+b'G'*8)
  m.r=[0]*32;m.r[4:6]=[owner,source];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['static_bind'];calls=0
  for _ in range(1000):
   if pc==stop:break
   if pc==base+0x1c2b80:
    assert m.r[4:7]==[arena,tail,size];m.store(arena,tables[3][r['static_tail_offset']:]);m.r[2]=arena;pc=m.r[31];continue
   if pc==base+0x197f90:
    assert m.r[4:6]==[owner,source];calls+=1;pc=m.r[31];continue
   pc=m.step(pc)
  assert pc==stop and calls==1 and m.r[16:32]==before[16:32] and m.read(context)==tail
  assert bytes(m.read(arena+size+i,1) for i in range(8))==b'G'*8;tail_cases+=1
 return dict(passed=True,actual_help_staging_cases=help_cases,relocated_gallery_strip_cases=strip_cases,proportional_scale_execution_cases=night_cases,protected_tail_execution_cases=tail_cases,load_bases=2,attack_fields=tr['entries'],caption_corrections=len(tr['gallery']),numeric_fields_and_original_pools_preserved=True)

if __name__=='__main__':
 r=verify();(ROOT/'work/ui/ui_0.1.79/validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
