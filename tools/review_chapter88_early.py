"""Record source/context meaning review of Chapter 2 early seven slices."""
import argparse,json
from chapter_patch import ROOT,FOLDER,read,sha
from chapter_source import chapter_source
FIXES={22:"they go!?",154:"attacked you, right?",156:"attacked you, didn't they?",160:"So I...",
161:"So that's why you took",162:"such a terrible risk",163:"to protect it...",
164:"So that's why you took",165:"such a terrible risk",166:"to protect it.",
181:"Good for you,",189:"Beep beep! ♪",209:"attacked you, right?",211:"attacked you, didn't they?",
215:"So that's why you took",216:"such a terrible risk",217:"to protect it...",
218:"So that's why you took",219:"such a terrible risk",220:"to protect it.",224:"That's not true.",
256:"Meow, meow! ♪",273:"attacked you, right?",275:"attacked you, didn't they?",
279:"So that's why you took",280:"such a terrible risk",281:"to protect it...",286:"That's not true.",
319:"Bwee-bwee! ♪",336:"attacked you, right?",338:"attacked you, didn't they?",339:"U-Um...!",
345:"So that's why you took",346:"such a terrible risk",347:"to protect it...",374:"Kyuu-py! ♪"}

def prepare():
    _,rows,_=chapter_source(88);folder=FOLDER/'0088';files=[]
    for start in range(0,560,80):
        path=folder/f'slice_{start:04d}.targets.json'
        files.append(dict(target_file=str(path.relative_to(ROOT)).replace('\\','/'),target_file_sha256=sha(path.read_bytes()),assigned_range=[start,start+79],rows_examined=[max(0,start-20),start+99]))
    reasons={22:'The pupil refers to the selected protagonist; this branch can be male or female.',160:'The pupil starts to explain their own action; the draft changes speaker and joins it incorrectly to the next reply.',181:'The following source fragment already supplies R; remove duplicate name.',224:'Reply denies the pupil acted wrongly; draft pronoun could invert its meaning.',286:'Reply denies the pupil acted wrongly; draft pronoun could invert its meaning.',339:'Hesitant interjection is not a denial.'}
    fixes=[]
    for n,text in FIXES.items():
        reason=reasons.get(n,'Restore musical-note expression.' if '♪' in text else 'The teacher is acknowledging the pupil risking themselves to protect their companion, not the companion protecting the teacher. Adjacent pupil replies settle the referent.')
        if n in (154,156,209,211,273,275,336,338):reason='Teacher addresses the pupil about the attack during their journey with the companion; draft wrongly singles out the companion as the victim.'
        fixes.append(dict(resource_row=n,source_id=rows[n]['id'],source_sha256=rows[n]['source_sha256'],replacement_text=text,reason=reason))
    return dict(resource_id='00:00088',review_type='independent_meaning_review',semantic_complete=True,reviewer='root (draft author terra_cabin_801)',reviewed_slices=files,required_corrections=fixes,uncertainties=[dict(rows=[250,251],note='Teco is named after the sound/quality of its gait; the English keeps the explanation without inventing a new pet name.'),dict(rows=[61,62],note='Wrong to wake you is an acceptable polite explanation for not wanting to disturb sleep; stylistic change not required.')],additional_review='review_empty_fragments.json redistributes merged English without empty target rows.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();d=prepare()
    print(json.dumps(dict(mode='write' if a.write else 'dry run',reviewed=560,corrections=d['required_corrections'],uncertainties=d['uncertainties']),indent=2))
    if a.write:(FOLDER/'0088'/'review_meaning_early.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
