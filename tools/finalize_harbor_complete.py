"""Record inspected final-ISO evidence and update current acceptance metadata."""
import argparse,json,hashlib
from pathlib import Path
from sn3_archive import ROOT

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    folder=ROOT/'work/output/0.1.11';mp=folder/'manifest.json';m=read(mp)
    runtime=ROOT/'work/ui/harbor_complete_0.1.11/runtime';traces=sorted(runtime.glob('final*.trace.json'))
    ids=set()
    for path in traces:
        trace=read(path);assert trace['candidate_sha256']==m['output_sha256']
        assert trace['live_script_sha256']==m['script_changes'][0]['decoded_sha256']
        for state in trace['states']:
            ids.update(r['id'] for r in state['lines'] if r['id'])
    assert all('harbor_complete_'+g+':page:0:line:0' in ids for g in ('585_586_587','594_595_596'))
    names=read(runtime/'name_table_validation.json');assert names['all_bytes_match'] and names['candidate_sha256']==m['output_sha256']
    captures=[]
    for file,description in [('gender_selected.png','Girl option visibly selected'),
        ('salome_emphasis_full.png','Complete two-line emphatic speech; no clipping'),
        ('salome_future.png','Complete three-line young-lady continuation; no clipping'),
        ('backlog_salome.png','English Salome speaker labels and complete translated continuation'),
        ('continuation.png','Normal dialogue continues after closing backlog')]:
        path=runtime/file;meta=read(path.with_suffix('.json'));digest=sha(path)
        assert digest==meta['capture']['png_sha256']
        captures.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=digest,visual_review=description))
    report=dict(version='0.1.11',candidate_sha256=m['output_sha256'],
        emulator='PPSSPP 1.20.4 isolated software-renderer instance; fresh boot; Rexx/Belfrau route',
        scope='Opening through Salome harbor dialogue, both reported special-style groups, separate name table, backlog and normal continuation.',
        decoded_script_sha256=m['script_changes'][0]['decoded_sha256'],complete_script_matches_memory=True,
        physical_text_ids_observed=len(ids),new_logical_rows_visually_verified=[585,586,587,594,595,596],
        name_table_validation=names,captures=captures,
        traces=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in traces],
        user_emulator_untouched=True,all_routes_playtested=False,audio_playback_retested=False,
        limits=['Other newly translated branches (exclamations, quiz, music note, young-master counterpart) have static checks only.',
                'Later scenes, unrelated interface labels and full-game behavior are not covered.'],
        qa_tools_sha256={p:sha(ROOT/p) for p in ['tools/harbor_complete_qa.py','tools/verify_backlog_names_live.py']})
    print(json.dumps(dict(mode='write' if a.write else 'dry run',candidate=m['output_sha256'],
        physical_text_ids_observed=len(ids),new_logical_rows_visually_verified=report['new_logical_rows_visually_verified'],
        captures=captures,acceptance='reported_dialogue_and_backlog_verified_partial_translation'),indent=2))
    if not a.write:return
    dest=folder/'harbor_runtime_validation.json';assert not dest.exists();dest.write_text(json.dumps(report,indent=2)+'\n')
    m['runtime_validation']=dict(report=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),scope=report['scope'])
    m['static_validation'].update(runtime_verified=True,visual_verified=True)
    mp.write_text(json.dumps(m,indent=2)+'\n')
    sp=ROOT/'docs/translation_status.json';s=read(sp)
    s['latest_candidate'].update(acceptance='reported_dialogue_and_backlog_verified_partial_translation',runtime_verified=True,
        visual_verified=True,scope_limit=report['scope']+' Other branches statically checked; later game not translated.',
        runtime_report=dest.relative_to(ROOT).as_posix())
    sp.write_text(json.dumps(s,indent=2)+'\n')

if __name__=='__main__':main()
