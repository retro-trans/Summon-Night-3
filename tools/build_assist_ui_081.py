"""Build an executable-only Assist spacing fix on immutable 0.1.80."""
import argparse,copy,json,struct
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource
from build_candidate import hash_file,copy_range,directory_records,extent_hash
from scan_source import inventory
from build_battle import clean
from build_ui_080 import verify_inputs
from assist_ui_081 import BASE,prepare_elf
from verify_assist_ui_081 import verify

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 dest=ROOT/'work/output/0.1.81';assert not dest.exists()
 previous=json.loads((BASE/'manifest.json').read_text());prior=BASE/previous['output_iso'];assert hash_file(prior)==previous['output_sha256']
 verify_inputs(previous['inputs_sha256']);elf,report=prepare_elf();checks=verify()
 with prior.open('rb') as src:
  pvd,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size);entry=next(x for x in files if x['path']=='/PSP_GAME/SYSDIR/EBOOT.BIN')
  assert extent_hash(src,entry['sector'],entry['size_bytes'])==hash_file(BASE/'EBOOT.elf')
  start=entry['sector']*2048;span=(entry['size_bytes']+2047)//2048*2048;newspan=(len(elf)+2047)//2048*2048;delta=newspan-span
  assert all(s*2048+n<start for s,n in dirs)
  print(json.dumps(dict(mode='write' if a.write else 'preview',version='0.1.81',checks=checks,iso_growth_bytes=delta)),flush=True)
  if not a.write:return
  dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.81.iso';partial=iso.with_suffix('.iso.partial')
  with partial.open('xb') as out:
   copy_range(src,out,0,start);out.write(elf);out.write(bytes(newspan-len(elf)));copy_range(src,out,start+span,prior.stat().st_size-start-span)
  with partial.open('r+b') as out:
   for r in records:
    sector=r['sector']+(delta//2048 if r['sector']*2048>=start+span else 0);size=len(elf) if r['path']==entry['path'] else r['size_bytes']
    out.seek(r['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector));out.seek(r['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
   count=partial.stat().st_size//2048;out.seek(16*2048+80);out.write(struct.pack('<I',count)+struct.pack('>I',count))
  verified=[]
  with partial.open('rb') as out:
   _,actual=inventory(out,partial.stat().st_size);old={r['path']:r for r in files};assert set(old)=={r['path'] for r in actual}
   for r in actual:
    h=extent_hash(out,r['sector'],r['size_bytes']);o=old[r['path']]
    assert h==(report['output_sha256'] if r['path']==entry['path'] else extent_hash(src,o['sector'],o['size_bytes']))
    verified.append(dict(path=r['path'],sha256=h,changed=r['path']==entry['path']))
  with GameSource(partial) as candidate:assert len(candidate.indexes)==23
  inputs=dict(previous['inputs_sha256'])
  for name in ('build_assist_ui_081.py','assist_ui_081.py','verify_assist_ui_081.py'):
   path=ROOT/'tools'/name;inputs[path.relative_to(ROOT).as_posix()]=hash_file(path)
  verify_inputs(inputs);partial.rename(iso)
  manifest=clean(copy.deepcopy(previous));digest=hash_file(iso)
  checks.update(iso_sha256=digest,executable_matches_expected=True,all_other_iso_files_unchanged=True)
  manifest.update(version='0.1.81',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=digest,previous_build_sha256=previous['output_sha256'],inputs_sha256=inputs,assist081_fix=report,static_validation=dict(comparison_build='0.1.80',per_file=verified,runtime_verified=False))
  (dest/'EBOOT.elf').write_bytes(elf);(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(dest/'asset-validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(dict(iso=str(iso),sha256=digest)),flush=True)

if __name__=='__main__':main()
