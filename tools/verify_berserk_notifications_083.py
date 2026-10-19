"""Execute the actual native row binder; reproduce and prevent the bad store."""
import json,struct
from berserk_notifications_083 import BASE,TARGET,encoded,prepare_elf
from sn3_archive import ROOT
from verify_guards_050 import GuardCPU
from stat_spacing_026 import _file_offset_for_va as off

def run_row(elf,report,base,text):
 c=GuardCPU(elf,report,base);owner=0x08eaa580;pool=owner+0xa0;row=0x08eb1720;rows=row-0x100;src=0x09800000;stack=0x09fff360
 for va in range(0x1b2a0,0x1b334,4):
  w=struct.unpack_from('<I',elf,off(elf,va))[0]
  if w>>26==3:w=w&0xfc000000|((w&0x3ffffff)+(base>>2))&0x3ffffff
  c.store(base+va,struct.pack('<I',w))
 c.store(row-16,b'G'*160);c.store(rows,struct.pack('<I',src)+bytes(12));c.store(src,encoded(text));c.store(owner,bytes(128));c.store(owner+0x64,b'\x80')
 c.r=[0]*32;c.r[21]=row;c.r[19]=pool;c.r[22]=owner;c.r[23]=rows;c.r[29]=stack
 pc=base+0x1b2a0;calls=[];bad=None
 for _ in range(10000):
  if pc==base+0x1b334:break
  if pc==base+0x1e4ac8:c.r[2]=len(text);pc=c.r[31];continue
  if pc==base+0x1cbe48:
   assert c.r[4]==pool+len(calls)*224 and c.r[5]==src+len(calls)*2 and c.r[6:8]==[1,1]
   calls.append(c.r[5]);pc=c.r[31];continue
  if pc==base+0x1b30c and not row<=c.r[5]<row+128:bad=c.r[5];break
  pc=c.step(pc)
 else:raise AssertionError('Native binder budget exceeded')
 if bad is None:
  assert len(calls)==len(text) and c.read(row+124)==len(text)
  assert bytes(c.read(row-16+i,1) for i in range(16))==b'G'*16
  assert bytes(c.read(row+128+i,1) for i in range(16))==b'G'*16
 return dict(glyphs=len(calls),bad_store=hex(bad) if bad else None)

def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes();spec=json.loads(TARGET.read_text('utf8'));cases=0
 # No added instructions: provide existing segment metadata to the emulator.
 from stages_pupil_names import parse_elf
 seg=parse_elf(elf)['phdrs'][3];machine=dict(added_segment_file_offset=seg[1],added_segment_bytes=seg[4],extra_relocation_records=[])
 for base in (0x08804000,0x0890c000):
  for row in spec['entries']:
   assert run_row(elf,machine,base,row['english'])['bad_store'] is None;cases+=1
  assert run_row(elf,machine,base,'A'*31)['bad_store'] is None;cases+=1
 prior=next(x['prior_english'] for x in spec['entries'] if x['source_address']==0x21b608)
 failure=run_row(old,machine,0x08804000,prior);assert failure['bad_store']=='0x2c961c20',failure
 for lo,hi in [(0,0x228000)]:assert old[off(old,lo)+192:off(old,hi)]==elf[off(elf,lo)+192:off(elf,hi)]
 return dict(passed=True,version='0.1.83',native_binder_cases=cases,load_bases=2,prior_bad_store_reproduced=failure['bad_store'],adjacent_row_guards=True,complete_messages_preserved=True,code_and_relocations_unchanged=True,output_elf_sha256=r['output_sha256'])

if __name__=='__main__':
 result=verify();d=ROOT/'work/ui/battle_0.1.83';d.mkdir(parents=True,exist_ok=True);(d/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
