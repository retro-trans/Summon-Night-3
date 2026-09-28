"""Mechanically import image-generated battle tutorial pages; dry-run by default."""
import argparse, json, hashlib
from PIL import Image
from sn3_archive import ROOT, GameSource
from sn3_ui_textures import texture_records, decode_texture
from setup_ui_patch import encode_texture

ASSETS=ROOT/'work/ui/battle_0.1.13/generated'
def sha(b):return hashlib.sha256(b).hexdigest()
def prepare(source):
    spec=json.loads((ASSETS/'index.json').read_text(encoding='utf-8'))
    original=json.loads((ASSETS.parent/'discovery/fullpage_03892_03924/index.json').read_text())
    known={int(r['resource_id'].split(':')[1]):r for r in original['textures']}
    replacements={}; images=[]; reports=[]
    for entry in spec['assets']:
        n=entry['resource']; p=ASSETS/entry['file']; data=source.resource('02.DAT',n)
        assert sha(data)==known[n]['source_sha256'],n
        assert sha(p.read_bytes())==entry['sha256'],p
        rows=texture_records(data); assert len(rows)==1
        row=rows[0]; old=decode_texture(data,row)
        same,_,_=encode_texture(data,row,old);assert same==data
        art=Image.open(p).convert('RGBA')
        assert abs(art.width/art.height-480/272)<0.02
        art=art.resize(old.size,Image.Resampling.LANCZOS)
        packed,decoded,changed=encode_texture(data,row,art)
        assert len(packed)==len(data)
        replacements[n]=packed;images.append((n,decoded))
        reports.append(dict(resource=n,source_sha256=sha(data),generated_sha256=entry['sha256'],
                            native_sha256=sha(packed),native_size=list(old.size),changed_pixels=changed))
    return replacements,images,dict(method='built-in imagegen; resize and native palette quantization only',pages=reports)
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    with GameSource(ROOT/'work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso') as source:
        packs,images,report=prepare(source)
    print(json.dumps(dict(mode='write' if a.write else 'dry-run',**report),indent=2))
    if a.write:
        folder=ASSETS.parent/'native';folder.mkdir(exist_ok=True)
        for n,im in images:im.save(folder/f'{n:05d}.png')
        (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
