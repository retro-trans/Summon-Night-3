"""Gallery QA; isolated PPSSPP port 19382 with copied in-game saves."""
from ui_fixes_runtime_026 import request,press
from sn3_archive import ROOT
import capture_framebuffer,json

def capture(name):
    capture_framebuffer.request=request
    png,report=capture_framebuffer.capture(hold=True)
    folder=ROOT/'work/ui/gallery_0.1.36/runtime';folder.mkdir(parents=True,exist_ok=True)
    path=folder/(name+'.png');path.write_bytes(png)
    path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    return path

if __name__=='__main__':
    import sys
    if sys.argv[1]=='capture':print(capture(sys.argv[2]))
    elif sys.argv[1]=='press':
        for button in sys.argv[2:]:press(button)
    else:print(request('game.status'))
