"""Publish the verified battle build; preview before --write."""
import argparse,json,hashlib
from pathlib import Path
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/battle_candidate_0.1.24').resolve();dst=(ROOT/'work/output/0.1.24').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
assert hash_file(src/'EBOOT.elf')==hash_file(ROOT/'work/output/0.1.23/EBOOT.elf')
reports=m['battle024'];shared=[r for r in reports if 'canonical_translation_resource' in r]
assert len(reports)==53 and len(shared)==31
assert len({r['source_sha256'] for r in shared})==len({r['output_sha256'] for r in shared})==1
coverage=dict(version='0.1.24',main_fragments=528,side_candidate_fragments=8,shared_fragments=1140,distinct_contexts=1676,physical_occurrences=sum(r['covered_source_rows'] for r in reports),packs=53,shared_copies=31,compiled_pages_excluding_duplicate_copies=sum(len(g['pages']) for r in reports for g in r.get('groups',[])),remaining_scoped_japanese_rows=0,side_review='Root compared all eight rows against source and adjacent context.',all_display_spans_simulated=all(r['all_display_spans_simulated'] for r in reports),scope_evidence='docs/battle_scope_024_draft.json',limitations=['Chapter mapping is structural and semantic, not a complete loader trace.','Runtime tests cover the first pirate battle only.'])
runtime_folder=ROOT/'work/ui/battle_0.1.24/runtime'
checks=['final_load','final_kyle','final_health_first','final_health_second','final_protect','final_after_tutorial']
evidence={}
for name in checks:
 for ext in ('.png','.json'):
  f=runtime_folder/(name+ext);evidence[str(f.relative_to(ROOT)).replace('\\','/')]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,emulator='PPSSPP 1.20.4, isolated software rendering',verified=['Fresh save load and map VWF','Kyle opening speech with VWF','Aty long dialogue split across two pages with correct speaker','Protect line and continuation into battle tutorials','Return to interactive unit commands after the tutorials'],evidence_sha256=evidence,all_routes_tested=False)
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],coverage=coverage,runtime=runtime),indent=2))
if not a.write:raise SystemExit
(ROOT/'docs/battle_coverage_0.1.24.json').write_text(json.dumps(coverage,indent=2)+'\n')
(runtime_folder/'verification.json').write_text(json.dumps(runtime,indent=2)+'\n')
m['battle024_coverage']=coverage;m['battle024_runtime']=runtime;m['static_validation']['runtime_verified']=True;m['static_validation']['runtime_scope']='First pirate battle only; see battle024_runtime.'
for n in ['tools/publish_battle_024.py','docs/BATTLE_DIALOGUE_0.1.24.md','docs/battle_coverage_0.1.24.json','docs/battle_scope_024_draft.json','docs/battle_renderer_024.json','tools/battle_runtime_024.py','tools/finalize_battle_024.py']:
 m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence)
(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
changelog=ROOT/'CHANGELOG.md';text=changelog.read_text(encoding='utf8');assert '## 0.1.24 ' not in text
entry='''## 0.1.24 — battle dialogue through Chapter 8, 2026-09-27

- Translated 528 main-battle fragments, 8 early side-battle candidates, and
  1,140 shared repeatable-battle conversation fragments. Updated all 31 copies
  of the shared script: 53 battle packs in total.
- Retained full dialogue with proportional text and additional pages; preserved
  speaker selection, player placeholders, event flow and previous UI fixes.
- Verified every rewritten display span and unchanged archive resource. Fresh
  in-game save testing confirms the first pirate battle speech and added pages.
  Other routes have static validation; no eight-chapter playthrough is claimed.
- See `docs/BATTLE_DIALOGUE_0.1.24.md` for coverage and limits.

'''
changelog.write_text(text.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
readme=ROOT/'README.md';text=readme.read_text(encoding='utf8');notice='''Latest build: **[0.1.24 test ISO](work/output/0.1.24/Summon_Night_3_EN_0.1.24.iso)**.
Battle dialogue through Chapter 8 now includes 1,676 source-fragment contexts,
with shared conversations patched in every copy. Existing story and UI work
is retained. See [coverage and test limits](docs/BATTLE_DIALOGUE_0.1.24.md).
Older progress snapshots below describe their stated versions.

'''
readme.write_text(text.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst)
print('Published',dst)
