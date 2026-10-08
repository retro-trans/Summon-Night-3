"""Mechanically crop generated glyphs and assemble native-size menu atlases."""
import json,shutil
import numpy as np
from PIL import Image
from sn3_archive import ROOT,GameSource
from menu_art_075 import descend,tiles as old_tiles,FOLDER as OLD
from sn3_ui_textures import texture_records,decode_texture
F=ROOT/'work/ui/menus_0.1.76';D=ROOT/'work/scratch/menus076-discovery'
LABELS='Music Volume|Event Voices|Forecast|Cursor Direction|L/R Function|Map Rotation|Unit Cycling|Ending|Events|Artwork|Tutorial|Glossary|View Event|Back|Confirm|Cancel|Exit Options|System'.split('|')

def glyphs():
 return cut(F/'generated/atlas.png',LABELS)
def cut(path,labels):
 im=Image.open(path).convert('RGBA');a=np.asarray(im.getchannel('A'));on=(a>200).sum(axis=1)>3;bands=[];start=None
 for y,v in enumerate(list(on)+[False]):
  if v and start is None:start=y
  if not v and start is not None:bands.append((start,y));start=None
 merged=[]
 for lo,hi in bands:
  if merged and lo-merged[-1][1]<18:merged[-1]=(merged[-1][0],hi)
  else:merged.append((lo,hi))
 assert len(merged)==len(labels),(len(merged),merged)
 result={}
 for text,(lo,hi) in zip(labels,merged):
  p=im.crop((0,lo,im.width,hi));alpha=p.getchannel('A').point(lambda v:v if v>100 else 0);p.putalpha(alpha);p=p.crop(alpha.getbbox());result[text]=p
 return result

