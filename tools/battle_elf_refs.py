"""Read-only mapping of relocation-backed native text references."""
import struct
from collections import defaultdict
from stages_pupil_names import parse_elf

def signed(v):return (v&65535)-65536 if v&32768 else v&65535
def written_register(w):
    op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
    if op==0:return None if fn in (8,12,13,17,19,24,25,26,27) else rd
    if op==3:return 31
    if op in (8,9,10,11,12,13,14,15,32,33,34,35,36,37,38,39,48,56):return rt
    if op in (16,17) and rs in (0,2):return rt
    return None

def references(data):
    elf=parse_elf(data);ph=elf['phdrs'];rel=next(p for p in ph if p[0]==0x700000a0)
    records=list(struct.iter_unpack('<II',data[rel[1]:rel[1]+rel[4]]));info=dict(records)
    def word(a):return struct.unpack_from('<I',data,a+0xc0)[0]
    result=defaultdict(list);users=defaultdict(list)
    for address,i in records:
        if i==2:result[word(address)].append(dict(kind='pointer',address=address))
        if i!=6:continue
        w=word(address);reg=w>>21&31
        if reg==0:continue
        high=None
        for a in range(address-4,max(-1,address-0x400),-4):
            q=word(a)
            if written_register(q)==reg:
                if q>>26==15 and info.get(a)==5:high=a
                break
        if high is None:continue
        value=((word(high)&65535)<<16)+signed(w)
        users[high].append(dict(low=address,target=value,opcode=w>>26))
        if w>>26==9:
            result[value].append(dict(kind='hilo',high=high,low=address,register=reg))
    # PPSSPP's relocation resolution pairs each HI with the next non-HI LO.
    # Require the static value's high adjustment to use exactly that LO too.
    pair={}
    for n,(a,i) in enumerate(records):
        if i!=5:continue
        for lo,j in records[n+1:]:
            if j==5:continue
            if j in (1,6):pair[a]=lo;break
    return dict(result),dict(users),pair

if __name__=='__main__':
    import json
    from pathlib import Path
    data=Path('work/output/0.1.12/EBOOT.elf').read_bytes()
    refs,users,pairs=references(data)
    index=json.loads(Path('work/translation/en/interface.index.json').read_text())
    for r in index['executable_literals']:
        addr=int(r['module_address'],16)
        if addr in refs:
            print(r['id'],json.dumps(refs[addr]))
