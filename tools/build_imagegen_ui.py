"""Convert imagegen artwork to native sprites and build 0.1.7; preview before writes."""
import argparse,copy,json,shutil
from datetime import datetime,timezone
from PIL import Image
from build_candidate import *
from setup_ui_patch import encode_texture
from sn3_ui_textures import texture_records,decode_texture

ASSETS=ROOT/'work/ui/imagegen_0.1.7'
BASE=ROOT/'work/output/0.1.6'
DEST=ROOT/'work/output/0.1.7'


def prepare_art():
    spec=json.loads((ASSETS/'prompts.json').read_text(encoding='utf-8'))
    previous=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
    packs={};renders=[];report=[]
    with GameSource(BASE/previous['output_iso']) as source:
        for number in (28,29):
            data=decompress(source.resource('02.DAT',number),0x9831)[0]
            index=parse_index(data,len(data));original=child(data,index,1);out=original
            rows={r['number']:r for r in texture_records(original)}
            for a in spec['assets']:
                row=rows[a['sprite']];old=decode_texture(original,row)
                saved=ASSETS/(a['id']+'_generated.png')
                image_path=saved if saved.exists() else Path(a['source'])
                generated=Image.open(image_path).convert('RGBA')
                # Mechanical import only: trim transparent padding, downsample to
                # the original sprite footprint and quantize to its native palette.
                bounds=generated.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox()
                box=old.getbbox();w,h=box[2]-box[0],box[3]-box[1]
                fitted=Image.new('RGBA',old.size)
                fitted.paste(generated.crop(bounds).resize((w,h),Image.Resampling.LANCZOS),box[:2])
                out,decoded,pixels=encode_texture(out,row,fitted)
                name=f"02_{number:05d}_00001_sprite_{a['sprite']:03d}.png"
                renders.append((name,decoded))
                report.append(dict(pack=number,sprite=a['sprite'],asset_id=a['id'],native_image=name,
                    generated_sha256=hash_file(image_path),generated_alpha_bounds=bounds,
                    native_bounds=box,native_size=old.size,modified_pixels=pixels,
                    native_rgba_sha256=hashlib.sha256(decoded.tobytes()).hexdigest()))
            modified=repack(data,{1:out});packed=compress(modified,0x9831)
            assert decompress(packed,0x9831)[0]==modified
            new_index=parse_index(modified,len(modified))
            for e in index['entries']:
                if e['id']!=1:assert child(data,index,e['id'])==child(modified,new_index,e['id'])
            # Other sprites in child 1 must remain pixel-identical to 0.1.6.
            for n,row in rows.items():
                if n not in (0,4):assert decode_texture(original,row).tobytes()==decode_texture(out,row).tobytes()
            packs[number]=packed
    return packs,renders,dict(version='0.1.7',method='built-in image_gen',
        records=report,scope='Two complete generated assets, each used in both protagonist packs.',
        imports='Crop alpha padding; downsample; map to original native palette. No text drawing or paint-over patches.',
        inputs_sha256={'work/ui/imagegen_0.1.7/prompts.json':hash_file(ASSETS/'prompts.json'),
                      'tools/build_imagegen_ui.py':hash_file(Path(__file__))},
        native_packs=[dict(number=n,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)) for n,b in packs.items()])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-assets',action='store_true');p.add_argument('--write-iso',action='store_true')
    args=p.parse_args();assert not(args.write_assets and args.write_iso)
    packs,renders,art=prepare_art()
    print(json.dumps(dict(mode='write assets' if args.write_assets else 'write ISO' if args.write_iso else 'dry run',
                         destination=str(DEST),art=art),indent=2),flush=True)
    if args.write_assets:
        assert not (ASSETS/'index.json').exists()
        spec=json.loads((ASSETS/'prompts.json').read_text(encoding='utf-8'))
        for a in spec['assets']:shutil.copyfile(a['source'],ASSETS/(a['id']+'_generated.png'))
        for name,im in renders:im.save(ASSETS/name)
        for n,b in packs.items():(ASSETS/f'pack_{n:05d}.bin').write_bytes(b)
        (ASSETS/'index.json').write_text(json.dumps(art,indent=2)+'\n',encoding='utf-8')
        return
    if not args.write_iso:return
    assert json.loads((ASSETS/'index.json').read_text(encoding='utf-8'))==json.loads(json.dumps(art))
    assert not DEST.exists()
    previous=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
    assert hash_file(BASE/previous['output_iso'])==previous['output_sha256']
    executable=(BASE/'EBOOT.elf').read_bytes()
    assert hashlib.sha256(executable).hexdigest()==previous['executable_patch']['patched_elf_sha256']
    with GameSource() as source,GameSource(BASE/previous['output_iso']) as prior:
        plans,changes,entries=prepare(source)
        scripts,reports=prepare_scripts(source,ROOT/'work/translation/en/opening_harbor_0.1.5.targets.json',FONT_PROFILE)
        assert reports[0]['decoded_sha256']==previous['script_changes'][0]['decoded_sha256']
        allpacks={n:packs.get(n,prior.resource('02.DAT',n)) for n in (28,29,30,31,32)}
        plan02=plan_bank(source,'02.DAT',allpacks)
        combined=dict(plans[0]['replacements']);combined.update(scripts)
        combined[44]=repack(combined[44],{1:plan02['index_bytes']})
        plans[0]=plan_bank(source,'00.DAT',combined);plans.append(plan02)
        assert hash_file(ROOT/'work/source/original.iso')==previous['source_iso_sha256']
        DEST.mkdir()
        iso=DEST/'Summon_Night_3_EN_0.1.7.iso';partial=iso.with_suffix('.iso.partial')
        files={'/PSP_GAME/SYSDIR/EBOOT.BIN':executable}
        write_iso(source,plans,partial,files)
        validation=verify_candidate(partial,source,changes,entries,reports,files,{'02.DAT':allpacks})
        partial.rename(iso)
        manifest=copy.deepcopy(previous)
        for k in ('runtime_validation','setup_ui_runtime_verified'):manifest.pop(k,None)
        manifest.update(version='0.1.7',built_at_utc=datetime.now(timezone.utc).isoformat(),
            output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),
            static_validation=validation,script_changes=reports,imagegen_ui=art,
            previous_build_sha256=previous['output_sha256'])
        for name in ['tools/build_imagegen_ui.py','work/ui/imagegen_0.1.7/prompts.json','work/ui/imagegen_0.1.7/index.json',
                     'work/ui/imagegen_0.1.7/character_banner_generated.png','work/ui/imagegen_0.1.7/confirm_button_generated.png']:
            manifest['inputs_sha256'][name]=hash_file(ROOT/name)
        (DEST/'EBOOT.elf').write_bytes(executable)
        (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(built=str(iso),sha256=manifest['output_sha256'],validation=validation),indent=2))


if __name__=='__main__':main()
