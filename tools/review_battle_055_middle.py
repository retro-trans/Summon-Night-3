"""Independent meaning review of another author's battle slices240-479."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'work/translation/en/battle_0.1.55'

DETAILS = {
    240: {
        'examined': [232, 328],
        'drafts': [160, 240, 320],
        'uncertainties': [
            {'rows':[245,246,247,248], 'note':'Unnamed organization remains generic; no faction name inferred. Cowardly motive belongs to the responding speaker.'},
            {'rows':[276,277,278,279,280,281], 'note':'Appearance-versus-substance taunts and mirrored speaker operands support disguise; exact mimic mechanism is not asserted.'},
            {'rows':[292,293,294], 'note':'Source summoning invocation leaves number unspecified. Demons is a reasonable collective rendering but singular versus plural remains unresolved from dialogue alone.'},
            {'rows':[304,305,306], 'note':'Impersonal It really was foolish avoids guessing whether this is a mirror self or a separate speaker; reciprocal hurt and added pain remain intact.'},
        ],
        'omissions': [
            {'rows':[241,242,243,244], 'note':'Victory result trails off at Now, matching both protagonist variants.'},
            {'rows':[245,246], 'note':'Someone as skilled as you is a deliberate nominal echo following the complete question.'},
            {'rows':[286,287,288,289,290,291], 'note':'The suspended first box is completed directly in the next: no other means remain.'},
            {'rows':[304,305,306], 'note':'The source leaves the person doing the reciprocal hurting unidentified. Impersonal English retains that omission rather than inventing I/you/we.'},
        ],
    },
    320: {
        'examined': [312, 407],
        'drafts': [240, 320, 400],
        'uncertainties': [
            {'rows':[320,321], 'note':'Clyps follows the established provisional glossary spelling, not an independently claimed official spelling.'},
            {'rows':[349,350,351,352], 'note':'Repeated this one likely accompanies distinct visual targets. Physical versus summon-magic effectiveness preserved without inventing a camera direction.'},
            {'rows':[373,374], 'note':'Even damage to the two pillars is supported by preceding risk of losing control. The source explicitly requires destruction as simultaneously as possible; correction makes timing explicit.'},
            {'rows':[396,397], 'note':'Broken Azlier name and apology retained. Source does not finish either word; target should not silently complete them.'},
        ],
        'omissions': [
            {'rows':[396,397], 'note':'Interrupted name and apology preserve failed speech, with I restored in the apology.'},
        ],
    },
    400: {
        'examined': [392, 487],
        'drafts': [320, 400, 480],
        'uncertainties': [
            {'rows':[400,401,402], 'note':'You is supplied from the preceding berserk protagonist confrontation; speaker condemns escalation of violence.'},
            {'rows':[416,417,418], 'note':'The source leaves bodily consequence unfinished, but the immediately preceding explicit crash warning supports wont hold out. This completion is meaning-grounded.'},
            {'rows':[440,441,442,443,444,445], 'note':'Malfunctioning machine report retains protection damage, erased donor personality and regeneration as bug; no gender assumed.'},
            {'rows':[451,452,453,454], 'note':'Source explicitly identifies elder sister/younger brother relationship, so older sister is supported independently of a name.'},
            {'rows':[470,471], 'note':'My brilliant mind attributes the boast to the speaker based on neighboring taunts; source possessive itself is implicit.'},
        ],
        'omissions': [
            {'rows':[422], 'note':'Another me is a deliberate startled nominal utterance, completed by a full judgment in the following two fragments.'},
            {'rows':[425,426,427], 'note':'My former self is a vocative, not an ungrammatical omitted subject; I supplies subject of the promise.'},
            {'rows':[428,429,430], 'note':'Suspended curse invocation is completed by curse of death in next VM box.'},
            {'rows':[460,461,462], 'note':'Final thats remains deliberately unfinished as speaker trails off.'},
        ],
    },
}

def build(start):
    s=DETAILS[start]
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (FOLDER/f'slice_{n:04}.targets.json' for n in s['drafts'])}
    corrections=[]
    if start==320:
        d=json.loads((FOLDER/'slice_0320.targets.json').read_text('utf8'))
        t=next(t for t in d['translations'].values() if t['ordered_index']==374)
        assert t['text']=='and destroy them as close together as possible.'
        corrections=[dict(ordered_index=374,id=t['id'],resource=t['resource'],resource_row=t['resource_row'],
                          before=t['text'],after='and destroy them as nearly simultaneously as possible.',
                          reason='Source requires simultaneous destruction in time; close together could incorrectly imply spatial proximity.')]
    return dict(version='0.1.55',reviewer='independent_agent_c',reviewed_range_inclusive=[start,start+79],
                rows_in_slice=80,rows_examined=s['examined'][1]-s['examined'][0]+1,
                source_ranges_examined=[s['examined']],draft_inputs_sha256=hashes,corrections=corrections,
                uncertainties=s['uncertainties'],preserved_source_omissions=s['omissions'],
                semantic_complete=True,blockers=[],
                notes='Independently reviewed author B, never own drafts. Full actual VM groups with adjacent context were compared against English. The480-487 adjoining own draft was read only as boundary context and is not independently accepted here. Root must apply recorded correction then bind compiler acceptance.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    for start in DETAILS:
        d=build(start);p=FOLDER/f'review_{start:04}.json'
        print(json.dumps(dict(mode='write' if args.write else 'dry-run',range=d['reviewed_range_inclusive'],
                             rows_examined=d['rows_examined'],corrections=d['corrections']),indent=2))
        if args.write:
            assert not p.exists()
            p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
