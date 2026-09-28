"""Package verified 0.1.41 with the Retro Trans release contract."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--patcher',type=Path,default=ROOT/'work/scratch/retro-trans-tools-release041')
    args=parser.parse_args()
    sys.path.insert(0,str(args.patcher.resolve()))
    from retro_trans.release import build_release,validate_directory
    from retro_trans.core import sha256_file
    folder=ROOT/'work/output/0.1.41'
    local=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    target=folder/local['output_iso']
    assert sha256_file(target)==local['output_sha256']
    for name,digest in local['inputs_sha256'].items():assert sha256_file(ROOT/name)==digest,name
    commit=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],text=True).strip()
    config=dict(game_id='summon-night-3',game_name='Summon Night 3',platform='PSP',version='0.1.41',source_commit=commit,patches=[])
    for version,source,name in [('original',ROOT/'work/source/original.iso','SN3-English-v0.1.41.xdelta'),('0.1.36',ROOT/'work/output/0.1.36/Summon_Night_3_EN_0.1.36.iso','SN3-English-v0.1.36-to-v0.1.41.xdelta')]:
        config['patches'].append(dict(patch=name,edition='Japanese NPJH50380',language='en',source_version=version,source_format='iso',target_format='iso',source=str(source),target=str(target)))
    out=ROOT/'work/output/release-v0.1.41'
    print(json.dumps(dict(mode='write' if args.write else 'preview',destination=str(out),source_commit=commit,patches=[p['patch'] for p in config['patches']]),indent=2),flush=True)
    if not args.write:return
    config_path=ROOT/'work/scratch/release041-config.json';config_path.write_text(json.dumps(config,indent=2),encoding='utf8')
    build_release(config_path,out,cache=ROOT/'work/scratch/release041-cache')
    validate_directory(out)
    print('Both patches passed full round-trip verification.',flush=True)

if __name__=='__main__':main()
