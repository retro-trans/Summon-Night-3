"""Append bounded condition text and exact-match UI name/VWF dispatch."""
import json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from battle_elf_refs import references
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
from stat_spacing_026 import _file_offset_for_va as off
from menus_fix_074 import emit_static_bind
from menus_fix_076 import TAIL_SITES
from list_vwf_020 import name_pairs
from font_patch import Assembler
from report_ui_061 import add
from prof_reflow_080 import emit as prof_emit
from skill_pool_080 import emit as pool_emit
BASE=ROOT/'work/output/0.1.79';TEXT=ROOT/'work/translation/en/ui_0.1.80/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_tables(source):
 cfg=json.loads(TEXT.read_text());st=source.resource('02.DAT',3);ix=parse_index(st,len(st));changes=[];replacement={}
 for n in sorted({e['table'] for e in cfg['entries']}):
  before=child(st,ix,n);out=bytearray(before);allowed=set()
  for e in (e for e in cfg['entries'] if e['table']==n):
   raw=lines_at(before,e['source_offset'])[0][0];assert sha(raw)==e['source_sha256']
   p=len(out);out.extend(b''.join(encode_dialogue(t,raw.decode('cp932'))[0]+bytes(2) for t in e['english'])+bytes(2))
   assert struct.unpack_from('<I',before,e['field'])[0]==e['source_offset'];struct.pack_into('<I',out,e['field'],p);allowed.update(range(e['field'],e['field']+4));changes.append(dict(e,new_offset=p))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b);replacement[n]=bytes(out)
 patched=repack(st,replacement);master=repack(source.resource('00.DAT',44),{7:patched})
 return {3:patched},{},master,dict(entries=len(changes),changes=changes,numeric_fields_unchanged=True,original_pools_preserved=True)

