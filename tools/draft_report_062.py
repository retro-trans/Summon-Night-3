"""Preview reported awakening and Mujina translations before writing."""
import argparse,json
from sn3_archive import ROOT
TEXT=ROOT/'work/translation/en/report_0.1.62/strings.json'
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 prior=json.loads((ROOT/'work/translation/en/report_0.1.61/strings.json').read_text(encoding='utf8'))
 spells=[dict(record=64,slot=8,source='すすオトシ',english='Soot Drop'),dict(record=65,slot=8,source='すすシバキ',english='Soot Strike'),dict(record=66,slot=8,source='双舞・闇シバキ',full_translation='Twin Dance: Dark Strike',english='Twin Dark Strike')]
 help=['Awaken; ailment immunity.','No poss.; Berserk Summon OK']
 skills=[dict(record=n,slot=8,source=jp,english=en) for n,jp,en in [(0,'抜剣覚醒','Blade Awakening'),(1,'抜剣覚醒・改','Blade Awakening+'),(2,'抜剣覚醒・暴走','Berserk Blade'),(3,'抜剣覚醒','Blade Awakening')]]
 spec=dict(version='0.1.62',source_build='0.1.61',spells=spells,skills=skills,awakening=dict(full_translation="Release the sword's power to awaken. Immune to all status ailments and possession; enables Berserk Summoning.",help=help),
  summon=dict(record=23,base_name='Mujina',alternates=[dict(slot=10,source='ポン太君',english='Ponta-kun'),dict(slot=11,source='チャガマ',english='Chagama')],source=['踊り好きなたぬきの妖怪　夜な夜な宴を開いて大騒ぎをする','お風呂ぎらいで有名'],full_translation='A tanuki yokai who loves dancing. It throws rowdy feasts every night and is famous for hating baths.',help=['Dancing tanuki yokai; noisy','night feasts. Hates baths.'],compression='The compact lore retains dancing, tanuki/yokai, noisy nightly feasts and hatred of baths; fame is implicit in this profile.'),
  set_hint=dict(english='Set',icon_x=424,text_x=440),banner_names=sorted(set(prior['banner_names']+[x['english'] for x in spells+skills])),attacks=prior['attacks'],discovery_placeholders_preserved=True,references=['https://w.atwiki.jp/sn3psp/pages/94.html','https://w.atwiki.jp/sn3psp/pages/108.html'])
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(TEXT),spec=spec),ensure_ascii=False,indent=2),flush=True)
 if a.write:TEXT.parent.mkdir(parents=True,exist_ok=True);TEXT.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
