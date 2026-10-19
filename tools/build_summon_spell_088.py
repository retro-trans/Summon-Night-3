"""Apply same-size summon spell caption edit without rebuilding archive layouts."""
import argparse,copy,json,shutil
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource,parse_index,child
from build_candidate import hash_file,extent_hash
from scan_source import inventory
from build_battle import clean
from build_ui_080 import verify_inputs
from summon_spell_088 import BASE,TEXT,prepare,prepare_elf

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
 previous=json.loads((BASE/'manifest.json').read_text('utf8'));prior=BASE/previous['output_iso']
 assert hash_file(prior)==previous['output_sha256'];verify_inputs(previous['inputs_sha256'])
 with GameSource(prior) as source:
  replacements,report=prepare(source);elf,elf_report=prepare_elf();report['banner_lookup']=elf_report
  print(json.dumps(dict(version='0.1.88',changes=report['changes'],audited_names=report['nonempty_names'],write=args.write)),flush=True)
  if not args.write:return
  dest=ROOT/'work/output/0.1.88';assert not dest.exists();dest.mkdir()
  iso=dest/'Summon_Night_3_EN_0.1.88.iso';partial=iso.with_suffix('.iso.partial');shutil.copyfile(prior,partial)
  with prior.open('rb') as original:
   _,files=inventory(original,prior.stat().st_size);boot=next(f for f in files if f['path']=='/PSP_GAME/SYSDIR/EBOOT.BIN')
   assert boot['size_bytes']==len(elf) and extent_hash(original,boot['sector'],boot['size_bytes'])==elf_report['source_sha256']
  with partial.open('r+b') as out:
   out.seek(boot['sector']*2048);out.write(elf)
   for bank,(n,data) in replacements.items():
    entry=source.indexes[bank]['entries'][n];assert len(data)==entry['size']
    out.seek(source.files[bank]['sector']*2048+entry['offset']);out.write(data)
  verified=[];unchanged=0
  with prior.open('rb') as old,partial.open('rb') as new:
   _,files=inventory(old,prior.stat().st_size);_,candidate=inventory(new,partial.stat().st_size);assert files==candidate
   for row in files:
    before=extent_hash(old,row['sector'],row['size_bytes']);after=extent_hash(new,row['sector'],row['size_bytes'])
    changed=row['path'] in ['/PSP_GAME/USRDIR/'+b for b in replacements]+[boot['path']]
    assert changed or before==after
    if row['path']==boot['path']:assert after==elf_report['output_sha256']
    verified.append(dict(path=row['path'],sha256=after,changed=changed))
  with GameSource(partial) as candidate:
   assert len(candidate.indexes)==23
   for bank,index in source.indexes.items():
    assert candidate.indexes[bank]==index
    for entry in index['entries']:
     n=entry['id'];actual=candidate.resource(bank,n)
     if bank in replacements and n==replacements[bank][0]:assert actual==replacements[bank][1]
     else:assert actual==source.resource(bank,n);unchanged+=1
   master=candidate.resource('00.DAT',44);assert child(master,parse_index(master,len(master)),7)==candidate.resource('02.DAT',3)
  inputs=dict(previous['inputs_sha256'])
  for path in [TEXT,ROOT/'tools/summon_spell_088.py',ROOT/'tools/build_summon_spell_088.py']:
   inputs[path.relative_to(ROOT).as_posix()]=hash_file(path)
  verify_inputs(inputs);partial.rename(iso);digest=hash_file(iso)
  checks=dict(passed=True,version='0.1.88',iso_sha256=digest,spell_names_audited=report['nonempty_names'],all_spell_names_fit=True,
   archive_indexes_unchanged=True,master_cache_synchronized=True,unchanged_bank_resources=unchanged,executable_instructions_unchanged=True,banner_lookup_synchronized=True,iso_size_unchanged=True,loaded_memory_growth_bytes=0)
  manifest=clean(copy.deepcopy(previous));manifest.update(version='0.1.88',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,
   output_size_bytes=iso.stat().st_size,output_sha256=digest,previous_build_sha256=previous['output_sha256'],inputs_sha256=inputs,summon_spell088_fix=report,
   static_validation=dict(comparison_build='0.1.87',per_file=verified,runtime_verified=False))
  (dest/'EBOOT.elf').write_bytes(elf)
  for path,value in [(dest/'manifest.json',manifest),(dest/'asset-validation.json',checks),(ROOT/'work/ui/ui_0.1.88/validation.json',checks)]:
   path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n','utf8',newline='\n')
  print(json.dumps(dict(iso=str(iso),sha256=digest,checks=checks)),flush=True)

if __name__=='__main__':main()
