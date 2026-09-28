"""Fresh-boot checks on the isolated 19381 emulator only; preview before input."""
import argparse,base64,hashlib,json,time
from setup_qa import request,ROOT
import capture_framebuffer

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--press');p.add_argument('--capture');p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    session=json.loads((ROOT/'work/scratch/setup_qa_0.1.13/session.json').read_text(encoding='utf-8-sig'))
    assert session['port']==19381 and session['game'].endswith('Summon_Night_3_EN_0.1.13.iso')
    manifest=json.loads((ROOT/'work/output/0.1.13/manifest.json').read_text())
    game=request('game.status');assert game['game']['id']=='NPJH50380'
    elf=(ROOT/'work/output/0.1.13/EBOOT.elf').read_bytes()
    checked=[]
    for entry in manifest['battle_elf']['entries']:
        address=0x08804000+int(entry['new_address'],16)
        expected=elf[entry['new_file_offset']:entry['new_file_offset']+entry['bundle_bytes']]
        actual=base64.b64decode(request('memory.read',address=address,size=len(expected))['base64'])
        assert actual==expected,entry['id']
        checked.append(entry['id'])
    print(json.dumps(dict(mode='execute' if a.execute else 'dry-run',port=19381,
                         press=a.press,capture=a.capture,loaded_english_bundles=len(checked),game=game)),flush=True)
    if not a.execute:return
    if a.press:
        if request('cpu.status')['stepping']:request('cpu.resume')
        for button in a.press.split(','):
            assert button in ('circle','cross','up','down','left','right','start','select','l','r')
            request('input.buttons.press',button=button,duration=10);time.sleep(3)
    if a.capture:
        folder=ROOT/'work/ui/battle_0.1.13/runtime';folder.mkdir(exist_ok=True)
        target=folder/a.capture
        assert target.resolve().parent==folder.resolve() and target.suffix=='.png' and not target.exists()
        if request('cpu.status')['stepping']:request('cpu.resume')
        time.sleep(2)
        capture_framebuffer.request=request
        png,meta=capture_framebuffer.capture(hold=False)
        target.write_bytes(png)
        target.with_suffix('.json').write_text(json.dumps(dict(session=session,capture=meta,
            iso_sha256=manifest['output_sha256'],loaded_english_bundles=checked,
            scope='Fresh boot and relocated English payload check; not a battle playthrough.'),indent=2)+'\n')
        print(json.dumps(dict(capture=str(target),sha256=hashlib.sha256(png).hexdigest())))

if __name__=='__main__':main()
