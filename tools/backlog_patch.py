"""Pack Latin ink in the backlog's existing native texture strips; preview first."""
import argparse, json, struct, hashlib
from pathlib import Path
import font_patch
from font_patch import Assembler, REG
from sn3_archive import ROOT

BASE = ROOT/'work/output/0.1.8/EBOOT.elf'
SOURCE_SHA = 'ca2a32ade1e11a7d456128bd00d05fc2b777220ffec6f4a2550052300b1f2749'

def compile_code(base):
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
    a.label('bind');a.i(9,'sp','sp',-2240)
    saved=[(reg,2176+i*4) for i,reg in enumerate(['s0','s1','s2','s3','s4','s5','s6','s7','fp','ra'])]
    for reg,off in saved:a.i(43,reg,'sp',off)
    a.move('s0','a0');a.move('s2','a1');a.move('s3','a2')
    a.jump(0x1cbe48);a.i(43,'v0','sp',2220)
    a.i(35,'s1','s0',0xc0);a.branch(4,'s1','zero','bind_done')
    a.branch(4,'s3','zero','bind_done');a.i(11,'t0','s3',17)
    a.branch(4,'t0','zero','bind_done')
    address('t0',0x22a340);a.i(35,'s4','t0',0);a.i(9,'s4','s4',0xcac)
    a.move('a0','s4');a.move('a1','s1');a.move('a2','s2');a.move('a3','s3')
    a.jump(0x1d8e34)
    # Mark the populated cache ready. Invalidate its code comparison cells so
    # the next owner always repaints original full-cell glyphs on cache reuse.
    a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x100);a.i(43,'t0','s0',0)
    a.i(43,'s2','sp',2080);a.i(43,'s3','sp',2084)
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
    a.label('character');a.i(35,'t0','sp',2080);shift('t1','s0',1);r(0x21,'t0','t0','t1')
    a.i(37,'a0','t0',0);a.jump('lookup')
    # lookup: v0 advance, v1 source left edge, a0 ink width; fallback 16/0/16.
    a.i(43,'v0','sp',2088);a.move('s2','a0');a.move('s3','v1')
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
    a.label('next_character');a.i(35,'t0','sp',2088);r(0x21,'s1','s1','t0')
    a.i(9,'s0','s0',1);a.i(35,'t0','sp',2084);a.branch(5,'s0','t0','character')
    a.label('bind_done');a.i(35,'v0','sp',2220)
    for reg,off in saved:a.i(35,reg,'sp',off)
    a.i(9,'sp','sp',2240);a.ret()

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

def patch(data):
    assert hashlib.sha256(data).hexdigest()==SOURCE_SHA
    phoff,shoff=struct.unpack_from('<II',data,28)
    ps,pn,ss,sn=struct.unpack_from('<4H',data,42);assert(ps,pn,ss)==(32,4,40)
    ph=[list(struct.unpack_from('<8I',data,phoff+i*32)) for i in range(pn)]
    sh=[list(struct.unpack_from('<10I',data,shoff+i*40)) for i in range(sn)]
    seg=ph[3];old_payload=data[seg[1]:seg[1]+seg[4]]
    extra_base=seg[2]+len(old_payload);code,labels,relocs=compile_code(extra_base)
    rel=ph[2];old_reloc=data[rel[1]:rel[1]+rel[4]]
    records=list(struct.iter_unpack('<II',old_reloc));new_records=[]
    hooks={0xfe93c:('bind',3<<26|0x1cbe48>>2),0xfeba0:('bind',3<<26|0x1cbe48>>2),
           0xfe9d8:('advance',0x461e6302),0xfec44:('advance',0x461e6302)}
    out=bytearray(data)
    for va,(label,expected) in hooks.items():
        actual=struct.unpack_from('<I',data,va+0xc0)[0]
        assert actual==expected,(hex(va),hex(actual),hex(expected))
        struct.pack_into('<I',out,va+0xc0,3<<26|(extra_base+labels[label])>>2)
        if (va,4) not in records:new_records.append((va,4))
    new_records += [(len(old_payload)+o,info) for o,info in relocs]
    # Move the complete added load segment and relocation table to appended
    # storage. Existing segment-relative addresses and prior code stay intact.
    def pad(n):out.extend(bytes((-len(out))%n))
    pad(64);new_seg_offset=len(out);out.extend(old_payload+code)
    pad(16);new_rel_offset=len(out);out.extend(old_reloc)
    out.extend(b''.join(struct.pack('<II',*r) for r in new_records))
    for s in sh:
        if s[1]==0x700000a0:s[4]+=new_rel_offset-rel[1]
        if s[3]==seg[2] and s[4]==seg[1]:s[4]=new_seg_offset;s[5]=len(old_payload)+len(code)
    code_section=next(i for i,s in enumerate(sh) if s[3]==seg[2] and s[4]==new_seg_offset)
    sh.append([0,0x700000a0,0,0,new_rel_offset+len(old_reloc),len(new_records)*8,52,code_section,4,8])
    seg[1]=new_seg_offset;seg[4]=seg[5]=len(old_payload)+len(code)
    rel[1]=new_rel_offset;rel[4]=len(old_reloc)+len(new_records)*8
    pad(16);new_shoff=len(out);out.extend(b''.join(struct.pack('<10I',*s) for s in sh))
    for i,p in enumerate(ph):struct.pack_into('<8I',out,phoff+i*32,*p)
    struct.pack_into('<I',out,32,new_shoff);struct.pack_into('<H',out,48,len(sh))
    report=dict(profile='backlog_native_strip_ink_spacing_v1',source_elf_sha256=SOURCE_SHA,
        patched_elf_sha256=hashlib.sha256(out).hexdigest(),code_address=hex(extra_base),
        code_bytes=len(code),hooks={hex(k):v[0] for k,v in hooks.items()},labels=labels,
        new_relocations=new_records,added_segment_file_offset=new_seg_offset,added_segment_bytes=seg[4],
        extra_relocation_records=[r for r in records+new_records if r[1]>>8&255==3],
        original_glyph_pixels_preserved=True,unmapped_advance=16,maximum_strip_cells=16,
        source_assets_unchanged=True)
    return bytes(out),report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'work/scratch/backlog_patch_0.1.9');args=p.parse_args()
    data,report=patch(BASE.read_bytes());print(json.dumps(dict(mode='write' if args.write else 'dry run',output=str(args.output),report=report),indent=2))
    if args.write:
        assert ROOT in args.output.resolve().parents;args.output.mkdir()
        (args.output/'EBOOT.elf').write_bytes(data)
        (args.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
