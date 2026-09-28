"""Build 0.1.9 from the verified 0.1.8 ISO, replacing only its executable."""
import argparse, copy, json, struct, hashlib
from datetime import datetime, timezone
from backlog_patch import patch, BASE
from build_candidate import ROOT, hash_file, directory_records, copy_range, extent_hash
from scan_source import inventory
from sn3_archive import GameSource

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    previous=json.loads((BASE.parent/'manifest.json').read_text());prior=BASE.parent/previous['output_iso']
    data,report=patch(BASE.read_bytes());dest=ROOT/'work/output/0.1.9';iso=dest/'Summon_Night_3_EN_0.1.9.iso'
    assert hash_file(prior)==previous['output_sha256']
    with prior.open('rb') as source:
        pvd,dirs,records=directory_records(source);_,files=inventory(source,prior.stat().st_size)
        eboot=next(f for f in files if f['path']=='/PSP_GAME/SYSDIR/EBOOT.BIN')
        assert extent_hash(source,eboot['sector'],eboot['size_bytes'])==report['source_elf_sha256']
        start=eboot['sector']*2048;end=start+(eboot['size_bytes']+2047)//2048*2048
        span=(len(data)+2047)//2048*2048;delta=span-(end-start)
        assert all(s*2048+n<start for s,n in dirs)
        print(json.dumps(dict(mode='write' if a.write else 'dry run',output=str(iso),
            changed_file=eboot['path'],prior_sha256=previous['output_sha256'],executable=report,
            additional_iso_bytes=delta,preserve='Every other ISO file, including all translations and audio'),indent=2),flush=True)
        if not a.write:return
        dest.mkdir();partial=iso.with_suffix('.iso.partial')
        with partial.open('xb') as out:
            copy_range(source,out,0,start);out.write(data);out.write(bytes(span-len(data)))
            copy_range(source,out,end,prior.stat().st_size-end)
        with partial.open('r+b') as out:
            for rec in records:
                sector=rec['sector']+(delta//2048 if rec['sector']*2048>=end else 0)
                size=len(data) if rec['path']==eboot['path'] else rec['size_bytes']
                out.seek(rec['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector))
                out.seek(rec['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
            sectors=partial.stat().st_size//2048;out.seek(16*2048+80)
            out.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
        with partial.open('rb') as out:
            volume,actual=inventory(out,partial.stat().st_size)
            expected={r['path']:r for r in files};assert set(expected)=={r['path'] for r in actual}
            checked=[]
            for row in actual:
                old=expected[row['path']];digest=extent_hash(out,row['sector'],row['size_bytes'])
                want=hashlib.sha256(data).hexdigest() if row['path']==eboot['path'] else extent_hash(source,old['sector'],old['size_bytes'])
                assert digest==want,row['path'];checked.append(dict(path=row['path'],sha256=digest,bytes=row['size_bytes']))
        with GameSource(partial) as game:assert len(game.indexes)==23
        partial.rename(iso);manifest=copy.deepcopy(previous)
        for k in ('runtime_validation','setup_ui_runtime_verified'):manifest.pop(k,None)
        manifest.update(version='0.1.9',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,
            output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'])
        manifest['prior_executable_patch']=manifest['executable_patch'];manifest['executable_patch']=report
        manifest['backlog_patch']=report
        manifest['static_validation']=dict(prior_validation=previous['static_validation'],iso_file_count=len(actual),
            validated_bank_indexes=23,unchanged_iso_files=len(actual)-1,changed_files=[eboot['path']],
            per_file_validation=checked,comparison_build='0.1.8',runtime_verified=False,visual_verified=False)
        for name in ['tools/backlog_patch.py','tools/build_backlog.py','tools/verify_backlog_patch.py','work/ui/latin_font_metrics.json']:
            manifest['inputs_sha256'][name]=hash_file(ROOT/name)
        (dest/'EBOOT.elf').write_bytes(data);(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(built=str(iso),sha256=manifest['output_sha256'],byte_identical_files=len(actual)-1),indent=2))

if __name__=='__main__':main()
