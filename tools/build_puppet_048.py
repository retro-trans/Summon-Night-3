"""Build Summon Puppet name encoding fix on immutable v0.1.47."""
import argparse,copy,json,struct
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource
from sn3_repack import plan_bank,repack,write_bank
from build_candidate import hash_file,copy_range,directory_records,extent_hash
from scan_source import inventory
from build_battle import clean
from puppet_048 import prepare_elf,prepare_tables
from puppet_048 import verify
from summon_text_019 import sha
from sn3_archive import parse_index,child

BASE=ROOT/'work/output/0.1.47';EBOOT='/PSP_GAME/SYSDIR/EBOOT.BIN'
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--destination',default='work/scratch/puppet_candidate_0.1.48');a=p.parse_args()
 dest=(ROOT/a.destination).resolve();assert ROOT in dest.parents and not dest.exists()
 previous=json.loads((BASE/'manifest.json').read_text());prior=BASE/previous['output_iso']
 assert hash_file(prior)==previous['output_sha256']
 for n,h in previous['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 inputs={}
 for path in [ROOT/'tools'/n for n in ['build_puppet_048.py','puppet_048.py']]+list((ROOT/'work/translation/en/puppet_0.1.48').glob('*.json'))+[ROOT/'work/glossary/character_reference_sn6_vita.json']:
  inputs[str(path.relative_to(ROOT)).replace('\\','/')]=hash_file(path)
 executable,tr=prepare_elf()
 with GameSource(prior) as source,prior.open('rb') as src:
  tables02,tables01,master,tbr=prepare_tables(source)
  tr['native_checks']=verify(executable,tables02[3])
  p01=plan_bank(source,'01.DAT',tables01)
  p02=plan_bank(source,'02.DAT',tables02)
  master=repack(master,{0:p01['index_bytes'],1:p02['index_bytes']})
  bankplans=[plan_bank(source,'00.DAT',{44:master}),p01,p02]
  for plan in bankplans:
   f=source.files[plan['bank']];plan.update(kind='bank',start=f['sector']*2048,end=f['sector']*2048+f['size_bytes'],old_span=f['size_bytes'],new_span=plan['new_size'],path='/PSP_GAME/USRDIR/'+plan['bank'])
   assert plan['new_span']%2048==plan['old_span']%2048==0
  pvd,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size)
  oldelf=next(f for f in files if f['path']==EBOOT)
  assert extent_hash(src,oldelf['sector'],oldelf['size_bytes'])==hash_file(BASE/'EBOOT.elf')
  plans=sorted(bankplans+[dict(kind='elf',start=oldelf['sector']*2048,end=oldelf['sector']*2048+(oldelf['size_bytes']+2047)//2048*2048,old_span=(oldelf['size_bytes']+2047)//2048*2048,new_span=(len(executable)+2047)//2048*2048,new_size=len(executable),path=EBOOT)],key=lambda x:x['start'])
  assert all(x['end']<=y['start'] for x,y in zip(plans,plans[1:]))
  assert all(s*2048+n<plans[0]['start'] for s,n in dirs)
  pt=struct.unpack_from('<I',pvd,132)[0]
  assert all(s*2048+pt<plans[0]['start'] for s in struct.unpack_from('<II',pvd,140)+struct.unpack_from('>II',pvd,148) if s)
  print(json.dumps(dict(mode='write' if a.write else 'dry-run',destination=str(dest),text_groups=len(tr['entries']),text_strings=len(tr['entries']),unit_labels=len(tbr['units']),table_names=sum(len(t['changes']) for t in tbr['tables']),samples=[t['target_text'] for t in tr['entries'][:3]],banks=[dict(bank=b['bank'],old=b['old_span'],new=b['new_span']) for b in bankplans]),indent=2),flush=True)
  if not a.write:return
  dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.48.iso';partial=iso.with_suffix('.iso.partial')
  with partial.open('xb') as out:
   cursor=0
   for plan in plans:
    copy_range(src,out,cursor,plan['start']-cursor)
    if plan['kind']=='bank':write_bank(source,plan,out)
    else:out.write(executable);out.write(bytes(plan['new_span']-len(executable)))
    cursor=plan['end']
   copy_range(src,out,cursor,prior.stat().st_size-cursor)
  sizes={p['path']:p['new_size'] for p in plans}
  with partial.open('r+b') as out:
   for r in records:
    delta=sum(p['new_span']-p['old_span'] for p in plans if p['end']<=r['sector']*2048)
    sector=r['sector']+delta//2048;size=sizes.get(r['path'],r['size_bytes'])
    out.seek(r['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector))
    out.seek(r['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
   sectors=partial.stat().st_size//2048;out.seek(16*2048+80);out.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
  verified=[];unchanged=0
  with partial.open('rb') as out:
   _,actual=inventory(out,partial.stat().st_size);old={r['path']:r for r in files};assert set(old)=={r['path'] for r in actual}
   for r in actual:
    h=extent_hash(out,r['sector'],r['size_bytes']);o=old[r['path']]
    if r['path'] not in sizes:assert h==extent_hash(src,o['sector'],o['size_bytes']),r['path']
    elif r['path']==EBOOT:assert h==sha(executable)
    verified.append(dict(path=r['path'],sha256=h,changed=r['path'] in sizes))
  with GameSource(partial) as candidate:
   assert len(candidate.indexes)==23
   cm=candidate.resource('00.DAT',44);ci=parse_index(cm,len(cm))
   assert child(cm,ci,7)==candidate.resource('02.DAT',3)
   cached=child(cm,ci,6);bankcopy=candidate.resource('01.DAT',1)
   assert cached==bankcopy[:len(cached)] and not any(bankcopy[len(cached):])
   cc=parse_index(cached,len(cached));bc=parse_index(bankcopy,len(bankcopy))
   assert cc['count']==bc['count']
   assert all(child(cached,cc,n)==child(bankcopy,bc,n) for n in range(cc['count']))
   for plan in bankplans:
    for entry in source.indexes[plan['bank']]['entries']:
     n=entry['id'];data=candidate.resource(plan['bank'],n)
     if n in plan['replacements']:
      wanted=plan['replacements'][n];assert data[:len(wanted)]==wanted and not any(data[len(wanted):])
     else:assert data==source.resource(plan['bank'],n);unchanged+=1
  for n,h in {**previous['inputs_sha256'],**inputs}.items():assert hash_file(ROOT/n)==h,n
  partial.rename(iso)
  manifest=clean(copy.deepcopy(previous));manifest.update(version='0.1.48',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],puppet048_text=tr,puppet048_tables=tbr,static_validation=dict(comparison_build='0.1.47',per_file=verified,unchanged_bank_resources=unchanged,bank_indexes=23,runtime_verified=False))
  manifest['inputs_sha256'].update(inputs)
  (dest/'EBOOT.elf').write_bytes(executable);(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(json.dumps(dict(iso=str(iso),sha256=manifest['output_sha256'],unchanged=unchanged)),flush=True)
if __name__=='__main__':main()
