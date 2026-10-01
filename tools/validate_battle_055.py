"""Validate reviewed battle targets; save an English-only acceptance checkpoint."""
import argparse,copy,json,struct
from unittest.mock import patch
from battle_pass_055 import scope,draft_targets,FOLDER
from battle_accept_055 import validate_review
from battle_compiler_055 import prepare,simulate
from battle_source_024 import ROOT,load,sha

def negative_checks():
    drafts,_=draft_targets()
    base=json.loads((FOLDER/'review_0000.json').read_text('utf8'))
    def rejected(doc,start=0):
        try:validate_review(doc,start,drafts)
        except (AssertionError,KeyError):return
        raise AssertionError('Invalid review accepted')
    d=copy.deepcopy(base);d['draft_inputs_sha256']={};rejected(d)
    d=copy.deepcopy(base);d['reviewer']='author';rejected(d)
    d=copy.deepcopy(base);d['source_ranges_examined']=[];d['rows_examined']=0;rejected(d)
    d=copy.deepcopy(base);d['rows_examined']+=1;rejected(d)
    d=copy.deepcopy(base);key=next(iter(d['draft_inputs_sha256']));d['draft_inputs_sha256'][key]='0'*64;rejected(d)
    middle=json.loads((FOLDER/'review_0320.json').read_text('utf8'))
    d=copy.deepcopy(middle);d['corrections'][0]['resource']=136;rejected(d,320)
    d=copy.deepcopy(middle);d['corrections']*=2;rejected(d,320)
    resource,rows,source=load(148);bad=bytearray(source)
    # The extra append is accepted only for an empty pool entry, never real text.
    pool=struct.unpack_from('<I',source,20)[0]*2;bad[pool:pool+2]=b'A\x00'
    with patch('battle_compiler_055.load',return_value=(resource,rows,bytes(bad))):
        try:prepare(148)
        except (AssertionError,ValueError):pass
        else:raise AssertionError('Nonempty special append was accepted')
    return 8

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    count=negative_checks();reports=[];bindings={}
    for number in sorted({r['resource'] for r in scope()}):
        data,report,inputs=prepare(number)
        assert all(len(page)<=3 and all(line['pixels']<=208 for line in page) for g in report['groups'] for page in g['pages'])
        if number==148:
            group=next(g for g in report['groups'] if g['rows']==[55,56])
            assert group['original_span']==[1704,1736]
            old=simulate(load(number)[2],1704,1736)
            assert old[0]['lines'][-1]=='' and old[0]['speaker']==('source_value',9,0,(26,))
            assert all(line['text'] for page in group['pages'] for line in page)
        reports.append(report);bindings.update(inputs)
    for name in ('tools/validate_battle_055.py','tools/dialogue_encoding.py','tools/dialogue_layout.py','tools/font_metrics_014.py','tools/stages_patch.py','tools/chapter_patch_014.py','tools/sn3_vm.py','tools/script_strings.py','tools/story_source_054.py'):
        bindings[name]=sha((ROOT/name).read_bytes())
    checkpoint=dict(version='0.1.55',status='reviewed translation inputs; not a released build',
        source_fragments=sum(r['covered_source_rows'] for r in reports),resources=len(reports),
        dialogue_groups=sum(len(r['groups']) for r in reports),
        generated_pages=sum(len(g['pages']) for r in reports for g in r['groups']),
        negative_checks_passed=count,inputs_sha256=bindings,reports=reports,
        limitations=['No ISO or release created.','Not yet tested in PPSSPP.','Google Sheet has not been changed by this checkpoint.'])
    assert checkpoint['source_fragments']==642 and checkpoint['resources']==27
    samples={str(t['ordered_index']):t['text'] for r in reports for t in r['targets'].values() if t['ordered_index'] in (13,211,213,374,560,561,628)}
    print(json.dumps(dict(mode='write' if a.write else 'dry-run',**{k:v for k,v in checkpoint.items() if k not in ('reports','inputs_sha256')},samples=samples),indent=2))
    if a.write:
        (FOLDER/'accepted.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
