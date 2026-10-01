"""Independent English-only, source-bound review of battle slices 0480-0640."""
import argparse
import json
from battle_pass_055 import FOLDER, ROOT, scope, source, source_text, sha
from dialogue_encoding import control_tokens, encode_dialogue

CORRECTIONS = {
    560: ("That's more 'beaten up'", 'Remove the invented addressee who supposedly gets injured. The source compares the results with being lovestruck and being battered; the impersonal situation subject preserves its ambiguity.'),
    561: ("than 'lovestruck,' isn't it?", 'Complete the comparison without asserting that the person addressed becomes the injured party.'),
}

def review(start,end,examined,inputs,uncertainties,omissions,write):
    rows=scope(); hashes={}
    targets={}
    for n in inputs:
        path=FOLDER/f'slice_{n:04d}.targets.json'
        hashes[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        targets.update(json.loads(path.read_text('utf8'))['translations'])
    corrections=[]
    for n in range(start,end+1):
        row=rows[n]; t=targets[row['id']]
        assert t['ordered_index']==n and t['source_sha256']==row['source_sha256']
        text=CORRECTIONS.get(n,(t['text'],''))[0]
        original=source_text(row,source(row['resource'])[2])
        assert control_tokens(text)==control_tokens(original)
        encode_dialogue(text,original)
        if n in CORRECTIONS:
            corrections.append(dict(ordered_index=n,resource=row['resource'],resource_row=row['resource_row'],source_sha256=row['source_sha256'],text=text,reason=CORRECTIONS[n][1]))
    doc=dict(version='0.1.55',reviewer='independent_agent_b',reviewed_range_inclusive=[start,end],rows_in_slice=end-start+1,
             rows_examined=len({n for a,b in examined for n in range(a,b+1)}),source_ranges_examined=examined,
             draft_inputs_sha256=hashes,corrections=corrections,uncertainties=uncertainties,
             preserved_source_omissions=omissions,semantic_complete=True,blockers=[],
             notes='Read every source VM group and compared English whole-box meaning with surrounding context. Reviewed direction, subjects, names, Teacher terminology, tactical claims, and intentional incomplete speech. This review is independent of the author. Root applies the corrections before acceptance; no original source script is persisted.')
    path=FOLDER/f'review_{start:04d}.json'
    print(json.dumps(dict(mode='write' if write else 'dry-run',path=str(path),range=[start,end],examined=doc['rows_examined'],corrections=corrections,hashes=hashes),indent=2))
    if write:
        assert not path.exists()
        path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main(write):
    review(480,559,[[472,567]],[400,480,560],[
        {'rows':[478,479,480],'note':'Cross-slice sentence verified as It looks like that girl Marurur is egging everyone on; no dropped or duplicated meaning.'},
        {'rows':[507,508,517,518,524,525],'note':'Teacher is inferred as the absent protector from parallel student variants; no gender is inferred.'},
        {'rows':[512,513,514,515],'note':'Matching speaker operand22 and the first-person boast establish Belfraw encouraging herself, rather than another person speaking to her.'},
        {'rows':[535,536,537],'note':'The source itself explicitly supplies female pronoun for Kunon, consistent with the character context glossary.'},
    ],[],write)
    review(560,639,[[551,641]],[480,560,640],[
        {'rows':[560,561,562],'note':'The source omits who is battered in the smitten/battered joke. Prior speech concerns monsters being charmed; the draft introduced an unsupported injured you. Corrections use an impersonal situation subject without choosing who is battered.'},
        {'rows':[570,571,572],'note':'Berserk Summoning is the root-approved provisional term; lack of restraint accurately conveys the warning that enemies will not act responsibly.'},
        {'rows':[574,575,576,577,578],'note':'Yukres Village matches the location glossary. Beardy follows story_additions_0.1.54.json for Jakini; the next group names Jakini and resolves the nickname.'},
        {'rows':[608,609,610,617,618,619],'note':'Lawler and Magna/Toris Clesment follow current root-approved terminology and existing references. The named oath is kept distinct from the enemy Dielgo.'},
        {'rows':[628,629,630,638],'note':'Seat of Core Cognizance and Dielgo of Primal Sin are approved provisional compounds; Clyps remains an established provisional reading.'},
    ],[
        {'rows':[560,561],'note':'The identity of who is battered remains unspecified; corrected English uses that as a grammatical subject referring to the situation.'},
        {'rows':[574,575],'note':'The alarmed names remain trailing phrases, with the exact threat unspoken.'},
        {'rows':[581,582,583],'note':'The gunpowder scheme is intentionally unfinished before laughter.'},
        {'rows':[597,598],'note':'The shaking character leaves the disbelief unfinished.'},
        {'rows':[599,600,601,602,603,604],'note':'Both protagonist variants retain the unknown sensed identity rather than naming it.'},
        {'rows':[625,626,627,631,632,633],'note':'Speculative conditionals intentionally omit the feared consequences, matching the source suspense.'},
    ],write)
    review(640,641,[[631,641]],[560,640],[
        {'rows':[639,640,641],'note':'Complete control over the Core Cognizance conveys full command of its functions; cross-slice if-clause and trailing speculation are intact.'},
    ],[
        {'rows':[639,640,641],'note':'The feared consequence is unspoken in source and remains then could it...!? in English.'},
    ],write)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();main(a.write)
