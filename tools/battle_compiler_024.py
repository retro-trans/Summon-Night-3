"""Relocate native battle dialogue, preserving speaker calls and event flow."""
import argparse,copy,json,struct,re
from pathlib import Path
from battle_source_024 import load,sha,ROOT,source_text
from dialogue_encoding import encode_dialogue,control_tokens
from dialogue_layout import operand_instruction,latin_width
from font_metrics_014 import collect
from stages_patch import wrap,units
from chapter_patch_014 import normalize
from sn3_vm import instructions
from script_strings import parse_pool

FOLDER=ROOT/'work/translation/en/battle_0.1.24'

def targets(number,rows,data):
 result={};inputs={}
 for path in sorted(FOLDER.glob('*.targets.json')):
  doc=json.loads(path.read_text(encoding='utf8'));inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
  for identity,t in doc['translations'].items():
   if t['resource']!=number:continue
   n=t['resource_row'];r=rows[n];assert n not in result and identity==r['id']
   for key in ('source_offset','source_sha256','source_byte_length','reference_instructions'):assert t[key]==r[key],(identity,key)
   result[n]=copy.deepcopy(t)
 assert set(result)==set(range(len(rows))),(number,'incomplete',len(result),len(rows))
 for path in sorted(FOLDER.glob('review_*.json')):
  review=json.loads(path.read_text(encoding='utf8'))
  for name,h in review['draft_inputs_sha256'].items():assert sha((ROOT/name).read_bytes())==h,name
  inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
  for fix in review.get('corrections',[]):
   if fix['resource']!=number:continue
   n=fix['resource_row'];assert fix['source_sha256']==rows[n]['source_sha256'];result[n]['text']=fix['text']
 for n,t in result.items():
  t['text']=normalize(t['text'])
  for old,new in json.loads((ROOT/'work/glossary/battle_0.1.24.json').read_text())['aliases'].items():
   t['text']=re.sub(r'(?<![A-Za-z])'+re.escape(old)+r'(?![A-Za-z])',new,t['text'])
  source=source_text(rows[n],data)
  assert control_tokens(t['text'])==control_tokens(source),(number,n,'controls')
  encode_dialogue(t['text'],source)
 return result,inputs

def simulate(data,start,end,at=None):
 if at is None:at={i['offset']:i for i in instructions(data)}
 pool=struct.unpack_from('<I',data,20)[0]*2
 pc=start;stack=['sentinel'];pending=[];pages=[];steps=0
 while pc!=end:
  steps+=1;assert steps<2000
  i=at[pc];pc+=i['size'];op=i['opcode']
  if op==0:continue
  if op==10:pc=i['target_word']*2;continue
  if op==5:
   if i['mode']==4:
    p=pool+i['string_word']*2;q=p
    while data[q:q+2]!=b'\0\0':q+=2
    stack.append(data[p:q].decode('cp932'))
   else:stack.append(('source_value',i['mode'],i['high'],tuple(i['operands'])))
  elif op==8:
   assert i['mode']==1 and i['operands'][0] in (0x20c7,0x20c9)
   arg=stack.pop()
   if i['operands'][0]==0x20c7:assert isinstance(arg,str);pending.append(arg)
   else:assert pending;pages.append(dict(speaker=arg,lines=pending));pending=[]
  else:raise AssertionError(i)
 assert stack==['sentinel'] and not pending
 return pages

