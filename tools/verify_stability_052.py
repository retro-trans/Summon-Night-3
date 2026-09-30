"""Read-only regression audit of an actual candidate ISO; nonzero on failure.

Known text-rendering paths only. This is not a full-game stability claim.
Example: python tools/verify_stability.py --build work/output/0.1.48
"""
import argparse,hashlib,json,struct,sys,time
if not __debug__:raise RuntimeError("Stability checks require Python assertions; do not use -O")
from datetime import datetime,timezone
from pathlib import Path
from sn3_archive import ROOT,GameSource,parse_index,child
from scan_source import inventory
from character_labels import collect
from puppet_048 import audit as audit_names
from brave_fix_042 import verify as verify_brave
from verify_equipment_047 import CPU as EquipmentCPU,stage,BaseCPU
from verify_descriptions_021 import CPU as SpellCPU

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()

def renderer_for(elf,static):
 if struct.unpack_from("<I",elf,0x64820+192)[0]>>26==2:
  from verify_guards_049 import AliasCPU,stage as guarded_stage
  return AliasCPU(elf,static),guarded_stage
 return BaseCPU(elf,static),stage

def equipment(elf,static):
 renderer,stage_fn=renderer_for(elf,static);cases=0;max_cells=0;max_slot=-1;failures=[]
 for kind in range(3):
  c=EquipmentCPU(elf,static,kind)
  for rec in range(1,c.count):
   for key in (False,True):
    try:
     r=c.run(rec,key)
     assert r['total']<=54,('total cells',r['total'])
     assert max(r['lengths'],default=0)<=27,('row cells',r['lengths'])
     staged=stage_fn(renderer,c.mem[0x5019f0:0x5019f0+178])
     max_cells=max(max_cells,r['total']);max_slot=max(max_slot,staged['max_slot'])
    except (AssertionError,ValueError,IndexError) as e:
     failures.append(dict(kind=kind,record=rec,key_item=key,error=str(e)))
    cases+=1
 return dict(passed=not failures,cases=cases,max_cells=max_cells,max_glyph_slot=max_slot,failures=failures)

def spells(elf,static):
 c=SpellCPU(elf,static);renderer,stage_fn=renderer_for(elf,static);p,t=c.tables[13]
 cases=0;failures=[];max_cells=0
 for rec in range(1,t['record_count']):
  if not c.read(p+4+rec*40+32):continue
  try:
   c.run(rec);payload=c.mem[0x5019f0:0x5019f0+178]
   # Count native cells, not normalized Unicode characters.
   pos=0;lengths=[]
   while pos+2<=len(payload) and payload[pos:pos+2]!=b'\0\0':
    n=0
    while pos+2<=len(payload) and payload[pos:pos+2]!=b'\0\0':pos+=2;n+=1
    lengths.append(n);pos+=2
   assert pos+2<=len(payload), 'missing empty-line terminator'
   assert len(lengths)<=3 and max(lengths,default=0)<=27,('rows',lengths)
   assert sum(lengths)<=54,('total cells',sum(lengths))
   stage_fn(renderer,payload);max_cells=max(max_cells,sum(lengths))
  except (AssertionError,ValueError,IndexError) as e:
   failures.append(dict(record=rec,error=str(e)))
  cases+=1
 return dict(passed=not failures,cases=cases,max_cells=max_cells,failures=failures)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--build',type=Path,required=True)
 p.add_argument('--report',type=Path)
 a=p.parse_args();folder=(ROOT/a.build).resolve()
 manifest=json.loads((folder/'manifest.json').read_text())
 iso=folder/manifest['output_iso'];checks=[];started=time.monotonic()
 def check(name,fn):
  print('Checking '+name,flush=True)
  try:
   details=fn();r=dict(name=name,passed=details.pop('passed',True),details=details)
  except Exception as e:r=dict(name=name,passed=False,error=type(e).__name__+': '+str(e))
  checks.append(r);return r['passed']
 def identity():
  actual=sha(iso)
  assert actual==manifest['output_sha256'],'ISO differs from build manifest'
  return dict(iso_sha256=actual)
 if check('ISO identity',identity):
  with iso.open('rb') as f:
   _,files=inventory(f,iso.stat().st_size)
   entry=next(x for x in files if x['path']=='/PSP_GAME/SYSDIR/EBOOT.BIN')
   f.seek(entry['sector']*2048);elf=f.read(entry['size_bytes'])
  with GameSource(iso) as source:
   static=source.resource('02.DAT',3)
   def copies():
    master=source.resource('00.DAT',44);mi=parse_index(master,len(master))
    assert child(master,mi,7)==static,'static table cache differs'
    bank=source.resource('01.DAT',1);cache=child(master,mi,6)
    assert bank[:len(cache)]==cache and not any(bank[len(cache):]),'label cache differs'
    assert len(source.indexes)==23
    assert elf==(folder/'EBOOT.elf').read_bytes(),'ISO executable differs from build sidecar'
    return dict(bank_indexes=23,cache_copies_equal=True,executable_matches_iso=True)
   check('Archive and cached-table consistency',copies)
   check('All referenced unit-name/class encodings',lambda:audit_names(collect(source)[0]))
   def brave():
    r=verify_brave(elf,static)
    return dict(cases=len(r['native_copy_cases']),glyph_capacity=r['glyph_capacity'])
   check('Brave Goal termination and native staging',brave)
   check('All equipment formatter and staging variants',lambda:equipment(elf,static))
   check('All populated spell help formatter and staging variants',lambda:spells(elf,static))
   from verify_skills_041 import verify as skills
   from verify_cooking_046 import verify as cooking
   from cooking_title_052 import prior_layout_view
   def skill_checks():
    r=skills(elf,static)
    return dict(pact_names=len(r['native_pact_names']),pact_help=len(r['native_pact_help']),vwf_call_sites=r['vwf_call_sites'])
   def cooking_checks():
    r=cooking(prior_layout_view(elf),static)
    return dict(text_entries=len(r['text_checks']),native_staging_cases=r['native_staging_cases'],position_cases=r['position_cases'],load_bases=r['load_bases'],system_menu_regression=True)
   check('Skill labels and dynamic Pact help',skill_checks)
   check('Cooking text, native staging, positioning and System menu',cooking_checks)
   if 'stability049_text' in manifest:
    from verify_guards_050 import verify as guards
    check('Shared renderer guards and relocation',lambda:guards(elf,static))
   from verify_inventory_050 import verify as inventory_checks
   check('Two-row equipment help and weapon-name coverage',lambda:inventory_checks(elf,static))
   from verify_armor_051 import verify as armor_checks
   check('Armor names and symbolic stat placement',lambda:armor_checks(prior_layout_view(elf),static))
   from verify_cooking_title_052 import verify as title_checks
   check('Centered Cooking title pixels',lambda:title_checks(elf,static))

 report=dict(version=manifest['version'],iso_sha256=manifest['output_sha256'],created_at_utc=datetime.now(timezone.utc).isoformat(),
  passed=all(r['passed'] for r in checks),elapsed_seconds=round(time.monotonic()-started,2),checks=checks,
  limits=['Known rendering paths only; other menus and story paths remain outside this audit.',
          'Native formatter/staging execution uses boundary stubs for graphics calls.',
          'A pass does not replace fresh-boot PPSSPP tests or a playthrough.'])
 if a.report:
  target=(ROOT/a.report).resolve();assert ROOT in target.parents
  target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
 return 0 if report['passed'] else 1

if __name__=='__main__':sys.exit(main())
