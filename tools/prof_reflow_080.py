"""Bounded display-only deduplication/reflow of weapon-proficiency help."""
from font_patch import REG
from dialogue_encoding import encode_dialogue

def emit(a,prior):
 space=int.from_bytes(encode_dialogue(' ','')[0],'little')
 def sub(rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x23)
 a.label('prof_reflow');a.i(9,'t2','zero',11);a.branch(5,'a2','t2','prof_original');a.i(11,'t2','a3',0xbd1);a.branch(5,'t2','zero','prof_original');a.i(11,'t2','a3',0xbde);a.branch(4,'t2','zero','prof_original');a.branch(4,'a1','zero','prof_original')
 a.i(9,'sp','sp',-512)
 for reg,o in [('a0',400),('a1',404),('a2',408),('a3',412),('t0',416),('t1',420),('ra',424)]+[(f's{i}',432+i*4) for i in range(8)]:a.i(43,reg,'sp',o)
 # Build a <=56-cell flat copy. Consecutive identical rows are duplicate
 # native/master descriptions; compare complete rows, including punctuation.
 a.move('s4','a1');a.move('s5','sp');a.move('s2','zero');a.move('s3','zero');a.move('s6','zero');a.i(9,'s7','zero',256)
 a.label('prof_line');a.move('s0','s4');a.move('s1','zero')
 a.label('prof_scan');a.branch(4,'s7','zero','prof_abandon');a.i(37,'t2','s4',0);a.i(9,'s4','s4',2);a.i(9,'s7','s7',-1);a.branch(4,'t2','zero','prof_line_end');a.i(9,'s1','s1',1);a.i(11,'t2','s1',57);a.branch(4,'t2','zero','prof_abandon');a.branch(4,'zero','zero','prof_scan')
 a.label('prof_line_end');a.branch(4,'s1','zero','prof_flat_done');a.move('t3','s4');a.i(9,'t3','t3',-4);a.i(13,'t8','zero',space)
 a.label('prof_trim');a.i(37,'t2','t3',0);a.branch(5,'t2','t8','prof_trim_done');a.i(9,'s1','s1',-1);a.i(9,'t3','t3',-2);a.branch(5,'s1','zero','prof_trim');a.branch(4,'zero','zero','prof_line')
 a.label('prof_trim_done');a.branch(4,'s2','zero','prof_copy');a.emit(REG['s3']<<21|REG['s1']<<16|REG['t2']<<11|0x2b);a.branch(5,'t2','zero','prof_copy');sub('t2','s3','s1');a.emit(REG['t2']<<16|REG['t2']<<11|1<<6);a.emit(REG['s2']<<21|REG['t2']<<16|REG['t4']<<11|0x21);a.branch(4,'t2','zero','prof_compare_start');a.i(37,'t2','t4',-2);a.branch(5,'t2','t8','prof_copy')
 a.label('prof_compare_start');a.move('t3','s0');a.move('t5','s1')
 a.label('prof_compare');a.i(37,'t6','t3',0);a.i(37,'t7','t4',0);a.branch(5,'t6','t7','prof_copy');a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','prof_compare');a.branch(4,'zero','zero','prof_line')
 a.label('prof_copy');a.branch(4,'s6','zero','prof_no_space');a.i(13,'t2','zero',space);a.i(41,'t2','s5',0);a.i(9,'s5','s5',2);a.i(9,'s6','s6',1)
 a.label('prof_no_space');a.move('s2','s5');a.move('s3','s1');a.move('t3','s0');a.move('t5','s1')
 a.label('prof_copy_cell');a.i(37,'t2','t3',0);a.i(41,'t2','s5',0);a.i(9,'t3','t3',2);a.i(9,'s5','s5',2);a.i(9,'s6','s6',1);a.i(11,'t4','s6',57);a.branch(4,'t4','zero','prof_abandon');a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','prof_copy_cell');a.branch(4,'zero','zero','prof_line')
 a.label('prof_flat_done');a.i(9,'s4','sp',192);a.move('s5','zero');a.move('s7','zero');a.move('s0','sp')
 # Wrap at whole-word spaces. At most two spaces become row terminators.
 a.label('prof_wrap');a.branch(4,'s6','zero','prof_wrapped');a.i(9,'s7','s7',1);a.i(11,'t2','s7',4);a.branch(4,'t2','zero','prof_abandon');a.move('s1','s6');a.i(11,'t2','s6',28);a.branch(5,'t2','zero','prof_span_ready')
 a.move('t3','s0');a.move('s1','zero');a.i(9,'t5','zero',0);a.i(13,'t8','zero',space)
 a.label('prof_find_space');a.i(37,'t2','t3',0);a.branch(5,'t2','t8','prof_next_space');a.branch(4,'t5','zero','prof_next_space');a.move('s1','t5')
 a.label('prof_next_space');a.i(9,'t3','t3',2);a.i(9,'t5','t5',1);a.i(11,'t2','t5',28);a.branch(5,'t2','zero','prof_find_space');a.branch(4,'s1','zero','prof_abandon')
 a.label('prof_span_ready');add_count=REG['s5']<<21|REG['s1']<<16|REG['s5']<<11|0x21;a.emit(add_count);a.i(11,'t2','s5',55);a.branch(4,'t2','zero','prof_abandon');a.move('t5','s1')
 a.label('prof_out_copy');a.i(37,'t2','s0',0);a.i(41,'t2','s4',0);a.i(9,'s0','s0',2);a.i(9,'s4','s4',2);a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','prof_out_copy');a.i(41,'zero','s4',0);a.i(9,'s4','s4',2);sub('s6','s6','s1');a.branch(4,'s6','zero','prof_wrapped');a.i(9,'s0','s0',2);a.i(9,'s6','s6',-1);a.branch(4,'zero','zero','prof_wrap')
 a.label('prof_wrapped');a.i(41,'zero','s4',0);a.i(41,'zero','s4',2);a.i(9,'a1','sp',192);a.i(43,'a1','sp',404)
 a.label('prof_abandon')
 for reg,o in [('a0',400),('a1',404),('a2',408),('a3',412),('t0',416),('t1',420)]:a.i(35,reg,'sp',o)
 a.jump(prior)
 for reg,o in [(f's{i}',432+i*4) for i in range(8)]+[('ra',424)]:a.i(35,reg,'sp',o)
 a.i(9,'sp','sp',512);a.ret()
 a.label('prof_original');a.jump(prior,link=False)
