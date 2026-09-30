"""Repair Brave Goal bundles on immutable 0.1.41; never modify rule fields."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at,glyph_check
from verify_descriptions_021 import CPU
BASE=ROOT/'work/output/0.1.41'
TARGETS=ROOT/'work/translation/en/brave_0.1.42/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def verify(elf,static):
 table=child(static,parse_index(static,len(static)),45)
 c=CPU(elf,static);cases=[]
 for e in json.loads(TARGETS.read_text())['entries']:
  for slot,expected in [(7,[e['title']]),(8,e['lines'])]:
   p=struct.unpack_from('<I',table,4+e['record']*68+slot*4)[0]
   lines,end=lines_at(table,p);counts=glyph_check(lines)
   assert lines==[encode_dialogue(s,'')[0] for s in expected]
   assert table[end:end+2]==b'\0\0' and max(counts)<=27
   # Execute the unmodified staging-copy loop, including MIPS delay slots.
   owner,source=0x500000,0x600000;buf=owner+0x144
   payload=table[p:end+2];c.mem[source:source+len(payload)]=payload
   c.mem[buf-16:buf+174+16]=b'G'*(174+32);c.mem[buf:buf+174]=bytes(174)
   c.r=[0]*32;c.r[16]=source;c.r[17]=owner;c.write(owner+0x44,source)
   pc=0x64990
   for _ in range(10000):
    if pc==0x64a38:break
    pc=c.step(pc)
   else:raise AssertionError('native copy instruction limit')
   assert c.mem[buf-16:buf]==b'G'*16 and c.mem[buf+174:buf+190]==b'G'*16
   assert c.mem[buf:buf+len(payload)]==payload
   cases.append(dict(record=e['record'],slot=slot,lines=expected,counts=counts,total=sum(counts),staging_guard=True))
 return dict(native_copy_cases=cases,glyph_capacity=54,max_line_cells=27,staging_bytes=174)

def prepare_elf():
 return (BASE/'EBOOT.elf').read_bytes(),dict(entries=[],unchanged=True)

def prepare_tables(source):
 static=source.resource('02.DAT',3);ix=parse_index(static,len(static));before=child(static,ix,45);out=bytearray(before)
 changes=[];fields=set();old_unsafe=[]
 for e in json.loads(TARGETS.read_text())['entries']:
  for slot,texts in [(7,[e['title']]),(8,e['lines'])]:
   f=4+e['record']*68+slot*4;old=struct.unpack_from('<I',before,f)[0]
   raw=[encode_dialogue(s,'')[0] for s in texts];glyph_check(raw)
   payload=b''.join(s+b'\0\0' for s in raw)+b'\0\0'
   if slot==8:
    previous,end=lines_at(before,old)
    try:glyph_check(previous)
    except AssertionError:old_unsafe.append(e['record'])
    else:raise AssertionError(('expected old overrun',e['record']))
   out.extend(bytes(-len(out)%2));p=len(out);out.extend(payload)
   struct.pack_into('<I',out,f,p);fields.update(range(f,f+4))
   changes.append(dict(record=e['record'],slot=slot,old_offset=old,new_offset=p,lines=texts,bytes=len(payload)))
 assert old_unsafe==list(range(5))
 assert all(x==y or i in fields for i,(x,y) in enumerate(zip(before,out)))
 patched=repack(static,{45:bytes(out)})
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched})
 report=dict(units=[],tables=[dict(child=45,changes=changes)],old_unsafe_descriptions=old_unsafe,unchanged_gameplay_fields=True,table_before_sha256=sha(before),table_after_sha256=sha(out))
 return {3:patched},{},master,report

if __name__=='__main__':
 from sn3_archive import GameSource
 elf,_=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as source:tables,_,_,report=prepare_tables(source)
 report['validation']=verify(elf,tables[3]);print(json.dumps(report,indent=2))
