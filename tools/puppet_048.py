"""Correct two legacy ASCII unit names consumed as two-byte CP932 cells."""
import hashlib,json,struct,unicodedata
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from character_labels import collect
from dialogue_encoding import encode_dialogue

BASE=ROOT/'work/output/0.1.47'
FOLDER=ROOT/'work/translation/en/puppet_0.1.48'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 return (BASE/'EBOOT.elf').read_bytes(),dict(entries=[],executable_unchanged=True)

def audit(data):
 count=struct.unpack_from('<I',data)[0];pointers=set();references=0
 for row in range(count):
  for slot in range(1,8):
   p=struct.unpack_from('<I',data,4+row*32+slot*4)[0]
   if not p:continue
   assert p%2==0 and 4+count*32<=p<len(data),(row,slot,p)
   end=data.index(b'\0',p);raw=data[p:end]
   assert len(raw)%2==0,(row,slot,raw)
   for lead,trail in zip(raw[::2],raw[1::2]):
    assert (0x81<=lead<=0x9f or 0xe0<=lead<=0xfc) and 0x40<=trail<=0xfc and trail!=0x7f,(row,slot,hex(lead),hex(trail))
   raw.decode('cp932');pointers.add(p);references+=1
 return dict(records=count,unique_labels=len(pointers),references=references,all_referenced_labels_two_byte=True)

def prepare_tables(source):
 before,count,rows=collect(source);out=bytearray(before);changes=[];fields=set()
 entries=json.loads((FOLDER/'targets.json').read_text())['entries']
 for entry in entries:
  row=next(r for r in rows if r['source_offset']==entry['old_offset'])
  raw=before[row['source_offset']:row['source_offset']+row['source_byte_length']]
  assert sha(raw)==entry['source_sha256'] and raw==entry['text'].encode('ascii')
  assert [r['row'] for r in row['references']]==entry['expected_rows']
  assert all(r['slot']==1 for r in row['references'])
  encoded,display=encode_dialogue(entry['text'],'');assert len(encoded)==2*len(entry['text'])
  out.extend(bytes(-len(out)%2));pos=len(out);out.extend(encoded+b'\0\0')
  for ref in row['references']:
   p=ref['pointer_field_offset'];assert struct.unpack_from('<I',out,p)[0]==entry['old_offset']
   struct.pack_into('<I',out,p,pos);fields.update(range(p,p+4))
  changes.append(dict(id=row['id'],text=entry['text'],new_offset=pos,display_text=display,references=row['references']))
 assert len(changes)==2 and len(fields)==32
 assert all(a==b for i,(a,b) in enumerate(zip(before,out)) if i not in fields)
 checks=audit(out)
 # Both runtime copies must contain exactly the same corrected pointers/data.
 bank=source.resource('01.DAT',1);master=source.resource('00.DAT',44)
 mi=parse_index(master,len(master));cached=child(master,mi,6)
 assert child(cached,parse_index(cached,len(cached)),0)==before
 patched=repack(bank,{0:bytes(out)});cache=repack(cached,{0:bytes(out)})
 master=repack(master,{6:cache})
 return {3:source.resource('02.DAT',3)},{1:patched},master,dict(units=changes,tables=[],name_encoding_audit=checks,only_eight_default_name_pointers_changed=True,player_entered_names_untouched=True)

def verify(elf,static):
 assert elf==(BASE/'EBOOT.elf').read_bytes()
 return dict(executable_unchanged=True,all_prior_code_fixes_preserved=True)
