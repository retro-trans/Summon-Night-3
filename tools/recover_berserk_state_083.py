"""Migrate only verified notification literals in a private copy of the 0.1.81 state."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
from sn3_archive import ROOT
from berserk_notifications_083 import TARGET,encoded

def recover(source,dest):
 # Use the already-installed local diagnostic dependency; never download code.
 sys.path.insert(0,str(ROOT/'work/scratch/crash_continue041_diagnosis/vendor'))
 import zstandard
 raw=source.read_bytes();rev,compression,size,uncompressed=struct.unpack_from('<4I',raw)
 assert rev==5 and compression==2 and len(raw)==176+size
 body=bytearray(zstandard.ZstdDecompressor().decompress(raw[176:]));assert len(body)==uncompressed
 old=(ROOT/'work/output/0.1.81/EBOOT.elf').read_bytes();sample=0x67a4c;needle=old[sample+192:sample+192+32];at=body.find(needle)
 assert at>=0 and body.find(needle,at+1)<0
 delta=at-(0x08804000+sample);allowed=set();before=bytes(body);changes=[]
 for row in json.loads(TARGET.read_text('utf8'))['entries']:
  if row['english']==row['prior_english']:continue
  a=delta+0x08804000+row['current_address'];prior=encoded(row['prior_english']);new=encoded(row['english'])
  assert body[a:a+len(prior)]==prior,(hex(a),row['prior_english'])
  body[a:a+len(prior)]=new+bytes(len(prior)-len(new));allowed.update(range(a,a+len(prior)))
  changes.append(dict(module_address=hex(row['current_address']),prior_cells=len(prior)//2-1,cells=len(new)//2-1))
 # This particular state was captured after the 32nd entry had overwritten
 # the row counter. Restart only the interrupted glyph-binding loop. The
 # stack, game logic and character/turn data remain intact.
 owner=0x08eaa580;row=0x08eb1720;src=0x08b367ac;pool=0x08eaa620
 expected=[32,src+64,row+124,pool+32*224,52,row,owner,row-0x100]
 needle=struct.pack('<8I',*expected);context=before.find(needle,before.find(b'MIPSState'))
 assert context>=0 and before.find(needle,context+1)<0,'Unexpected saved renderer context'
 for i,value in [(0,0),(1,src),(3,pool),(4,31)]:
  at=context+i*4;struct.pack_into('<I',body,at,value);allowed.update(range(at,at+4))
 # MIPSState v4 serializes PC at GPR start + 0x340. The state is already
 # returning from the 33rd bind, so resetting registers alone skips glyph 0.
 assert before[before.find(b'MIPSState')+16:before.find(b'MIPSState')+20]==struct.pack('<I',4)
 at=context-64+0x340;assert struct.unpack_from('<I',before,at)[0]==0x0881f320
 struct.pack_into('<I',body,at,0x0881f2a0);allowed.update(range(at,at+4))
 at=delta+row+124;assert struct.unpack_from('<I',before,at)[0]==pool+31*224+1
 struct.pack_into('<I',body,at,0);allowed.update(range(at,at+4))
 stack=struct.unpack_from('<I',before,context+13*4)[0];assert stack==0x09fff360
 for address,prior,value in [(owner+0x40,728.,434.),(owner+0x44,728.,434.),(row-0x100+8,728.,434.),(stack,-364.,-217.)]:
  at=delta+address;assert struct.unpack_from('<f',before,at)[0]==prior,(hex(address),struct.unpack_from('<f',before,at)[0])
  struct.pack_into('<f',body,at,value);allowed.update(range(at,at+4))
 assert len(body)==len(before) and all(i in allowed for i,(a,b) in enumerate(zip(before,body)) if a!=b)
 compressed=zstandard.ZstdCompressor(level=3).compress(body);header=bytearray(raw[:176]);struct.pack_into('<I',header,8,len(compressed));result=bytes(header)+compressed
 assert zstandard.ZstdDecompressor().decompress(result[176:])==body
 assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(result)
 report=dict(source_sha256=hashlib.sha256(raw).hexdigest(),recovered_sha256=hashlib.sha256(result).hexdigest(),notification_literals=changes,renderer_loop_restarted=True,renderer_registers_reset=['s0','s1','s3','s4'],corrupted_row_counter_reset=True,cached_message_width_and_center_corrected=True,renderer_pc_restarted_from='0x0881f320',renderer_pc_restarted_at='0x0881f2a0',combat_and_save_data_unchanged=True,code_unchanged=True,original_state_unchanged=True)
 dest.with_suffix('.recovery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 src=a.source.resolve();dst=a.destination.resolve();assert src.is_relative_to(ROOT) and dst.is_relative_to(ROOT) and src!=dst
 if a.write:print(json.dumps(recover(src,dst)))
 else:print(json.dumps(dict(mode='preview',source=str(src),destination=str(dst),scope='Nine notification literals and interrupted renderer context; original state retained.')))
