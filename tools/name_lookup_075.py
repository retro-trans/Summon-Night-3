"""Display-only lookup for newly translated default unit names; custom names pass."""
import struct
from sn3_archive import ROOT,GameSource,parse_index,child
from dialogue_encoding import encode_dialogue
from list_vwf_020 import name_pairs,emitter
from font_patch import Assembler
from menu_code_020 import append
from stages_pupil_names import parse_elf
import json
def prepare(data):
 old_pairs,_,_=name_pairs();a=Assembler();emitter(len(old_pairs))(a)
 # The original list helper was appended at this immutable address in 020.
 original_base=0x349328
 # Resolve its entry from the historical manifest instead of guessing a build offset.
 m=json.loads((ROOT/'work/output/0.1.20/manifest.json').read_text())
 report=m['menu020_text']['list_vwf'] if 'menu020_text' in m else m.get('menu_vwf',{}).get('list_vwf')
 if report is None:
  from menu_release_020 import prepare_elf
  report=prepare_elf()[1]['list_vwf']
 lookup=int(report['code_address'],16)+report['labels']['saved_name']
 entries=json.loads((ROOT/'work/translation/en/menus_0.1.75/labels.json').read_text())['labels'];pairs=dict(old_pairs);audit=[]
 with GameSource(ROOT/'work/output/0.1.74/Summon_Night_3_EN_0.1.74.iso') as s:
  bank=s.resource('01.DAT',1);raw=child(bank,parse_index(bank,len(bank)),0)
  for e in entries:
   if not any(r['slot']==1 for r in e['references']):continue
   src=raw[e['source_offset']:e['source_offset']+e['source_byte_length']]
   target=encode_dialogue(e['english'][0],'')[0];pairs[src]=target
   audit.append(dict(source_sha256=e['source_sha256'],english=e['english'][0]))
  # Include names translated before this category sweep, notably protagonists.
  # Match original complete defaults only; never rewrite stored player names.
  import unicodedata,hashlib
  targets={r['pointer_field_offset']:encode_dialogue(e['english'][0],'')[0] for e in entries for r in e['references'] if r['slot']==1}
  with GameSource() as original:
   ob=original.resource('01.DAT',1);orig=child(ob,parse_index(ob,len(ob)),0)
  for row in range(struct.unpack_from('<I',orig)[0]):
   field=4+row*32+4;op=struct.unpack_from('<I',orig,field)[0];cp=struct.unpack_from('<I',raw,field)[0]
   if not op or not cp:continue
   oe=next(i for i in range(op,len(orig),2) if orig[i:i+2]==b'\0\0');ce=next(i for i in range(cp,len(raw),2) if raw[i:i+2]==b'\0\0')
   src=orig[op:oe];dst=targets.get(field,raw[cp:ce]);name=unicodedata.normalize('NFKC',dst.decode('cp932'))
   if not name.isascii() or len(dst)>32:continue
   pairs[src]=dst
   audit.append(dict(source_sha256=hashlib.sha256(src).hexdigest(),english=name))
 pairs=sorted(pairs.items());payload=bytearray(len(pairs)*8)
 for n,(src,dst) in enumerate(pairs):
  so=len(payload);payload.extend(src+b'\0\0');do=len(payload);payload.extend(dst+b'\0\0');struct.pack_into('<II',payload,n*8,so,do)
 payload.extend(bytes(-len(payload)%4));seg=parse_elf(data)['phdrs'][3];base=seg[2]+seg[4]
 def emit(a):
  a.label('default_name');a.move('v0','a0');a.branch(4,'a0','zero','return')
  a.table_address('t0');a.move('t2','t0');a.i(9,'t1','zero',len(pairs))
  a.label('next');a.i(35,'t3','t2',0);a.emit(11<<21|8<<16|11<<11|0x21);a.move('t4','a0');a.i(9,'t7','zero',33)
  a.label('compare');a.i(37,'t5','t3',0);a.i(37,'t6','t4',0);a.branch(5,'t5','t6','miss');a.branch(4,'t5','zero','found')
  a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.i(9,'t7','t7',-1);a.branch(5,'t7','zero','compare')
  a.label('miss');a.i(9,'t1','t1',-1);a.i(9,'t2','t2',8);a.branch(5,'t1','zero','next')
  a.label('return');a.ret()
  a.label('found');a.i(35,'v0','t2',4);a.emit(2<<21|8<<16|2<<11|0x21);a.ret()
  a.relocs.append((lookup-seg[2]-seg[4],0x304))
  a.label('named_type');a.i(9,'sp','sp',-48)
  for reg,off in [('ra',44),('a0',16),('a1',20),('a2',24)]:a.i(43,reg,'sp',off)
  a.move('a0','a1');a.jump('default_name');a.i(43,'v0','sp',28)
  a.move('a0','v0');a.jump(0x1e4ac8)
  a.i(35,'a0','sp',16);a.i(35,'a1','sp',28);a.i(35,'a2','sp',24)
  a.i(11,'t0','v0',17);a.branch(4,'t0','zero','named_native')
  a.move('a3','a2');a.move('a2','v0');a.jump(0x32e060);a.branch(4,'zero','zero','named_done')
  a.label('named_native');a.jump(0x1cbdec)
  a.label('named_done')
  for reg,off in [('a0',16),('a1',20),('a2',24),('ra',44)]:a.i(35,reg,'sp',off)
  a.i(9,'sp','sp',48);a.ret()
  a.relocs.append((0x347b5c-seg[2]-seg[4],0x304))
 # Keep the original relocated HI in the jump delay slot; dispatch resets t0.
 out=bytearray(data);f=seg[1]+lookup-seg[2];assert struct.unpack_from('<I',out,f)[0]==0x00801021
 struct.pack_into('<I',out,f,2<<26|base>>2)
 # Existing whole-string fields include status/gear and battle-card names.
 probe=Assembler();emit(probe);type_entry=base+probe.labels['named_type'];tf=seg[1]+0x347b5c-seg[2]
 assert struct.unpack_from('<II',out,tf)==(0x27bdffd0,0xafbf002c)
 struct.pack_into('<II',out,tf,2<<26|type_entry>>2,0)
 result,r=append(bytes(out),emit,{},bytes(payload))
 r.update(lookup_entry=lookup,lookup_file_offset=f,type_entry=0x347b5c,type_file_offset=tf,pairs=len(pairs),new_default_names=audit,save_bytes_unchanged=True,custom_names_preserved=True)
 return result,r,pairs
