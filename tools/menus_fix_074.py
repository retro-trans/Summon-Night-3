"""Append menu targets and preserve symbolic stat cells on their native grid."""
import json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from battle_elf_refs import references
from font_patch import REG
from stages_pupil_names import validate_loader_structure

BASE=ROOT/'work/output/0.1.73'
TEXT=ROOT/'work/translation/en/menus_0.1.74/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_tables(source):
 cfg=json.loads(TEXT.read_text());static=source.resource('02.DAT',3);si=parse_index(static,len(static));replacements={};reports=[]
 for n in sorted({e['table'] for e in cfg['entries']}):
  before=child(static,si,n);out=bytearray(before);allowed=set();changes=[]
  for e in (e for e in cfg['entries'] if e['table']==n):
   p=e['source_offset'];raw=lines_at(before,p)[0];raw=raw[:1] if e['kind']=='name' else raw
   assert sha(b'\0\0'.join(raw))==e['source_sha256']
   payload=b''.join(encode_dialogue(s,'')[0]+b'\0\0' for s in e['english'])+b'\0\0';at=len(out);assert at%2==0;out.extend(payload)
   for f in e['pointer_fields']:
    assert struct.unpack_from('<I',before,f)[0]==p
    struct.pack_into('<I',out,f,at);allowed.update(range(f,f+4))
   changes.append(dict(e,new_offset=at))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
  replacements[n]=bytes(out);reports.append(dict(table=n,changes=changes,numeric_fields_unchanged=True,original_pool_preserved=True))
 patched=repack(static,replacements)
 labels_pack=source.resource('01.DAT',1);li=parse_index(labels_pack,len(labels_pack));before=child(labels_pack,li,0);out=bytearray(before);allowed=set();label_changes=[]
 for e in cfg['labels']:
  p=e['source_offset'];assert sha(before[p:p+e['source_byte_length']])==e['source_sha256']
  raw=encode_dialogue(e['english'][0],'')[0];assert len(raw)//2<=16
  at=len(out);out.extend(raw+b'\0\0')
  for ref in e['references']:
   f=ref['pointer_field_offset'];assert struct.unpack_from('<I',before,f)[0]==p
   struct.pack_into('<I',out,f,at);allowed.update(range(f,f+4))
  label_changes.append(dict(e,new_offset=at))
 assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
 bank=repack(labels_pack,{0:bytes(out)})
 # The bank has archive-sector padding; the resident copy ends at its own
 # index boundary. Copying bank-sector padding shifts all following tables.
 cached=bank[:parse_index(bank,len(bank))['indexed_end']]
 master=repack(source.resource('00.DAT',44),{6:cached,7:patched})
 return {3:patched},{1:bank},master,dict(entries=len(cfg['entries'])+len(cfg['labels']),tables=reports,units=label_changes,numeric_fields_unchanged=True,original_pools_preserved=True,custom_player_name_logic_unchanged=True)

def emit_stat_dispatch(a):
 # s2 owns the mode; s4 advances by 0x3a for each row. Reading s4+0x34
 # misclassifies subsequent rows. The live Summon Index uses mode 2.
 a.label('stat_dispatch');a.i(35,'t0','s2',0x34)
 a.i(9,'t1','zero',2);a.branch(4,'t0','t1','prefix')
 a.i(9,'t1','zero',6);a.branch(4,'t0','t1','prefix')
 a.i(9,'t1','zero',26);a.branch(5,'t0','t1','prior')
 a.label('prefix');a.i(37,'t0','s4',0x4c)
 for cell in (0xaa84,0xac84):
  a.i(13,'t1','zero',cell);a.branch(4,'t0','t1','native')
 a.i(12,'t1','t0',255);a.i(9,'t2','zero',0x83);a.branch(5,'t1','t2','vwf')
 a.emit(REG['t0']<<16|REG['t1']<<11|8<<6|2)
 a.i(9,'t1','t1',-0x9f);a.i(11,'t1','t1',0x18);a.branch(4,'t1','zero','vwf')
 a.label('native');a.emit(REG['a2']<<21|8);a.emit(0)
 a.label('vwf');a.jump(0x347be0,link=False)
 a.label('prior');a.jump(0x352570,link=False)

