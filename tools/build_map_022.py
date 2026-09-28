"""Build 0.1.22 by changing one relocated font-bind call; preview by default."""
import argparse,json,shutil
from datetime import datetime,timezone
from sn3_archive import ROOT
from map_vwf_022 import BASE,prepare,sha
from build_candidate import hash_file,extent_hash
from scan_source import inventory

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 dest=ROOT/'work/scratch/map_candidate_0.1.22';assert not dest.exists()
 m=json.loads((BASE/'manifest.json').read_text());prior=BASE/m['output_iso']
 assert hash_file(prior)==m['output_sha256']
 for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 elf,report=prepare()
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',destination=str(dest),**report),indent=2),flush=True)
 if not a.write:return
 dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.22.iso';shutil.copyfile(prior,iso)
 with iso.open('r+b') as f:
  _,files=inventory(f,iso.stat().st_size);e=next(e for e in files if e['path']=='/PSP_GAME/SYSDIR/EBOOT.BIN')
  assert e['size_bytes']==len(elf);f.seek(e['sector']*2048);f.write(elf)
 checked=[]
 with iso.open('rb') as f,prior.open('rb') as p:
  for row in files:
   actual=extent_hash(f,row['sector'],row['size_bytes']);changed=row['path']==e['path']
   assert actual==(sha(elf) if changed else extent_hash(p,row['sector'],row['size_bytes'])),row['path']
   checked.append(dict(path=row['path'],sha256=actual,changed=changed))
 previous=m['output_sha256'];m.update(version='0.1.22',built_at_utc=datetime.now(timezone.utc).isoformat(),
  output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous,
  map022_vwf=report,static_validation=dict(comparison_build='0.1.21',per_file=checked,all_23_banks_byte_identical=True,runtime_verified=False))
 for n in ['map_vwf_022.py','build_map_022.py']:
  f=ROOT/'tools'/n;m['inputs_sha256'][f.relative_to(ROOT).as_posix()]=hash_file(f)
 (dest/'EBOOT.elf').write_bytes(elf);(dest/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(iso=str(iso),sha256=m['output_sha256'])),flush=True)
if __name__=='__main__':main()
