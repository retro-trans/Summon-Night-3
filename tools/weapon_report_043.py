"""Translate the reported weapon, Ishlar arts/name and shared sword-art help."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from character_labels import collect
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at,glyph_check
from verify_descriptions_021 import CPU
BASE=ROOT/'work/output/0.1.42'
TARGETS=ROOT/'work/translation/en/weapon_report_0.1.43/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 # Runtime trace: Generasneil -> native heading 0x1cbee0, caller RA 0x86250.
 # Reuse the proven magic-heading wrapper (null/unallocated native fallback).
 site=0x86248;word=struct.unpack_from('<I',old,0xc0814+192)[0]
 assert word==3<<26|0x34cbfc>>2
 assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbee0>>2
 from stages_pupil_names import parse_elf
 h=parse_elf(old)['phdrs'][2]
 assert (site,4) in list(struct.iter_unpack('<II',old[h[1]:h[1]+h[4]]))
 struct.pack_into('<I',out,site+192,word)
 assert all(a==b or site+192<=i<site+196 for i,(a,b) in enumerate(zip(old,out)))
 return bytes(out),dict(entries=[],weapon_heading_call=hex(site),vwf_wrapper='0x34cbfc',existing_jal_relocation=True)


def prepare_tables(source):
 targets=json.loads(TARGETS.read_text());index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));replacements={};reports=[]
 for n in sorted({e['table'] for e in targets['entries']}):
  table=next(t for t in index['tables'] if t['resource_path']==[3,n]);rows={r['id']:r for r in table['strings']}
  before=child(static,si,n);out=bytearray(before);fields=set();changes=[]
  for e in [e for e in targets['entries'] if e['table']==n]:
   r=rows[e['id']];p=r['source_offset'];nb=r['source_byte_length']
   assert sha(before[p:p+nb])==e['source_sha256']==r['source_sha256']
   raw=[encode_dialogue(s,'')[0] for s in e['lines']];counts=glyph_check(raw)
   assert max(counts)<=27 and (e['kind']=='help' or len(raw)==1 and counts[0]<=16)
   payload=b''.join(s+b'\0\0' for s in raw)+b'\0\0'
   out.extend(bytes(-len(out)%2));new=len(out);out.extend(payload)
   for ref in r['references']:
    f=ref['pointer_field_offset'];assert struct.unpack_from('<I',before,f)[0]==p
    struct.pack_into('<I',out,f,new);fields.update(range(f,f+4))
   changes.append(dict(e,new_offset=new,references=r['references'],counts=counts))
  assert all(a==b or i in fields for i,(a,b) in enumerate(zip(before,out)))
  replacements[n]=bytes(out);reports.append(dict(child=n,changes=changes,gameplay_fields_unchanged=True))
 patched=repack(static,replacements)
 labels,_,rows=collect(source);rows={r['id']:r for r in rows};out=bytearray(labels);fields=set();units=[]
 for e in targets['units']:
  r=rows[e['id']];p=r['source_offset'];nb=r['source_byte_length'];assert sha(labels[p:p+nb])==e['source_sha256']
  assert all(ref['slot']==1 for ref in r['references'])
  raw,_=encode_dialogue(e['text'],'');assert len(raw)//2<=10
  out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0')
  for ref in r['references']:
   f=ref['pointer_field_offset'];assert struct.unpack_from('<I',labels,f)[0]==p
   struct.pack_into('<I',out,f,new);fields.update(range(f,f+4))
  units.append(dict(e,new_offset=new,references=r['references']))
 assert all(a==b or i in fields for i,(a,b) in enumerate(zip(labels,out)))
 bank=source.resource('01.DAT',1);bi=parse_index(bank,len(bank));assert child(bank,bi,0)==labels
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 cached=child(master,mi,6);ci=parse_index(cached,len(cached));assert child(cached,ci,0)==labels
 master=repack(master,{7:patched,6:repack(cached,{0:bytes(out)})})
 return {3:patched},{1:repack(bank,{0:bytes(out)})},master,dict(units=units,tables=reports,character_name_reference='work/glossary/character_reference_sn6_vita.json')

def verify(elf,static):
 targets=json.loads(TARGETS.read_text());index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());si=parse_index(static,len(static));c=CPU(elf,static);cases=[]
 for e in targets['entries']:
  t=next(t for t in index['tables'] if t['resource_path']==[3,e['table']]);row=next(r for r in t['strings'] if r['id']==e['id']);tb=child(static,si,e['table'])
  for ref in row['references']:
   p=struct.unpack_from('<I',tb,ref['pointer_field_offset'])[0];lines,end=lines_at(tb,p);counts=glyph_check(lines)
   assert lines==[encode_dialogue(s,'')[0] for s in e['lines']] and tb[end:end+2]==b'\0\0'
  if e['kind']=='help':
   owner,source=0x500000,0x600000;buf=owner+0x144;payload=tb[p:end+2]
   c.mem[source:source+len(payload)]=payload;c.mem[buf-16:buf+190]=b'G'*206;c.mem[buf:buf+174]=bytes(174)
   c.r=[0]*32;c.r[16]=source;c.r[17]=owner;c.write(owner+0x44,source);pc=0x64990
   for _ in range(10000):
    if pc==0x64a38:break
    pc=c.step(pc)
   else:raise AssertionError('native staging-copy limit')
   assert c.mem[buf-16:buf]==b'G'*16 and c.mem[buf+174:buf+190]==b'G'*16
   assert c.mem[buf:buf+len(payload)]==payload
  cases.append(dict(id=e['id'],kind=e['kind'],lines=e['lines'],counts=counts))
 # Keep the confirmed Brave Goals crash fix in the cumulative build.
 from brave_fix_042 import verify as verify_brave
 assert struct.unpack_from('<I',elf,0x86248+192)[0]==struct.unpack_from('<I',elf,0xc0814+192)[0]
 from verify_menu_vwf_020 import CPU as VWFCPU
 from font_patch import CODE_VA
 heading=json.loads((BASE/'manifest.json').read_text())['magic_heading033_text']['heading'];dispatch_cases=0
 for base in [0x08804000,0x0890c000]:
  for allocated,text_present in [(False,False),(False,True),(True,False),(True,True)]:
   cpu=VWFCPU(elf,heading,base);obj=0x09000000;src=obj+0x1000;cpu.store(obj,bytes(256));cpu.store(obj+0xc0,struct.pack('<I',obj+0x2000 if allocated else 0))
   cpu.store(src,encode_dialogue('Generasneil','')[0]+b'\0\0');cpu.set('a0',obj);cpu.set('a1',src if text_present else 0);cpu.set('a2',77);seen=[]
   def packed(m):seen.append(('vwf',m.reg[4:7]));return {'v0':9}
   def native(m):seen.append(('native',m.reg[4:7]));return {'v0':7}
   cpu.native_handlers={base+0x34a0c8:packed,base+0x1cbee0:native};cpu.run(0x34cbfc-CODE_VA)
   good=allocated and text_present;assert seen==[('vwf' if good else 'native',[obj,src if text_present else 0,1 if good else 77])];dispatch_cases+=1
 return dict(cases=cases,native_help_cases=sum(e['kind']=='help' for e in targets['entries']),heading_dispatch_cases=dispatch_cases,brave_regression=verify_brave(elf,static),runtime_evidence='See work/ui/weapon_report_0.1.43/runtime.json')

if __name__=='__main__':
 from sn3_archive import GameSource
 elf,_=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as source:tables,_,_,report=prepare_tables(source)
 report['verification']=verify(elf,tables[3]);print(json.dumps(report,indent=2))
