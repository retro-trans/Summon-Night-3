"""Package v0.1.51 only after rechecking the exact candidate ISO."""
import sys,json,subprocess
from pathlib import Path
if not __debug__:raise RuntimeError('Assertions required')
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'work/scratch/retro-trans-tools-release041'))
from retro_trans.core import engine_context,encode,decode,sha256_file

def main():
 out=root/'work/output/0.1.51';manifest=json.loads((out/'manifest.json').read_text())
 subprocess.run([sys.executable,str(root/'tools/verify_stability_051.py'),'--build',str(out),'--report',str(out/'stability-report.json')],check=True)
 target=out/manifest['output_iso'];expected=manifest['output_sha256']
 assert sha256_file(target)==expected
 for name,digest in manifest['inputs_sha256'].items():assert sha256_file(root/name)==digest,name
 rows=[]
 with engine_context(cache=root/'work/scratch/release041-cache') as engine:
  for source,name in [(root/'work/output/0.1.50/Summon_Night_3_EN_0.1.50.iso','SN3-English-v0.1.50-to-v0.1.51.xdelta'),(root/'work/output/0.1.42/Summon_Night_3_EN_0.1.42.iso','SN3-English-v0.1.42-to-v0.1.51.xdelta'),(root/'work/source/original.iso','SN3-English-v0.1.51.xdelta')]:
   patch=out/name;check=root/'work/scratch'/('verify051-'+name+'.iso')
   assert not patch.exists() and not check.exists()
   print('Encoding '+name,flush=True);encode(engine,source,target,patch)
   decode(engine,source,patch,check,target.stat().st_size)
   result=sha256_file(check);assert result==expected
   check.unlink()
   rows.append(dict(patch=name,bytes=patch.stat().st_size,sha256=sha256_file(patch),source_sha256=sha256_file(source),target_sha256=result,round_trip_verified=True))
   print(json.dumps(rows[-1]),flush=True)
 (out/'XDELTA-VALIDATION.json').write_text(json.dumps(dict(version='0.1.51',engine='retro-trans-tools',release_status='test build; see runtime coverage',patches=rows),indent=2)+'\n')
 (out/'XDELTA-SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['patch']+'\n' for r in rows))
if __name__=='__main__':main()
