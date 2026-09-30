"""Compact overflowing equipment help after the native formatter returns."""
import json,struct
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from verify_equipment_047 import CPU,stage,BaseCPU

BASE=ROOT/'work/output/0.1.46'
FOLDER=ROOT/'work/translation/en/equipment_0.1.47'

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes()
 pairs=json.loads((FOLDER/'targets.json').read_text())['compact_overflow_only']
 table=b'';entries=[]
 for source,target in pairs.items():
  b=encode_dialogue(source,'')[0];c=encode_dialogue(target,'')[0]
  assert len(c)<=len(b)
  entries.append((len(table),len(b),len(c)));table+=b+c
 table+=bytes(-len(table)%4)
 space=int.from_bytes(encode_dialogue(' ','')[0],'little')
 def emit(a):
  # Output pointer is saved at sp+0x248. The original epilogue restores
  # s3 and every other callee-saved register, including the caller's ra.
  a.label('compact');a.i(35,'s3','sp',0x248);a.move('t0','s3');a.i(9,'t1','zero',0)
  a.label('count');a.i(37,'t2','t0',0);a.i(9,'t0','t0',2)
  a.branch(5,'t2','zero','count_char')
  a.i(37,'t2','t0',0);a.branch(4,'t2','zero','count_done')
  a.branch(4,'zero','zero','count')
  a.label('count_char');a.i(9,'t1','t1',1);a.branch(4,'zero','zero','count')
  a.label('count_done');a.i(11,'t2','t1',55);a.branch(5,'t2','zero','done')
  a.move('t0','s3');a.move('t1','s3');a.i(9,'t9','zero',0)
  a.label('scan');a.i(37,'t2','t0',0)
  a.branch(4,'t2','zero','line_end')
  for n,(off,oldbytes,newbytes) in enumerate(entries):
   a.table_address('t3');a.i(9,'t3','t3',off);a.move('t4','t0');a.i(9,'t5','zero',oldbytes//2)
   a.label(f'match{n}');a.i(37,'t6','t3',0);a.i(37,'t7','t4',0)
   a.branch(5,'t6','t7',f'next{n}');a.i(9,'t3','t3',2);a.i(9,'t4','t4',2)
   a.i(9,'t5','t5',-1);a.branch(5,'t5','zero',f'match{n}')
   a.move('t0','t4');a.i(9,'t5','zero',newbytes//2)
   a.label(f'copy{n}');a.i(37,'t6','t3',0);a.i(41,'t6','t1',0)
   a.move('t9','t6');a.i(9,'t3','t3',2);a.i(9,'t1','t1',2)
   a.i(9,'t5','t5',-1);a.branch(5,'t5','zero',f'copy{n}')
   a.branch(4,'zero','zero','scan');a.label(f'next{n}')
  # Collapse redundant key-label alignment spaces, retaining one separator.
  a.i(13,'t8','zero',space);a.branch(5,'t2','t8','literal')
  a.branch(4,'t9','t8','skip')
  a.label('literal');a.i(41,'t2','t1',0);a.i(9,'t1','t1',2);a.move('t9','t2')
  a.label('skip');a.i(9,'t0','t0',2);a.branch(4,'zero','zero','scan')
  a.label('line_end');a.i(41,'zero','t1',0);a.i(9,'t1','t1',2);a.i(9,'t0','t0',2)
  a.i(9,'t9','zero',0);a.i(37,'t2','t0',0);a.branch(5,'t2','zero','scan')
  a.i(41,'zero','t1',0)
  a.label('done');a.move('v0','s3');a.jump(0x658b8,link=False)
 data,report=append(old,emit,{0x658b4:('compact',0x8fa20248)},table)
 # append emits JAL; the existing next instruction is a harmless saved-register
 # load. The helper rejoins the full epilogue, which reloads the caller's ra.
 report['entries']=[dict(target_text=b,source_text=a) for a,b in pairs.items()]
 return data,report

def prepare_tables(source):
 return {3:source.resource('02.DAT',3)},{},source.resource('00.DAT',44),dict(units=[],tables=[])

def verify(elf,static):
 before=(BASE/'EBOOT.elf').read_bytes();results=[];changed=[]
 renderer=BaseCPU(elf,static)
 baseline=CPU(before,static,0);baseline.run(26)
 try:stage(BaseCPU(before,static),baseline.mem[0x5019f0:0x5019f0+178])
 except AssertionError as error:
  assert error.args[0]==('glyph pool overflow',54),error
 else:raise AssertionError('Reported baseline did not reproduce')
 for kind in range(3):
  c=CPU(elf,static,kind);b=CPU(before,static,kind)
  for rec in range(1,c.count):
   for key in (False,True):
    prior=b.run(rec,key);r=c.run(rec,key);r.update(kind=kind,key_item=key)
    assert r['total']<=54,r
    assert max(r['lengths'],default=0)<=27,r
    r['staging']=stage(renderer,c.mem[0x5019f0:0x5019f0+178])
    if prior['total']<=54:assert r['lines']==prior['lines'],r
    else:changed.append(dict(kind=kind,record=rec,key_item=key,before=prior,after=r))
    results.append(r)
 return dict(cases=len(results),native_staging_cases=len(results),baseline_failure_slot=54,max_cells=max(r['total'] for r in results),max_glyph_slot=max(r['staging']['max_slot'] for r in results),changed=changed)

