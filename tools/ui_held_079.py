"""Capture an Options state after explicit held/released debugger input."""
import argparse
import json
import time
from options_runtime_078 import client
from sn3_archive import ROOT


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('name')
    p.add_argument('--case', default='ui079-candidate')
    p.add_argument('buttons', nargs='*')
    p.add_argument('--hold', type=float, default=.35)
    a = p.parse_args()
    assert a.name.replace('_', '').isalnum() and .05 <= a.hold <= 2
    names = ['circle', 'cross', 'up', 'down', 'left', 'right', 'start', 'select', 'ltrigger', 'rtrigger', 'triangle', 'square']
    assert set(a.buttons) <= set(names)
    request = client(19444)
    session = json.loads((ROOT/'work/scratch'/a.case/'session.json').read_text('utf-8-sig'))
    assert session['port'] == 19444 and session['fresh_boot']
    cpu = request('cpu.status')
    if cpu['stepping']:
        addresses = [f['address'] for f in request('hle.func.list')['functions'] if f['name'] == 'zz_sceDisplaySetFrameBuf']
        assert cpu['pc'] in addresses
        request('cpu.resume')
    request('input.buttons.send', buttons={n: False for n in names})
    time.sleep(1)
    for n in a.buttons:
        request('input.buttons.send', buttons={n: True})
        time.sleep(a.hold)
        request('input.buttons.send', buttons={n: False})
        time.sleep(1)
    time.sleep(2)
    import capture_framebuffer
    capture_framebuffer.request = request
    png, report = capture_framebuffer.capture(hold=True)
    report.update(buttons=a.buttons, hold_seconds=a.hold, session=session, input_method='explicit hold/release')
    dest = ROOT/'work/ui/ui_0.1.79/reviewed'/a.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    assert not dest.with_suffix('.png').exists()
    dest.with_suffix('.png').write_bytes(png)
    dest.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
    print(dest.with_suffix('.png'), flush=True)


if __name__ == '__main__':
    main()

