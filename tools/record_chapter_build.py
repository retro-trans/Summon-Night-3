"""Record inspected chapter artwork and runtime evidence; preview before writes."""
import argparse, json
from sn3_archive import ROOT
from build_candidate import hash_file

def prepare():
    directory=ROOT/'work/output/0.1.8'
    mp=directory/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
    assert hash_file(directory/m['output_iso'])==m['output_sha256']
    art=ROOT/'work/ui/chapter_0.1.8';captures=[]
    for name,label in [('boot','Title screen'),('setup','Character selection'),
                       ('batch2/08','Chapter 1 at full opacity'),('batch2/12','Chapter 1 fading out'),
                       ('batch2/13','Return to beach after chapter card')]:
        p=art/'runtime'/f'{name}.png'
        meta=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
        assert hash_file(p)==meta['png_sha256']
        captures.append(dict(screen=label,path=p.relative_to(ROOT).as_posix(),sha256=meta['png_sha256']))
    sheets=[dict(path=(art/f'contact_{i:02d}.png').relative_to(ROOT).as_posix(),
                 sha256=hash_file(art/f'contact_{i:02d}.png')) for i in range(4)]
    qa=dict(version='0.1.8',candidate_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4 software rendering',
        scope='Fresh boot and setup; Chapter 1 reached naturally, rendered at full opacity, faded out and returned to the beach.',
        native_artwork_visual_review=dict(cards=31,distinct_titles=30,contact_sheets=sheets,
            checks=['Full English titles and chapter headings','Original English subtitle wording',
                    'No clipped lettering or Japanese remnants','No rectangular cover patches','Readable native 480x272 output']),
        captures=captures,all_ending_branches_runtime_tested=False,
        audio_files_byte_identical=31,audio_playback_retested=False,user_emulator_untouched=True)
    m['runtime_validation']=qa
    m['static_validation'].update(runtime_verified=True,visual_verified=True,runtime_scope=qa['scope'])
    m['chapter_titles']['native_visual_reviewed_cards']=31
    m['chapter_titles']['runtime_verified_packs']=[93]
    m['chapter_titles']['executable_metadata_strings_changed']=False
    for name in ['tools/record_chapter_build.py','tools/chapter_qa.py','docs/CHAPTER_TITLES.md']:
        m['inputs_sha256'][name]=hash_file(ROOT/name)
    s_path=ROOT/'docs/translation_status.json';s=json.loads(s_path.read_text(encoding='utf-8'))
    assert s['latest_build']=='0.1.7'
    s['prior_candidate_0_1_7']=s['latest_candidate']
    s.update(latest_build='0.1.8',next_build_version='0.1.9',
        latest_build_kind='30 image-generated chapter, side-story, bonus and ending titles in 31 native cards; Chapter 1 checked in PPSSPP')
    s['latest_candidate']=dict(s['latest_candidate'],candidate_sha256=m['output_sha256'],
        acceptance='chapter_artwork_verified_partial_translation',qa_report='docs/BUILD_0.1.8.md',
        chapter_title_assets=30,chapter_title_native_cards=31,runtime_verified=True,visual_verified=True,
        imagegen_assets=32,imagegen_sprite_instances=35,
        modified_native_sprites=99,scope_limit=qa['scope']+' Other title cards checked as decoded native images; all ending routes not played.')
    s['interface_work'].update(chapter_titles_report='docs/CHAPTER_TITLES.md',
        chapter_titles_translated=30,chapter_title_native_instances=31,
        chapter_title_asset_report='work/ui/chapter_0.1.8/index.json')
    s['runtime']['latest_build_runtime_verified']=True
    s['runtime']['latest_build_runtime_scope']=qa['scope']
    s['coverage_counts_baseline']='0.1.8 adds 30 distinct title translations in 31 native cards. Prior 609 dialogue entries, 3 labels and setup translations are preserved.'
    notes=f'''# Build 0.1.8 — translated chapter cards

[ISO](../work/output/0.1.8/{m['output_iso']}) · [Chapter 1 in-game](../work/ui/chapter_0.1.8/runtime/batch2/08.png)

Translated and redrew all 30 distinct title cards in the discovered native family:
16 numbered chapters, the final chapter, five side stories, one bonus title and
seven ending titles. The additional Chapter 2 copy is replaced too, for 31 native
cards. The supplied screenshot is now **Chapter 1 — A Sudden Beginning**, keeping
the subtitle **Where am I now?**

## Artwork and translations

The built-in image generator redrew the complete cards, retaining each source
palette, star motif and existing English subtitle. Full-canvas downsampling and
native-palette conversion preserve transparency; no cover rectangles or text
overlays are added. All generated assets are saved in
`work/ui/chapter_0.1.8/chapter_93_generated.png` through
`chapter_122_generated.png`.

- [Complete translation list and scope](CHAPTER_TITLES.md)
- [Exact prompts](../work/ui/chapter_0.1.8/prompts.json)
- [Independent meaning review](../work/translation/en/chapter_titles.meaning_review.json)
- [Native conversion records](../work/ui/chapter_0.1.8/index.json)
- [Runtime and visual evidence](../work/output/0.1.8/chapter_runtime_validation.json)

## Validation and limits

All 31 native images were decoded and visually inspected at 480×272. Every pack
round-tripped, retained its decoded size, texture descriptors and palette, and
preserved its RIFF/WAVE audio byte-for-byte. Final ISO verification checked all
23 bank indexes, 32 unchanged ISO files and 3,527 unchanged bank resources.
The executable, prior setup graphics, 609 dialogue entries and three character
labels are preserved from 0.1.7.

The final ISO was booted in a separate PPSSPP 1.20.4 instance with a fresh game.
Chapter 1 was reached naturally, displayed clearly, faded out and returned to the
beach. Other chapter and ending branches were not played through; their artwork
passed native-image and archive checks. Audio playback was not retested. The
user's running emulator and saves were untouched.

Separate executable heading/title metadata remains Japanese until its save/gallery
consumers and layout are verified. Other untranslated UI and dialogue remain;
this is a partial translation, not a full-game release.

SHA-256: `{m['output_sha256']}`. Size: {m['output_size_bytes']:,} bytes.
Restart the game when switching ISO; an old save state may retain loaded textures.
Next unused version: **0.1.9**.
'''
    readme=ROOT/'README.md';r=readme.read_text(encoding='utf-8')
    r=r.replace('Status: **test ISO 0.1.7 is built with image-generated menu artwork**.',
        'Status: **test ISO 0.1.8 is built with all 30 discovered chapter-card titles translated**.\n'
        'It replaces 31 native chapter, side-story, bonus and ending cards using image-generated artwork.\n'
        'Chapter 1 was checked in PPSSPP; see the [complete title list](docs/CHAPTER_TITLES.md).')
    r=r.replace('docs/BUILD_0.1.7.md','docs/BUILD_0.1.8.md').replace(
        'work/output/0.1.7/Summon_Night_3_EN_0.1.7.iso','work/output/0.1.8/Summon_Night_3_EN_0.1.8.iso')
    r=r.replace('next unused version is **0.1.8**','next unused version is **0.1.9**')
    r=r.replace('docs/workspace_audit_0.1.7.json','docs/workspace_audit_0.1.8.json')
    logpath=ROOT/'CHANGELOG.md';log=logpath.read_text(encoding='utf-8')
    log=log.replace('# Changelog\n\n','''# Changelog

## 0.1.8 — chapter-title artwork, 2026-09-26

- Translated and independently reviewed 30 distinct titles across all 16 numbered
  chapters, the final chapter, five side stories, a bonus title and seven endings.
- Redrew complete cards with built-in imagegen and inserted all 31 native instances,
  including both Chapter 2 copies. Preserved original English subtitles and audio.
- Inspected every decoded native card; verified transparency, pack round trips,
  unchanged descriptors/palettes, audio identity and final ISO structure.
- Reached Chapter 1 naturally in isolated PPSSPP and checked its display, fade-out
  and return to the beach. Other title branches remain unplayed.
- Preserved prior translations. Separate executable title metadata and other
  untranslated game text remain outside this artwork build. Next version: 0.1.9.

''',1)
    return {mp:json.dumps(m,indent=2)+'\n',directory/'chapter_runtime_validation.json':json.dumps(qa,indent=2)+'\n',
        s_path:json.dumps(s,ensure_ascii=False,indent=2)+'\n',ROOT/'docs/BUILD_0.1.8.md':notes,readme:r,logpath:log},qa

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    updates,qa=prepare()
    print(json.dumps(dict(mode='write' if a.write else 'dry run',updates=[p.relative_to(ROOT).as_posix() for p in updates],qa=qa),indent=2))
    if a.write:
        for p,t in updates.items():p.write_text(t,encoding='utf-8')

if __name__=='__main__':main()