def prepare(number):
 resource,rows,before=load(number);translated,inputs=targets(number,rows,before)
 code=instructions(before);at={i['offset']:i for i in code};pool=parse_pool(before)['pool_offset']
 assert code[-1]['opcode']==9
 destinations={i['target_word']*2 for i in code if 'target_word' in i}|{struct.unpack_from('<I',before,16)[0]*2}
 metrics=copy.deepcopy(collect()[0]['characters'])
 for c,width in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:metrics[c]={'proposed_advance_pixels':width}
 plans=[];done=set()
 for n,row in enumerate(rows):
  if n in done:continue
  assert len(row['reference_instructions'])==1
  start=row['reference_instructions'][0];ns=[n]
  while ns[-1]+1<len(rows) and rows[ns[-1]+1]['reference_instructions']==[start+8*len(ns)] and start+8*len(ns) not in destinations:ns.append(ns[-1]+1)
  for k in ns:
   p=rows[k]['reference_instructions'][0]
   assert at[p]['opcode']==5 and at[p]['mode']==4
   assert at[p+4]['opcode']==8 and at[p+4]['mode']==1 and at[p+4]['operands']==[0x20c7]
  tail_start=start+8*len(ns);end=tail_start
  assert at[end]['opcode']==5 and at[end]['mode'] in (3,9,10)
  end+=at[end]['size'];assert at[end]['opcode']==8 and at[end]['mode']==1 and at[end]['operands']==[0x20c9]
  end+=4;assert not any(start<x<end for x in destinations),(number,ns,'incoming branch')
  text=' '.join(translated[k]['text'] for k in ns);lines=wrap(text,208,metrics);pages=[lines[i:i+3] for i in range(0,len(lines),3)]
  assert all(sum(units(t) for t in page)<=93 for page in pages)
  plans.append(dict(rows=ns,span=[start,end],tail=before[tail_start:end],text=text,page_texts=pages,size=sum(8*len(page)+end-tail_start for page in pages)+4))
  done.update(ns)
 assert done==set(range(len(rows)))
 new_pool=pool+sum(p['size'] for p in plans);out=bytearray(before[:pool]+bytes(new_pool-pool)+b'\0\0');struct.pack_into('<I',out,20,new_pool//2)
 cursor=pool;groups=[]
 for plan in plans:
  start,end=plan['span'];emitted=bytearray();pages=[]
  for page in plan['page_texts']:
   records=[]
   for text in page:
    encoded,display=encode_dialogue(text,''.join(control_tokens(text)));offset=len(out);word=(offset-new_pool)//2;ref=cursor+len(emitted)
    assert len(encoded)//2<=127
    out.extend(encoded+b'\0\0');emitted.extend(operand_instruction(5,4,word)+operand_instruction(8,1,0x20c7))
    records.append(dict(text=text,display_text=display,new_offset=offset,reference=ref,expanded_units=units(text),pixels=latin_width(text,metrics)))
   emitted.extend(plan['tail']);pages.append(records)
  emitted.extend(operand_instruction(10,0,end//2));assert len(emitted)==plan['size']
  out[cursor:cursor+len(emitted)]=emitted;out[start:end]=operand_instruction(10,0,cursor//2)+bytes(end-start-4)
  groups.append(dict(rows=plan['rows'],original_span=plan['span'],trampoline_offset=cursor,pages=pages,text=plan['text']))
  cursor+=len(emitted)
 assert cursor==new_pool
 allowed=set(range(20,24))|{i for g in groups for i in range(*g['original_span'])}
 assert all(before[i]==out[i] for i in range(pool) if i not in allowed)
 parsed=parse_pool(out);new_at={i['offset']:i for i in instructions(out)}
 for g in groups:
  old=simulate(before,*g['original_span'],at=at);new=simulate(out,*g['original_span'],at=new_at);assert len(old)==1 and len(new)==len(g['pages'])
  for actual,expected in zip(new,g['pages']):assert actual['speaker']==old[0]['speaker'] and actual['lines']==[r['display_text'] for r in expected]
 report=dict(resource_id=resource['id'],index=number,source_sha256=sha(before),output_sha256=sha(out),source_bytes=len(before),output_bytes=len(out),covered_source_rows=len(rows),remaining_in_scope=0,groups=groups,targets=translated,vm_statistics=parsed['vm_statistics'],unchanged_event_code_verified=True,all_display_spans_simulated=True)
 return bytes(out),report,inputs

def main():
 p=argparse.ArgumentParser();p.add_argument('resource',type=int);a=p.parse_args();data,r,_=prepare(a.resource)
 print(json.dumps({k:v for k,v in r.items() if k not in ('groups','targets')},indent=2));print(json.dumps(r['groups'][:2],indent=2))
if __name__=='__main__':main()
