"""Bounded fresh-boot QA in an explicitly isolated0.1.14 emulator."""
import argparse,base64,hashlib,json,time
from pathlib import Path
from sn3_archive import ROOT
from chapter_qa_runtime import validate_session
from setup_qa import request
import capture_framebuffer

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--press');p.add_argument('--capture');p.add_argument('--execute',action='store_true');a=p.parse_args()
    candidate=ROOT/'work/output/0.1.14/Summon_Night_3_EN_0.1.14.iso'
    session,game=validate_session(ROOT/'work/scratch/setup_qa_0.1.14/session.json',candidate)
    manifest=json.loads(candidate.with_name('manifest.json').read_text(encoding='utf8'))
    print(json.dumps(dict(mode='execute' if a.execute else 'dry-run',session=session,press=a.press,capture=a.capture,scope='Fresh boot and inherited English payloads only; no Chapters4-8 route playthrough.')),flush=True)
    if not a.execute:return
    if a.press:
        if request('cpu.status')['stepping']:request('cpu.resume')
        for button in a.press.split(','):
            assert button in ('circle','cross','start')
            request('input.buttons.press',button=button,duration=10);time.sleep(2)
    elf=candidate.with_name('EBOOT.elf').read_bytes();checked=[]
    for entry in manifest['battle_elf']['entries']:
        expected=elf[entry['new_file_offset']:entry['new_file_offset']+entry['bundle_bytes']]
        actual=base64.b64decode(request('memory.read',address=0x08804000+int(entry['new_address'],16),size=len(expected))['base64'])
        assert expected==actual,entry['id'];checked.append(entry['id'])
    report=dict(version='0.1.14',session=session,game=game,iso_sha256=manifest['output_sha256'],inherited_english_bundles_verified=len(checked),bundle_ids=checked,scope='Fresh boot and inherited executable text; not a full route playthrough or live verification of newly translated chapter scripts.')
    if a.capture:
        folder=ROOT/'work/ui/chapters_0.1.14/runtime';folder.mkdir(parents=True,exist_ok=True)
        path=folder/a.capture;assert path.parent==folder and path.suffix=='.png' and not path.exists()
        capture_framebuffer.request=request
        png,meta=capture_framebuffer.capture(hold=False)
        path.write_bytes(png);report.update(capture=meta,capture_path=str(path),capture_sha256=hashlib.sha256(png).hexdigest())
        path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('bundle_ids','capture')},indent=2))
if __name__=='__main__':main()
