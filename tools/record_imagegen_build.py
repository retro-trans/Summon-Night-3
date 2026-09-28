"""Record the inspected imagegen UI build; preview before updating metadata."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file


def prepare():
    directory=ROOT/'work/output/0.1.7'
    mp=directory/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
    assert hash_file(directory/m['output_iso'])==m['output_sha256']
    captures=[]
    for name,label in [('title','Rexx character selection'),('aty','Aty character selection')]:
        p=ROOT/'work/ui/imagegen_0.1.7/runtime'/f'{name}.png'
        meta=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
        assert hash_file(p)==meta['png_sha256']
        captures.append(dict(screen=label,path=p.relative_to(ROOT).as_posix(),sha256=meta['png_sha256']))
    qa=dict(version='0.1.7',candidate_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4 software rendering',
            scope='Generated character-selection banner and Confirm button on both protagonist screens.',
            passed=['Exact English text','Continuous woodgrain with no cover rectangles or old glyph remnants',
                    'Both assets render within the existing sprite bounds','Both protagonist packs load successfully'],
            captures=captures,gameplay_or_other_UI_retested=False,user_emulator_untouched=True)
    m['runtime_validation']=qa
    m['static_validation'].update(runtime_verified=True,visual_verified=True,runtime_scope=qa['scope'])
    m['setup_ui']['base_artwork_version']='0.1.6; four sprite records are superseded by imagegen_ui'
    m['inputs_sha256']['tools/record_imagegen_build.py']=hash_file(ROOT/'tools/record_imagegen_build.py')
    s_path=ROOT/'docs/translation_status.json';s=json.loads(s_path.read_text(encoding='utf-8'))
    assert s['latest_build']=='0.1.6'
    s['prior_candidate_0_1_6']=s['latest_candidate']
    s.update(latest_build='0.1.7',next_build_version='0.1.8',
        latest_build_kind='Image-generated character-selection artwork; both protagonist screens inspected in PPSSPP')
    s['latest_candidate']=dict(s['latest_candidate'],candidate_sha256=m['output_sha256'],
        qa_report='docs/BUILD_0.1.7.md',imagegen_assets=2,imagegen_sprite_instances=4,scope_limit=qa['scope'])
    s['interface_work'].update(imagegen_asset_report='work/ui/imagegen_0.1.7/index.json',imagegen_assets=2)
    s['runtime']['latest_build_runtime_scope']=qa['scope']+' Earlier setup QA remains scoped to 0.1.6.'
    s['coverage_counts_baseline']='Translation totals unchanged from 0.1.6. Version 0.1.7 changes only two graphical assets in both protagonist packs.'
    notes=f'''# Build 0.1.7 — image-generated menu artwork

[ISO](../work/output/0.1.7/{m['output_iso']}) · [In-game preview](../work/ui/imagegen_0.1.7/runtime/title.png)

Replaced the entire character-selection banner and Confirm button using built-in
image generation. The new assets have continuous peach woodgrain, integrated
cream/brown lettering and clean borders. Both protagonist variants use them.
No hand-drawn text or paint-over patches were added to the generated artwork.

## Saved artwork and prompts

- [Generated banner](../work/ui/imagegen_0.1.7/character_banner_generated.png)
- [Generated Confirm button](../work/ui/imagegen_0.1.7/confirm_button_generated.png)
- [Exact prompts and source references](../work/ui/imagegen_0.1.7/prompts.json)
- [Native conversion records](../work/ui/imagegen_0.1.7/index.json)

The built-in image_gen tool edited the original native sprites. Import only crops
transparent padding, downsamples to the original sprite footprint and maps colors
to the original palette. Generated alpha is retained through this conversion.

## Checks and scope

The final ISO was booted in an isolated PPSSPP 1.20.4 instance. Both Rexx and Aty
screens were inspected: text is complete, no rectangular patches or Japanese
letter remnants remain, and the artwork fits the existing menu geometry.
[Runtime evidence](../work/output/0.1.7/artwork_runtime_validation.json).

Static checks verified native pack round trips, untouched sibling sprites and
resources, all 23 indexes, 32 unchanged ISO files and 3,558 untouched bank resources.
The executable, 609 dialogue entries, naming controls and other 0.1.6 translations
are unchanged. Other UI and gameplay were not retested for this artwork update.
The user's running emulator was not changed.

SHA-256: `{m['output_sha256']}`. Size: {m['output_size_bytes']:,} bytes.
Restart from the title screen when switching ISO; an old emulator save state may
retain the prior loaded textures. This remains a partial translation.
'''
    readme_path=ROOT/'README.md';r=readme_path.read_text(encoding='utf-8')
    r=r.replace('**test ISO 0.1.6 is built and its setup flow tested in PPSSPP**',
                '**test ISO 0.1.7 is built with image-generated menu artwork**')
    r=r.replace('docs/BUILD_0.1.6.md','docs/BUILD_0.1.7.md').replace('work/output/0.1.6/Summon_Night_3_EN_0.1.6.iso','work/output/0.1.7/Summon_Night_3_EN_0.1.7.iso')
    r=r.replace('next unused version is **0.1.7**','next unused version is **0.1.8**')
    r=r.replace('docs/workspace_audit_0.1.6.json','docs/workspace_audit_0.1.7.json')
    logpath=ROOT/'CHANGELOG.md';log=logpath.read_text(encoding='utf-8')
    log=log.replace('# Changelog\n\n','''# Changelog

## 0.1.7 — image-generated menu artwork, 2026-09-26

- Rebuilt the complete character-selection banner and Confirm button with the
  built-in image generator to remove visible paint-over patches and improve style matching.
- Inserted both assets in Rexx and Aty packs using the native palette and geometry.
  Saved original generated images, exact prompts and native conversion records.
- Checked both protagonist screens in PPSSPP and verified untouched sibling
  graphics/resources. Preserved the executable and all prior translations.
- Next unused version is 0.1.8. Remaining translation and full-game QA scope is unchanged.

''',1)
    return {mp:json.dumps(m,indent=2)+'\n',directory/'artwork_runtime_validation.json':json.dumps(qa,indent=2)+'\n',
            s_path:json.dumps(s,ensure_ascii=False,indent=2)+'\n',ROOT/'docs/BUILD_0.1.7.md':notes,readme_path:r,logpath:log},qa


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    updates,qa=prepare()
    print(json.dumps(dict(mode='write' if a.write else 'dry run',updates=[p.relative_to(ROOT).as_posix() for p in updates],qa=qa),indent=2))
    if a.write:
        for p,t in updates.items():p.write_text(t,encoding='utf-8')


if __name__=='__main__':main()
