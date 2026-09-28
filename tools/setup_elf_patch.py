"""Relocate reviewed naming literals into the existing added ELF load segment."""
import hashlib
import struct
from dialogue_encoding import encode_dialogue


def wide(text):
    return encode_dialogue(text,'')[0]+b'\0\0'


def patch(data):
    specs=[('Rexx',0x21c8b8,0x129c98,0x129ca4),
           ('Aty',0x21c8c4,0x129cb8,0x129cc4),
           ('Use the name "',0x21c8d0,0x12a6e4,0x12a6f8),
           ('"?',0x21c8d4,0x12a6e8,0x12a700),
           ('Yes',0x21c8ec,0x12a70c,0x12a720),
           ('No',0x21c8f4,0x12a72c,0x12a73c),
           ('Please enter a name.',0x21c8fc,0x12a99c,0x12a9a4)]
    phoff,shoff=struct.unpack_from('<II',data,28)
    ps,pn,ss,sn=struct.unpack_from('<4H',data,42)
    assert (ps,pn,ss)==(32,4,40)
    ph=[list(struct.unpack_from('<8I',data,phoff+i*ps)) for i in range(pn)]
    sh=[list(struct.unpack_from('<10I',data,shoff+i*ss)) for i in range(sn)]
    seg=ph[3];assert seg[0]==1 and seg[2]==0x32dbc0
    insert=seg[1]+seg[4];base=seg[2]+seg[4]
    rel=ph[2];relocs=dict(struct.iter_unpack('<II',data[rel[1]:rel[1]+rel[4]]))
    payload=bytearray();changes=[]
    for text,old,hi,lo in specs:
        while len(payload)%4:payload.append(0)
        address=base+len(payload);payload.extend(wide(text))
        ih,il=[struct.unpack_from('<I',data,a+0xc0)[0] for a in (hi,lo)]
        assert ih>>26==15 and il>>26==9 and relocs[hi]==5 and relocs[lo]==6
        assert ((ih&65535)<<16)+struct.unpack('<h',struct.pack('<H',il&65535))[0]==old
        changes.append(dict(text=text,old_address=old,new_address=address,hi=hi,lo=lo))
    payload.extend(bytes((-len(payload))%64));delta=len(payload)
    out=bytearray(data[:insert]+payload+data[insert:])
    # Naming initialization: select column 2 (ABC/123), row 1. The original
    # action-table lookup below remains responsible for selecting keyboard data.
    keyboard=[(0x129d04,0xa200422c,0x34040002),(0x129d08,0x8204422c,0xa204422c)]
    for a,old,new in keyboard:
        assert struct.unpack_from('<I',data,a+0xc0)[0]==old
        assert a not in relocs
        struct.pack_into('<I',out,a+0xc0,new)
    for c in changes:
        for a,value in [(c['hi'],(c['new_address']+0x8000)>>16),(c['lo'],c['new_address']&65535)]:
            old=struct.unpack_from('<I',out,a+0xc0)[0]
            struct.pack_into('<I',out,a+0xc0,(old&0xffff0000)|value)
    for p in ph:
        if p[1]>=insert:p[1]+=delta
    seg[4]+=delta;seg[5]+=delta
    for s in sh:
        if s[4]>=insert:s[4]+=delta
        if s[3]==seg[2] and s[4]==seg[1]:s[5]+=delta
    for i,p in enumerate(ph):struct.pack_into('<8I',out,phoff+i*ps,*p)
    for i,s in enumerate(sh):struct.pack_into('<10I',out,shoff+delta+i*ss,*s)
    struct.pack_into('<I',out,32,shoff+delta)
    assert out[seg[1]:insert]==data[seg[1]:insert]
    assert out[ph[2][1]:ph[2][1]+ph[2][4]]==data[rel[1]-delta:rel[1]-delta+rel[4]]
    for c in changes:
        off=seg[1]+c['new_address']-seg[2]
        assert out[off:off+len(wide(c['text']))]==wide(c['text'])
    return bytes(out),dict(changes=changes,added_bytes=delta,default_keyboard='ABC/123',
                           keyboard_instructions=[{'module_address':hex(a),'before':hex(o),'after':hex(n)} for a,o,n in keyboard],original_font_code_preserved=True,
                           original_relocations_preserved=True,sha256=hashlib.sha256(out).hexdigest())
