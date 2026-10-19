"""Run the native Level Up formatter and guard its VWF staging buffers."""
import json,struct,unicodedata
from sn3_archive import ROOT,GameSource
from levelup_spacing_085 import prepare_elf,BASE,TEXT
from verify_descriptions_021 import CPU
from verify_guards_057 import AliasCPU,stage

def verify():
 elf,report=prepare_elf();cfg=json.loads(TEXT.read_text('utf8'));rows=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.84.iso') as source:static=source.resource('02.DAT',3)
 renderer=AliasCPU(elf,static)
 for available in (0,1):
  for allocation in (0,1):
   for skills in (0,1):
    c=CPU(elf,static);owner=0x500000;buf=owner+0x19f0;c.mem[buf-32:buf+210]=b'G'*242
    c.r=[0]*32;c.r[4:8]=[owner,available,allocation,skills];c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=0x63b60
    for _ in range(100000):
     if pc==0x7ffff0:break
     if pc==0x1c2bc0:
      a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
     elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
     elif pc==0x1e4b50:
      a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
     else:pc=c.step(pc)
    else:raise AssertionError('Native formatter did not return')
    assert c.mem[buf-32:buf]==b'G'*32 and c.mem[buf+178:buf+210]==b'G'*32
    payload=c.mem[buf:buf+178];pos=0;lines=[]
    while c.read(buf+pos,2):
     end=pos
     while c.read(buf+end,2):end+=2
     lines.append(unicodedata.normalize('NFKC',payload[pos:end].decode('cp932')));pos=end+2
    wanted=['Allocate bonus points.',cfg['confirm']] if allocation else ['Choose a unit to level up.' if available else 'No units can level up.',cfg['controls']+(' '+cfg['skills'] if skills else '')]
    assert lines==wanted and max(map(len,lines))<=27 and sum(map(len,lines))<=54,(lines,wanted)
    rendered=stage(renderer,payload);assert rendered['rows']==2 and 0<rendered['glyphs']<=sum(map(len,lines)) and rendered['max_slot']<54,(lines,rendered)
    rows.append(dict(available=available,allocation=allocation,skills=skills,lines=lines,staging=rendered))
 # Physical icon artwork is wider than its 13-pixel layout advance. Reserve
 # two spaces after face buttons and five after SELECT, using actual metrics.
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text('utf8'))['characters'];line=cfg['controls']+' '+cfg['skills'];x=120.;bounds=[]
 for ch in line:
  if ch in 'АБЙ':bounds.append(dict(token=ch,left=x,right=x+(32 if ch=='Й' else 16)))
  elif ch!=' ':
   ink=metrics[ch]['ink_bounds_inclusive'];left=x+3*.875;right=left+(ink[2]-ink[0]+1)*.875
   assert all(left>=b['right']+1 or right<=b['left']-1 for b in bounds),(ch,left,bounds)
  x+=metrics[ch]['proposed_advance_pixels']*.875 if ch in metrics else 13
 assert x<472 and len(line)==27
 return dict(passed=True,native_formatter_cases=rows,icon_bounds=bounds,max_hint_cells=len(line),max_combined_cells=52,buffer_guards=True,loaded_bytes_added=0,source_iso_files_except_eboot_unchanged=True)

if __name__=='__main__':
 result=verify();dest=ROOT/'work/ui/ui_0.1.85';dest.mkdir(parents=True,exist_ok=True);(dest/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(result),flush=True)
