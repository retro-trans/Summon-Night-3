"""Append English UI pools while preserving historical data and shared HI users."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from battle_elf_refs import references
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
from setup_native_075 import ui_lines
BASE=ROOT/'work/output/0.1.74'
TEXT=ROOT/'work/translation/en/menus_0.1.75'
def sha(b):return hashlib.sha256(b).hexdigest()
def prepare_tables(source):
 cfg=json.loads((TEXT/'labels.json').read_text());bank=source.resource('01.DAT',1);ix=parse_index(bank,len(bank));before=child(bank,ix,0);out=bytearray(before);allowed=set();changes=[]
 for e in cfg['labels']:
  p=e['source_offset'];assert sha(before[p:p+e['source_byte_length']])==e['source_sha256']
  raw=encode_dialogue(e['english'][0],'')[0];assert len(raw)//2<=16
  at=len(out);out.extend(raw+b'\0\0')
  for r in e['references']:
   f=r['pointer_field_offset'];assert struct.unpack_from('<I',before,f)[0]==p
   struct.pack_into('<I',out,f,at);allowed.update(range(f,f+4))
  changes.append(dict(e,new_offset=at))
 assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
 patched=repack(bank,{0:bytes(out)});cached=patched[:parse_index(patched,len(patched))['indexed_end']]
 master=repack(source.resource('00.DAT',44),{6:cached})
 return {3:source.resource('02.DAT',3)},{1:patched},master,dict(entries=len(changes),units=changes,numeric_fields_unchanged=True,original_pools_preserved=True,custom_player_name_logic_unchanged=True)
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads((TEXT/'native.json').read_text());refs,users,pairs=references(old)
 entries={e['source_address']:e for e in cfg['entries']};targets=set(entries)
 # A shared HI instruction is a unit: preserve every sibling low reference.
 while True:
  more={u['target'] for va in targets for r in refs.get(va,[]) if r['kind']=='hilo' for u in users[r['high']]}
  if more<=targets:break
  targets|=more
 assert all(0x215000<=v<0x21fc00 for v in targets),[hex(v) for v in targets if not 0x215000<=v<0x21fc00]
 from reward_width_075 import emit as reward_emit
 def emit(a):reward_emit(a)
 seg=parse_elf(old)['phdrs'][3]
 from font_patch import Assembler
 probe=Assembler();emit(probe);table=seg[2]+seg[4]+len(probe.words)*4
 start=((table+0x8000+0xffff)//0x10000)*0x10000-0x8000
 payload=bytearray(start-table);offsets={};report=[]
 for va in sorted(targets):
  e=entries.get(va);raw=ui_lines(old,va+192,e['source_lines'] if e else 3)
  if e:
   raw=raw[:e['source_lines']];assert sha(b'\0\0'.join(raw))==e['source_sha256']
   assert refs[va]==e['bindings']
   encoded=[encode_dialogue(s,src.decode('cp932'))[0] for s,src in zip(e['english'],raw)]
  else:encoded=raw
  offsets[va]=len(payload)
  payload.extend(b''.join(s+b'\0\0' for s in encoded)+b'\0\0')
  report.append(dict(source_address=va,english=e['english'] if e else None,source_sha256=sha(b'\0\0'.join(raw)),shared_sibling_preserved=e is None,new_address=table+offsets[va]))
 assert len(payload)-(start-table)<65536
 hooks={p:(0x34a0c8,3<<26|0x1cbdec>>2) for p in [0x6ec54,0x6ed3c,0x6ed58,0x6ed74,0x6ed90]}
 hooks[0x6ecec]=('reward_cells',3<<26|0x1e4ac8>>2)
 payload.extend(bytes(-len(payload)%4));data,app=append(old,emit,hooks,bytes(payload));out=bytearray(data)
 assert int(app['code_address'],16)+app['labels']['table']==table
 words={};highs={}
 for va in sorted(targets):
  new=table+offsets[va]
  for r in refs.get(va,[]):
   if r['kind']=='pointer':words[r['address']]=new;continue
   hi,lo=r['high'],r['low'];h,l=struct.unpack_from('<I',old,hi+192)[0],struct.unpack_from('<I',old,lo+192)[0]
   assert all(u['target'] in targets for u in users[hi])
   hv=(new+0x8000)>>16;assert hi not in highs or highs[hi]==hv;highs[hi]=hv
   words[hi]=(h&0xffff0000)|hv;words[lo]=(l&0xffff0000)|(new&65535)
 for at,value in words.items():struct.pack_into('<I',out,at+192,value)
 allowed={i for at in words for i in range(at+192,at+196)}
 assert all(i in allowed for i,(a,b) in enumerate(zip(data,out)) if a!=b)
 assert validate_loader_structure(out)
 app.update(source_sha256=sha(old),output_sha256=sha(out),entries=report,changed_native_words={hex(k):hex(v) for k,v in words.items()},original_pool_preserved=True,shared_hi_users_preserved=True)
 from name_lookup_075 import prepare as names
 final,names_report,_=names(bytes(out));app['default_name_lookup']=names_report
 app['output_sha256']=sha(final)
 return final,app
if __name__=='__main__':
 e,r=prepare_elf();print(json.dumps(dict(entries=len(r['entries']),bytes_added=r['code_bytes'],shared_siblings=sum(x['shared_sibling_preserved'] for x in r['entries']))))
