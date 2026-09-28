"""Export likely dialogue name strips from indexed source resources; preview first."""
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from sn3_archive import ROOT,GameSource
from sn3_ui_textures import decode_texture

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--purple',action='store_true');p.add_argument('--ids');a=p.parse_args()
    index=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());dest=ROOT/'work/ui/nameplates_0.1.10'/('ids_'+a.ids.replace(':','_').replace(',','_') if a.ids else 'purple' if a.purple else 'source')
    images=[]
    with GameSource() as source:
        for res in index['resources']:
            occ=res['occurrences'][0]
            if a.ids:
                if occ['id'] not in a.ids.split(','):continue
            elif not a.purple and (occ['bank']!='02.DAT' or not 1332<=occ['path'][0]<=1346):continue
            for row in res['textures']:
                if a.ids:pass
                elif a.purple:
                    if not (64<=row['width']<=256 and 16<=row['height']<=48):continue
                elif (row['width'],row['height'])!=(112,24):continue
                data=source.read(occ['bank'],occ['offset'],occ['size'])
                assert hashlib.sha256(data).hexdigest()==res['source_sha256']
                try:im=decode_texture(data,row)
                except ValueError:continue
                if a.purple:
                    px=np.asarray(im).astype('int32');r,g,b,alpha=[px[:,:,i] for i in range(4)]
                    if np.count_nonzero((r>g*1.6)&(b>g*1.5)&(r>25)&(b>25)&(alpha>200))<120:continue
                    if np.count_nonzero((r>200)&(g>170)&(b>120)&(alpha>200))<70:continue
                name=occ['id'].replace(':','_').replace('/','_')+f"_{row['number']}.png"
                images.append((dict(id=occ['id'],sprite=row['number'],file=name,occurrences=res['occurrences'],source_sha256=res['source_sha256']),im))
    print(json.dumps(dict(mode='write' if a.write else 'dry run',destination=str(dest),count=len(images),samples=[r for r,im in images[:3]]),indent=2))
    if not a.write:return
    dest.mkdir(parents=True)
    for row,im in images:im.save(dest/row['file'])
    sheets=[]
    for page,start in enumerate(range(0,len(images),36)):
        sheet=Image.new('RGB',(1080,720),(100,110,120));d=ImageDraw.Draw(sheet)
        for slot,(r,im) in enumerate(images[start:start+36]):
            x=slot%3*360;y=slot//3*60;d.text((x+4,y+2),r['id']+':'+str(r['sprite']),fill='white')
            preview=im.resize((224,48));sheet.paste(preview,(x+6,y+13),preview)
        name=f'contact_{page}.png';sheet.save(dest/name);sheets.append(name)
    (dest/'index.json').write_text(json.dumps(dict(records=[r for r,im in images],sheets=sheets),indent=2)+'\n')

if __name__=='__main__':main()
