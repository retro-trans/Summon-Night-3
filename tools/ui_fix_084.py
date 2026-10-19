"""Bounded VWF for reward/class panes and default summon animation labels."""
import hashlib,json,struct
from sn3_archive import ROOT
from font_patch import Assembler,REG
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
from stat_spacing_026 import _file_offset_for_va as off
from dialogue_encoding import encode_dialogue
from battle_elf_refs import references
from equipment_ui_082 import captions
from reward_width_075 import emit as width_emit

BASE=ROOT/'work/output/0.1.83'
TEXT=ROOT/'work/translation/en/ui_0.1.84/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def encoded(t):return (encode_dialogue(t,t)[0] if t else b'')+bytes(2)

def emit(a,prior):
 width_emit(a)
 # The 082 captions already occupy an immutable arena. Match those pointers
 # rather than allocating a duplicate text index in scarce PSP user memory.
 a.label('match');a.move('v0','zero');a.branch(4,'a0','zero','match_end');a.table_address('t0');a.branch(4,'a0','t0','found')
 # Class confirmation concatenates into a native buffer; recognize the copied
 # question as well, without duplicating its literal or modifying the buffer.
 a.move('t3','a0');a.move('t4','t0');a.i(9,'t7','zero',17)
 a.label('question_compare');a.i(37,'t5','t3',0);a.i(37,'t6','t4',0);a.branch(5,'t5','t6','caption_range');a.branch(4,'t5','zero','found');a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.i(9,'t7','t7',-1);a.branch(5,'t7','zero','question_compare')
 a.label('caption_range')
 for reg,value in [('t0',0x3e035a),('t1',0x3e0f90)]:
  a.relocs.append((len(a.words)*4,0x305));a.i(15,reg,'zero',(value+0x8000)>>16)
  a.relocs.append((len(a.words)*4,0x306));a.i(9,reg,reg,value&65535)
 a.emit(REG['a0']<<21|REG['t0']<<16|REG['t2']<<11|0x2b);a.branch(5,'t2','zero','match_end')
 a.emit(REG['a0']<<21|REG['t1']<<16|REG['t2']<<11|0x2b);a.branch(4,'t2','zero','match_end')
 a.label('found');a.i(9,'v0','zero',1)
 a.label('match_end');a.ret()
 a.label('draw');a.i(9,'sp','sp',-96)
 for r,o in [('ra',92),('s0',64),('s1',68),('s2',72),('s3',76),('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(43,r,'sp',o)
 a.move('s0','a0');a.move('s1','zero');a.branch(4,'s0','zero','native_draw');a.i(35,'s2','s0',0x30);a.branch(4,'s2','zero','native_draw');a.i(35,'s3','s0',0x3c);a.branch(4,'s3','zero','native_draw');a.i(11,'t0','s3',257);a.branch(4,'t0','zero','native_draw')
 a.i(35,'t0','s0',0x34);a.i(43,'t0','sp',48);a.i(36,'t0','s0',0x64);a.i(43,'t0','sp',52)
 a.label('rows');a.i(35,'a0','s2',0);a.jump('match');a.branch(5,'v0','zero','vwf');a.i(9,'s2','s2',16);a.i(9,'s3','s3',-1);a.branch(5,'s3','zero','rows');a.branch(4,'zero','zero','native_draw')
 a.label('vwf');a.i(9,'s1','zero',1);a.i(43,'zero','s0',0x34);a.i(9,'t0','zero',-1);a.i(40,'t0','s0',0x64);a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x400);a.i(43,'t0','s0',0)
 a.label('native_draw')
 for r,o in [('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(35,r,'sp',o)
 a.jump(prior);a.branch(4,'s1','zero','draw_return');a.i(35,'t0','sp',48);a.i(43,'t0','s0',0x34);a.i(35,'t0','sp',52);a.i(40,'t0','s0',0x64)
 a.label('draw_return')
 for r,o in [('s0',64),('s1',68),('s2',72),('s3',76),('ra',92)]:a.i(35,r,'sp',o)
 a.i(9,'sp','sp',96);a.ret()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TEXT.read_text('utf8'));refs,users,_=references(old)
 # Branch-specific sibling shares the HI with the other class-help branch.
 refs[0x21c7bc]=[dict(kind='hilo',high=0x11c5cc,low=0x11c5dc,register=5)]
 entries={int(e['source_address'],16):e['english'] for e in cfg['class_change']}
 prior=(struct.unpack_from('<I',old,0x1b0f8+192)[0]&0x3ffffff)<<2
 names=sorted(set(captions())- {''} | {'Use this class?'})
 # First literal is the direct confirmation-question pointer used above.
 payload=bytearray();offsets={}
 for va in [0x21c7f4]+[v for v in sorted(entries) if v!=0x21c7f4]:
  offsets[va]=len(payload);payload.extend(b''.join(encoded(t) for t in entries[va])+bytes(2))
 seg=parse_elf(old)['phdrs'][3];assert seg[2]+seg[4]>=0x3e0f90
 probe=Assembler();emit(probe,prior);table=seg[2]+seg[4]+len(probe.words)*4
 # All class literals share one HI region without a 64 KiB padding block.
 assert (table+0x8000)>>16==(table+len(payload)+0x8000)>>16
 heading=len(payload);payload.extend(encoded(cfg['reward_heading']));party_prefix=len(payload);payload.extend(encoded(cfg['party_prefix']));party_suffix=len(payload);payload.extend(encoded(cfg['party_suffix']));payload.extend(bytes(-len(payload)%4))
 # The whole Party Ability / discovery / reward popup category uses native
 # font objects, so switch its remaining direct bindings to the existing VWF.
 sites=[p for p in range(0x6f3d0,0x7497c,4) if struct.unpack_from('<I',old,p+192)[0]==3<<26|0x1cbdec>>2]
 hooks={p:(0x347b5c,3<<26|0x1cbdec>>2) for p in sites}
 # Summon animation has TWO branches. 020 covered spells but left default
 # summon-name banners (6748c -> 14ecbc) on the original fixed-cell binder.
 hooks[0x14ecbc]=(0x347b5c,3<<26|0x1cbdec>>2)
 hooks[0x71dfc]=('reward_cells',3<<26|0x1e4ac8>>2)
 hooks[0x1b0f8]=('draw',struct.unpack_from('<I',old,0x1b0f8+192)[0])
 data,r=append(old,lambda a:emit(a,prior),hooks,bytes(payload));out=bytearray(data);assert int(r['code_address'],16)+r['labels']['table']==table
 struct.pack_into('<I',out,0x1b0f8+192,2<<26|(int(r['code_address'],16)+r['labels']['draw'])>>2)
 words={};highs={}
 def pair(hi,lo,new):
  hv=(new+0x8000)>>16;assert hi not in highs or highs[hi]==hv;highs[hi]=hv
  for at,v in [(hi,hv),(lo,new&65535)]:words[at]=(struct.unpack_from('<I',old,at+192)[0]&0xffff0000)|v
 for va in entries:
  assert refs.get(va),hex(va)
  for ref in refs[va]:
   if ref['kind']=='pointer':words[ref['address']]=table+offsets[va]
   else:pair(ref['high'],ref['low'],table+offsets[va])
 pair(0x6ee3c,0x6ee54,table+heading)
 for hi,lo in [(466804,466824),(476860,476880)]:pair(hi,lo,table+party_prefix)
 pair(467276,467292,table+party_suffix)
 for at,v in words.items():struct.pack_into('<I',out,at+192,v)
 assert validate_loader_structure(out)
 r.update(prior_draw=prior,exact_captions=names,class_literals={hex(k):table+v for k,v in offsets.items()},reward_heading=table+heading,changed_native_words={hex(k):hex(v) for k,v in words.items()},discovery_vwf_sites=sites,source_sha256=sha(old),output_sha256=sha(out),custom_names_preserved=True,save_bytes_unchanged=True,equipment_caption_start=0x3e035a,equipment_caption_end=0x3e0f90,duplicated_caption_bytes=0)
 return bytes(out),r
