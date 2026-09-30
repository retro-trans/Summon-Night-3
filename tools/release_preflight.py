"""Check candidate identity and recorded evidence before a test or stable release."""
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['continue_late_battle','brave_goals','equipment','summon_index','puppet_shop','room_skills','cooking','save_reload','early_chapter','night_talk']
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
def check(folder,channel):
 manifest=json.loads((folder/'manifest.json').read_text())
 iso=folder/manifest['output_iso'];expected=manifest['output_sha256']
 errors=[]
 if digest(iso)!=expected:errors.append('ISO does not match manifest')
 for name,wanted in manifest['inputs_sha256'].items():
  if digest(ROOT/name)!=wanted:errors.append('Changed build input: '+name)
 audit=json.loads((folder/'stability-report.json').read_text())
 if audit.get('iso_sha256')!=expected or not audit.get('passed') or not audit.get('checks') or any(not c.get('passed') for c in audit['checks']):errors.append('Combined audit missing, failed or bound to another ISO')
 runtime=json.loads((folder/'runtime-validation.json').read_text())
 if runtime.get('iso_sha256')!=expected or not runtime.get('fresh_boot'):errors.append('Fresh-boot evidence does not match this ISO')
 for item in runtime.get('evidence',[]):
  if digest(ROOT/item['path'])!=item['sha256']:errors.append('Runtime evidence changed: '+item['path'])
 cases=runtime.get('cases',{})
 missing=[name for name in REQUIRED if cases.get(name,{}).get('status')!='passed']
 for name in ['continue_late_battle','brave_goals','equipment','summon_index']:
  if name in missing:errors.append('Required smoke test missing: '+name)
 if channel=='stable' and missing:errors.append('Stable release coverage incomplete: '+', '.join(missing))
 return dict(version=manifest['version'],channel=channel,passed=not errors,errors=errors,pending_runtime=missing,iso_sha256=expected)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--channel',choices=['test','stable'],required=True);a=p.parse_args()
 try:r=check((ROOT/a.build).resolve(),a.channel)
 except Exception as e:r=dict(passed=False,errors=[type(e).__name__+': '+str(e)])
 print(json.dumps(r,indent=2));return 0 if r['passed'] else 1
if __name__=='__main__':sys.exit(main())
