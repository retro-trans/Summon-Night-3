"""Build battle-event translations on 0.1.23; dry-run before --write."""
import argparse,copy,json,struct
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource,parse_v4,child
from sn3_repack import plan_bank,repack,write_bank
from build_candidate import hash_file,copy_range,directory_records,extent_hash
from scan_source import inventory
from build_battle import clean
from battle_compiler_024 import prepare,FOLDER

BASE=ROOT/'work/output/0.1.23'
SHARED=list(range(175,190))+list(range(195,211))
DEFAULT=list(range(116,136))+[155,156]+SHARED
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--destination',default='work/scratch/battle_candidate_0.1.24');p.add_argument('--resources',default=','.join(map(str,DEFAULT)));a=p.parse_args()
 numbers=list(map(int,a.resources.split(',')));dest=(ROOT/a.destination).resolve();assert ROOT in dest.parents and not dest.exists()
 previous=json.loads((BASE/'manifest.json').read_text());prior=BASE/previous['output_iso'];assert hash_file(prior)==previous['output_sha256']
 for n,h in previous['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 inputs={};reports=[];replacements={}
 paths=[ROOT/'tools'/n for n in ['build_battle_024.py','battle_compiler_024.py','battle_source_024.py']]+[ROOT/'work/glossary/character_reference_sn6_vita.json',ROOT/'work/glossary/battle_0.1.24.json']
 for path in paths:inputs[str(path.relative_to(ROOT)).replace('\\','/')]=hash_file(path)
 with GameSource(prior) as source,prior.open('rb') as src:
  cached_shared=None
  for n in numbers:
   if n in SHARED:
    if cached_shared is None:cached_shared=prepare(175)
    data,canonical,bindings=cached_shared;report=copy.deepcopy(canonical)
    report.update(index=n,canonical_translation_resource=175,identical_source_verified=True)
    if n!=175:
     report.pop('targets');report.pop('groups');report['canonical_report_index']=175
   else:data,report,bindings=prepare(n)
   inputs.update(bindings);reports.append(report)
   parent=source.resource('01.DAT',n);idx=parse_v4(parent)
   assert hash_file_bytes(child(parent,idx,1))==report['source_sha256'],('modified baseline battle',n)
   updated=repack(parent,{1:data});ui=parse_v4(updated)
   assert all(child(parent,idx,k)==child(updated,ui,k) for k in range(idx['count']) if k!=1)
   replacements[n]=updated
  p01=plan_bank(source,'01.DAT',replacements);master=repack(source.resource('00.DAT',44),{0:p01['index_bytes']})
  plans=[plan_bank(source,'00.DAT',{44:master}),p01]
  for plan in plans:
   f=source.files[plan['bank']];plan.update(start=f['sector']*2048,end=f['sector']*2048+f['size_bytes'],old_span=f['size_bytes'],new_span=plan['new_size'],path='/PSP_GAME/USRDIR/'+plan['bank'])
   assert plan['new_span']%2048==plan['old_span']%2048==0
  plans.sort(key=lambda x:x['start']);assert plans[0]['end']<=plans[1]['start']
  pvd,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size)
  assert all(s*2048+n<plans[0]['start'] for s,n in dirs)
  pt=struct.unpack_from('<I',pvd,132)[0];assert all(s*2048+pt<plans[0]['start'] for s in struct.unpack_from('<II',pvd,140)+struct.unpack_from('>II',pvd,148) if s)
  print(json.dumps(dict(mode='write' if a.write else 'dry-run',destination=str(dest),resources=numbers,rows=sum(r['covered_source_rows'] for r in reports),pages=sum(len(g['pages']) for r in reports for g in r.get('groups',[])),largest_script=max(r['output_bytes'] for r in reports),samples=[g['text'] for r in reports if r['index']==117 for g in r.get('groups',[])[:3]],banks=[dict(bank=b['bank'],old=b['old_span'],new=b['new_span']) for b in plans]),indent=2),flush=True)
  if not a.write:return
  dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.24.iso';partial=iso.with_suffix('.iso.partial')
  with partial.open('xb') as out:
   cursor=0
   for plan in plans:copy_range(src,out,cursor,plan['start']-cursor);write_bank(source,plan,out);cursor=plan['end']
   copy_range(src,out,cursor,prior.stat().st_size-cursor)
  sizes={p['path']:p['new_size'] for p in plans}
  with partial.open('r+b') as out:
   for r in records:
    delta=sum(p['new_span']-p['old_span'] for p in plans if p['end']<=r['sector']*2048);sector=r['sector']+delta//2048;size=sizes.get(r['path'],r['size_bytes'])
    out.seek(r['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector));out.seek(r['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
   sectors=partial.stat().st_size//2048;out.seek(16*2048+80);out.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
  verified=[];unchanged=0
  with partial.open('rb') as out:
   _,actual=inventory(out,partial.stat().st_size);old={r['path']:r for r in files};assert set(old)=={r['path'] for r in actual}
   for r in actual:
    h=extent_hash(out,r['sector'],r['size_bytes']);o=old[r['path']]
    if r['path'] not in sizes:assert h==extent_hash(src,o['sector'],o['size_bytes']),r['path']
    verified.append(dict(path=r['path'],sha256=h,changed=r['path'] in sizes))
  with GameSource(partial) as candidate:
   assert len(candidate.indexes)==23
   for bank,idx in source.indexes.items():
    changed=next((p['replacements'] for p in plans if p['bank']==bank),{})
    for entry in idx['entries']:
     n=entry['id'];data=candidate.resource(bank,n)
     if n in changed:wanted=changed[n];assert data[:len(wanted)]==wanted and not any(data[len(wanted):])
     else:assert data==source.resource(bank,n);unchanged+=1
  for n,h in {**previous['inputs_sha256'],**inputs}.items():assert hash_file(ROOT/n)==h,n
  partial.rename(iso);manifest=clean(copy.deepcopy(previous))
  manifest.update(version='0.1.24',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],battle024=reports,static_validation=dict(comparison_build='0.1.23',per_file=verified,unchanged_bank_resources=unchanged,bank_indexes=23,runtime_verified=False))
  manifest['inputs_sha256'].update(inputs);(dest/'EBOOT.elf').write_bytes((BASE/'EBOOT.elf').read_bytes());(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(json.dumps(dict(iso=str(iso),sha256=manifest['output_sha256'],unchanged=unchanged)),flush=True)
def hash_file_bytes(data):return __import__('hashlib').sha256(data).hexdigest()
if __name__=='__main__':main()
