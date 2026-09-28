"""Build 0.1.11 with complete opening text and separate backlog names."""
import argparse,copy,json,struct,shutil
from datetime import datetime,timezone
from harbor_complete_patch import prepare,read,sha,PRIOR,TARGET,REVIEW
from backlog_names import prepare_names
from build_candidate import ROOT,hash_file,directory_records,copy_range,extent_hash
from sn3_archive import GameSource,parse_index,child
from sn3_repack import repack,plan_bank,write_bank
from scan_source import inventory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--dest',default='work/output/0.1.11');a=p.parse_args()
    previous=read(PRIOR/'manifest.json');prior=PRIOR/previous['output_iso']
    assert hash_file(prior)==previous['output_sha256']
    dest=(ROOT/a.dest).resolve();assert ROOT in dest.parents;iso=dest/'Summon_Night_3_EN_0.1.11.iso'
    with GameSource(prior) as source,prior.open('rb') as src:
        script,script_report,selection,checks=prepare(source)
        replacements,names=prepare_names(source)
        assert read(ROOT/TARGET)==selection
        plan02=plan_bank(source,'02.DAT',replacements)
        master=source.resource('00.DAT',44);new_master=repack(master,{1:plan02['index_bytes']})
        plan00=plan_bank(source,'00.DAT',{44:new_master,65:script});plans=[plan00,plan02]
        _,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size)
        for plan in plans:
            f=source.files[plan['bank']];plan.update(start=f['sector']*2048,end=f['sector']*2048+f['size_bytes'],path='/PSP_GAME/USRDIR/'+plan['bank'])
            assert plan['new_size']%2048==plan['old_size']%2048==0
        plans.sort(key=lambda r:r['start']);assert all(s*2048+n<plans[0]['start'] for s,n in dirs)
        print(json.dumps(dict(mode='write' if a.write else 'dry run',output=str(iso),checks=checks,
            names=names['names'],backlog_name_packs=sorted(replacements),banks=[dict(bank=p['bank'],old=p['old_size'],new=p['new_size']) for p in plans],
            preserve='0.1.10 executable, nameplate art, audio and all unrelated resources'),indent=2),flush=True)
        if not a.write:return
        dest.mkdir();partial=iso.with_suffix('.iso.partial')
        with partial.open('xb') as out:
            cursor=0
            for plan in plans:
                copy_range(src,out,cursor,plan['start']-cursor);write_bank(source,plan,out);cursor=plan['end']
            copy_range(src,out,cursor,prior.stat().st_size-cursor)
        sizes={p['path']:p['new_size'] for p in plans}
        with partial.open('r+b') as out:
            for rec in records:
                delta=sum(p['new_size']-p['old_size'] for p in plans if p['end']<=rec['sector']*2048)
                sector=rec['sector']+delta//2048;size=sizes.get(rec['path'],rec['size_bytes'])
                out.seek(rec['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector))
                out.seek(rec['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
            sectors=partial.stat().st_size//2048;out.seek(16*2048+80);out.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
        verified=[]
        with partial.open('rb') as out:
            _,actual=inventory(out,partial.stat().st_size);expected={r['path']:r for r in files}
            assert set(expected)=={r['path'] for r in actual}
            for row in actual:
                digest=extent_hash(out,row['sector'],row['size_bytes']);old=expected[row['path']]
                if row['path'] not in sizes:assert digest==extent_hash(src,old['sector'],old['size_bytes']),row['path']
                verified.append(dict(path=row['path'],sha256=digest,bytes=row['size_bytes'],changed=row['path'] in sizes))
        count=0
        with GameSource(partial) as candidate:
            assert len(candidate.indexes)==23
            for plan in plans:
                for row in source.indexes[plan['bank']]['entries']:
                    n=row['id'];data=candidate.resource(plan['bank'],n)
                    if n in plan['replacements']:
                        want=plan['replacements'][n];assert data[:len(want)]==want and not any(data[len(want):])
                    else:assert data==source.resource(plan['bank'],n);count+=1
            oldix=parse_index(master,len(master));newix=parse_index(new_master,len(new_master))
            for n in range(oldix['count']):
                if n!=1:assert child(master,oldix,n)==child(new_master,newix,n)
        partial.rename(iso);manifest=copy.deepcopy(previous)
        for k in ('runtime_validation','setup_ui_runtime_verified'):manifest.pop(k,None)
        manifest.update(version='0.1.11',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,
            output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],
            script_changes=[script_report],backlog_names=names,opening_complete_checks=checks)
        manifest['static_validation']=dict(prior_validation=previous['static_validation'],comparison_build='0.1.10',
            iso_file_count=len(actual),validated_bank_indexes=23,unchanged_iso_files=len(actual)-2,
            unchanged_resources_in_changed_banks=count,changed_files=list(sizes),per_file_validation=verified,
            runtime_verified=False,visual_verified=False)
        manifest['inputs_sha256'].pop('work/translation/en/opening_harbor_0.1.10.targets.json')
        for name in [TARGET,REVIEW,'tools/build_harbor_complete.py','tools/harbor_complete_patch.py',
                     'tools/backlog_names.py','work/glossary/opening_harbor.json']:
            manifest['inputs_sha256'][name]=hash_file(ROOT/name)
        shutil.copyfile(PRIOR/'EBOOT.elf',dest/'EBOOT.elf')
        (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(built=str(iso),sha256=manifest['output_sha256'],unchanged_files=len(actual)-2,unchanged_bank_resources=count),indent=2))

if __name__=='__main__':main()
