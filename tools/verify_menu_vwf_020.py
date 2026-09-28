"""Execute actual emitted menu/help MIPS against guarded memory and native ABI stubs."""
import json,struct
from pathlib import Path
from sn3_archive import ROOT
from font_patch import REG,CODE_VA
from verify_font_patch import Machine,signed
from menu_text_020 import prepare as text_prepare
from menu_vwf_020 import prepare as strip_prepare
from help_vwf_020 import prepare as help_prepare
from dialogue_encoding import encode_dialogue

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
                elif fn in (8,9):
                    if fn==9:self.reg[rd]=pc+8
                    n=x;branch=True
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
            elif op==49:self.fp[rt]=self.read(self.reg[rs]+imm,4)
            elif op==57:self.store(self.reg[rs]+imm,struct.pack('<I',self.fp[rt]))
            elif op==17 and rs==16 and fn in (0,2):
                x=struct.unpack('<f',struct.pack('<I',self.fp[rd]))[0]
                y=struct.unpack('<f',struct.pack('<I',self.fp[rt]))[0]
                self.fp[w>>6&31]=int.from_bytes(struct.pack('<f',x+y if fn==0 else x*y),'little')
            elif op==17 and rs==4:self.fp[rd]=self.reg[rt]
            elif op==17 and rs==20 and fn==32:
                self.fp[w>>6&31]=int.from_bytes(struct.pack('<f',signed(self.fp[rd])),'little')
            else:raise AssertionError((hex(pc),hex(w)))
            if branch:assert self.read(pc+4,4)==0
            self.reg=[r&0xffffffff for r in self.reg];self.reg[0]=0;pc=n
        raise AssertionError('Hook instruction budget exceeded')

def verify():
    data,tr=text_prepare();data,sr=strip_prepare(data);data,hr=help_prepare(data)
    metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
    assert max(m['ink_bounds_inclusive'][2]-m['ink_bounds_inclusive'][0]+1 if m['ink_bounds_inclusive'] else 0 for m in metrics.values())<16
    cases=0
    def fp(cpu,n):return struct.unpack('<f',struct.pack('<I',cpu.fp[n]))[0]
    def setfp(cpu,n,v):cpu.fp[n]=int.from_bytes(struct.pack('<f',v),'little')
    for base in (0x08804000,0x0890c000):
        def new():
            cpu=CPU(data,hr,base);cpu.store(0x09effe00,b'\x79'*1024)
            for r in range(16,31):cpu.reg[r]=0x34560000+r
            cpu.set('sp',0x09f00000)
            for n in range(32):setfp(cpu,n,n+.25)
            return cpu
        def check(cpu,before,fs,changed=()):
            assert cpu.reg[16:24]+cpu.reg[26:31]==before[:8]+before[10:]
            assert all(cpu.fp[n]==fs[n] for n in range(20,32) if n not in changed)
            assert cpu.bytes(0x09effe00,0x1a0)==b'\x79'*0x1a0
            assert cpu.bytes(0x09f00000,0x200)==b'\x79'*0x200
        entry=int(sr['code_address'],16)-CODE_VA
        for count in (0,4,16,17):
            c=new();obj=0x09000000;src=0x09010000;c.store(src,(encode_dialogue('A'*count,'')[0] if count else b'')+b'\0\0');calls=[]
            for reg,val in [('a0',obj),('a1',src),('a2',7)]:c.set(reg,val)
            before=c.reg[16:31].copy();fs=c.fp.copy()
            def length(m):
                assert m.reg[4]==src; m.store(m.reg[29],b'X'*16);return {'v0':count}
            def bind(m):
                assert m.reg[4:8]==[obj,src,count,7];calls.append('vwf');m.store(m.reg[29],b'Y'*16);return {'v0':123}
            def fallback(m):
                assert m.reg[4:7]==[obj,src,7];calls.append('native');return {'v0':456}
            c.native_handlers={base+0x1e4ac8:length,base+0x32e060:bind,base+0x1cbdec:fallback}
            c.run(entry+sr['labels']['type']);check(c,before,fs)
            assert calls==['vwf' if count<=16 else 'native'];cases+=1
        for text in ('Study Manual','Drill Hurricane','iiiiiiiiWWWWWWWW','A A!あA?W'*3):
            encoded=encode_dialogue(text,'')[0]
            for prefix in (0,min(8,len(text)),min(16,len(text))):
                for scale in (1.,.5,1.25):
                    c=new();owner=0x09000000;desc=0x09010000;src=0x09020000
                    c.store(owner,bytes(0x60));c.store(owner+0x44,struct.pack('<I',src));c.float_store(owner+0x20,scale)
                    c.store(desc,bytes([prefix])+bytes(0x10f));c.store(src,encoded+b'\0\0')
                    for reg,val in [('s0',owner),('s3',desc),('a0',desc+0x30),('a1',2)]:c.set(reg,val)
                    def style(m):assert m.reg[4:6]==[desc+0x30,2];return {}
                    c.native_handlers={base+0x1cbf60:style};before=c.reg[16:31].copy();fs=c.fp.copy()
                    c.run(entry+sr['labels']['strip']);check(c,before,fs,(22,))
                    expected=sum(metrics[x]['proposed_advance_pixels'] if x in metrics else 16 for x in text[:prefix])*scale
                    assert fp(c,22)==expected,(text,prefix,fp(c,22),expected);cases+=1
        helpentry=int(hr['code_address'],16)-CODE_VA+hr['labels']['help_position']
        for text in ('Large-drill land developer.','Built for long polar work.','日本語あ','A あ!W i'):
            encoded=encode_dialogue(text,'')[0]
            for index,ch in enumerate(text):
                c=new();row=0x09000000;obj=0x09010000;callback=base+0x1000
                c.store(row,bytes(0x4c)+encoded+b'\0\0')
                for reg,val in [('s4',row),('s3',index),('a0',obj),('a2',callback)]:c.set(reg,val)
                setfp(c,15,64.0);before=c.reg[16:31].copy();fs=c.fp.copy();positions=[]
                def position(m):
                    assert m.reg[4]==obj;assert m.fp[13:15]==fs[13:15]
                    positions.append(fp(m,12));return {}
                c.native_handlers={callback:position};c.run(helpentry);check(c,before,fs)
                expected=64+sum(metrics[x]['proposed_advance_pixels']*.875 if x in metrics else 13 for x in text[:index])
                if ch in metrics:
                    bounds=metrics[ch]['ink_bounds_inclusive'];left=bounds[0] if bounds else 0;expected+=(3-left)*.875
                assert positions==[expected],(text,index,positions,expected);cases+=1
    return {'actual_mips_cases':cases,'load_bases':2,'native_boundary_stubs':True,'stack_guards':True,'real_metric_lookup':True,'runtime_rendering_test_separate':True}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
