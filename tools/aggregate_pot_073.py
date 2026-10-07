"""Include the new name-cache regression group in the cumulative report."""
import json
from sn3_archive import ROOT
from build_candidate import hash_file
def main():
 folder=ROOT/'work/output/0.1.73';path=folder/'stability-report.json';r=json.loads(path.read_text())
 new=json.loads((folder/'name-cache-validation.json').read_text());assert r['passed'] and new['passed']
 title='Summon defaults, renaming and saved-cache repair'
 assert not any(c['name']==title for c in r['checks'])
 r['checks'].append(dict(name=title,passed=True,details=new));path.write_text(json.dumps(r,indent=2)+'\n')
 mpath=folder/'manifest.json';m=json.loads(mpath.read_text())
 m['stability_validation'].update(groups=len(r['checks']),sha256=hash_file(path))
 m['inputs_sha256']['tools/aggregate_pot_073.py']=hash_file(ROOT/'tools/aggregate_pot_073.py')
 mpath.write_text(json.dumps(m,indent=2)+'\n');print(dict(passed=True,groups=len(r['checks'])))
if __name__=='__main__':main()
