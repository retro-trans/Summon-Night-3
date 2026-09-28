"""Record inspected backlog screenshots and 0.1.9 release notes; preview first."""
import argparse,json
from build_candidate import ROOT,hash_file

def prepare():
    out=ROOT/'work/output/0.1.9';mp=out/'manifest.json';m=json.loads(mp.read_text())
    assert hash_file(out/m['output_iso'])==m['output_sha256']
    captures=[]
    for name,label in [('start','Fresh boot: naming screen'),('backlog','English backlog'),
                       ('scrolled','Earlier entries after scrolling'),('dialogue_visible','Normal dialogue typing after closing backlog'),
                       ('reopened','New entries after reopening backlog')]:
        p=ROOT/f'work/ui/backlog_0.1.9/runtime/{name}.png';meta=json.loads(p.with_suffix('.json').read_text())
        assert hash_file(p)==meta['png_sha256']
        captures.append(dict(screen=label,path=p.relative_to(ROOT).as_posix(),sha256=meta['png_sha256']))
    abi=json.loads((ROOT/'work/ui/backlog_0.1.9/abi_validation.json').read_text())
    assert abi['patched_elf_sha256']==m['executable_patch']['patched_elf_sha256']
    qa=dict(version='0.1.9',candidate_sha256=m['output_sha256'],
        emulator='PPSSPP 1.20.4 software renderer; isolated fresh game',captures=captures,
        scope='Fresh boot, naming, opening beach dialogue, backlog, scrolling, closing and reopening with new entries.',
        original_baseline='work/ui/backlog_0.1.9/probe/square_before.png',
        harbor_scene_replayed=False,full_game_tested=False,audio_playback_retested=False,
        user_emulator_untouched=True,abi_validation=abi)
    m['runtime_validation']=qa;m['static_validation'].update(runtime_verified=True,visual_verified=True,runtime_scope=qa['scope'])
    for name in ['tools/record_backlog_build.py','tools/inspect_backlog.py','work/ui/backlog_0.1.9/abi_validation.json']:
        m['inputs_sha256'][name]=hash_file(ROOT/name)
    sp=ROOT/'docs/translation_status.json';s=json.loads(sp.read_text(encoding='utf-8'))
    assert s['latest_build']=='0.1.8';s['prior_candidate_0_1_8']=s['latest_candidate']
    s.update(latest_build='0.1.9',next_build_version='0.1.10',latest_build_kind='Proportional English spacing in dialogue history')
    s['latest_candidate']=dict(s['latest_candidate'],candidate_sha256=m['output_sha256'],qa_report='docs/BUILD_0.1.9.md',
        acceptance='backlog_spacing_verified_partial_translation',runtime_verified=True,visual_verified=True,
        scope_limit=qa['scope']+' Harbor and full game not replayed; prior translations preserved.')
    s['runtime']['latest_build_runtime_verified']=True;s['runtime']['latest_build_runtime_scope']=qa['scope']
    s['coverage_counts_baseline']='0.1.9 changes backlog rendering only. All translation counts and chapter assets from 0.1.8 are unchanged.'
    notes=f'''# Build 0.1.9 — backlog spacing

[ISO](../work/output/0.1.9/{m['output_iso']}) · [Backlog screenshot](../work/ui/backlog_0.1.9/runtime/backlog.png)

The dialogue history used fixed 16-pixel Japanese cells for English, separately
from the proportional dialogue-window renderer. Long lines ran beyond the panel.
Both speaker names and history text now use the same measured Latin ink widths
as dialogue. Original glyph pixels, sentence content, font size and line breaks
are preserved. Unmapped characters keep their original 16-pixel cells.

The patch packs the ink inside each existing native 1/8/16-cell texture strip and
advances the next strip by its measured width. It changes only four backlog call
sites. It does not expand the object pool or alter other font users. Cache keys
are invalidated after packing so later owners repaint their original glyphs.

## Verification

- Executed the emitted MIPS instructions in 202 guarded cases at two load bases:
  all 93 supported Latin characters, spaces, punctuation, 16-cell strips and
  mixed Japanese fallback. Checked pixels, strip boundaries, stack/register
  preservation, cache invalidation and measured advance.
- Booted the final ISO in isolated PPSSPP 1.20.4. Inspected naming, beach backlog,
  earlier entries after scrolling, normal dialogue after closing, and new history
  entries after reopening. [Evidence](../work/output/0.1.9/backlog_runtime_validation.json).
- All 35 other ISO files are byte-identical to 0.1.8, including every resource
  bank and audio file. Validated all 23 bank indexes and the changed executable.
- The 512 lines in the current reflowed dialogue groups have a maximum measured
  width of 243 pixels, within the 356-pixel history panel.

The exact harbor scene from the report and full-game routes were not replayed.
The voice-playback label remains Japanese; this build fixes spacing and does not
add translations. Prior chapter cards and translations are retained. This is
still a partial English translation. Audio playback was not retested.

Boot the new ISO from a fresh start, then load an ordinary in-game save if needed.
Old PPSSPP save states retain the old executable in memory and can restore the bug.

SHA-256: `{m['output_sha256']}`. Size: {m['output_size_bytes']:,} bytes.
Next unused version: **0.1.10**.
'''
    rp=ROOT/'README.md';r=rp.read_text(encoding='utf-8').replace(
        'Status: **test ISO 0.1.8 is built with all 30 discovered chapter-card titles translated**.',
        'Status: **test ISO 0.1.9 fixes English spacing and clipping in the dialogue backlog**.\n'
        'Scrolling, closing and reopening were checked in PPSSPP. Prior translations remain included.')
    r=r.replace('docs/BUILD_0.1.8.md','docs/BUILD_0.1.9.md').replace('work/output/0.1.8/Summon_Night_3_EN_0.1.8.iso','work/output/0.1.9/Summon_Night_3_EN_0.1.9.iso')
    r=r.replace('next unused version is **0.1.9**','next unused version is **0.1.10**').replace('docs/workspace_audit_0.1.8.json','docs/workspace_audit_0.1.9.json')
    lp=ROOT/'CHANGELOG.md';log=lp.read_text(encoding='utf-8').replace('# Changelog\n\n','''# Changelog

## 0.1.9 — backlog spacing, 2026-09-26

- Fixed widely spaced English speaker names and dialogue in history by packing
  original glyph ink in native texture strips and measuring each strip's advance.
- Preserved complete text, glyph shapes, Japanese fallback and cache reuse.
- Passed 202 emitted-instruction checks and fresh-boot PPSSPP checks for backlog
  display, scrolling, closing, ordinary dialogue and reopening with new entries.
- Kept all 35 other ISO files byte-identical to 0.1.8. No new translations.
- Next version: 0.1.10. Restart the game; old emulator states retain old code.

''',1)
    return {mp:json.dumps(m,indent=2)+'\n',out/'backlog_runtime_validation.json':json.dumps(qa,indent=2)+'\n',
        sp:json.dumps(s,ensure_ascii=False,indent=2)+'\n',ROOT/'docs/BUILD_0.1.9.md':notes,rp:r,lp:log},qa

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    updates,qa=prepare();print(json.dumps(dict(mode='write' if a.write else 'dry run',updates=[str(p) for p in updates],qa=qa),indent=2))
    if a.write:
        for p,t in updates.items():p.write_text(t,encoding='utf-8')

if __name__=='__main__':main()
