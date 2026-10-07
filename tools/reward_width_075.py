"""Measure reward-name spacing in native 16-pixel units for the VWF glyphs."""
from font_patch import REG
def emit(a):
 a.label('reward_cells');a.i(9,'sp','sp',-48)
 for reg,off in [('s0',16),('s1',20),('s2',24),('ra',44)]:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.move('s1','zero');a.i(9,'s2','zero',32)
 a.branch(4,'s0','zero','reward_done')
 a.label('reward_loop');a.i(37,'a0','s0',0);a.branch(4,'a0','zero','reward_done');a.jump(0x32e380)
 a.emit(REG['s1']<<21|REG['v0']<<16|REG['s1']<<11|0x21)
 a.i(9,'s0','s0',2);a.i(9,'s2','s2',-1);a.branch(5,'s2','zero','reward_loop')
 a.label('reward_done');a.i(9,'v0','s1',15);a.emit(REG['v0']<<16|REG['v0']<<11|4<<6|2)
 for reg,off in [('s0',16),('s1',20),('s2',24),('ra',44)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',48);a.ret()
