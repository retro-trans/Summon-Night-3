"""Proportional positions for the fixed-capacity per-glyph menu help renderer.

Uses native glyphs unchanged. Latin advance is metric*7/8, the original glyph
scale. Japanese/control cells retain the original 13-pixel advance.
"""
from font_patch import REG
from menu_code_020 import append
LOOKUP=0x32e380

def emit(a):
    def r(fn,rd,rs,rt='zero'):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
    def shift(rd,rt,n):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6)
    a.label('help_position');a.i(9,'sp','sp',-64)
    for reg,off in [('ra',60),('s0',32),('s1',36),('s2',40),('s3',44),('a0',48),('a2',52)]:a.i(43,reg,'sp',off)
    a.i(9,'s0','s4',0x4c);a.move('s1','s3');a.move('s2','zero')
    a.label('prefix');a.branch(4,'s1','zero','current')
    a.i(37,'a0','s0',0);a.jump(LOOKUP)
    # Unknown lookup is 16/0/16; all supported Latin ink widths are <16.
    a.i(9,'t3','zero',16);a.branch(4,'a0','t3','fallback')
    shift('t3','v0',3);r(0x23,'t3','t3','v0');a.branch(4,'zero','zero','accumulate')
    a.label('fallback');a.i(9,'t3','zero',104)
    a.label('accumulate');r(0x21,'s2','s2','t3');a.i(9,'s0','s0',2);a.i(9,'s1','s1',-1)
    a.branch(4,'zero','zero','prefix')
    a.label('current');a.i(37,'a0','s0',0);a.jump(LOOKUP)
    a.i(9,'t3','zero',16);a.branch(4,'a0','t3','position')
    a.i(9,'t3','zero',3);r(0x23,'t3','t3','v1');shift('t4','t3',3);r(0x23,'t3','t4','t3');r(0x21,'s2','s2','t3')
    a.label('position');a.int_to_float('s2',12)
    # 0.125f. Original f15 holds the help line's X anchor.
    a.i(15,'t3','zero',0x3e00);a.emit(17<<26|4<<21|REG['t3']<<16|2<<11)
    a.emit(17<<26|16<<21|2<<16|12<<11|12<<6|2);a.add_float(12,15,12)
    a.i(35,'a0','sp',48);a.i(35,'t9','sp',52)
    a.emit(REG['t9']<<21|REG['ra']<<11|9);a.emit(0) # native virtual position callback
    for reg,off in [('s0',32),('s1',36),('s2',40),('s3',44),('ra',60)]:a.i(35,reg,'sp',off)
    a.i(9,'sp','sp',64);a.ret()

def prepare(data):
    return append(data,emit,{0x642c0:('help_position',REG['a2']<<21|REG['ra']<<11|9)})
