"""Compose reviewed 0.1.20 menu translations, native art, and VWF."""
from sn3_archive import ROOT
from menu_text_020 import prepare as text_prepare
from menu_vwf_020 import prepare as strip_prepare
from help_vwf_020 import prepare as help_prepare
from list_vwf_020 import prepare as list_prepare
from menu_graphics_020 import prepare as graphics_prepare

def prepare_elf():
    elf,text=text_prepare()
    elf,strip=strip_prepare(elf)
    elf,help_report=help_prepare(elf)
    elf,list_report=list_prepare(elf)
    text.update(strip_vwf=strip,help_vwf=help_report,list_vwf=list_report)
    return elf,text

def prepare_tables(source):
    graphics,report=graphics_prepare(source)
    return {int(k.split(':')[1]):v for k,v in graphics.items()},{},source.resource('00.DAT',44),dict(units=[],tables=[],graphics=report)
