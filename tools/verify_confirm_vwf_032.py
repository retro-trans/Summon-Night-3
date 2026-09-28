"""Execute confirmation positioning and both prior popup paths at two load bases."""
import json,struct
from confirm_vwf_032 import prepare_elf
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
import notice_vwf_027 as notice

def verify():
 data,r=prepare_elf();r=r['notice_vwf'];rows=list(r['rows']);old=notice.TEXT
 try:
  for address,text in [(notice.NOTICE,old),(0x34ca00,'Not available yet.')]:
   notice.TEXT=text;v,w=notice.positions();rows.append(dict(address=address,text=text,positions=v))
 finally:notice.TEXT=old
 rows.append(dict(address=0x123456,text='Japanese',positions=None));cases=0
 for base in [0x08804000,0x0890c000]:
  for e in rows:
   for index in range(len(e['text'])+1):
    cpu=CPU(data,r,base);sp=0x09f00000;row=0x09000000;callback=base+0x1000;seen=[]
    cpu.store(sp,bytes(64));cpu.float_store(sp+0x10,.875);cpu.float_store(sp+0x30,1)
    cpu.store(row,struct.pack('<IIf',base+e['address'],0,len(e['text'])*14))
    for i in range(16,31):cpu.reg[i]=0x55000000+i
    cpu.set('s1',index);cpu.set('s7',row);cpu.set('sp',sp);saved=cpu.reg[16:31].copy()
    cpu.set('a0',0x09001000);cpu.set('a2',callback);x=-len(e['text'])*7+index*14
    for reg,value in [(12,x),(13,1.25),(14,498)]:cpu.fp[reg]=struct.unpack('<I',struct.pack('<f',value))[0]
    def native(m):
     seen.append([struct.unpack('<f',struct.pack('<I',m.fp[n]))[0] for n in (12,13,14)])
     assert m.reg[4]==0x09001000;return {}
    cpu.native_handlers={callback:native};cpu.run(int(r['code_address'],16)-CODE_VA+r['labels']['position'])
    expected=x+(e['positions'][index]*.875+len(e['text'])*7 if e['positions'] and index<len(e['text']) else 0)
    assert len(seen)==1 and abs(seen[0][0]-expected)<.001 and seen[0][1:]==[1.25,498],(e,index,seen,expected)
    assert cpu.reg[16:24]+cpu.reg[26:31]==saved[:8]+saved[10:]
    cases+=1
 return dict(cases=cases,load_bases=2,coverage=['prompt and both choices','both prior VWF notices','unrelated source fallback','out-of-range index','callback and preserved registers','Y/Z unchanged'])
if __name__=='__main__':print(json.dumps(verify(),indent=2))
