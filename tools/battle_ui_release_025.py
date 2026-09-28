"""Compose battle command artwork and reviewed native text."""
from battle_ui_text_025 import prepare_elf,prepare_tables as text_tables
from battle_ui_graphics_025 import prepare as art_prepare

def prepare_tables(source):
 p02,p01,master,r=text_tables(source);art02,art01,images,report=art_prepare(source)
 assert not set(p02)&set(art02) and not set(p01)&set(art01)
 p02.update(art02);p01.update(art01);r['graphics']=report
 return p02,p01,master,r
