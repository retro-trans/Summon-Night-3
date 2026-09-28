"""Execute backlog MIPS hooks on guarded font strips, including cache reuse."""
import argparse, json, struct
from backlog_patch import patch, BASE
from font_patch import REG, CODE_VA
from font_metrics import collect
from verify_font_patch import Machine, signed
from sn3_archive import ROOT

class CPU(Machine):
    def run(self,entry):
        pc=self.base+CODE_VA+entry;stop=0x0bad0000;self.set('ra',stop);lo=0
        for step in range(500000):
            if pc==stop:return step
            if pc in self.native_handlers:
                returns=self.native_handlers[pc](self);pc=self.reg[31]
                for r in list(range(2,16))+[24,25]:self.reg[r]=0xcafe0000+r
                for k,v in returns.items():self.set(k,v)
                continue
            w=self.read(pc,4);op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
            imm=signed(w&65535,16);n=pc+4;branch=False
            if op==0:
                x,y=self.reg[rs],self.reg[rt];sa=w>>6&31
                if fn==0:self.reg[rd]=y<<sa
                elif fn==2:self.reg[rd]=y>>sa
                elif fn==4:self.reg[rd]=y<<(x&31)
                elif fn==6:self.reg[rd]=y>>(x&31)
                elif fn==8:n=x;branch=True
                elif fn==0x21:self.reg[rd]=x+y
                elif fn==0x23:self.reg[rd]=x-y
                elif fn==0x25:self.reg[rd]=x|y
                elif fn==0x18:lo=x*y&0xffffffff
                elif fn==0x12:self.reg[rd]=lo
                else:raise AssertionError(hex(w))
            elif op in (2,3):
                if op==3:self.reg[31]=pc+8
                n=(pc+4)&0xf0000000|(w&0x3ffffff)<<2;branch=True
            elif op in (4,5):
                cond=(self.reg[rs]==self.reg[rt])==(op==4);n=pc+4+imm*4 if cond else pc+8;branch=True
            elif op==9:self.reg[rt]=self.reg[rs]+imm
            elif op==11:self.reg[rt]=int(self.reg[rs]<(imm&0xffffffff))
            elif op==12:self.reg[rt]=self.reg[rs]&(w&65535)
            elif op==13:self.reg[rt]=self.reg[rs]|(w&65535)
            elif op==15:self.reg[rt]=(w&65535)<<16
            elif op in (35,36,37):self.reg[rt]=self.read(self.reg[rs]+imm,{35:4,36:1,37:2}[op])
            elif op in (40,41,43):
                size={40:1,41:2,43:4}[op];self.store(self.reg[rs]+imm,(self.reg[rt]&((1<<(size*8))-1)).to_bytes(size,'little'))
            elif op==17 and rs==4:self.fp[rd]=self.reg[rt]
            elif op==17 and rs==20 and fn==32:
                self.fp[w>>6&31]=int.from_bytes(struct.pack('<f',signed(self.fp[rd])),'little')
            else:raise AssertionError((hex(pc),hex(w)))
            if branch:assert self.read(pc+4,4)==0
            self.reg=[r&0xffffffff for r in self.reg];self.reg[0]=0;pc=n
        raise AssertionError('Hook instruction budget exceeded')

def verify():
    data,report=patch(BASE.read_bytes());metrics,font=collect();chars=metrics['characters']
    samples=list(chars)+['Still, it all','WWWWWWWWWWWWWWWW','iiiiiiiiiiiiiiii','A A A A A A A A ',
                         'Rexx','?!.;,','mix'+chr(0x3042)+'W','                ']
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
            cpu=CPU(data,report,base);stack=0x09f00000;obj=0x09000000;entry=obj+0x1000;src=obj+0x2000
            manager=0x09100000;wrapper=manager+0xcac;bitmap=0x09200000;cache=0x09300000
            cpu.store(stack-2400,b'\x79'*2600);cpu.store(obj,bytes(0xe0));cpu.store(src,text+b'\0\0')
            cpu.store(entry,struct.pack('<4H',32,16,count,1));cpu.store(base+0x22a340,struct.pack('<I',manager))
            cpu.store(wrapper,bytes(64));cpu.store(wrapper+4,struct.pack('<H',512));cpu.store(wrapper+8,struct.pack('<H',32))
            cpu.store(wrapper+0x24,struct.pack('<II',cache,bitmap));cpu.store(cache,b'\xaa'*2048)
            cpu.store(bitmap,b'\xb6'*(256*64))
            def bind(m):
                assert m.reg[4:8]==[obj,src,count,1]
                m.store(obj+0xc0,struct.pack('<I',entry));return {'v0':0x12345}
            def populate(m):
                assert m.reg[4:8]==[wrapper,entry,src,count]
                for j,glyph in enumerate(glyphs):
                    for y in range(16):m.store(bitmap+(16+y)*256+16+j*8,glyph[y*8:y*8+8])
                m.store(cache+(32+2)*2,text);return {}
            cpu.native_handlers={base+0x1cbe48:bind,base+0x1d8e34:populate}
            for r in range(16,31):cpu.reg[r]=0x34560000+r
            cpu.set('sp',stack);saved=cpu.reg[16:31].copy()
            for reg,val in [('a0',obj),('a1',src),('a2',count),('a3',1)]:cpu.set(reg,val)
            off=int(report['code_address'],16)-CODE_VA
            maximum=max(maximum,cpu.run(off+report['labels']['bind']))
            assert cpu.reg[16:24]+cpu.reg[26:31]==saved[:8]+saved[10:] and cpu.reg[2]==0x12345
            assert cpu.bytes(stack-2400,160)==b'\x79'*160 and cpu.bytes(stack,200)==b'\x79'*200
            assert cpu.read(obj,4)&256 and cpu.bytes(cache+68,count*2)==bytes(count*2)
            target=bytearray(b'\xb6'*(256*64))
            for y in range(16):target[(16+y)*256+16:(16+y)*256+16+count*8]=bytes(count*8)
            for x,left,width,glyph in expected:
                for y in range(16):
                    for p in range(width):
                        val=glyph[y*8+(left+p)//2]>>(4*((left+p)%2))&15
                        target[(16+y)*256+16+(x+p)//2]|=val<<(4*((x+p)%2))
            assert cpu.bytes(bitmap,len(target))==target,(sample,'pixel mismatch or out-of-strip write')
            cpu.set('s0',count);cpu.set('s5',src+count*2)
            before=cpu.reg.copy();maximum=max(maximum,cpu.run(off+report['labels']['advance']))
            assert cpu.reg[:31]==before[:31]
            assert struct.unpack('<f',struct.pack('<I',cpu.fp[12]))[0]==adv
            total+=1
    return dict(cases=total,load_bases=2,maximum_instructions=maximum,
        coverage=['All 93 supported Latin glyphs','16-cell strips','Spaces and punctuation','Mixed Japanese fallback',
                  'Native pixels and transparent tail','Cache invalidation','Stack and callee-saved registers',
                  'Chunk advance and volatile registers','No writes outside allocated texture strips'],
        patched_elf_sha256=report['patched_elf_sha256'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    result=verify();print(json.dumps(dict(mode='write' if a.write else 'dry run',**result),indent=2))
    if a.write:
        target=ROOT/'work/ui/backlog_0.1.9/abi_validation.json';assert not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
