"""Import reviewed imagegen outputs and mechanically crop their transparent margins."""
import argparse,hashlib,json,shutil
from PIL import Image,ImageOps
from sn3_archive import ROOT

FOLDER=ROOT/'work/ui/battle_0.1.13/encounter_generated'
DISCOVERY=FOLDER.parent/'intro_discovery_01_00004_00064_full/index.json'
LOSSES={9:'HERO OR SONOLAR\nDEFEATED',10:'HERO OR KYLE\nDEFEATED',15:'HERO OR GUARDIAN\nDEFEATED',17:'HERO OR PUPIL\nDEFEATED',29:'HERO, AZLIER OR\nGALLEOR DEFEATED',30:'HERO, SCARREL OR\nYARD DEFEATED',43:'HERO OR PHLAIZ\nDEFEATED',44:'HERO OR CUNNON\nDEFEATED',45:'HERO OR ARDYLLIA\nDEFEATED',46:'HERO OR JAKINIE\nDEFEATED',48:'HERO OR AZLIER\nDEFEATED',49:'HERO OR OUKINIE\nDEFEATED',63:'ALL ALLIES\nDEFEATED'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    rows={r['id']:r for r in json.loads(DISCOVERY.read_text())['candidates']}
    generated=json.loads((FOLDER/'generation_sources.json').read_text())['assets']
    for n,txt in LOSSES.items():
        generated.append(dict(key=f'loss_{n:05d}',path=str(FOLDER/f'loss_{n:05d}.png'),text=txt,
            prompt='Recreate source defeat-condition sprite, exact two-line English: '+txt+'. White/lavender bold beveled fantasy serif, navy outline, genuine transparent background, 5% padding.'))
    planned=[];catalog=[]
    def add(key,path,prompt,text,targets,crop=None):
        file=FOLDER/(key+'.native-source.png')
        with Image.open(path) as src:im=src.convert('RGBA')
        assert im.getchannel('A').getextrema()==(0,255),path
        if crop is not None:
            i,count=crop;im=im.crop((round(i*im.width/count),0,round((i+1)*im.width/count),im.height))
        alpha=im.getchannel('A')
        # The generated heading atlas has near-transparent export noise outside
        # its letters. Locate the crop by visible alpha; preserve pixels inside.
        box=(alpha.point(lambda x:255 if x>=32 else 0) if crop is not None else alpha).getbbox();assert box
        im=im.crop(box)
        # Production normalization only: trim unused transparent space and retain
        # 5% clear padding. No letters, colors, scene content or outlines are drawn.
        im=ImageOps.expand(im,border=max(2,round(min(im.size)*.05)),fill=(0,0,0,0))
        target_rows=[]
        for top,ch,num in targets:
            ident=f'01:{top:05d}/{ch:05d}:sprite:{num:03d}';r=rows[ident]
            target_rows.append(dict(resource_id=r['resource_id'],number=num,source_sha256=r['source_sha256']))
            catalog.append(dict(id=ident,source_sha256=r['source_sha256'],source_image_path=r['image_file'],
                target_text=text,generated_key=key,type='title' if ch==4 else 'heading' if ch==1 else 'condition'))
        planned.append((file,im,dict(key=key,file=file.name,prompt=prompt,target_text=text,
            generation_source=str(path),generation_source_sha256=sha(open(path,'rb').read()),targets=target_rows)))
    for g in generated:
        key=g['key'];targets=[]
        if key=='headers':
            for i,txt in enumerate(['W','IN','IF','LO','SE']):add(f'header_{i}',g['path'],g['prompt'],txt,[(4,1,i)],(i,5))
            continue
        if key=='title_pirates':targets=[(4,4,0),(5,4,0)]
        elif key.startswith('title_'):
            n=int(key.split('_')[1]);targets=[(n,4,0)]
            if n==18:targets.append((44,4,0))
            if n==43:targets.append((63,4,0))
        elif key=='victory_all':targets=[(4,2,0),(15,2,0)]
        elif key=='victory_leader':targets=[(16,2,0)]
        elif key=='victory_dielgo':targets=[(36,2,0)]
        elif key=='loss_hero':targets=[(4,3,0)]
        elif key.startswith('loss_'):targets=[(int(key.split('_')[1]),3,0)]
        else:raise ValueError(key)
        add(key,g['path'],g['prompt'],g['text'],targets)
    expected={r['id'] for r in rows.values() if r['path'][1] in (1,2,3,4)}
    assert expected=={r['id'] for r in catalog},(expected-{r['id'] for r in catalog})
    print(json.dumps(dict(mode='write' if a.write else 'dry-run',assets=len(planned),source_sprites=len(catalog),
        examples=[{k:r[k] for k in ('id','target_text')} for r in catalog[:8]],
        full_category_coverage=True),indent=2))
    if not a.write:return
    entries=[]
    for file,im,entry in planned:
        im.save(file);entry['sha256']=sha(file.read_bytes());entries.append(entry)
    (FOLDER/'index.json').write_text(json.dumps(dict(schema_version=1,entries=entries),indent=2)+'\n')
    target=ROOT/'work/translation/en/battle_0.1.13/encounter_art.targets.json'
    target.write_text(json.dumps(dict(schema_version=1,build_version='0.1.13',status='root_reviewed_source_art',
        scope='Every unique text sprite in encounter family 01:4-64; duplicate bank occurrences found during import.',
        source_export=str(DISCOVERY.relative_to(ROOT)),source_export_sha256=sha(DISCOVERY.read_bytes()),
        provisional_terms=['Jilcooda','Shadow of Primal Sin'],entries=catalog),indent=2)+'\n')
if __name__=='__main__':main()
