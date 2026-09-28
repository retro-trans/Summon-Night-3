"""Advance only the isolated 0.1.8 QA instance, retaining intermediate frames."""
import argparse, json, time
from PIL import Image, ImageDraw
from setup_qa import request, ROOT
import capture_framebuffer

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('name');p.add_argument('--pairs',type=int,default=12)
    p.add_argument('--execute',action='store_true');a=p.parse_args()
    assert a.name.isalnum() and 1<=a.pairs<=18
    path=ROOT/'work/ui/chapter_0.1.8/runtime'/a.name
    assert not path.exists()
    session=json.loads((ROOT/'work/scratch/setup_qa_0.1.8/session.json').read_text(encoding='utf-8-sig'))
    assert '0.1.8' in session['game'] and session['port']==19381
    game=request('game.status');assert game['game']['id']=='NPJH50380'
    print(json.dumps(dict(mode='execute' if a.execute else 'dry run',
        action='Press Circle twice per frame; capture and pause between pairs',pairs=a.pairs,
        port=19381,output=str(path),game=game)),flush=True)
    if not a.execute:return
    path.mkdir();capture_framebuffer.request=request
    frames=[]
    for i in range(a.pairs):
        if request('cpu.status')['stepping']:request('cpu.resume')
        for j in range(2):
            request('input.buttons.press',button='circle',duration=2)
            time.sleep(.6)
        png,meta=capture_framebuffer.capture(hold=True)
        dest=path/f'{i:02d}.png';dest.write_bytes(png)
        dest.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
        frames.append(dest)
        print('Captured '+str(i),flush=True)
    for b in range((len(frames)+7)//8):
        group=frames[b*8:b*8+8]
        sheet=Image.new('RGB',(960,296*((len(group)+1)//2)))
        draw=ImageDraw.Draw(sheet)
        for j,f in enumerate(group):
            x,y=(j%2)*480,(j//2)*296
            draw.text((x+4,y+4),f.stem,fill='white')
            sheet.paste(Image.open(f),(x,y+24))
        sheet.save(path/f'contact_{b}.png')

if __name__=='__main__':main()
