"""Retain native metrics for four source reaction symbols, with glyph proof."""
import struct
from font_metrics import collect as latin_collect,ROOT,ELF_SEGMENT_OFFSET,MAP_VA,digest

def collect():
    report,font=latin_collect();elf=(ROOT/'work/source/EBOOT.elf').read_bytes()
    count=(len(font)-28)//128
    for c in '○△□×':
        lead,trail=c.encode('cp932');page=struct.unpack_from('<I',elf,ELF_SEGMENT_OFFSET+MAP_VA+(lead-0x80)*4)[0]
        assert page
        index=struct.unpack_from('<H',elf,ELF_SEGMENT_OFFSET+page+(trail-0x40)*2)[0]
        assert 1<=index<=count
        bitmap=font[28+(index-1)*128:28+index*128];assert any(bitmap)
        report['characters'][c]=dict(proposed_advance_pixels=16,glyph_index=index,glyph_sha256=digest(bitmap),metric_basis='Unmodified native16px advance; symbol is not in the Latin hook lookup table.')
    return report,font
