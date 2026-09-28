"""Build battle UI 0.1.13 incrementally from 0.1.12; dry-run by default."""
import argparse,copy,json,struct
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import plan_bank,repack,write_bank
from build_candidate import hash_file,copy_range,directory_records,extent_hash
from scan_source import inventory
from battle_elf_patch import prepare as prepare_elf,sha256
from battle_table_patch import plan as prepare_tables
from battle_art_patch import prepare as prepare_art
from battle_encounter_patch import prepare as prepare_encounters

BASE=ROOT/'work/output/0.1.12';DEST=ROOT/'work/output/0.1.13'
EBOOT='/PSP_GAME/SYSDIR/EBOOT.BIN'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def clean(obj):
    if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items() if 'runtime' not in k.lower() and 'visual' not in k.lower()}
    if isinstance(obj,list):return [clean(v) for v in obj]
    return obj
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    previous=read(BASE/'manifest.json');prior=BASE/previous['output_iso']
    assert hash_file(prior)==previous['output_sha256']
    for name,h in previous['inputs_sha256'].items():assert hash_file(ROOT/name)==h,name
    for item in read(ROOT/'work/translation/en/battle_0.1.13/build_inputs.json')['inputs']:
        assert hash_file(ROOT/item['path'])==item['sha256'],item['path']
    executable,elf_report=prepare_elf((BASE/'EBOOT.elf').read_bytes())
    with GameSource(prior) as source,prior.open('rb') as src:
        tables=prepare_tables(source);art,images,art_report=prepare_art(source)
        encounters,encounter_images,encounter_report=prepare_encounters(source)
        assert not encounter_report['unsupported_other_bank_count']
        p01=plan_bank(source,'01.DAT',encounters)
        changes02={3:tables['resources']['02:00003'],**art}
        p02=plan_bank(source,'02.DAT',changes02)
        master=tables['resources']['00:00044'];newmaster=repack(master,{0:p01['index_bytes'],1:p02['index_bytes']})
        p00=plan_bank(source,'00.DAT',{44:newmaster})
        bankplans=[p00,p01,p02]
        for p in bankplans:
            f=source.files[p['bank']];p.update(kind='bank',start=f['sector']*2048,end=f['sector']*2048+f['size_bytes'],old_span=f['size_bytes'],new_span=p['new_size'],path='/PSP_GAME/USRDIR/'+p['bank'])
            assert p['new_span']%2048==p['old_span']%2048==0
        pvd,dirs,records=directory_records(src);_,files=inventory(src,prior.stat().st_size)
        oldelf=next(f for f in files if f['path']==EBOOT)
        assert extent_hash(src,oldelf['sector'],oldelf['size_bytes'])==hash_file(BASE/'EBOOT.elf')
        eboot=dict(kind='elf',start=oldelf['sector']*2048,end=oldelf['sector']*2048+(oldelf['size_bytes']+2047)//2048*2048,old_span=(oldelf['size_bytes']+2047)//2048*2048,new_span=(len(executable)+2047)//2048*2048,new_size=len(executable),path=EBOOT)
        plans=sorted(bankplans+[eboot],key=lambda p:p['start'])
        assert all(a['end']<=b['start'] for a,b in zip(plans,plans[1:]))
        assert all(s*2048+n<plans[0]['start'] for s,n in dirs)
        pt_size=struct.unpack_from('<I',pvd,132)[0]
        assert all(s*2048+pt_size<plans[0]['start'] for s in struct.unpack_from('<II',pvd,140)+struct.unpack_from('>II',pvd,148) if s)
        print(json.dumps(dict(mode='write' if args.write else 'dry-run',elf_entries=len(elf_report['entries']),table_entries=tables['report']['selected_entries'],tutorial_pages=len(art),encounter_sprites=encounter_report['targeted_sprite_count'],samples=[e['target_text'] for e in elf_report['entries'][:5]],banks=[dict(bank=p['bank'],old=p['old_span'],new=p['new_span']) for p in bankplans]),indent=2),flush=True)
        if not args.write:return
        DEST.mkdir();iso=DEST/'Summon_Night_3_EN_0.1.13.iso';partial=iso.with_suffix('.iso.partial')
        with partial.open('xb') as out:
            cursor=0
            for p in plans:
                copy_range(src,out,cursor,p['start']-cursor)
                if p['kind']=='bank':write_bank(source,p,out)
                else:out.write(executable);out.write(bytes(p['new_span']-len(executable)))
                cursor=p['end']
            copy_range(src,out,cursor,prior.stat().st_size-cursor)
        sizes={p['path']:p['new_size'] for p in plans}
        with partial.open('r+b') as out:
            for r in records:
                delta=sum(p['new_span']-p['old_span'] for p in plans if p['end']<=r['sector']*2048)
                sector=r['sector']+delta//2048;size=sizes.get(r['path'],r['size_bytes'])
                out.seek(r['record_offset']+2);out.write(struct.pack('<I',sector)+struct.pack('>I',sector))
                out.seek(r['record_offset']+10);out.write(struct.pack('<I',size)+struct.pack('>I',size))
            sectors=partial.stat().st_size//2048;out.seek(16*2048+80);out.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
        verified=[]
        with partial.open('rb') as out:
            _,actual=inventory(out,partial.stat().st_size);expected={r['path']:r for r in files}
            assert set(expected)=={r['path'] for r in actual}
            for r in actual:
                h=extent_hash(out,r['sector'],r['size_bytes']);old=expected[r['path']]
                if r['path'] not in sizes:assert h==extent_hash(src,old['sector'],old['size_bytes']),r['path']
                elif r['path']==EBOOT:assert h==sha256(executable)
                verified.append(dict(path=r['path'],sha256=h,changed=r['path'] in sizes))
        unchanged=0
        with GameSource(partial) as candidate:
            assert len(candidate.indexes)==23
            for p in bankplans:
                for r in source.indexes[p['bank']]['entries']:
                    n=r['id'];data=candidate.resource(p['bank'],n)
                    if n in p['replacements']:
                        target=p['replacements'][n];assert data[:len(target)]==target and not any(data[len(target):])
                    else:assert data==source.resource(p['bank'],n);unchanged+=1
            cm=candidate.resource('00.DAT',44);assert child(cm,parse_index(cm,len(cm)),7)==candidate.resource('02.DAT',3)
        partial.rename(iso)
        manifest=clean(copy.deepcopy(previous))
        manifest['battle_encounters']=encounter_report
        manifest.update(version='0.1.13',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],battle_elf=elf_report,battle_tables=tables['report'],battle_art=art_report,static_validation=dict(comparison_build='0.1.12',per_file=verified,unchanged_bank_resources=unchanged,bank_indexes=23,runtime_verified=False))
        inputs=[ROOT/'tools'/n for n in ['build_battle.py','battle_elf_patch.py','battle_elf_refs.py','battle_table_patch.py','battle_art_patch.py','import_battle_art.py','normalize_battle_names.py','battle_encounter_patch.py','import_encounter_art.py','battle_qa.py']]
        inputs.append(ROOT/'work/glossary/battle_0.1.13.json')
        inputs.append(ROOT/'work/ui/battle_0.1.13/discovery/fullpage_03892_03924/index.json')
        inputs+=list((ROOT/'work/translation/en/battle_0.1.13').glob('*.json'))+list((ROOT/'work/ui/battle_0.1.13/generated').glob('*'))
        inputs+=list((ROOT/'work/ui/battle_0.1.13/encounter_generated').glob('*'))
        inputs.append(ROOT/'work/ui/battle_0.1.13/intro_discovery_01_00004_00064_full/index.json')
        for p in inputs:
            if p.is_file():manifest['inputs_sha256'][str(p.relative_to(ROOT)).replace('\\','/')]=hash_file(p)
        (DEST/'EBOOT.elf').write_bytes(executable);(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(iso=str(iso),sha256=manifest['output_sha256'],unchanged_bank_resources=unchanged),indent=2))
if __name__=='__main__':main()
