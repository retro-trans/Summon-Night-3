"""Normalize glossary spellings after whole-resource meaning review; dry-run default."""
import argparse,json,re
from story_source_054 import FOLDER,target_text
from story_review_audit_054 import audit
from sn3_archive import ROOT
from stages_patch import sha

def run(number,write=False):
    folder=FOLDER/f'{number:04d}'
    proof=audit(number);assert not proof['errors'],proof['errors']
    coverage=next(x for x in proof['resources'] if x['resource']==number)
    targets=sorted(folder.glob('slice_*.targets.json'))
    scoped_chapter={410:16,433:17,458:18,459:18,460:18,
                    461:'18b',462:'18b',463:'18b',468:'18b',469:'18b',
                    465:'18c',473:'18c',475:'18c',479:'18c'}.get(number)
    scoped_glossary=ROOT/f'work/glossary/chapter{scoped_chapter}_terms_0.1.54.json'
    if number in (482,485):
        scoped_glossary=ROOT/f'work/glossary/story_branch{number}_terms_0.1.54.json'
    scoped_rules={}
    if scoped_chapter is not None or number in (482,485):
        scoped_rules={r['resource_row']:r for r in json.loads(scoped_glossary.read_text('utf8'))['normalization_by_resource'][str(number)]}
    count=sum(len(json.loads(p.read_text('utf8'))['translations']) for p in targets)
    assert coverage['reviewed_rows_with_current_proof']==count and coverage['rows_awaiting_correction']==0
    changes=[];outputs=[]
    for path in targets:
        raw=path.read_bytes();doc=json.loads(raw);rows=[]
        for t in doc['translations'].values():
            old=t['text'];new=target_text(old)
            new=re.sub(r'\bRed Gloves\b','Crimson Gloves',new)
            new=re.sub(r'\bdarima\b','Dalima',new)
            for pattern, canonical in ((r'\b(?:[Tt]he )?Blue Wise Emperor\b','Shartos'),
                    (r'\bAzure Wise Emperor\b','Azure Sage Emperor'),
                    (r'\bOni Demon Realm\b','Yokai World'),
                    (r'\bRicht\b','Rikuto'),
                    (r'\bDemon Princess of the White South Wind\b','Oni Princess of the Summer Wind'),
                    (r'\bDemon Princess\b','Oni Princess'),
                    (r'\b(?:[Tt]he )?Red Tyrant\b','Crissles'),
                    (r'\bMeitolpa\b','Maetropa'), (r'\bSapeleth\b','Sapureth'),
                    (r'\bAzlia\b','Azlier'), (r'\b(?:Isura|Isla)\b','Ishlar'),
                    (r'\bThorn Princess\b','Lady of Thorns'),
                    (r'\bOrfle\b','Orful'), (r'\bSapuresu\b','Sapureth'),
                    (r'\bKilsless\b','Crissles'), (r'\bFuraika Village\b','Land of Wind and Thunder'),
                    (r'\bCore Mark\b','Core Cognizance'), (r'\bVAR-Xe-LD\b','Var-Xe-LD')):
                new=re.sub(pattern,canonical,new)
            if t['resource_row'] in scoped_rules:
                rule=scoped_rules[t['resource_row']]
                assert t['source_sha256']==rule['source_sha256'], 'Scoped glossary source identity changed'
                for replacement in rule.get('replacements',[rule]):
                    assert new.count(replacement['from'])==1, (number,t['resource_row'],'Scoped glossary term changed')
                    new=new.replace(replacement['from'],replacement['to'],1)
            if old!=new:
                rows.append(dict(resource_row=t['resource_row'],before=old,after=new));t['text']=new
        if rows:
            out=(json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode('utf8')
            changes.append(dict(target_file=str(path.relative_to(ROOT)).replace('\\','/'),target_before_sha256=sha(raw),target_after_sha256=sha(out),changes=rows))
            outputs.append((path,out))
    glossary=['work/glossary/character_reference_sn6_vita.json','work/glossary/terminology_preferences.json','work/glossary/story_additions_0.1.54.json','work/glossary/chapter6_terms_0.1.14.json','work/glossary/chapter48_story_terms_0.1.14.json','work/glossary/setup_ui.json','work/glossary/story_core_terms_0.1.54.json','work/glossary/island_0.1.12.json','work/glossary/chapter13_titles_0.1.54.json']
    if number >= 387:
        glossary.append('work/glossary/chapter15_terms_0.1.54.json')
        glossary.extend(['work/glossary/chapter48_additions_0.1.14.json', 'work/glossary/chapter8_fiction_0.1.14.json'])
    if scoped_rules:
        glossary.append(scoped_glossary.relative_to(ROOT).as_posix())
    receipt=dict(status='Names normalized after meaning corrections; no semantic rewrites',resource=number,glossary_inputs_sha256={n:sha((ROOT/n).read_bytes()) for n in glossary},files=changes)
    print(json.dumps(dict(mode='write' if write else 'dry-run',**receipt),ensure_ascii=False,indent=2))
    if write and changes:
        record=folder/'name_normalization.json';assert not record.exists()
        for path,out in outputs:path.write_bytes(out)
        record.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resource',type=int);p.add_argument('--write',action='store_true');a=p.parse_args();run(a.resource,a.write)
