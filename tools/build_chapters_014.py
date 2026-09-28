"""Build reviewed Chapters4-8 onto0.1.13; preview before writing0.1.14."""
import argparse,copy,json,struct
from datetime import datetime,timezone
from pathlib import Path
from sn3_archive import ROOT,GameSource
from sn3_repack import plan_bank,repack,write_bank
from build_candidate import hash_file,copy_range,directory_records,extent_hash
from scan_source import inventory
from chapter_patch_014 import prepare,FOLDER
from chapter_names_014 import prepare_names
from build_battle import clean

BASE=ROOT/'work/output/0.1.13';DEST=ROOT/'work/output/0.1.14'
MAIN=[134,157,180,203,226]
SUPPORT=[135,136,137,138,139,140,141,143,144,145,146,147,148,158,159,160,161,162,163,164,166,167,168,169,170,171,181,182,183,184,185,186,187,189,190,191,192,193,194,204,205,206,207,208,209,210,212,213,214,215,216,217,227,228,229,230,231,232,233,235,236,237,238,239,240,242]
RESOURCES=sorted(MAIN+SUPPORT)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def relative(p):return str(p.relative_to(ROOT)).replace('\\','/')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    previous=read(BASE/'manifest.json');prior=BASE/previous['output_iso']
    assert hash_file(prior)==previous['output_sha256']
    for n,h in previous['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
    replacements={};reports=[];checks={};inputs={}
    for f in ['build_chapters_014.py','chapter_names_014.py','script_compact_014.py','chapter_compiler_014.py','chapter_patch_014.py','font_metrics_014.py','generate_compiler_014.py','accept_chapters_014.py','test_chapter_compiler_014.py']:
        path=ROOT/'tools'/f;inputs[relative(path)]=hash_file(path)
    for path in (ROOT/'work/glossary').glob('*0.1.14.json'):inputs[relative(path)]=hash_file(path)
    for n in RESOURCES:
        packed,report,selection,check=prepare(n,True)
        assert not check['remaining_in_scope']
        replacements[n]=packed;reports.append(report);checks[str(n)]=check
        for name,h in selection['review_inputs_sha256'].items():
            assert inputs.setdefault(name,h)==h
        print(json.dumps(dict(resource=n,rows=check['covered_source_rows'],bytes=report['decoded_size'])),flush=True)
    with GameSource(prior) as source,prior.open('rb') as src:
        for report in reports:
            assert __import__('hashlib').sha256(source.resource('00.DAT',report['index'])).hexdigest()==report['source_sha256'],('baseline already modifies selected script',report['index'])
        names,name_report=prepare_names(source)
        p02=plan_bank(source,'02.DAT',names)
        master=repack(source.resource('00.DAT',44),{1:p02['index_bytes']})
        p00=plan_bank(source,'00.DAT',{44:master,**replacements})
        plans=[]
        for plan in (p00,p02):
            f=source.files[plan['bank']]
            plan.update(start=f['sector']*2048,end=f['sector']*2048+f['size_bytes'],old_span=f['size_bytes'],new_span=plan['new_size'],path='/PSP_GAME/USRDIR/'+plan['bank'])
            assert plan['old_span']%2048==plan['new_span']%2048==0
            plans.append(plan)
        plans.sort(key=lambda p:p['start']);assert plans[0]['end']<=plans[1]['start']
        pvd,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size)
        assert all(s*2048+n<plans[0]['start'] for s,n in dirs)
        pt=struct.unpack_from('<I',pvd,132)[0]
        assert all(s*2048+pt<plans[0]['start'] for s in struct.unpack_from('<II',pvd,140)+struct.unpack_from('>II',pvd,148) if s)
        print(json.dumps(dict(mode='write' if a.write else 'dry-run',version='0.1.14',resources=len(reports),rows=sum(c['covered_source_rows'] for c in checks.values()),largest_script=max(r['decoded_size'] for r in reports),backlog_names=name_report,banks=[dict(bank=p['bank'],old=p['old_span'],new=p['new_span']) for p in plans]),indent=2),flush=True)
        if not a.write:return
        DEST.mkdir();iso=DEST/'Summon_Night_3_EN_0.1.14.iso';partial=iso.with_suffix('.iso.partial')
        with partial.open('xb') as out:
            cursor=0
            for plan in plans:
                copy_range(src,out,cursor,plan['start']-cursor);write_bank(source,plan,out);cursor=plan['end']
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
            _,actual=inventory(out,partial.stat().st_size);old={r['path']:r for r in files}
            assert set(old)=={r['path'] for r in actual}
            for r in actual:
                h=extent_hash(out,r['sector'],r['size_bytes']);o=old[r['path']]
                if r['path'] not in sizes:assert h==extent_hash(src,o['sector'],o['size_bytes']),r['path']
                verified.append(dict(path=r['path'],sha256=h,changed=r['path'] in sizes))
        with GameSource(partial) as candidate:
            assert len(candidate.indexes)==23
            for plan in plans:
                for entry in source.indexes[plan['bank']]['entries']:
                    n=entry['id'];data=candidate.resource(plan['bank'],n)
                    if n in plan['replacements']:
                        wanted=plan['replacements'][n];assert data[:len(wanted)]==wanted and not any(data[len(wanted):])
                    else:assert data==source.resource(plan['bank'],n);unchanged+=1
        for name,h in inputs.items():assert hash_file(ROOT/name)==h,name
        partial.rename(iso)
        manifest=clean(copy.deepcopy(previous))
        manifest.update(version='0.1.14',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],chapters_4_to_8=reports,chapter48_checks=checks,chapter48_backlog_names=name_report,static_validation=dict(comparison_build='0.1.13',per_file=verified,unchanged_bank_resources=unchanged,bank_indexes=23,runtime_verified=False))
        manifest['inputs_sha256'].update(inputs)
        (DEST/'EBOOT.elf').write_bytes((BASE/'EBOOT.elf').read_bytes())
        (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(iso=str(iso),sha256=manifest['output_sha256']),indent=2))
if __name__=='__main__':main()
