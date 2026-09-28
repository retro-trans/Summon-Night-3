"""Decode only the final five encounter headings; dry-run before --write."""
import argparse,json
from PIL import Image
from sn3_archive import GameSource,ROOT,parse_v4,child
from sn3_ui_textures import texture_records
from setup_ui_patch import encode_texture

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    folder=ROOT/'work/ui/battle_0.1.13/encounter_generated'
    with GameSource(ROOT/'work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso') as s:
        raw=s.resource('01.DAT',4);raw=child(raw,parse_v4(raw),1)
    decoded=[]
    for row in texture_records(raw):
        n=row['number'];im=Image.open(folder/f'header_{n}.native-source.png').convert('RGBA')
        im=im.resize((row['width'],row['height']),Image.Resampling.LANCZOS)
        _,im,_=encode_texture(raw,row,im);decoded.append((n,im))
    print(json.dumps(dict(mode='write' if a.write else 'dry-run',headings=[dict(number=n,size=im.size,alpha=im.getchannel('A').getextrema()) for n,im in decoded])))
    if a.write:
        dest=folder/'heading_r2';dest.mkdir(exist_ok=True)
        for n,im in decoded:im.save(dest/f'{n}.png')
if __name__=='__main__':main()