def emit(a,arena,tail,size,prior,guard):
 emit_static_bind(a,arena,tail,size)
 prof_emit(a,guard)
 pool_emit(a)
 # Index by first U16 cell; most unrelated Latin widgets exit without scanning names.
 a.label('match');a.move('v0','a0');a.branch(4,'a0','zero','match_return');a.table_address('t0');a.i(35,'t1','t0',0);a.i(9,'t2','t0',4);a.i(37,'t8','a0',0)
 a.label('group');a.branch(4,'t1','zero','match_return');a.i(35,'t3','t2',0);a.branch(4,'t3','t8','group_found');a.i(9,'t2','t2',12);a.i(9,'t1','t1',-1);a.branch(4,'zero','zero','group')
 a.label('group_found');a.i(35,'t1','t2',4);a.i(35,'t2','t2',8);add(a,'t2','t0','t2')
 a.label('candidate');a.branch(4,'t1','zero','match_return');a.i(35,'t3','t2',0);add(a,'t3','t0','t3');a.move('t4','a0');a.i(9,'t7','zero',33)
 a.label('compare');a.i(37,'t5','t3',0);a.i(37,'t6','t4',0);a.branch(5,'t5','t6','miss');a.branch(4,'t5','zero','found');a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.i(9,'t7','t7',-1);a.branch(5,'t7','zero','compare')
 a.label('miss');a.i(9,'t2','t2',8);a.i(9,'t1','t1',-1);a.branch(4,'zero','zero','candidate')
 a.label('found');a.i(35,'v0','t2',4);add(a,'v0','t0','v0');a.i(9,'v1','zero',1);a.ret()
 a.label('match_return');a.move('v1','zero');a.ret()
 a.label('draw');a.i(9,'sp','sp',-96)
 for r,o in [('ra',92),('s0',64),('s1',68),('s2',72),('s3',76),('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(43,r,'sp',o)
 a.move('s0','a0');a.move('s1','zero');a.branch(4,'s0','zero','native_draw')
 a.i(35,'s2','s0',0x30);a.branch(4,'s2','zero','native_draw');a.i(35,'s3','s0',0x3c);a.branch(4,'s3','zero','native_draw');a.i(11,'t0','s3',257);a.branch(4,'t0','zero','native_draw')
 a.i(35,'t0','s0',0x34);a.i(43,'t0','sp',48);a.i(36,'t0','s0',0x64);a.i(43,'t0','sp',52)
 a.label('rows');a.i(35,'a0','s2',0);a.jump('match');a.branch(4,'v1','zero','next_row');a.i(43,'v0','s2',0);a.i(9,'s1','zero',1)
 a.label('next_row');a.i(9,'s2','s2',16);a.i(9,'s3','s3',-1);a.branch(5,'s3','zero','rows');a.branch(4,'s1','zero','native_draw')
 # Use the existing long Latin strip binder for every row of this exact UI widget.
 a.i(43,'zero','s0',0x34);a.i(9,'t0','zero',-1);a.i(40,'t0','s0',0x64);a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x400);a.i(43,'t0','s0',0)
 a.label('native_draw')
 for r,o in [('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(35,r,'sp',o)
 a.jump(prior);a.branch(4,'s1','zero','draw_return');a.i(35,'t0','sp',48);a.i(43,'t0','s0',0x34);a.i(35,'t0','sp',52);a.i(40,'t0','s0',0x64)
 a.label('draw_return')
 for r,o in [('s0',64),('s1',68),('s2',72),('s3',76),('ra',92)]:a.i(35,r,'sp',o)
 a.i(9,'sp','sp',96);a.ret()

def prepare_elf(static):
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TEXT.read_text());refs,users,_=references(old);entries={e['source_address']:e for e in cfg['menus']};targets=set(entries)
 # Two branch-specific HI/LO pairs are intentionally separate; linear pairing missed them.
 explicit={0x21debc:[dict(kind='hilo',high=0x141da8,low=0x141e04,register=5)],0x21dedc:[dict(kind='hilo',high=0x141db4,low=0x141e20,register=5)]}
 for va,rs in explicit.items():refs[va]=rs
 while True:
  more={u['target'] for va in targets for r in refs.get(va,[]) if r['kind']=='hilo' for u in users.get(r['high'],[])}
  if more<=targets:break
  targets|=more
 tail=parse_index(static,len(static))['entries'][37]['offset'];size=len(static)-tail
 prior=(struct.unpack_from('<I',old,0x1b0f8+192)[0]&0x3ffffff)<<2
 guard=(struct.unpack_from('<I',old,0x64820+192)[0]&0x3ffffff)<<2
 pairs=dict(name_pairs()[0])
 # Identity matches select VWF without changing the wording.
 for t in cfg['popup_vwf_names']:
  raw=encode_dialogue(t,'')[0];pairs[raw]=raw
 pairs=sorted(pairs.items());groups={}
 for src,dst in pairs:groups.setdefault(struct.unpack_from('<H',src)[0],[]).append((src,dst))
 payload=bytearray(4+12*len(groups));struct.pack_into('<I',payload,0,len(groups))
 for i,(key,group) in enumerate(sorted(groups.items())):
  records=len(payload);payload.extend(bytes(8*len(group)));struct.pack_into('<III',payload,4+12*i,key,len(group),records)
  for j,(src,dst) in enumerate(group):
   sp=len(payload);payload.extend(src+bytes(2));dp=len(payload);payload.extend(dst+bytes(2));struct.pack_into('<II',payload,records+8*j,sp,dp)
 payload.extend(bytes(-len(payload)%4))
 probe=Assembler();emit(probe,0,tail,size,prior,guard);seg=parse_elf(old)['phdrs'][3];table=seg[2]+seg[4]+len(probe.words)*4
 start=((table+len(payload)+0x8000+0xffff)//0x10000)*0x10000-0x8000;payload.extend(bytes(start-table-len(payload)));offsets={};rows=[]
 for va in sorted(targets):
  e=entries.get(va);raw=lines_at(old,off(old,va))[0][:e['source_lines'] if e else 3]
  if e:assert sha(b'\0\0'.join(raw))==e['source_sha256']
  offsets[va]=len(payload);encoded=[encode_dialogue(t,src.decode('cp932'))[0] for t,src in zip(e['english'],raw)] if e else raw
  payload.extend(b''.join(t+bytes(2) for t in encoded)+bytes(2));rows.append(dict(source_address=va,new_address=table+offsets[va],english=e['english'] if e else None))
 assert len(payload)-(start-table)<65536
 payload.extend(bytes(-len(payload)%4));arena=len(payload);payload.extend(bytes(size+16))
 hooks={p:('static_child',struct.unpack_from('<I',old,p+192)[0]) for p in TAIL_SITES};hooks[0x13a44]=('static_bind',struct.unpack_from('<I',old,0x13a44+192)[0]);hooks[0x1b0f8]=('draw',struct.unpack_from('<I',old,0x1b0f8+192)[0])
 hooks[0x64820]=('prof_reflow',struct.unpack_from('<I',old,0x64820+192)[0])
 hooks[0x146fcc]=('learn_bind',3<<26|0x347b5c>>2)
 data,r=append(old,lambda a:emit(a,arena,tail,size,prior,guard),hooks,bytes(payload));assert int(r['code_address'],16)+r['labels']['table']==table
 out=bytearray(data)
 for site,name in [(0x1b0f8,'draw'),(0x64820,'prof_reflow')]:struct.pack_into('<I',out,site+192,2<<26|(int(r['code_address'],16)+r['labels'][name])>>2)
 words={};highs={}
 for va in sorted(targets):
  new=table+offsets[va]
  for ref in refs.get(va,[]):
   if ref['kind']=='pointer':words[ref['address']]=new;continue
   hi,lo=ref['high'],ref['low'];hv=(new+0x8000)>>16;assert hi not in highs or highs[hi]==hv;highs[hi]=hv
   for at,value in [(hi,hv),(lo,new&65535)]:words[at]=(struct.unpack_from('<I',old,at+192)[0]&0xffff0000)|value
 for at,value in words.items():struct.pack_into('<I',out,at+192,value)
 assert validate_loader_structure(out)
 r.update(entries=rows,changed_native_words={hex(k):hex(v) for k,v in words.items()},static_tail_offset=tail,static_arena_bytes=size,static_arena_context=table+arena,static_arena_address=table+arena+16,prior_draw=prior,prior_guard=guard,exact_name_pairs=len(pairs),summon_name_pairs=len(name_pairs()[0]),bounded_match_cells=32,output_sha256=sha(out))
 return bytes(out),r