def small(im,h):return im.resize((round(im.width*h/im.height),h),Image.Resampling.LANCZOS)
def main():
 p=F/'generated';p.mkdir(parents=True,exist_ok=True)
 origin=ROOT/'work/scratch/menus076-generation-paths.json';paths=json.loads(origin.read_text())
 for name,path in paths.items():shutil.copyfile(path,p/(name+'.png'))
 art=glyphs();entries=[]
 def save(path,sprite,im,text,**kw):
  name='_'.join(map(str,path))+'_'+str(sprite);im.save(p/(name+'.png'));entries.append(dict(bank='02.DAT',path=path,sprite=sprite,text=text,image=name+'.png',**kw))
 with GameSource(ROOT/'work/output/0.1.75/Summon_Night_3_EN_0.1.75.iso') as s:
  d=descend(s.resource('02.DAT',33),[2]);rows=texture_records(d)
  for nums,text in [([3,4],'Music Volume'),([6],'Event Voices'),([7],'Forecast'),([8],'Cursor Direction'),([9],'L/R Function'),([10],'Music Volume'),([11],'Event Voices'),([12],'Forecast'),([13,14],'Cursor Direction'),([15],'L/R Function'),([27],'Map Rotation'),([36],'Map Rotation'),([31,32],'Unit Cycling'),([37,38],'Unit Cycling')]:
   sizes=[decode_texture(d,rows[n]).size for n in nums];w=sum(x[0] for x in sizes);h=sizes[0][1];assert all(x[1]==h for x in sizes)
   g=small(art[text],11)
   if g.width>w-4:g=g.resize((w-4,11),Image.Resampling.LANCZOS)
   im=Image.new('RGBA',(w,h));im.alpha_composite(g,(2,(h-11)//2));x=0
   for n,(width,height) in zip(nums,sizes):save([33,2],n,im.crop((x,0,x+width,h)),text,font_height=11,left_margin=2);x+=width
  original=Image.open(D/'original_33_3_5.png').convert('RGBA');gen=Image.open(p/'blank_frame.png').convert('RGBA');gen.putalpha(gen.getchannel('A').point(lambda v:255 if v>100 else 0));gen=gen.crop(gen.getbbox()).resize(original.size,Image.Resampling.LANCZOS)
  current=descend(s.resource('02.DAT',33),[3]);frame=decode_texture(current,texture_records(current)[5]);box=(96,218,336,241);frame.paste(gen.crop(box),box)
  # Native icons are preserved, and the footer has one label set per mode.
  for icon,where in [((118,221,132,237),(118,221)),((176,221,190,237),(176,221))]:frame.alpha_composite(original.crop(icon),where)
  confirm=small(art['Confirm'],9).resize((36,9),Image.Resampling.LANCZOS)
  frame.alpha_composite(confirm,(136,224));frame.alpha_composite(small(art['Exit Options'],9),(195,224))
  save([33,3],5,frame,'Options frame',changed_box=list(box))
  footer=gen.crop((80,216,336,248));src=Image.open(D/'original_33_2_0.png').convert('RGBA')
  footer.alpha_composite(src.crop((41,6,57,23)),(41,6));footer.alpha_composite(src.crop((99,6,115,23)),(99,6))
  footer.alpha_composite(confirm,(61,10));footer.alpha_composite(small(art['Cancel'],9),(119,10));save([33,2],0,footer,'Confirm / Cancel')
  # The generated heading is fitted to the original visible banner bounds.
  old=Image.open(D/'ending_heading.png').convert('RGBA');e=Image.open(p/'ending.png').convert('RGBA');a=e.getchannel('A').point(lambda v:255 if v>100 else 0);e.putalpha(a);e=e.crop(a.getbbox());box=old.getchannel('A').getbbox();native=Image.new('RGBA',old.size);native.alpha_composite(e.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS),box[:2]);save([3569,3],0,native,'Ending')
  spec=json.loads((OLD/'atlas_spec.json').read_text());shops={state:old_tiles('shop_'+state,spec['shop'],1) for state in ('selected','unselected')}
  words=json.loads((D/'word_groups.json').read_text())
  for path,sprite,text,state in [([1332,6],0,'Inventory','unselected'),([1341,6],0,'Replay','unselected'),([1341,8],0,'Endless Halls','unselected')]:
   group=next(g for g in words if any(e['path']==path and e['sprite']==sprite for e in g))
   for e in group:save(e['path'],e['sprite'],shops[state][text].resize(tuple(e['size']),Image.Resampling.LANCZOS),text)
  d=descend(s.resource('02.DAT',1334),[10,39]);system=decode_texture(d,texture_records(d)[0])
  group=next(g for g in words if any(e['path']==[1332,14] and e['sprite']==29 for e in g))
  for e in group:save(e['path'],e['sprite'],system,'System')
  extra_labels=['Artwork','Sound','Night Talks']+[f'Chapter {i}' for i in range(1,21)]+['Epilogue'];extra=cut(p/'gallery_atlas.png',extra_labels)
  for n,text in [(3,'Artwork'),(4,'Artwork'),(5,'Sound'),(6,'Sound'),(7,'Night Talks'),(8,'Night Talks'),(9,'Ending'),(10,'Ending')]:
   g=small(extra.get(text,art.get(text)),15);g=g.resize((min(104,g.width),15),Image.Resampling.LANCZOS);native=Image.new('RGBA',(112,32));native.alpha_composite(g,((112-g.width)//2,8));save([3567,n],0,native,text)
  blank=Image.open(D/'original_3570_3_24.png').convert('RGBA');g=small(extra['Night Talks'],14);blank.alpha_composite(g,((208-g.width)//2,15));save([3568,5],0,blank,'Night Talks')
  chapter=Image.open(p/'chapter_blank.png').convert('RGBA');chapter.putalpha(chapter.getchannel('A').point(lambda v:255 if v>100 else 0));chapter=chapter.crop(chapter.getbbox()).resize((80,32),Image.Resampling.LANCZOS)
  for i,label in enumerate(extra_labels[3:]):
   native=chapter.copy();g=small(extra[label],10);g=g.resize((min(72,g.width),10),Image.Resampling.LANCZOS);native.alpha_composite(g,((80-g.width)//2,4));save([3568,6+i],0,native,label)
  names={}
  for i,labels in enumerate(spec['names']):names.update(old_tiles('names_'+str(i),labels))
  labels='Nup|Belfraw|Alieze|Will|Ardylia|Kyuuma|Falzen|Fariel|Yafha|Kyle|Sonolar|Scarrel|Yard|Kunon|Misumi|Subaru|Phlaiz|Marurur|Azlier'.split('|')
  for n,label in enumerate(labels,28):
   d=descend(s.resource('02.DAT',3568),[n]);size=decode_texture(d,texture_records(d)[0]).size;native=Image.new('RGBA',size);g=small(names[label],min(size[1]-4,18));g=g.resize((min(size[0]-4,g.width),g.height),Image.Resampling.LANCZOS);native.alpha_composite(g,((size[0]-g.width)//2,(size[1]-g.height)//2));save([3568,n],0,native,label)
 (ROOT/'work/translation/en/menus_0.1.76/graphics.json').write_text(json.dumps(dict(entries=entries),indent=2)+'\n')
 (F/'atlas_spec.json').write_text(json.dumps(dict(labels=LABELS,font_height=11,footer_font_height=9),indent=2)+'\n');print(len(entries))
if __name__=='__main__':main()