def emit_static_bind(a,offset,tail,size):
 # Protect only the overlapping tail: keep PSP video/audio allocation headroom.
 # Copy before native binding, then redirect its twelve tail-child lookups.
 a.label('static_bind');a.i(9,'sp','sp',-32)
 for reg,off in [('s0',16),('s1',20),('ra',28)]:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.move('s1','a1');a.table_address('a0')
 a.i(15,'t0','zero',offset>>16);a.i(13,'t0','t0',offset&65535)
 a.emit(REG['a0']<<21|REG['t0']<<16|REG['a0']<<11|0x21)
 a.i(15,'t0','zero',tail>>16);a.i(13,'t0','t0',tail&65535)
 a.emit(REG['s1']<<21|REG['t0']<<16|REG['a1']<<11|0x21)
 a.i(43,'a1','a0',0);a.i(9,'a0','a0',16)
 a.i(15,'a2','zero',size>>16);a.i(13,'a2','a2',size&65535);a.jump(0x1c2b80)
 a.move('a0','s0');a.move('a1','s1');a.jump(0x197f90)
 for reg,off in [('s0',16),('s1',20),('ra',28)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',32);a.ret()
 a.label('static_child');a.i(9,'sp','sp',-32);a.i(43,'ra','sp',28)
 a.jump(0x1e6bd4);a.table_address('t1')
 a.i(15,'t0','zero',offset>>16);a.i(13,'t0','t0',offset&65535)
 a.emit(REG['t1']<<21|REG['t0']<<16|REG['t1']<<11|0x21)
 a.i(35,'t0','t1',0);a.emit(REG['v0']<<21|REG['t0']<<16|REG['t0']<<11|0x23)
 a.emit(REG['t0']<<16|REG['t2']<<11|11<<6|2)
 assert size%2048==0
 a.i(11,'t2','t2',size//2048);a.branch(4,'t2','zero','child_done')
 a.i(9,'t1','t1',16);a.emit(REG['t1']<<21|REG['t0']<<16|REG['v0']<<11|0x21)
 a.label('child_done');a.i(35,'ra','sp',28);a.i(9,'sp','sp',32);a.ret()

def emit_title_style(a):
 # The native footer starts at x=407: retain its style and height, but fit
 # the complete English label into the remaining 72 pixels.
 a.label('title_style');a.i(43,'a1','a0',0xc4)
 a.i(15,'t0','zero',0x3f40);a.i(43,'t0','sp',0x10);a.ret()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TEXT.read_text());payload=bytearray();offsets=[]
 for e in cfg['menus']:
  raw=lines_at(old,e['source_address']+192)[0][:e['source_lines']]
  assert sha(b'\0\0'.join(raw))==e['source_sha256']
  offsets.append(len(payload));payload.extend(b''.join(encode_dialogue(s,'')[0]+b'\0\0' for s in e['english'])+b'\0\0')
 payload.extend(bytes(-len(payload)%4))
 with GameSource(BASE/'Summon_Night_3_EN_0.1.73.iso') as source:static=prepare_tables(source)[0][3]
 tail=parse_index(static,len(static))['entries'][37]['offset'];tail_size=len(static)-tail
 arena_offset=len(payload);payload.extend(bytes(16+tail_size))
 hooks={0x642c0:('stat_dispatch',3<<26|0x352570>>2),0x158e68:(0x347b5c,3<<26|0x1cbdec>>2),0x158e84:(0x347b5c,3<<26|0x1cbdec>>2),0x158e90:('title_style',3<<26|0x1cbf60>>2),0x13a44:('static_bind',3<<26|0x197f90>>2)}
 tail_sites=(0x198620,0x19869c,0x1986fc,0x198764,0x198784,0x1987c8,0x1987f0,0x19881c,0x198840,0x198858,0x1989bc,0x1989e4)
 hooks.update({p:('static_child',3<<26|0x1e6bd4>>2) for p in tail_sites})
 def emit(a):emit_stat_dispatch(a);emit_static_bind(a,arena_offset,tail,tail_size);emit_title_style(a)
 data,r=append(old,emit,hooks,bytes(payload));out=bytearray(data);table=int(r['code_address'],16)+r['labels']['table'];refs,users,_=references(old);changed={};hv={};bindings=[];targets={e['source_address'] for e in cfg['menus']}
 for e,offset in zip(cfg['menus'],offsets):
  va=e['source_address'];new=table+offset
  if e.get('branch_delay_references'):
   assert va==0x21629c and e['bindings']==[dict(kind='hilo',high=hi,low=0x5d534,register=4) for hi in (0x5d508,0x5d510,0x5d520)]
   assert all(struct.unpack_from('<I',old,hi+192)[0]==0x3c040021 for hi in (0x5d508,0x5d510,0x5d520))
   assert struct.unpack_from('<I',old,0x5d534+192)[0]==0x2484629c
  else:assert refs[va]==e['bindings']
  for ref in e['bindings']:
   if ref['kind']=='pointer':changed[ref['address']]=new
   else:
    hi,lo=ref['high'],ref['low']
    if not e.get('branch_delay_references'):assert all(x['target'] in targets for x in users[hi])
    h,l=struct.unpack_from('<I',old,hi+192)[0],struct.unpack_from('<I',old,lo+192)[0];v=(new+0x8000)>>16
    assert hi not in hv or hv[hi]==v;hv[hi]=v
    changed[hi]=(h&0xffff0000)|v;changed[lo]=(l&0xffff0000)|(new&65535)
  bindings.append(dict(e,new_address=new))
 for f,w in changed.items():struct.pack_into('<I',out,f+192,w)
 r.update(source_sha256=sha(old),output_sha256=sha(out),entries=bindings,changed_native_words={hex(k):hex(v) for k,v in changed.items()},structure=validate_loader_structure(out),stat_rule='Modes 2, 6 or 26 with symbolic stat prefix: native grid; ordinary text: existing VWF.',original_pool_preserved=True,static_arena_address=table+arena_offset+16,static_arena_context=table+arena_offset,static_arena_bytes=tail_size,static_tail_offset=tail,static_full_bytes=len(static),static_child_hooks=[hex(p) for p in tail_sites],static_arena_offset=arena_offset)
 assert r['structure'] and validate_loader_structure(out)
 return bytes(out),r

if __name__=='__main__':
 e,r=prepare_elf();print(json.dumps(dict(mode='preview',native_words=r['changed_native_words'],helper_bytes=r['code_bytes'])))
