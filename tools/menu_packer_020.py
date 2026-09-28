"""Extended native strip packer, optionally center ink in its original rectangle."""
import json,struct
import font_patch
from font_patch import Assembler,REG
from sn3_archive import ROOT
def compile_code(base,center=False):
    metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
    entries=[]
    for m in metrics.values():
        b=m['ink_bounds_inclusive']
        entries.append((int.from_bytes(bytes.fromhex(m['cp932_hex']),'little'),
                        m['proposed_advance_pixels'],b[0] if b else 0,b[2]-b[0]+1 if b else 0))
    table=b''.join(struct.pack('<HBBB3x',*r) for r in sorted(entries))
    a=Assembler()
    def r(fn,rd,rs,rt='zero'):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
    def shift(rd,rt,n,right=False):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6|(2 if right else 0))
    def address(reg,va):
        a.relocs.append((len(a.words)*4,0x305));a.i(15,reg,'zero',(va+0x8000)>>16)
        a.relocs.append((len(a.words)*4,0x306));a.i(9,reg,reg,va&65535)

    # Only two backlog calls enter this wrapper. All other font users keep the
    # stock cache population path, and no object layout or pool size changes.
    a.label('bind');a.i(9,'sp','sp',-4288)
    saved=[(reg,4224+i*4) for i,reg in enumerate(['s0','s1','s2','s3','s4','s5','s6','s7','fp','ra'])]
    for reg,off in saved:a.i(43,reg,'sp',off)
    a.move('s0','a0');a.move('s2','a1');a.move('s3','a2')
    a.jump(0x1cbe48);a.i(43,'v0','sp',4268)
    a.i(35,'s1','s0',0xc0);a.branch(4,'s1','zero','bind_done')
    a.branch(4,'s3','zero','bind_done');a.i(11,'t0','s3',33)
    a.branch(4,'t0','zero','bind_done')
    address('t0',0x22a340);a.i(35,'s4','t0',0);a.i(9,'s4','s4',0xcac)
    a.move('a0','s4');a.move('a1','s1');a.move('a2','s2');a.move('a3','s3')
    a.jump(0x1d8e34)
    # Mark the populated cache ready. Invalidate its code comparison cells so
    # the next owner always repaints original full-cell glyphs on cache reuse.
    a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x100);a.i(43,'t0','s0',0)
    a.i(43,'s2','sp',4128);a.i(43,'s3','sp',4132)
    a.i(37,'t0','s1',2);shift('t0','t0',4,True)
    a.i(37,'t1','s4',8);r(0x18,'zero','t0','t1');a.emit(REG['t0']<<11|0x12)
    a.i(37,'t1','s1',0);shift('t1','t1',4,True);r(0x21,'t0','t0','t1');shift('t0','t0',1)
    a.i(35,'t1','s4',0x24);r(0x21,'t0','t0','t1');a.move('t1','s3')
    a.label('invalidate');a.i(41,'zero','t0',0);a.i(9,'t0','t0',2);a.i(9,'t1','t1',-1)
    a.branch(5,'t1','zero','invalidate')
    a.i(37,'s6','s4',4);shift('s6','s6',1,True)
    a.i(35,'s5','s4',0x28);a.i(37,'t0','s1',2)
    r(0x18,'zero','t0','s6');a.emit(REG['t0']<<11|0x12);r(0x21,'s5','s5','t0')
    a.i(37,'t0','s1',0);shift('t0','t0',1,True);r(0x21,'s5','s5','t0')
    shift('s7','s3',3);a.move('t0','s5');a.move('t1','sp');a.i(9,'t2','zero',16)
    # Scratch holds the untouched strip: at most 16 cells * 128 bytes.
    a.label('copy_row');a.move('t3','t0');a.move('t4','s7')
    a.label('copy_byte');a.i(36,'t5','t3',0);a.i(40,'t5','t1',0);a.i(40,'zero','t3',0)
    a.i(9,'t3','t3',1);a.i(9,'t1','t1',1);a.i(9,'t4','t4',-1)
    a.branch(5,'t4','zero','copy_byte');r(0x21,'t0','t0','s6');a.i(9,'t2','t2',-1)
    a.branch(5,'t2','zero','copy_row')
    a.move('s0','zero');a.move('s1','zero')
    if center:
        a.i(35,'a2','sp',4128);a.i(35,'a3','sp',4132);a.move('t8','zero')
        a.label('center_measure');a.i(37,'a0','a2',0);a.jump('lookup');r(0x21,'t8','t8','v0')
        a.i(9,'a2','a2',2);a.i(9,'a3','a3',-1);a.branch(5,'a3','zero','center_measure')
        r(0x23,'t8','t8','v0');r(0x21,'t8','t8','a0')
        shift('s1','s3',4);r(0x23,'s1','s1','t8');shift('s1','s1',1,True)
    a.label('character');a.i(35,'t0','sp',4128);shift('t1','s0',1);r(0x21,'t0','t0','t1')
    a.i(37,'a0','t0',0);a.jump('lookup')
    # lookup: v0 advance, v1 source left edge, a0 ink width; fallback 16/0/16.
    a.i(43,'v0','sp',4136);a.move('s2','a0');a.move('s3','v1')
    a.branch(4,'s2','zero','next_character')
    shift('s4','s0',3);r(0x21,'s4','sp','s4');a.move('fp','s5');a.i(9,'t9','zero',16)
    a.label('pixel_row');a.move('t0','zero')
    a.label('pixel');r(0x21,'t1','s3','t0');shift('t2','t1',1,True);r(0x21,'t2','s4','t2')
    a.i(36,'t3','t2',0);a.i(12,'t1','t1',1);shift('t1','t1',2)
    r(6,'t3','t1','t3');a.i(12,'t3','t3',15)
    r(0x21,'t1','s1','t0');shift('t2','t1',1,True);r(0x21,'t2','fp','t2')
    a.i(12,'t1','t1',1);shift('t1','t1',2);r(4,'t3','t1','t3')
    a.i(36,'t4','t2',0);r(0x25,'t3','t3','t4');a.i(40,'t3','t2',0)
    a.i(9,'t0','t0',1);a.branch(5,'t0','s2','pixel')
    r(0x21,'s4','s4','s7');r(0x21,'fp','fp','s6');a.i(9,'t9','t9',-1)
    a.branch(5,'t9','zero','pixel_row')
    a.label('next_character');a.i(35,'t0','sp',4136);r(0x21,'s1','s1','t0')
    a.i(9,'s0','s0',1);a.i(35,'t0','sp',4132);a.branch(5,'s0','t0','character')
    a.label('bind_done');a.i(35,'v0','sp',4268)
    for reg,off in saved:a.i(35,reg,'sp',off)
    a.i(9,'sp','sp',4288);a.ret()

    # Called instead of the fixed count*16 multiply after each text strip.
    # The original delay instruction still decrements the remaining count.
    a.label('advance');a.i(9,'sp','sp',-96)
    volatile=['v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9','ra']
    for i,reg in enumerate(volatile):a.i(43,reg,'sp',i*4)
    shift('a2','s0',1);r(0x23,'a2','s5','a2');a.move('a3','s0');a.move('t8','zero')
    a.label('advance_loop');a.i(37,'a0','a2',0);a.jump('lookup');r(0x21,'t8','t8','v0')
    a.i(9,'a2','a2',2);a.i(9,'a3','a3',-1);a.branch(5,'a3','zero','advance_loop')
    a.int_to_float('t8',12)
    for i,reg in enumerate(volatile):a.i(35,reg,'sp',i*4)
    a.i(9,'sp','sp',96);a.ret()
    a.label('lookup');a.table_address('t0');a.i(9,'t1','zero',len(entries))
    a.label('lookup_loop');a.i(37,'t2','t0',0);a.branch(4,'t2','a0','found')
    a.i(9,'t0','t0',8);a.i(9,'t1','t1',-1);a.branch(5,'t1','zero','lookup_loop')
    a.i(9,'v0','zero',16);a.move('v1','zero');a.i(9,'a0','zero',16);a.ret()
    a.label('found');a.i(36,'v0','t0',2);a.i(36,'v1','t0',3);a.i(36,'a0','t0',4);a.ret()
    old=font_patch.CODE_VA
    try:
        font_patch.CODE_VA=base;code=a.finish(table)
    finally:font_patch.CODE_VA=old
    return code,a.labels,a.relocs
