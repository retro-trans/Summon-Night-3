"""Preview derivative builder and isolated QA helper generation before writing."""
import argparse,json
from sn3_archive import ROOT
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    text=(ROOT/'tools/build_cache_065.py').read_text()
    text=text.replace('0.1.64','0.1.65').replace('0.1.65\'','0.1.66\'').replace('0.1.65.iso','0.1.66.iso')
    # Set the prior input explicitly after replacing target-version literals.
    text=text.replace("BASE=ROOT/'work/output/0.1.66'","BASE=ROOT/'work/output/0.1.65'")
    text=text.replace('from cache_065 import prepare_names,prepare_elf','from status_fix_066 import prepare_tables,prepare_elf')
    text=text.replace("['build_cache_065.py','cache_065.py','verify_cache_065.py','verify_stability_064.py','setup_cache_065.py']","['build_status_066.py','status_fix_066.py','verify_status_066.py','setup_status_066.py']")
    text=text.replace('work/translation/en/skills_0.1.66','work/translation/en/status_0.1.66')
    text=text.replace('work/translation/en/skills_0.1.65','work/translation/en/status_0.1.66')
    text=text.replace("tables02,tbr=prepare_names(source);tables01={};master=source.resource('00.DAT',44)","tables02,tables01,master,tbr=prepare_tables(source)")
    text=text.replace('cache065_arena=dict(art=tbr,elf=elf_report)','status066_fix=dict(labels=tbr,elf=elf_report)')
    text=text.replace("comparison_build='0.1.66'","comparison_build='0.1.65'")
    text=text.replace('Summon_Night_3_EN_0.1.65.iso','Summon_Night_3_EN_0.1.66.iso')
    launch=(ROOT/'tools/launch_release_065.ps1').read_text().replace('release065-runtime','status066-runtime').replace('0.1.65','0.1.66').replace('19402','19403')
    runtime=(ROOT/'tools/release_runtime_065.py').read_text().replace('release065','status066').replace('release_0.1.65','status_0.1.66').replace('0.1.65','0.1.66').replace('19402','19403')
    files={'tools/build_status_066.py':text,'tools/launch_status_066.ps1':launch,'tools/status_runtime_066.py':runtime}
    print(json.dumps(dict(mode='write' if a.write else 'preview',files=list(files),builder_sample=text[:1250]),indent=2))
    if a.write:
        for name,value in files.items():
            path=ROOT/name;assert not path.exists();path.write_text(value,encoding='utf8')
if __name__=='__main__':main()
