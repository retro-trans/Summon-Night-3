"""Record the root agent's completed source comparison, preview by default."""
import argparse,json,hashlib
from chapter_source_014 import load
from sn3_archive import ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    folder=ROOT/'work/translation/en/chapters_0.1.14/0180';_,rows,_=load(180)
    inputs={};slices=[]
    for start in (0,80):
        path=folder/f'slice_{start:04d}.targets.json';h=hashlib.sha256(path.read_bytes()).hexdigest()
        slices.append(dict(target_file=str(path.relative_to(ROOT)).replace('\\','/'),target_file_sha256=h,assigned_range=[start,start+79],translation_count=80))
    fixes={75:'Indeed...',96:'In any case, come for a visit.',97:"They'll explain",98:"everything when you're there."}
    corrections=[dict(resource_row=n,id=rows[n+3957]['id'],source_sha256=rows[n+3957]['source_sha256'],text=t) for n,t in fixes.items()]
    doc=dict(resource_id='00:00180',review_type='independent_meaning_review',semantic_complete=True,reviewed_slices=slices,reviewed_rows=list(range(160)),rows_examined=170,examined_relative_range=[0,169],corrections=corrections,uncertainties=['Ardylia uses an indirect reference for the person who will explain the patient situation. The correction keeps the referent gender-neutral instead of assigning an unsupported male pronoun.'],notes=['Compared every source and target in two80-row slices, including the next10rows. Fixed the unattached verb in row75 and the unsupported pronoun in96-98. Equivalent translations left intact.'])
    print(json.dumps(dict(mode='write' if a.write else 'dry-run',rows=160,examined=170,corrections=corrections),ensure_ascii=False))
    if a.write:(folder/'review_meaning_0000_0159.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
