"""Coalesce unused adjacent eight-cell strips for longer Learn Skills names."""
from report_ui_061 import add
from font_patch import REG

def emit(a):
 a.label('learn_bind');a.i(9,'sp','sp',-32)
 for reg,o in [('ra',28),('a0',16),('a1',20),('a2',24)]:a.i(43,reg,'sp',o)
 a.move('a0','a1');a.jump(0x1e4ac8);a.i(11,'t0','v0',9);a.branch(5,'t0','zero','learn_ready');a.i(11,'t0','v0',17);a.branch(4,'t0','zero','learn_ready');a.move('t7','v0')
 a.i(35,'t0','sp',16);a.i(35,'t0','t0',0xc0);a.branch(4,'t0','zero','learn_pool');a.i(37,'t1','t0',4);a.emit(REG['t1']<<21|REG['t7']<<16|REG['t1']<<11|0x2b);a.branch(4,'t1','zero','learn_ready')
 a.label('learn_pool');a.relocs.append((len(a.words)*4,0x305));a.i(15,'t0','zero',0x23);a.relocs.append((len(a.words)*4,0x306));a.i(35,'t0','t0',0xa340);a.i(9,'t0','t0',0xcac);a.i(35,'t2','t0',0x1c);a.i(35,'t3','t0',0x20);a.move('t4','t2');a.move('t5','t3')
 a.label('learn_free');a.branch(4,'t5','zero','learn_merge_start');a.i(37,'t6','t4',6);a.branch(5,'t6','zero','learn_free_next');a.i(37,'t6','t4',4);a.emit(REG['t6']<<21|REG['t7']<<16|REG['t6']<<11|0x2b);a.branch(4,'t6','zero','learn_ready')
 a.label('learn_free_next');a.i(9,'t4','t4',8);a.i(9,'t5','t5',-1);a.branch(4,'zero','zero','learn_free')
 a.label('learn_merge_start');a.move('t4','t2');a.i(9,'t5','t3',-1)
 a.label('learn_merge');a.branch(4,'t5','zero','learn_ready');a.i(37,'t6','t4',6);a.branch(5,'t6','zero','learn_merge_next');a.i(37,'t6','t4',14);a.branch(5,'t6','zero','learn_merge_next');a.i(37,'t6','t4',4);a.i(9,'t7','zero',8);a.branch(5,'t6','t7','learn_merge_next');a.i(37,'t6','t4',12);a.branch(5,'t6','t7','learn_merge_next');a.i(37,'t6','t4',2);a.i(37,'t7','t4',10);a.branch(5,'t6','t7','learn_merge_next');a.i(37,'t6','t4',0);a.i(9,'t6','t6',128);a.i(37,'t7','t4',8);a.branch(5,'t6','t7','learn_merge_next')
 a.i(9,'t6','zero',16);a.i(41,'t6','t4',4);a.i(41,'zero','t4',12);a.i(9,'t6','zero',1);a.i(41,'t6','t4',14);a.branch(4,'zero','zero','learn_ready')
 a.label('learn_merge_next');a.i(9,'t4','t4',8);a.i(9,'t5','t5',-1);a.branch(4,'zero','zero','learn_merge')
 a.label('learn_ready')
 for reg,o in [('a0',16),('a1',20),('a2',24),('ra',28)]:a.i(35,reg,'sp',o)
 a.i(9,'sp','sp',32);a.jump(0x347b5c,link=False)
