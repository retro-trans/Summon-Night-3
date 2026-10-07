"""Append UI translations; preserve source pools, stats, and prior native hooks."""
import json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from battle_elf_refs import references
from stages_pupil_names import validate_loader_structure
BASE=ROOT/'work/output/0.1.69';TEXT=ROOT/'work/translation/en/categories_0.1.70/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def prepare_tables(source):
 old=source.resource('02.DAT',3);ix=parse_index(old,len(old));replacements={};reports=[]
 entries=json.loads(TEXT.read_text())['entries']
 for n in sorted({e['table'] for e in entries}):
  before=child(old,ix,n);out=bytearray(before);allowed=set();changes=[]
  for e in (e for e in entries if e['table']==n):
   p=e['source_offset'];raw=lines_at(before,p)[0]
   name=(n==13 and e['slot']==8) or (n==19 and e['slot']==0)
   if name:raw=raw[:1]
   assert sha(b'\0\0'.join(raw))==e['source_sha256'],(n,p)
   source_text=''.join(x.decode('cp932') for x in raw)
   payload=b''.join(encode_dialogue(s,source_text)[0]+b'\0\0' for s in e['english'])
   if not name:payload+=b'\0\0'
   at=len(out);assert at%2==0;out.extend(payload)
   for f in e['pointer_fields']:
    assert struct.unpack_from('<I',before,f)[0]==p
    struct.pack_into('<I',out,f,at);allowed.update(range(f,f+4))
   changes.append(dict(records=e['records'],slot=e['slot'],pointer_fields=e['pointer_fields'],source_offset=p,new_offset=at,english=e['english']))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
  replacements[n]=bytes(out);reports.append(dict(table=n,entries=len(changes),changes=changes,original_pool_preserved=True,numeric_fields_unchanged=True))
 result=repack(old,replacements);ni=parse_index(result,len(result))
 assert all(child(result,ni,e['id'])==child(old,ix,e['id']) for e in ix['entries'] if e['id'] not in replacements)
 from PIL import Image
 from menu_art_015 import descend,replace_tree
 from sn3_ui_textures import texture_records,decode_texture
 from setup_ui_patch import encode_texture
 art=Image.open(ROOT/'work/ui/categories_0.1.70/notice_english.png').convert('RGBA')
 native=descend(source.resource('02.DAT',25),[0]);row=texture_records(native)[0]
 assert row['width']==480 and row['height']==272
 original=decode_texture(native,row);assert encode_texture(native,row,original)[0]==native
 packed,decoded,changed=encode_texture(native,row,art.resize((480,272),Image.Resampling.LANCZOS))
 assert len(packed)==len(native)
 packs={3:result,25:replace_tree(source.resource('02.DAT',25),{(0,):packed})}
 return packs,{},source.resource('00.DAT',44),dict(tables=reports,entries=len(entries),units=[],startup_notice=dict(source_sha256=sha(native),output_sha256=sha(packed),changed_pixels=changed,native_size=[480,272],palette_and_geometry_preserved=True),undiscovered_labels_preserved=True)
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();menus=json.loads(TEXT.read_text())['menus'];payload=bytearray();offsets=[]
 for e in menus:
  pos=e['source_address']+192;raw=[]
  for _ in range(e['source_lines']):
   end=pos
   while old[end:end+2]!=b'\0\0':end+=2
   raw.append(old[pos:end]);pos=end+2
  assert sha(b'\0\0'.join(raw))==e['source_sha256']
  offsets.append(len(payload))
  source=''.join(x.decode('cp932') for x in raw)
  payload.extend(b''.join((encode_dialogue(s,raw[i].decode('cp932'))[0] if s else b'')+b'\0\0' for i,s in enumerate(e['english']))+b'\0\0')
 payload.extend(bytes(-len(payload)%4));data,r=append(old,lambda a:a.ret(),{},bytes(payload));out=bytearray(data)
 table=int(r['code_address'],16)+r['labels']['table'];refs,users,pairs=references(old);changed={};hv={};bindings=[]
 targets={e['source_address'] for e in menus}
 for e,offset in zip(menus,offsets):
  va=e['source_address'];new=table+offset
  assert all(ref in refs[va] for ref in e['bindings'])
  assert e.get('selected_consumers') or refs[va]==e['bindings']
  for ref in e['bindings']:
   if ref['kind']=='pointer':
    f=ref['address'];assert struct.unpack_from('<I',old,f+192)[0]==va;changed[f]=new
   else:
    hi,lo=ref['high'],ref['low'];assert all(x['target'] in targets for x in users[hi]),('Shared high consumers',hex(hi),users[hi])
    h=struct.unpack_from('<I',old,hi+192)[0];l=struct.unpack_from('<I',old,lo+192)[0];v=(new+0x8000)>>16
    assert hi not in hv or hv[hi]==v;hv[hi]=v
    changed[hi]=(h&0xffff0000)|v;changed[lo]=(l&0xffff0000)|(new&65535)
  bindings.append(dict(**e,new_address=new))
 for f,w in changed.items():struct.pack_into('<I',out,f+192,w)
 allowed={i for f in changed for i in range(f+192,f+196)}
 assert all(i in allowed for i,(a,b) in enumerate(zip(data,out)) if a!=b)
 r.update(source_sha256=sha(old),output_sha256=sha(out),entries=bindings,changed_native_words={hex(k):hex(v) for k,v in changed.items()},original_text_pool_preserved=True,structure=validate_loader_structure(out))
 return bytes(out),r
if __name__=='__main__':
 e,r=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.69.iso') as src:_,_,_,t=prepare_tables(src)
 print(json.dumps(dict(mode='preview',menu_blocks=len(r['entries']),table_fields=t['entries'],native_words=r['changed_native_words']),indent=2))
