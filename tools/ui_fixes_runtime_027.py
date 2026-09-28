"""Isolated 0.1.27 runtime QA connection. Port 19382 only."""
from ui_fixes_runtime_026 import request,press
from sn3_archive import ROOT
import capture_framebuffer,json

def capture(name):
 capture_framebuffer.request=request;png,report=capture_framebuffer.capture(hold=True)
 folder=ROOT/'work/ui/ui_fixes_0.1.27/runtime';folder.mkdir(parents=True,exist_ok=True)
 path=folder/(name+'.png');path.write_bytes(png);path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
 return path
