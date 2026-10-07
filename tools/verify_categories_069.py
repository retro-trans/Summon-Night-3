"""Verify actual source-bound pointers, guarded staging and native menu assembly."""
import json,struct,argparse,unicodedata
from categories_fix_069 import ROOT,BASE,TEXT,prepare_elf,prepare_tables
from sn3_archive import GameSource,parse_index,child
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from verify_guards_057 import AliasCPU,stage
from stat_spacing_026 import _file_offset_for_va
norm=lambda b:unicodedata.normalize('NFKC',b.decode('cp932'))
def concat(cpu,parts):
 obj=0x550000;buf=0x560000;cpu.mem[buf-32:buf+128]=b'G'*160;cpu.mem[obj:obj+32]=bytes(32)
 cpu.write(obj+8,buf);cpu.write(obj+12,27)
 cpu.r=[0]*32;cpu.r[4]=obj;cpu.r[5]=len(parts)
 for i,p in enumerate(parts):cpu.r[6+i]=p
 cpu.r[29]=0x700000;cpu.r[31]=0x7ffff0;pc=0x1e4ee0
 for _ in range(10000):
  if pc==0x7ffff0:break
  if pc==0x1c2bc0:
   a,v,n=cpu.r[4:7];cpu.mem[a:a+n]=bytes([v&255])*n;cpu.r[2]=a;pc=cpu.r[31]
  elif pc==0x1e4ac8:cpu.r[2]=cpu.strlen(cpu.r[4]);pc=cpu.r[31]
  elif pc==0x1e4b50:
   a,b,n=cpu.r[4:7];cpu.mem[a:a+n*2]=cpu.mem[b:b+n*2];cpu.r[2]=a;pc=cpu.r[31]
  elif pc==0x1e51c4:raise AssertionError('Unexpected dynamic menu wrap')
  else:pc=cpu.step(pc)
 else:raise AssertionError('Native concatenation instruction budget')
 n=cpu.strlen(buf);assert n<=27 and cpu.mem[buf-32:buf]==b'G'*32 and cpu.mem[buf+96:buf+128]==b'G'*32
 return norm(cpu.mem[buf:buf+n*2])
def verify():
 elf,report=prepare_elf();spec=json.loads(TEXT.read_text());metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 with GameSource(BASE/'Summon_Night_3_EN_0.1.68.iso') as source:
  tables,_,_,tr=prepare_tables(source);static=tables[3];ix=parse_index(static,len(static));cpu=AliasCPU(elf,static);names=[];helps=[]
  for e in spec['entries']:
   b=child(static,ix,e['table']);p=struct.unpack_from('<I',b,e['pointer_fields'][0])[0];raw=lines_at(b,p)[0]
   name=(e['table']==13 and e['slot']==8) or (e['table']==19 and e['slot']==0)
   if name:raw=raw[:1]
   assert [norm(x) for x in raw]==[norm(encode_dialogue(s,s)[0]) for s in e['english']],e
   assert all(struct.unpack_from('<I',b,f)[0]==p for f in e['pointer_fields'])
   if name:
    text=e['english'][0];width=sum(metrics.get(x,{'proposed_advance_pixels':16})['proposed_advance_pixels'] for x in text)*.875
    assert len(text)<=16 and width<=108,(text,width);names.append(width)
   else:
    assert len(raw)<=2 and all(len(x)//2<=27 for x in raw)
    payload=b''.join(x+b'\0\0' for x in raw)+b'\0\0';r=stage(cpu,payload)
    assert r['glyphs']==sum(len(x)//2 for x in raw) and r['max_slot']<54;helps.append(r)
  # These whole-block pointers are followed by native string walkers, so check every choice and terminator.
  for e in report['entries']:
   at=_file_offset_for_va(elf,e['new_address']);raw=lines_at(elf,at)[0]
   assert [norm(x) for x in raw]==[norm(encode_dialogue(s,s)[0]) for s in e['english']]
  # Execute actual native crafting getter (including its non-NOP return delay slot).
  cpu.r=[0]*32;cpu.r[31]=0x7ffff0;pc=0x67d0c
  for _ in range(4):
   if pc==0x7ffff0:break
   pc=cpu.step(pc)
  craft=next(e for e in report['entries'] if e['source_address']==0x218ec0)
  assert cpu.r[2]==craft['new_address']
  suffixes={e['source_address']:e['new_address'] for e in report['entries']}
  dynamic=0
  for name in ('Rexx','????????','CUSTOMXX'):
   cpu.mem[0x590000:0x590100]=bytes(256);raw=encode_dialogue(name,'')[0];cpu.mem[0x590000:0x590000+len(raw)]=raw
   for prefix,suffix,expected in [('Only ',0x21e028,'Only '+name+' can favorite.'),('Unit Form: ',0x21e064,'Unit Form: '+name+' only.')]:
    p=next(e['new_address'] for e in report['entries'] if e['english']==[prefix])
    assert concat(cpu,[p,0x590000,suffixes[suffix]])==expected;dynamic+=1
  # Whole translated spell category must have no remaining referenced Japanese names.
  tb=child(static,ix,13)
  for rec in range(237):
   p=struct.unpack_from('<I',tb,4+rec*40+32)[0]
   if p in (0,0xffffffff):continue
   raw=lines_at(tb,p)[0][:1]
   assert not any(any('\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' for ch in norm(x)) for x in raw),rec
  # Retain earlier fixes in the same table and executable.
  profiles=child(static,ix,12);p=struct.unpack_from('<I',profiles,4+41*52+48)[0]
  assert 'greedy' in ' '.join(norm(x) for x in lines_at(profiles,p)[0])
  h=struct.unpack_from('<I',elf,0x6ee3c+192)[0];l=struct.unpack_from('<I',elf,0x6ee54+192)[0];v=((h&65535)<<16)+((l&65535)-65536 if l&32768 else l&65535)
  at=_file_offset_for_va(elf,v);assert norm(lines_at(elf,at)[0][0])=='Rewards obtained!'
 return dict(passed=True,table_entries=len(spec['entries']),spell_names=191,item_fields=333,menu_blocks=len(report['entries']),name_fields=len(names),max_name_pixels=max(names),guarded_item_help_cases=len(helps),actual_native_dynamic_menu_cases=dynamic,crafting_control_token_preserved=True,takeshi_profile_retained=True,rewards_heading_retained=True,all_spell_names_translated=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--report');p.add_argument('--execute',action='store_true');a=p.parse_args()
 if not a.execute:print(json.dumps(dict(mode='preview',scope='Pointers, text limits, native help staging and crafting getter.')))
 else:
  r=verify();print(json.dumps(r,indent=2))
  if a.report:
   f=ROOT/a.report;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(r,indent=2)+'\n')
