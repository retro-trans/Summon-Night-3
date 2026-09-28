"""Record source/target reviews actually completed by the Chapter 7 translator."""
import argparse,json,hashlib
from chapter_source_014 import load
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT
REVIEWED=[135,136,137,138,139,140,141,143,144,145,146,147,148,158,159,160,161,162,163,164,166,167,168,169,170,171,181,182,183,184,185,186,187,189,190,191,192,193,194]
FIXES={144:{37:'to be liked?'},148:{26:'a summoning spell misfiring...'},166:{73:'I know I did terrible things.'},170:{19:'Your pupil deserves credit for enduring it this long.'},189:{66:'"I am already dead..."'},190:{28:'for hopeless cases.'}}
UNCERTAINTIES={144:['The final thought omits the person whose affection is being considered; the context includes both Yafha and Marurur. Removed an unnecessary female pronoun to preserve ambiguity.'],148:['Kept the technical distinction between a spell misfire and a summon-beast rampage established in Chapter 5.'],166:['The atonement scene concerns Fariel personally; retained her individual responsibility rather than replacing it with collective we.'],170:['Scarrel praises the pupil for enduring the difficult situation; the original target made this an abstract claim about things holding together.'],189:['The final narration quotes Fariel saying she is already dead; corrected tense and marked it as a quotation.'],190:['Hopeless cases preserves the characterization in the source; nowhere else to turn instead asserted a circumstance the source does not give.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();total=0
 for number in REVIEWED:
  resource,rows,data=load(number);folder=ROOT/f'work/translation/en/chapters_0.1.14/{number:04d}';slices=[];seen=[]
  for path in sorted(folder.glob('slice_*.targets.json')):
   draft=json.loads(path.read_text(encoding='utf-8'));rr=sorted(t['resource_row'] for t in draft['translations'].values());assert len(rr)<=80;seen+=rr
   for t in draft['translations'].values():
    r=rows[t['resource_row']];assert t['source_sha256']==r['source_sha256'];src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');encode_dialogue(t['text'],src)
   slices.append({'target_file':str(path.relative_to(ROOT)).replace('\\','/'),'target_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'assigned_range':[min(rr),max(rr)],'translation_count':len(rr)})
  assert seen==list(range(11,len(rows)));fixes=[]
  for n,t in FIXES.get(number,{}).items():
   r=rows[n];src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');encode_dialogue(t,src);fixes.append({'resource_row':n,'source_sha256':r['source_sha256'],'text':t})
  doc={'resource_id':resource['id'],'review_type':'independent_meaning_review','semantic_complete':True,'independent_review':True,'reviewed_rows':seen,'reviewed_slices':slices,'corrections':fixes,'rows_examined':{'physical_range_inclusive':[6,len(rows)-1],'count':len(rows)-6},'uncertainties':UNCERTAINTIES.get(number,[]),'method':'Read and compared every assigned source/target row in slices of at most 80, with adjacent context. Reviewer did not author these drafts. Structural checks do not substitute for that meaning review.','change_log':['Build 0.1.14: independently reviewed all optional/night dialogue rows in this resource.']}
  print(number,'rows',len(seen),'corrections',fixes);total+=len(seen)
  if a.write:(folder/'independent_review.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Reviewed total',total)
if __name__=='__main__':main()
