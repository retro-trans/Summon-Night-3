"""Compare all published v0.1.65 assets with the verified local package."""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');a=p.parse_args()
    sys.path.insert(0,str(ROOT/'work/scratch/retro-trans-tools-release041'))
    from retro_trans.core import GitHubClient,Asset,sha256_file
    folder=ROOT/'work/output/release-v0.1.65'
    files=sorted(x for x in folder.iterdir() if x.is_file())
    assert len(files)==9 and len([x for x in files if x.suffix=='.xdelta'])==2
    out=ROOT/'work/ui/release_0.1.65/publication-validation.json'
    print(json.dumps(dict(mode='verify' if a.execute else 'preview',assets=[x.name for x in files],report=str(out)),indent=2),flush=True)
    if not a.execute:return
    assert not out.exists()
    client=GitHubClient();release=client.json('https://api.github.com/repos/retro-trans/Summon-Night-3/releases/tags/v0.1.65')
    assert not release['draft'] and not release['prerelease']
    remote={x['name']:x for x in release['assets']};assert set(remote)=={x.name for x in files}
    rows=[]
    for path in files:
        row=remote[path.name];digest=sha256_file(path)
        assert row['size']==path.stat().st_size and row['digest']=='sha256:'+digest
        url='https://github.com/retro-trans/Summon-Night-3/releases/download/v0.1.65/'+path.name
        assert row['browser_download_url']==url
        downloaded=client.download(Asset(path.name,url,path.stat().st_size,digest),ROOT/'work/scratch/public-assets065')
        assert sha256_file(downloaded)==digest
        rows.append(dict(name=path.name,bytes=path.stat().st_size,sha256=digest));print('Verified '+path.name,flush=True)
    manifest=json.loads((folder/'BUILD-MANIFEST.json').read_text())
    report=dict(version='0.1.65',url=release['html_url'],source_commit=manifest['source_commit'],all_public_assets_match=True,exactly_two_patches=True,assets=rows)
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
