"""Scoped reward and recruitment localization on immutable local 0.1.62."""
import json,struct,hashlib,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from menu_code_020 import append
from dialogue_encoding import encode_dialogue
from font_patch import REG
from stat_spacing_026 import _file_offset_for_va
from stages_pupil_names import parse_elf,validate_loader_structure
BASE=ROOT/'work/output/0.1.62'
TEXT=ROOT/'work/translation/en/rewards_0.1.63/strings.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
PAIRS=[(0x6ee3c,0x6ee54,0x219974),(0x6eee8,0x6eef8,0x219988),
 (0x6f45c,0x6f464,0x219998),(0x6f458,0x6f468,0x2199a0),(0x6f3d4,0x6f3d8,0x2199a4),
 (0x6f6d0,0x6f6d8,0x2199bc),(0x6f6e8,0x6f700,0x2199cc),(0x6f6f8,0x6f700,0x2199cc),
 (0x6f6f4,0x6f708,0x2199e0),(0x6f714,0x6f71c,0x2199bc),(0x6f710,0x6f724,0x2199f4),
 (0x6f728,0x6f730,0x219a0c),(0x6f6c0,0x6f734,0x219a20)]
def draft():
 return dict(version='0.1.63',source_build='0.1.62',literals=[dict(va=hex(va),source=jp,english=en) for va,jp,en in [
  (0x219974,'以下のものを手に','Rewards obtained!'),(0x219988,'入れました！！',' '),
  (0x219998,'傀儡「','Puppet "'),(0x2199a0,'「','"'),(0x2199a4,'」が','"'),
  (0x2199bc,'実体化した！','materialized!'),(0x2199cc,'戦列に加わった！','joined battle!'),
  (0x2199e0,'仲間に加わった！','joined the party!'),(0x2199f4,'サポートに加わった！','joined support!'),
  (0x219a0c,'戦列から外れた！','left battle!'),(0x219a20,'戦列に復帰した！','rejoined battle!')]],
  items=[dict(record=6,source='Fエイド',english='F Aid')]+[dict(record=189+n,source='設定イラスト'+(f'{n:02d}' if n else ''),english='Concept Art'+(f' {n:02d}' if n else '')) for n in range(34)],
  name_field_preserved=True,source_stats_and_rewards_preserved=True)
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();spec=json.loads(TEXT.read_text(encoding='utf8'));blob=bytearray();offsets={}
 for row in spec['literals']:
  va=int(row['va'],16);start=_file_offset_for_va(old,va);b=row['source'].encode('cp932');assert old[start:start+len(b)+2]==b+b'\0\0'
  offsets[va]=len(blob);blob.extend(encode_dialogue(row['english'],'')[0]+b'\0\0')
 def emit(a):
  a.label('popup');a.i(9,'sp','sp',-48)
  for reg,off in [('ra',44),('a0',16),('a1',20),('a2',24)]:a.i(43,reg,'sp',off)
  a.move('a0','a1');a.jump(0x1e4ac8);a.i(11,'t0','v0',33);a.i(43,'t0','sp',28)
  for reg,off in [('a0',16),('a1',20),('a2',24),('ra',44)]:a.i(35,reg,'sp',off)
  a.i(35,'t0','sp',28);a.i(9,'sp','sp',48);a.branch(4,'t0','zero','native');a.jump(0x34a0c8,link=False)
  a.label('native');a.jump(0x1cbdec,link=False)
 patched,r=append(old,emit,{},bytes(blob));out=bytearray(patched);table=int(r['code_address'],16)+r['labels']['table'];wrapper=int(r['code_address'],16)
 reloc=parse_elf(old)['phdrs'][2];records=set(struct.iter_unpack('<II',old[reloc[1]:reloc[1]+reloc[4]]));changed={};hvalues={}
 for hi,lo,source in PAIRS:
  h=struct.unpack_from('<I',old,hi+192)[0];l=struct.unpack_from('<I',old,lo+192)[0];signed=(l&65535)-65536 if l&32768 else l&65535
  assert h>>26==15 and l>>26==9 and ((h&65535)<<16)+signed==source
  assert (hi,5) in records and (lo,6) in records
  va=table+offsets[source];hv=(va+0x8000)>>16;assert hi not in hvalues or hvalues[hi]==hv;hvalues[hi]=hv
  for addr,w in [(hi,(h&0xffff0000)|hv),(lo,(l&0xffff0000)|(va&65535))]:
   assert addr not in changed or changed[addr]==w;changed[addr]=w;struct.pack_into('<I',out,addr+192,w)
 bindings={0x6ee50:wrapper,0x6eef4:wrapper,0x6f0f8:0x347b5c,0x6f474:wrapper,0x6f518:0x348a7c,0x6f5d4:wrapper,0x6f740:wrapper}
 for site,target in bindings.items():
  assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbdec>>2 and (site,4) in records
  word=3<<26|target>>2;struct.pack_into('<I',out,site+192,word);changed[site]=word
 allowed={i for va in changed for i in range(va+192,va+196)};assert all(i in allowed for i,(a,b) in enumerate(zip(patched,out)) if a!=b)
 report=dict(source_sha256=sha(old),output_sha256=sha(out),literal_addresses={hex(k):hex(table+v) for k,v in offsets.items()},pairs=[list(map(hex,x)) for x in PAIRS],bindings={hex(k):hex(v) for k,v in bindings.items()},popup_wrapper_address=hex(wrapper),append=r,structure=validate_loader_structure(out),player_name_field_unchanged=True)
 return bytes(out),report
def prior_audit_view(elf):
 expected,_=prepare_elf();assert elf==expected,'Unexpected 0.1.63 executable changes';return (BASE/'EBOOT.elf').read_bytes()
def prepare_names(source,write_assets=False):
 spec=json.loads(TEXT.read_text(encoding='utf8'));static=source.resource('02.DAT',3);ix=parse_index(static,len(static));old=child(static,ix,19);out=bytearray(old);reports=[];allowed=set()
 assert struct.unpack_from('<I',old)[0]==531
 for row in spec['items']:
  field=4+row['record']*24;ptr=struct.unpack_from('<I',old,field)[0];end=ptr
  while old[end:end+2]!=b'\0\0':end+=2
  assert unicodedata.normalize('NFKC',old[ptr:end].decode('cp932'))==row['source']
  b=encode_dialogue(row['english'],'')[0];assert len(b)//2<=16;out.extend(bytes(-len(out)%2));new=len(out);out.extend(b+b'\0\0');struct.pack_into('<I',out,field,new);allowed.update(range(field,field+4));reports.append(dict(**row,field=field,offset=new))
 out.extend(bytes(-len(out)%ix['unit_bytes']));assert all(i in allowed for i,(a,b) in enumerate(zip(old,out)) if a!=b)
 after=repack(static,{19:bytes(out)});ni=parse_index(after,len(after));assert all(child(after,ni,e['id'])==(bytes(out) if e['id']==19 else child(static,ix,e['id'])) for e in ix['entries'])
 return {3:after},[dict(table=19,entries=reports,original_pool_preserved=True,stats_unchanged=True)]
