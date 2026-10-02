"""Read-only Level Up title discovery; preview before native texture exports."""
import argparse,json
from PIL import Image,ImageDraw
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_ui_textures import texture_records,decode_texture
from menu_art_015 import descend

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    output=ROOT/'work/ui/levelup_0.1.60';items=[]
    with GameSource(ROOT/'work/output/0.1.59/Summon_Night_3_EN_0.1.59.iso') as s:
        raw=descend(s.resource('02.DAT',1333),[10]);ix=parse_index(raw,len(raw))
        for e in ix['entries']:
            data=child(raw,ix,e['id'])
            try:rows=texture_records(data)
            except ValueError:continue
            if len(rows)==1 and rows[0]['width']>=104:
                items.append((e['id'],decode_texture(data,rows[0])))
    print(json.dumps(dict(mode='export' if a.write else 'preview',output=str(output),
        titles=[dict(child=n,size=im.size) for n,im in items]),indent=2))
    if a.write:
        output.mkdir(parents=True,exist_ok=True)
        contact=Image.new('RGBA',(600,((len(items)+3)//4)*70),(70,75,80,255));draw=ImageDraw.Draw(contact)
        for i,(n,im) in enumerate(items):
            im.save(output/f'title_{n}_source.png')
            x=i%4*150;y=i//4*70;draw.text((x,y),str(n),fill='white');contact.alpha_composite(im,(x,y+20))
        contact.save(output/'source_contact.png')

if __name__=='__main__':main()
