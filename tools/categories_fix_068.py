"""Append source-bound category translations without changing numeric records."""
import argparse,json,struct,hashlib
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
BASE=ROOT/'work/output/0.1.67'
TEXT=ROOT/'work/translation/en/categories_0.1.68/targets.json'
MAP=ROOT/'work/translation/en/categories_0.1.68/map.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_tables(source):
 old=source.resource('02.DAT',3);ix=parse_index(old,len(old));replacements={};reports=[]
 entries=json.loads(TEXT.read_text())['entries']
 for n in sorted({e['table'] for e in entries}):
  before=child(old,ix,n);out=bytearray(before);allowed=set();changes=[]
  for e in (e for e in entries if e['table']==n):
   p=e['source_offset'];raw=lines_at(before,p)[0]
   if e['slot']==8:raw=raw[:1]
   assert sha(b'\0\0'.join(raw))==e['source_sha256'],(n,p)
   source_text=''.join(x.decode('cp932') for x in raw)
   encoded=b''.join(encode_dialogue(s,source_text)[0]+b'\0\0' for s in e['english'])
   if e['slot']!=8:encoded+=b'\0\0'
   at=len(out);assert at%2==0;out.extend(encoded)
   for f in e['pointer_fields']:
    assert struct.unpack_from('<I',before,f)[0]==p
    struct.pack_into('<I',out,f,at);allowed.update(range(f,f+4))
   changes.append(dict(records=e['records'],slot=e['slot'],pointer_fields=e['pointer_fields'],source_offset=p,new_offset=at,english=e['english'],encoded_bytes=len(encoded)))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
  replacements[n]=bytes(out);reports.append(dict(table=n,entries=len(changes),source_sha256=sha(before),output_sha256=sha(out),changes=changes,original_pool_preserved=True,numeric_fields_unchanged=True))
 result=repack(old,replacements);ni=parse_index(result,len(result))
 assert all(child(result,ni,e['id'])==child(old,ix,e['id']) for e in ix['entries'] if e['id'] not in replacements)
 return {3:result},{},source.resource('00.DAT',44),dict(tables=reports,entries=len(entries),units=[],undiscovered_labels_preserved=True)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();entries=json.loads(MAP.read_text())['entries'];payload=bytearray();offsets=[]
 rel=parse_elf(old)['phdrs'][2];relocs=set(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]))
 for e in entries:
  p=e['source_address'];end=old.index(b'\0',p+192)
  assert sha(old[p+192:end])==e['source_sha256']
  offsets.append(len(payload));payload.extend(encode_dialogue(e['english'],'')[0]+b'\0\0')
 payload.extend(bytes(-len(payload)%4))
 data,r=append(old,lambda a:a.ret(),{},bytes(payload));out=bytearray(data);base=int(r['code_address'],16)+r['labels']['table'];allowed=set();bindings=[]
 for e,offset in zip(entries,offsets):
  for f in e['pointer_fields']:
   assert (f,2) in relocs and struct.unpack_from('<I',old,f+192)[0]==e['source_address']
   struct.pack_into('<I',out,f+192,base+offset);allowed.update(range(f+192,f+196))
  bindings.append(dict(**e,new_address=hex(base+offset)))
 assert all(i in allowed for i,(a,b) in enumerate(zip(data,out)) if a!=b)
 r.update(source_sha256=sha(old),output_sha256=sha(out),entries=bindings,original_text_pool_preserved=True,existing_code_unchanged=True,structure=validate_loader_structure(out))
 return bytes(out),r

if __name__=='__main__':
 elf,r=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.67.iso') as src:_,_,_,t=prepare_tables(src)
 print(json.dumps(dict(mode='preview',elf_names=len(r['entries']),table_entries=t['entries'],tables=[dict(table=x['table'],entries=x['entries']) for x in t['tables']]),indent=2))
