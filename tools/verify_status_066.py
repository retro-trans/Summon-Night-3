"""Execute actual icon-position MIPS at two load bases and verify label isolation."""
import argparse,json,struct,unicodedata
from status_fix_066 import prepare_elf,prepare_tables,BASE,ROOT
from sn3_archive import GameSource,parse_index,child
from stages_pupil_names import parse_elf
from dialogue_encoding import encode_dialogue
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA

def verify():
    elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes();seg=parse_elf(old)['phdrs'][3];current=parse_elf(elf)['phdrs'][3]
    assert current[6]==7 and elf[current[1]:current[1]+seg[4]]==old[seg[1]:seg[1]+seg[4]]
    for va in (0x209a4,0x209e0,0x20b24):assert elf[va+192:va+196]==old[va+192:va+196]
    metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
    advances={int.from_bytes(bytes.fromhex(v['cp932_hex']),'little'):v['proposed_advance_pixels']*.875 for v in metrics.values()}
    def width(raw,n):return sum(advances.get(int.from_bytes(raw[i:i+2],'little'),13) for i in range(0,n*2,2))
    def sf(c,n,x):c.fp[n]=int.from_bytes(struct.pack('<f',x),'little')
    def ff(c,n):return struct.unpack('<f',struct.pack('<I',c.fp[n]))[0]
    cases=[]
    for base in (0x08804000,0x0890c000):
        for row,index,match in [(1,n,True) for n in (0,1,9,14,16)]+[(0,14,True),(1,14,False),(1,17,True),(2,14,True)]:
            c=CPU(elf,r,base);ctx=0x09000000;desc=0x09002000;cb=base+0x1000
            raw=bytearray(58);prefix=(b'\0\0'+encode_dialogue(' Switch Unit ','')[0])[:index*2].ljust(index*2,b'\0')
            raw[:len(prefix)]=prefix
            label=encode_dialogue('Give Food' if match else 'Learn Ski','')[0]
            start=index*2+4
            if start+len(label)<=58:raw[start:start+len(label)]=label
            c.store(ctx,bytes(0x200));c.store(ctx+0x4c+58,raw);c.store(desc,bytes(0x110));c.store(desc+0x100,bytes([index,row]));c.store(0x09effe00,b'G'*1024)
            for i in range(16,31):c.reg[i]=0x55500000+i
            c.set('sp',0x09f00000);c.set('s2',ctx);c.set('s3',desc);c.set('a0',desc);c.set('a2',cb)
            for n in range(32):sf(c,n,n+.25)
            sf(c,12,118+index*13);saved=c.reg[16:31].copy();fs=c.fp.copy();seen=[]
            corrected=row==1 and index<=16 and match
            c.native_handlers={cb:lambda m:(seen.append(('callback',m.reg[4],ff(m,12))) or {}),base+int(r['fallback'],16):lambda m:(seen.append(('fallback',m.reg[4],ff(m,12))) or {})}
            c.run(int(r['code_address'],16)-CODE_VA+r['labels']['food_icon'])
            expected=118+(width(raw,index) if corrected else index*13)
            assert seen==[('callback' if corrected else 'fallback',desc,expected)],(row,index,match,seen,expected)
            assert c.reg[16:24]+c.reg[26:31]==saved[:8]+saved[10:] and c.fp[13:]==fs[13:]
            assert c.bytes(0x09effe00,0x1c0)==b'G'*0x1c0 and c.bytes(0x09f00000,0x200)==b'G'*0x200
            cases.append(dict(base=hex(base),row=row,index=index,match=match,corrected=corrected,icon_x=expected))
    with GameSource(BASE/'Summon_Night_3_EN_0.1.65.iso') as src:
        _,banks,master,labels=prepare_tables(src)
        ix=parse_index(banks[1],len(banks[1]));data=child(banks[1],ix,0)
        mi=parse_index(master,len(master));cached=child(master,mi,6);ci=parse_index(cached,len(cached));assert child(cached,ci,0)==data
        for e in labels['units']:
            for ref in e['references']:
                pos=struct.unpack_from('<I',data,ref['pointer_field_offset'])[0];n=len(e['english'])*2
                assert unicodedata.normalize('NFKC',data[pos:pos+n].decode('cp932'))==e['english'] and data[pos+n:pos+n+2]==b'\0\0'
    return dict(passed=True,actual_mips_cases=len(cases),load_bases=2,stack_guards=True,all_other_icons_fall_back=True,previous_added_segment_unchanged=True,private_chapter_arena_retained=True,labels=labels['units'],cases=cases,exact_report_screen_verified=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--report');a=p.parse_args();r=verify();print(json.dumps(r,indent=2))
    if a.report:
        target=(ROOT/a.report).resolve();assert ROOT in target.parents and not target.exists();target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
