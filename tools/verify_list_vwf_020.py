"""Execute the 32-cell ink packer and saved-name lookup on guarded native strips."""
import json,struct
from menu_release_020 import prepare_elf
from verify_menu_vwf_020 import CPU
from font_patch import REG,CODE_VA
from font_metrics import collect
from list_vwf_020 import name_pairs
def verify(center=False):
    data,tr=prepare_elf();report=tr['list_vwf'];metrics,font=collect();chars=metrics['characters']
    samples=list(chars)+['Still, it all','WWWWWWWWWWWWWWWW','iiiiiiiiiiiiiiii','A A A A A A A A ',
                         'Rexx','?!.;,','mix'+chr(0x3042)+'W','                ','W'*32,'i'*32,'Large-drill land developer.','Built for long polar work.']
    total=0;maximum=0
    for base in (0x08804000,0x0890c000):
        for sample in samples:
            codes=[];glyphs=[];expected=[];adv=0
            for c in sample:
                m=chars.get(c);code=bytes.fromhex(m['cp932_hex']) if m else c.encode('cp932')
                glyph=font[m['font_byte_offset']:m['font_byte_offset']+128] if m else bytes(range(128))
                bounds=m['ink_bounds_inclusive'] if m else [0,0,15,15]
                width=bounds[2]-bounds[0]+1 if bounds else 0;left=bounds[0] if bounds else 0
                advance=m['proposed_advance_pixels'] if m else 16
                codes.append(code);glyphs.append(glyph);expected.append((adv,left,width,glyph));adv+=advance
            count=len(codes);text=b''.join(codes)
            if center:
                shift=(count*16-expected[-1][0]-expected[-1][2])//2
                expected=[(x+shift,left,width,glyph) for x,left,width,glyph in expected]
            cpu=CPU(data,report,base);stack=0x09f00000;obj=0x09000000;entry=obj+0x1000;src=obj+0x2000
            manager=0x09100000;wrapper=manager+0xcac;bitmap=0x09200000;cache=0x09300000
            cpu.store(stack-4600,b'\x79'*4800);cpu.store(obj,bytes(0xe0));cpu.store(src,text+b'\0\0')
            cpu.store(entry,struct.pack('<4H',0,16,count,1));cpu.store(base+0x22a340,struct.pack('<I',manager))
            cpu.store(wrapper,bytes(64));cpu.store(wrapper+4,struct.pack('<H',512));cpu.store(wrapper+8,struct.pack('<H',32))
            cpu.store(wrapper+0x24,struct.pack('<II',cache,bitmap));cpu.store(cache,b'\xaa'*2048)
            cpu.store(bitmap,b'\xb6'*(256*64))
            def bind(m):
                assert m.reg[4:8]==[obj,src,count,1]
                m.store(obj+0xc0,struct.pack('<I',entry));return {'v0':0x12345}
            def populate(m):
                assert m.reg[4:8]==[wrapper,entry,src,count]
                for j,glyph in enumerate(glyphs):
                    for y in range(16):m.store(bitmap+(16+y)*256+j*8,glyph[y*8:y*8+8])
                m.store(cache+64,text);return {}
            cpu.native_handlers={base+0x1cbe48:bind,base+0x1d8e34:populate}
            for r in range(16,31):cpu.reg[r]=0x34560000+r
            cpu.set('sp',stack);saved=cpu.reg[16:31].copy()
            for reg,val in [('a0',obj),('a1',src),('a2',count),('a3',1)]:cpu.set(reg,val)
            off=int(report['code_address'],16)-CODE_VA
            maximum=max(maximum,cpu.run(off+report['labels']['center_bind' if center else 'bind']))
            assert cpu.reg[16:24]+cpu.reg[26:31]==saved[:8]+saved[10:] and cpu.reg[2]==0x12345
            assert cpu.bytes(stack-4600,160)==b'\x79'*160 and cpu.bytes(stack,200)==b'\x79'*200
            assert cpu.read(obj,4)&256 and cpu.bytes(cache+64,count*2)==bytes(count*2)
            target=bytearray(b'\xb6'*(256*64))
            for y in range(16):target[(16+y)*256:(16+y)*256+count*8]=bytes(count*8)
            for x,left,width,glyph in expected:
                for y in range(16):
                    for p in range(width):
                        val=glyph[y*8+(left+p)//2]>>(4*((left+p)%2))&15
                        target[(16+y)*256+(x+p)//2]|=val<<(4*((x+p)%2))
            assert cpu.bytes(bitmap,len(target))==target,(sample,'pixel mismatch or out-of-strip write')
            cpu.set('s0',count);cpu.set('s5',src+count*2)
            before=cpu.reg.copy();maximum=max(maximum,cpu.run(off+report['labels']['advance']))
            assert cpu.reg[:31]==before[:31]
            assert struct.unpack('<f',struct.pack('<I',cpu.fp[12]))[0]==adv
            total+=1
    return dict(cases=total,load_bases=2,maximum_instructions=maximum,
        coverage=['All 93 supported Latin glyphs','32-cell strips','Spaces and punctuation','Mixed Japanese fallback',
                  'Native pixels and transparent tail','Cache invalidation','Stack and callee-saved registers',
                  'Chunk advance and volatile registers','No writes outside allocated texture strips'],
        patched_elf_sha256=report['patched_elf_sha256'])

def names_verify():
    data,tr=prepare_elf();report=tr['list_vwf'];pairs,_,_=name_pairs();count=0
    samples=pairs+[(b'Custom',b'Custom'),('テスト'.encode('cp932'),'テスト'.encode('cp932')),('Ｄｒｉｔｏｌ'.encode('cp932'),'Ｄｒｉｔｏｌ'.encode('cp932'))]
    for base in (0x08804000,0x0890c000):
        for source,target in samples:
            c=CPU(data,report,base);src=0x09000000;c.store(src,source+b'\0\0');c.set('a0',src)
            c.run(int(report['code_address'],16)-CODE_VA+report['labels']['saved_name'])
            assert c.bytes(c.reg[2],len(target)+2)==target+b'\0\0'
            assert c.bytes(src,len(source)+2)==source+b'\0\0';count+=1
    return count
if __name__=='__main__':print(json.dumps(dict(packer=verify(),centered_packer=verify(True),name_lookup_cases=names_verify()),indent=2))
