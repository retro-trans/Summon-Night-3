"""Read-only exact short UI label search."""
from sn3_archive import ROOT,GameSource
needle='はじまりの浜辺'.encode('cp932')
with GameSource(ROOT/'work/output/0.1.60/Summon_Night_3_EN_0.1.60.iso') as s:
 for bank,idx in s.indexes.items():
  found=[]
  for e in idx['entries']:
   b=s.resource(bank,e['id']);at=b.find(needle)
   if at>=0:found.append((e['id'],hex(at)))
  if found:print(bank,found,flush=True)
