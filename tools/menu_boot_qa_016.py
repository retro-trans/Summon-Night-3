"""Bounded fresh-boot verification on the explicitly isolated port 19381."""
import argparse,base64,json,hashlib
from sn3_archive import ROOT
from chapter_qa_runtime import validate_session
from setup_qa import request

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 folder=ROOT/'work/scratch/menu_candidate_0.1.16_final'
 candidate=folder/'Summon_Night_3_EN_0.1.16.iso'
 session,game=validate_session(ROOT/'work/scratch/setup_qa_0.1.16/session.json',candidate)
 m=json.loads((folder/'manifest.json').read_text());elf=(folder/'EBOOT.elf').read_bytes()
 entries=m['menu016_text']['entries']+m['menu016_text']['compact_conditions']+m['menu_text']['entries']
 checks=[]
 for e in entries:
  start=e['new_file_offset'];size=e['bundle_bytes'];expected=elf[start:start+size]
  actual=base64.b64decode(request('memory.read',address=0x08804000+int(e['new_address'],16),size=size)['base64'])
  assert actual==expected,e['id']
  checks.append(dict(id=e['id'],address=e['new_address'],bytes=size,sha256=hashlib.sha256(actual).hexdigest()))
 report=dict(mode='write' if a.write else 'dry-run',session=session,game=game,iso_sha256=m['output_sha256'],verified_bundles=len(checks),checks=checks,cpu=request('cpu.status'),limitations='Fresh boot and live executable bytes only. No battle-menu visual verification or save-state restoration.')
 print(json.dumps(dict(mode=report['mode'],verified_bundles=len(checks),cpu=report['cpu']),indent=2))
 if a.write:
  dest=ROOT/'work/ui/menu_0.1.16/runtime';dest.mkdir(exist_ok=False)
  (dest/'fresh_boot.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
