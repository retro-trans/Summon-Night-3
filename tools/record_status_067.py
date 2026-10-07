"""Preview and record the completed local Status hint candidate."""
import argparse,json,copy
from datetime import datetime,timezone
from sn3_archive import ROOT
from build_candidate import hash_file
from verify_status_chain_067 import verify as verify_chain
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 folder=ROOT/'work/output/0.1.67';ui=ROOT/'work/ui/status_0.1.67'
 manifest=json.loads((folder/'manifest.json').read_text());audit=json.loads((ui/'stability-report.json').read_text());native=json.loads((ui/'native-validation.json').read_text());prior=json.loads((ROOT/'work/output/0.1.66/stability-report.json').read_text());chain=verify_chain()
 assert audit['passed'] and native['passed'] and prior['passed'] and len(audit['checks'])==14 and len(prior['checks'])==17
 assert audit['iso_sha256']==manifest['output_sha256']==hash_file(folder/manifest['output_iso'])
 for name,sha in manifest['inputs_sha256'].items():assert hash_file(ROOT/name)==sha,name
 evidence=[ui/'reported.png',ui/'original.png',ui/'native-validation.json',ui/'stability-report.json']+sorted((ui/'runtime').glob('*'))
 log=(ROOT/'work/scratch/status067-runtime/runtime.log').read_text(errors='replace')
 assert '0.1.67.iso' in log and not any(s in log for s in ('Bad memory access','E[MEMMAP]','Game crashed'))
 config=(ROOT/'work/scratch/status067-runtime/strict.ini').read_text(encoding='utf-8-sig').replace(' ','');assert 'IgnoreBadMemAccess=False' in config and 'CPUCore=1' in config
 for n in ('title','load','battle','menu'):
  cap=json.loads((ui/'runtime'/f'{n}.json').read_text());assert cap['cpu']['pc']==144800668 and cap['cpu']['stepping']
 retained=copy.deepcopy(prior['checks'][14:])
 for item in retained:item['preservation_proof']='067 leaves label banks and the prior helpers unchanged; the retained feeding helper also executes at both load bases.'
 audit['checks']+=retained+[dict(name='Two-row Status help and SELECT position',passed=True,details=dict(native=native,retained_handler_chain=chain))]
 runtime=dict(version='0.1.67',iso_sha256=manifest['output_sha256'],fresh_boot=True,normal_save=True,save_state_used=False,emulator='PPSSPP 1.20.4',cpu='JIT',graphics='software',ignore_bad_memory_access=False,continue_to_chapter15=True,battle_menu=True,exact_report_screen_verified=False,limitation='The matching room save is unavailable. SELECT visibility/spacing is verified by native formatter and positioning execution; the Japanese saved protagonist name is preserved pending clarification.',evidence=[dict(path=str(x.relative_to(ROOT)).replace('\\','/'),sha256=hash_file(x)) for x in evidence])
 doc='''# Status help — local test build 0.1.67

The original help writer wraps the translated Learn Skills hint onto a third
row. This room screen displays only two rows, so both its SELECT icon and label
disappear. The new second row uses **L/R Switch — SELECT Learn Skills**.
Five native space cells reserve 34.875 pixels between SELECT and its label;
the icon itself follows the measured proportional prefix width.

The shortcut string is relocated to appended memory. Three audited native
bindings use the new string; the old string, adjacent descriptions, and Level
Up's separate hint remain intact. The L/R hint is shortened within its own
slot. No writer buffers, row limits, or glyph capacities are enlarged.

The name table already contains **Rexx** and **Aty** for all four protagonist
class ranks. A Japanese name in an older save is a player-name value, not an
untranslated table entry. This build preserves that value and all custom names.
Whether the reported name was kept as the default or entered manually remains
unconfirmed; no name conversion has been applied.

Validation passes 18 cumulative groups: 14 rerun on the completed ISO, three
retained groups supported by unchanged bank/helper checks, and the new native
Status formatter/position checks. The new checks cover 16 formatter combinations
and 18 icon cases at two load bases, with buffer/stack guards and nonmatch
fallbacks. The retained Give Food helper also executes through the new handler
at both bases. The private chapter-script arena remains writable and intact.

PPSSPP 1.20.4 fresh boot, normal Chapter 15 Continue/load, and battle-menu
interaction pass with JIT and IgnoreBadMemAccess disabled. No save state was
used. Exact room-screen visual verification remains pending a matching save.

Test ISO: `work/output/0.1.67/Summon_Night_3_EN_0.1.67.iso`.
This is a local test build; the published release remains 0.1.65.
'''
 change='''## 0.1.67 - Restore Status Learn Skills hint (local test build, 2026-10-03)

- Keep SELECT / Learn Skills on the visible second help row; shorten the
  L/R hint to Switch and reserve space for the SELECT icon.
- Place the matching SELECT icon using proportional prefix width, retaining
  the previous Give Food handler and all nonmatching shortcut behavior.
- Relocate the longer shortcut string; preserve adjacent descriptions,
  buffer limits, custom player names and the private chapter-script arena.
- Default protagonist table labels are already Rexx/Aty. Japanese names
  stored in existing saves remain unchanged pending default/custom clarification.
- Pass 18 cumulative regression groups and a strict PPSSPP 1.20.4 fresh-boot
  normal-save load and battle-menu check. Exact room-screen visuals remain pending.

'''
 print(json.dumps(dict(mode='write' if a.write else 'preview',iso=manifest['output_iso'],sha256=manifest['output_sha256'],groups=len(audit['checks']),native_formatter_cases=len(native['formatter_cases']),native_position_cases=len(native['position_cases']),save_name='Preserved; default/custom clarification pending',documentation='docs/STATUS_0.1.67.md'),indent=2))
 if not a.write:return
 for dest,data in [(folder/'stability-report.json',audit),(folder/'runtime-validation.json',runtime),(ui/'runtime-validation.json',runtime)]:
  assert not dest.exists();dest.write_text(json.dumps(data,indent=2)+'\n')
 (ROOT/'docs/STATUS_0.1.67.md').write_text(doc,encoding='utf8')
 ch=ROOT/'CHANGELOG.md';old=ch.read_text(encoding='utf8');assert '## 0.1.67' not in old;ch.write_text(old.replace('# Changelog\n\n','# Changelog\n\n'+change,1),encoding='utf8')
 manifest['stability_validation']=dict(passed=True,groups=18,report='stability-report.json',sha256=hash_file(folder/'stability-report.json'))
 manifest['runtime_validation']=dict(passed=True,report='runtime-validation.json',sha256=hash_file(folder/'runtime-validation.json'),exact_report_screen_verified=False)
 for name in ('probe_status_067.py','verify_stability_067.py','verify_status_chain_067.py'):
  path=ROOT/'tools'/name;manifest['inputs_sha256'][str(path.relative_to(ROOT)).replace('\\','/')]=hash_file(path)
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
