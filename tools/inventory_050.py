"""Two-row equipment help and source-bound weapon names on immutable 0.1.49."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from font_patch import REG
from menu_hotfix_017 import lines_at
BASE=ROOT/'work/output/0.1.49'
TARGETS=ROOT/'work/translation/en/inventory_0.1.50/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TARGETS.read_text());table=b'';pairs=[]
 for src,dst in cfg['help_compaction'].items():
  b=encode_dialogue(src,'')[0];c=encode_dialogue(dst,'')[0];pairs.append((len(table),len(b)//2,len(c)//2));table+=b+c
 table+=bytes(-len(table)%4);space=int.from_bytes(encode_dialogue(' ','')[0],'little')
 def emit(a):
  def sub(rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x23)
  def shift(rd,rt,n):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6)
  a.label('reflow');a.move('s0','v0');a.move('t0','s0');a.i(9,'t1','zero',1)
  a.label('count');a.i(37,'t2','t0',0);a.i(9,'t0','t0',2);a.branch(5,'t2','zero','count')
  a.i(37,'t2','t0',0);a.branch(4,'t2','zero','count_done');a.i(9,'t1','t1',1);a.branch(4,'zero','zero','count')
  a.label('count_done');a.i(11,'t2','t1',3);a.branch(5,'t2','zero','done')
  a.i(9,'sp','sp',-192);a.i(9,'s4','zero',-1);a.move('t0','s0');a.move('t1','sp');a.i(13,'t9','zero',space)
  a.label('scan');a.i(37,'t2','t0',0);a.branch(4,'t2','zero','line_end')
  for n,(off,oldlen,newlen) in enumerate(pairs):
   a.table_address('t3');a.i(9,'t3','t3',off);a.move('t4','t0');a.i(9,'t5','zero',oldlen)
   a.label(f'match{n}');a.i(37,'t6','t3',0);a.i(37,'t7','t4',0)
   a.branch(5,'t6','t7',f'next{n}');a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.i(9,'t5','t5',-1);a.branch(5,'t5','zero',f'match{n}')
   a.move('t0','t4');a.i(9,'t5','zero',newlen)
   a.label(f'copy{n}');a.i(37,'t6','t3',0);a.i(41,'t6','t1',0);a.move('t9','t6');a.i(9,'t3','t3',2);a.i(9,'t1','t1',2);a.i(9,'t5','t5',-1);a.branch(5,'t5','zero',f'copy{n}')
   a.branch(4,'zero','zero','scan');a.label(f'next{n}')
  a.i(9,'t0','t0',2);a.i(13,'t8','zero',space);a.branch(5,'t2','t8','literal');a.branch(4,'t9','t8','scan')
  a.label('literal');a.i(41,'t2','t1',0);a.i(9,'t1','t1',2);a.move('t9','t2');a.branch(4,'zero','zero','scan')
  a.label('line_end');a.i(9,'t6','zero',-1);a.branch(5,'s4','t6','line_recorded');sub('s4','t1','sp');a.emit(REG['s4']<<16|REG['s4']<<11|1<<6|2);a.i(13,'t6','zero',space);a.branch(5,'t9','t6','line_recorded');a.i(9,'s4','s4',-1);a.label('line_recorded');a.i(9,'t0','t0',2);a.i(37,'t2','t0',0);a.branch(4,'t2','zero','flat_done');a.i(13,'t2','zero',space);a.branch(4,'t9','t2','scan');a.branch(4,'zero','zero','literal')
  a.label('flat_done');a.i(13,'t8','zero',space);a.branch(5,'t9','t8','trim_done');a.i(9,'t1','t1',-2)
  a.label('trim_done');sub('s2','t1','sp');a.emit(REG['s2']<<16|REG['s2']<<11|1<<6|2)
  a.i(9,'s3','zero',-1);a.i(11,'t2','s2',28);a.branch(5,'t2','zero','copy_output')
  a.move('t0','sp');a.i(9,'t1','zero',0)
  a.label('find_split');a.i(37,'t2','t0',0);a.branch(5,'t2','t8','next_cell');a.branch(4,'t1','zero','next_cell')
  a.i(37,'t3','t0',-2);a.i(12,'t3','t3',255);a.i(11,'t3','t3',0x83);a.branch(4,'t3','zero','next_cell')
  sub('t3','s2','t1');a.i(11,'t3','t3',29);a.branch(4,'t3','zero','next_cell');a.move('s3','t1');a.branch(4,'s3','s4','copy_output')
  a.label('next_cell');a.i(9,'t0','t0',2);a.i(9,'t1','t1',1);a.i(11,'t2','t1',28);a.branch(5,'t2','zero','find_split')
  a.i(9,'t2','zero',-1);a.branch(4,'s3','t2','abandon')
  a.label('copy_output');a.move('t0','sp');a.move('t1','s0');a.i(9,'t2','zero',0)
  a.label('out_loop');a.branch(4,'t2','s2','out_end');a.i(37,'t3','t0',0);a.branch(5,'t2','s3','out_cell');a.move('t3','zero')
  a.label('out_cell');a.i(41,'t3','t1',0);a.i(9,'t0','t0',2);a.i(9,'t1','t1',2);a.i(9,'t2','t2',1);a.branch(4,'zero','zero','out_loop')
  a.label('out_end');a.i(41,'zero','t1',0);a.i(41,'zero','t1',2)
  a.label('abandon');a.i(9,'sp','sp',192)
  a.label('done');a.move('v0','s0');a.i(35,'s0','sp',0x250);a.i(35,'s1','sp',0x254);a.jump(0x658c0,link=False)
 data,report=append(old,emit,{0x658bc:('reflow',0x8fb10254)},table)
 report['entries']=[];report['max_rows']=2;report['cells_per_row']=27
 return data,report

def prepare_tables(source):
 cfg=json.loads(TARGETS.read_text());idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());rows={r['id']:r for t in idx['tables'] if t['resource_path']==[3,15] for r in t['strings']}
 static=source.resource('02.DAT',3);before=child(static,parse_index(static,len(static)),15);out=bytearray(before);fields=set();changes=[]
 for e in cfg['entries']:
  row=rows[e['id']];p=row['source_offset'];n=row['source_byte_length'];assert sha(before[p:p+n])==e['source_sha256']
  raw=encode_dialogue(e['text'],'')[0];assert len(raw)//2<=15
  out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0\0\0')
  for ref in row['references']:
   f=ref['pointer_field_offset'];assert struct.unpack_from('<I',before,f)[0]==p
   struct.pack_into('<I',out,f,new);fields.update(range(f,f+4))
  changes.append(dict(e,new_offset=new,references=row['references']))
 assert all(a==b or i in fields for i,(a,b) in enumerate(zip(before,out)))
 patched=repack(static,{15:bytes(out)});master=source.resource('00.DAT',44);assert child(master,parse_index(master,len(master)),7)==static
 return {3:patched},{},repack(master,{7:patched}),dict(units=[],tables=[dict(child=15,changes=changes)],gameplay_fields_unchanged=True)

def verify(elf,static):
 from verify_inventory_050 import verify as run
 return run(elf,static)
