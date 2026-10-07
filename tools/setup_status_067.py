"""Preview scaffolding for the immutable 0.1.67 build."""
import argparse,json
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 build=(ROOT/'tools/build_status_066.py').read_text().replace('0.1.66','0.1.67').replace('0.1.65','0.1.66').replace('066','067')
 launch=(ROOT/'tools/launch_status_066.ps1').read_text().replace('066','067').replace('0.1.66','0.1.67').replace('19403','19404')
 runtime=(ROOT/'tools/status_runtime_066.py').read_text().replace('066','067').replace('0.1.66','0.1.67').replace('19403','19404')
 files={'tools/build_status_067.py':build,'tools/launch_status_067.ps1':launch,'tools/status_runtime_067.py':runtime}
 print(json.dumps(dict(mode='write' if a.write else 'preview',files=list(files),base='0.1.66',target='0.1.67',changes=['Two-row status hint','Scoped proportional SELECT placement','Saved player names preserved']),indent=2))
 if a.write:
  for name,text in files.items():
   path=ROOT/name;assert not path.exists();path.write_text(text,encoding='utf8')
if __name__=='__main__':main()
