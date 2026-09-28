"""Prepare the 0.1.20 Type-menu VWF patch from the 0.1.19 executable."""
import argparse, hashlib, json, struct
from pathlib import Path

from sn3_archive import ROOT
from font_patch import Assembler, REG

BASE = ROOT / 'work/output/0.1.19/EBOOT.elf'
BASE_SHA256 = 'c0df15243ae2574788de2de868bd9345adfa5156c6512fbd39f75ec557e78a8d'
BACKLOG_BIND = 0x32e060
BACKLOG_LOOKUP = BACKLOG_BIND + 800
ORIGINAL_BIND = 0x1cbf60
ORIGINAL_TYPE_BIND = 0x1cbdec
COUNT_TEXT = 0x1e4ac8
FONT_SEGMENT = 3


def sha(data): return hashlib.sha256(data).hexdigest()


def emit_vwf(a):
    """Return two narrowly scoped wrappers.  `strip` changes f22 only."""
    a.label('strip')
    a.i(9, 'sp', 'sp', -64)
    for reg, off in [('ra', 60), ('s0', 32), ('s1', 36), ('s2', 40), ('s3', 44), ('s4', 48)]:
        a.i(43, reg, 'sp', off)
    # The caller passes a0=descriptor+0x30 and a1=owner style at +0x40.
    a.jump(ORIGINAL_BIND); a.emit(0)
    # In the 0x67390 caller s0 is owner and s3 is descriptor.  They are live
    # callee-saved registers; save them before using the native bind.
    a.i(35, 's1', 's0', 0x44)       # original encoded source
    a.i(36, 's2', 's3', 0)          # strip start cell index
    a.move('s4', 'zero')            # lookup clobbers t0–t2
    a.label('sum')
    a.branch(4, 's2', 'zero', 'sum_done')
    a.i(37, 'a0', 's1', 0)          # CP932 16-bit cell
    a.jump(BACKLOG_LOOKUP); a.i(9, 's1', 's1', 2)
    a.emit(REG['s4'] << 21 | REG['v0'] << 16 | REG['s4'] << 11 | 0x21)
    a.i(9, 's2', 's2', -1)
    a.branch(5, 's2', 'zero', 'sum'); a.emit(0)
    a.label('sum_done')
    a.int_to_float('s4', 22)
    a.fp_mem(49, 2, 0x20, 's0')
    a.emit(17 << 26 | 16 << 21 | 2 << 16 | 22 << 11 | 22 << 6 | 2) # mul.s f22,f22,f2
    for reg, off in [('s0', 32), ('s1', 36), ('s2', 40), ('s3', 44), ('s4', 48), ('ra', 60)]:
        a.i(35, reg, 'sp', off)
    a.i(9, 'sp', 'sp', 64); a.ret()

    a.label('type')
    a.i(9, 'sp', 'sp', -48)
    for reg, off in [('ra', 44), ('a0', 16), ('a1', 20), ('a2', 24)]: a.i(43, reg, 'sp', off)
    a.i(35, 'a0', 'sp', 20)                      # native count(text)
    a.jump(COUNT_TEXT); a.emit(0)
    a.i(35, 'a0', 'sp', 16); a.i(35, 'a1', 'sp', 20); a.i(35, 'a2', 'sp', 24)
    a.i(11, 't0', 'v0', 17)                     # t0=1 iff count <=16
    a.branch(4, 't0', 'zero', 'type_fallback')
    a.move('a3', 'a2')
    a.move('a2', 'v0')
    a.jump(BACKLOG_BIND); a.emit(0)
    a.branch(4, 'zero', 'zero', 'type_done'); a.emit(0)
    a.label('type_fallback')
    a.jump(ORIGINAL_TYPE_BIND); a.emit(0)
    a.label('type_done')
    for reg, off in [('a0', 16), ('a1', 20), ('a2', 24), ('ra', 44)]: a.i(35, reg, 'sp', off)
    a.i(9, 'sp', 'sp', 48); a.ret()
    return a


def prepare(data):
    from menu_code_020 import append
    hooks={0x63fb8:(BACKLOG_BIND,3<<26|0x1cbe48>>2),
           0x67390:('strip',3<<26|ORIGINAL_BIND>>2),
           0x1549f8:('type',3<<26|ORIGINAL_TYPE_BIND>>2)}
    out,report=append(data,emit_vwf,hooks)
    report['profile']='menu_vwf_020'
    return out,report


def main():
    p=argparse.ArgumentParser(); p.add_argument('--write',action='store_true'); p.add_argument('--output',type=Path,default=ROOT/'work/scratch/menu_vwf_020'); a=p.parse_args()
    elf,report=prepare(BASE.read_bytes()); print(json.dumps({'mode':'write' if a.write else 'dry-run','report':report},indent=2))
    if a.write:
        a.output.mkdir(); (a.output/'EBOOT.elf').write_bytes(elf); (a.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__': main()
