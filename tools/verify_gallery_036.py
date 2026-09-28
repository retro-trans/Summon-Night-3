from gallery_036 import prepare_tables,BASE
from sn3_archive import GameSource

def verify():
    with GameSource(BASE/'Summon_Night_3_EN_0.1.35.iso') as source:
        _,_,_,r=prepare_tables(source)
    return dict(tutorial_titles=len(r['tables'][0]['changes']),comment_labels=len(r['tables'][1]['changes']),tables=r['tables'],graphics=r['graphics'])
