"""Build accepted remaining-story scripts onto the immutable 0.1.53 ISO."""
import argparse,copy,json,struct
from datetime import datetime,timezone
from pathlib import Path
from sn3_archive import ROOT,GameSource
from sn3_repack import plan_bank,write_bank
from build_candidate import hash_file,copy_range,directory_records,extent_hash
from scan_source import inventory
from story_patch_054 import prepare,FOLDER
from build_battle import clean

BASE=ROOT/'work/output/0.1.53'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true');a=p.parse_args()
    dest=ROOT/'work/output/0.1.54';assert not dest.exists()
    previous=json.loads((BASE/'manifest.json').read_text())
    prior=BASE/previous['output_iso'];assert hash_file(prior)==previous['output_sha256']
    aggregate=json.loads((FOLDER/'current_compiler_revalidation_20261001.json').read_text())
    inputs={};replacements={};reports=[];checks={}
    for result in aggregate['results']:
        assert result['status']=='passed'
        for name,h in result['input_hashes'].items():assert inputs.setdefault(name,h)==h
    for n,h in inputs.items():assert hash_file(ROOT/n)==h,n
    inherited_changes={}
    for n,h in previous['inputs_sha256'].items():
        actual=hash_file(ROOT/n)
        if actual!=h:
            assert n in inputs and actual==inputs[n],('unexpected historical input change',n)
            inherited_changes[n]=dict(historical=h,current=actual)
    for n in ('tools/build_story_054.py','tools/sn3_repack.py','tools/build_candidate.py',
              'work/output/0.1.53/manifest.json',
              'work/translation/en/story_0.1.54/translation_audit_final_story_20261001.json',
              'work/translation/en/story_0.1.54/current_compiler_revalidation_20261001.json'):
        inputs[n]=hash_file(ROOT/n)
    for number in aggregate['resources']:
        packed,report,selection,check=prepare(number,True)
        assert not check['remaining_in_scope']
        for n,h in selection['review_inputs_sha256'].items():assert inputs.setdefault(n,h)==h
        replacements[number]=packed;reports.append(report);checks[str(number)]=check
        print(json.dumps(dict(resource=number,rows=check['covered_source_rows'],decoded=report['decoded_size'])),flush=True)
    with GameSource(prior) as source,prior.open('rb') as src:
        for r in reports:
            import hashlib
            assert hashlib.sha256(source.resource('00.DAT',r['index'])).hexdigest()==r['source_sha256'],r['index']
        plan=plan_bank(source,'00.DAT',replacements);f=source.files['00.DAT']
        plan.update(start=f['sector']*2048,end=f['sector']*2048+f['size_bytes'],old_span=f['size_bytes'],new_span=plan['new_size'],path='/PSP_GAME/USRDIR/00.DAT')
        assert plan['old_span']%2048==plan['new_span']%2048==0
        pvd,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size)
        assert all(s*2048+n<plan['start'] for s,n in dirs)
        pt=struct.unpack_from('<I',pvd,132)[0]
        assert all(s*2048+pt<plan['start'] for s in struct.unpack_from('<II',pvd,140)+struct.unpack_from('>II',pvd,148) if s)
        summary=dict(version='0.1.54',resources=len(reports),rows=sum(c['covered_source_rows'] for c in checks.values()),
            new_rows=43668,largest_script=max(r['decoded_size'] for r in reports),
            groups=sum(c['groups'] for c in checks.values()),pages=sum(c['pages'] for c in checks.values()),
            old_bank_bytes=plan['old_span'],new_bank_bytes=plan['new_span'],inherited_input_updates=inherited_changes)
        print(json.dumps(dict(mode='write' if a.write else 'dry-run',**summary),indent=2),flush=True)
        if not a.write:return
        dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.54.iso';partial=iso.with_suffix('.iso.partial')
        with partial.open('xb') as out:
            copy_range(src,out,0,plan['start']);write_bank(source,plan,out)
            copy_range(src,out,plan['end'],prior.stat().st_size-plan['end'])
        with partial.open('r+b') as out:
            for r in records:
                delta=plan['new_span']-plan['old_span'] if plan['end']<=r['sector']*2048 else 0
                sector=r['sector']+delta//2048;size=plan['new_size'] if r['path']==plan['path'] else r['size_bytes']
                out.seek(r['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector))
                out.seek(r['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
            sectors=partial.stat().st_size//2048;out.seek(16*2048+80);out.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
        verified=[];unchanged=0
        with partial.open('rb') as out:
            _,actual=inventory(out,partial.stat().st_size);old={r['path']:r for r in files}
            assert set(old)=={r['path'] for r in actual}
            for r in actual:
                h=extent_hash(out,r['sector'],r['size_bytes']);o=old[r['path']]
                if r['path']!=plan['path']:assert h==extent_hash(src,o['sector'],o['size_bytes']),r['path']
                verified.append(dict(path=r['path'],sha256=h,changed=r['path']==plan['path']))
        with GameSource(partial) as candidate:
            assert len(candidate.indexes)==23
            for entry in source.indexes['00.DAT']['entries']:
                n=entry['id'];data=candidate.resource('00.DAT',n)
                if n in replacements:
                    wanted=replacements[n];assert data[:len(wanted)]==wanted and not any(data[len(wanted):])
                else:assert data==source.resource('00.DAT',n);unchanged+=1
        for n,h in inputs.items():assert hash_file(ROOT/n)==h,n
        partial.rename(iso)
        manifest=clean(copy.deepcopy(previous))
        manifest.update(version='0.1.54',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,
            output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],
            story054=reports,story054_checks=checks,story054_summary=summary,
            static_validation=dict(comparison_build='0.1.53',per_file=verified,unchanged_bank_resources=unchanged,bank_indexes=23,runtime_verified=False))
        manifest['inputs_sha256'].update(inputs)
        (dest/'EBOOT.elf').write_bytes((BASE/'EBOOT.elf').read_bytes())
        (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(iso=str(iso),sha256=manifest['output_sha256'])),flush=True)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    main()
