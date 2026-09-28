"""Read-only ELF disassembly and backlog label reference discovery."""
import argparse, struct, sys
from sn3_archive import ROOT
sys.path.insert(0,str(ROOT/'tools/vendor/capstone-5.0.9'))
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--start',type=lambda x:int(x,0))
    p.add_argument('--size',type=lambda x:int(x,0),default=0x200);a=p.parse_args()
    data=(ROOT/'work/source/EBOOT.elf').read_bytes()
    cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    if a.start is not None:
        for i in cs.disasm(data[a.start+0xc0:a.start+0xc0+a.size],a.start):
            print(f'{i.address:08x}: {i.mnemonic:10} {i.op_str}')
        return
    for text in ['音声再生','バックログ']:
        pos=0
        while True:
            pos=data.find(text.encode('cp932'),pos)
            if pos<0:break
            va=pos-0xc0;print('Label',text,'file',hex(pos),'VA',hex(va))
            for off in range(0xc0,0x210000,4):
                w=struct.unpack_from('<I',data,off)[0]
                if w>>26!=15:continue
                rt=(w>>16)&31
                for delta in range(4,36,4):
                    lo=struct.unpack_from('<I',data,off+delta)[0]
                    if lo>>26==9 and (lo>>21)&31==rt:
                        signed=struct.unpack('<h',struct.pack('<H',lo&65535))[0]
                        if ((w&65535)<<16)+signed==va:
                            print('  reference',hex(off-0xc0),hex(off+delta-0xc0))
            pos+=2
    for target in [0x682e8,0x685cc,0x6a038]:
        word=3<<26|target>>2
        print('JAL callers',hex(target),[hex(o-0xc0) for o in range(0xc0,0x210000,4)
            if struct.unpack_from('<I',data,o)[0]==word])

if __name__=='__main__':main()
