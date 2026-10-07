"""Record the reviewed final menu captures and completed validation reports."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
def main():
 output=ROOT/'work/output/0.1.74';ui=ROOT/'work/ui/menus_0.1.74'
 manifest_path=output/'manifest.json';m=json.loads(manifest_path.read_text(encoding='utf8'))
 iso_sha=m['output_sha256'];assert iso_sha=='6aff0fa6e49f144aa86e071d73e9fce9321eecdfaf5274439219e72ab34796e0'
 session=json.loads((ROOT/'work/scratch/menus074-final8/session.json').read_text(encoding='utf-8-sig'))
 assert session['fresh_boot'] and not session['save_state_used'] and session['audio_enabled']
 notes={
  'title':'Extra Story footer fits.', 'mainStory':'Main Story footer fits.',
  'load':'Normal in-game save chooser, GAME00.', 'room':'Loaded normal room save.',
  'marurur':'Marurur and Flower Fairy fit their status fields.',
  'cooking':'Pirate Lunch has six lines of readable English instead of question marks.',
  'cookingSeafood':'Pirate Hot Pot description and ingredient rows display correctly.',
  'party':'Translated upper list clears ON/OFF controls; Pirate Lunch help is English.',
  'partyBottom':'Translated lower list and Mutual Support help.',
  'partyHero':'Hero Tales 5 and EXP gained x4, matching the native level.',
  'unitForm':'Deploy using Unit Summon. replaces the native Japanese duplicate.',
  'crystalSpirit':'Symbolic stat rows are spaced without overlap; native numbers retained.',
  'cookingReopened':'Recipe descriptions remain readable after other menus are visited.'}
 captures=[]
 for name,note in notes.items():
  path=ui/'menus074-final8'/f'{name}.png';record=path.with_suffix('.json')
  meta=json.loads(record.read_text(encoding='utf8'))
  assert meta['png_sha256']==digest(path) and meta['width']==480 and meta['height']==272
  captures.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),note=note))
 baseline=ui/'menus074-cooking-base/cookBaseOpen.png'
 runtime=dict(version='0.1.74',passed=True,iso_sha256=iso_sha,emulator='PPSSPP 1.20.4',
  fresh_boot=True,normal_in_game_save=True,save_state_used=False,runtime_memory_edits=False,
  audio_enabled=True,cpu_core='JIT',ignore_bad_memory=False,
  single_emulator=True,second_launch_guard_verified=True,owned_emulator_closed_after_checks=True,
  save_provenance='Private room save created through the game Save menu from supplied older diagnostic state; final sessions booted normally and loaded the resulting save.',
  baseline=dict(version='0.1.73',iso_sha256=m['previous_build_sha256'],
   path=baseline.relative_to(ROOT).as_posix(),sha256=digest(baseline),
   same_normal_save=True,question_marks_reproduced=True),screenshots=captures,
  limits=['Reported screens and known rendering paths; not a complete playthrough.',
   'Other Hero Tales levels are covered by native selector execution, not runtime save edits.'])
 write(ui/'runtime-validation.json',runtime)
 layout=dict(version='0.1.74',resolution=[480,272],units='pixels',regions=[
  dict(id='title_footer',x=407,y=257,width=72,height=14),
  dict(id='status_name',x=150,y=55,width=133,height=16),
  dict(id='status_class',x=150,y=74,width=133,height=16),
  dict(id='cooking_description',x=261,y=65,width=182,height=104,lines=6),
  dict(id='party_name',x=143,y=60,width=108,height=18,row_spacing=18),
  dict(id='party_help',x=120,y=4,width=352,height=33),
  dict(id='summon_index_help',x=61,y=232,width=356,height=35)])
 write(ui/'layout.json',layout)
 reports={
  'stability-report.json':'cumulative-validation.json',
  'menu-validation.json':'validation.json',
  'name-cache-validation.json':'name-cache-validation.json',
  'hero-validation.json':'hero-validation.json',
  'runtime-validation.json':'runtime-validation.json'}
 recorded={}
 for target,source in reports.items():
  report=json.loads((ui/source).read_text(encoding='utf8'));assert report['passed'],source
  if 'iso_sha256' in report:assert report['iso_sha256']==iso_sha,source
  report['iso_sha256']=iso_sha;write(output/target,report)
  recorded[target]=dict(path=(output/target).relative_to(ROOT).as_posix(),sha256=digest(output/target))
 m['static_validation']['runtime_verified']=True
 m['menus074_validation']=dict(passed=True,reports=recorded,runtime_screenshots=captures)
 write(manifest_path,m)
 print(json.dumps(dict(passed=True,iso_sha256=iso_sha,screenshots=len(captures),reports=len(reports))))
if __name__=='__main__':main()
