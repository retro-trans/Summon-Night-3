"""Record sourced spellings and bounded character guidance for Chapters2/3."""
import argparse,json
from sn3_archive import ROOT
WIKI='https://summonnight.fandom.com/wiki/Summon_Night_3'
GALLERY=WIKI+'/PSP_Gallery'
def entry(jp,en,role,gender=None,personality=None,url=WIKI,notes=None):
    return dict(source_name=jp,target_name=en,category='character',role=role,gender=gender,gender_status='unverified; do not infer from voice or name' if gender is None else 'supported by cited profile',nickname=None,nickname_status='No separate nickname established in checked sources',personality=personality or 'Not established in checked profile',evidence=[dict(url=WIKI,supports=['spelling']),dict(url=url,supports=['profile'])],notes=notes,status='researched',checked_on='2026-09-27')
def prepare():
    r='https://renote.net/articles/17584/page/'
    entries=[
      entry('アール','R','Nup\'s robot companion from Loreilal',url=r+'11',notes='Named after the R on its body. Preserve its electronic beeps; do not invent spoken meanings.'),
      entry('テコ','Teco','Will\'s catlike companion from Maetropa',url=r+'12',notes='Intelligent enough to read magic books. Name refers to its waddling walk.'),
      entry('オニビ','Onibi','Belfrau\'s fiery yokai companion from Silturn',url=r+'12',notes='Named for its fireball appearance. Do not infer gender.'),
      entry('キユピー','Quiupy','Alieze\'s angel-like companion from Sapureth',personality='Relaxed, sleepy appearance',url=r+'12',notes='Name combines cry and appearance. Do not infer base-form gender from its later girl-like transformation.'),
      entry('アルディラ','Ardylia','Guardian of Latrix; a Beiger from Loreilal','female','Rational and intelligent; uncomfortable with emotional matters',r+'13'),
      entry('キュウマ','Kyuuma','Oni ninja serving Misumi; guardian of the Land of Wind and Thunder',personality='Earnest, dutiful and reserved',url=r+'13'),
      entry('ファルゼン','Falzen','Armored guardian of the Realm of In Between',personality='Terse; speaks only when needed',url=r+'13',notes='Hidden identity is Falier, a woman. Keep the early armored persona ambiguous; do not reveal this through invented pronouns.'),
      entry('ヤッファ','Yafha','Tigerlike guardian of Yukres Village',personality='Lazy but an experienced mediator',url=r+'13'),
      entry('クノン','Cunnon','Medical mechanical doll and Ardylia\'s attendant',personality='Flat affect; limited understanding of emotions',url=r+'14'),
      entry('ミスミ','Misumi','Oni princess and leader of the Land of Wind and Thunder; Subaru\'s mother','female',url=r+'14'),
      entry('スバル','Subaru','Misumi\'s son','male','Wants to become strong and protect his mother',r+'14'),
    ]
    for jp,en,category,url in [
      ('シャルトス','Shartos','item','https://summonnight.fandom.com/wiki/Rexx'),
      ('リィンバウム','Lyndbaum','world','https://summonnight.fandom.com/wiki/Aty'),
      ('ラトリクス','Latrix','settlement',WIKI),
      ('風雷の郷','Land of Wind and Thunder','settlement',WIKI),
      ('狭間の領域','Realm of In Between','settlement',WIKI),
      ('ユクレス村','Yukres Village','settlement',WIKI),
      ('護人','Guardian','role',WIKI),
      ('無色の派閥','Colorless Faction','organization','https://summonnight.fandom.com/wiki/Rexx')]:
        entries.append(dict(source_name=jp,target_name=en,category=category,evidence=[dict(url=url,supports=['spelling'])],status='wiki_verified'))
    return dict(language='en',version='0.1.12',scope='Chapter2/3 names and profile guidance; existing opening/ship/realm glossary remains authoritative.',entries=entries,unresolved_terms=['ストラ','ロアーズ','ベイガー','フラーゼン'],change_log=['Added sourced island and companion names; unknown fields remain explicit.'])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();d=prepare()
    print(json.dumps(dict(mode='write' if a.write else 'dry run',entries=d['entries'],unresolved=d['unresolved_terms']),ensure_ascii=False,indent=2))
    if a.write:(ROOT/'work/glossary/island_0.1.12.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
