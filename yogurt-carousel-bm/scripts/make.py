import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
S=sys.argv[1]
B='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
SB='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
def load(i):
    im=Image.open(f'{S}/crop/{i}.png').convert('RGB')
    return im.resize((1100,1464))
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def title(im,text,cy,blank,size=44,maxw=920):
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,1100,blank[1]),fill='white')
    f=ImageFont.truetype(B,size)
    lines=wrap(d,text,f,maxw); lh=int(size*1.25)
    y=cy-lh*len(lines)/2
    for l in lines:
        w=d.textlength(l,font=f); d.text(((1100-w)/2,y),l,font=f,fill=(17,17,17)); y+=lh
def cups(im):
    a=np.array(im); d=ImageDraw.Draw(im)
    for box,lines in [((225,515,425,595),['20% lemak']),((655,505,865,610),['80%','bebas lemak'])]:
        c=tuple(int(v) for v in np.median(a[box[1]:box[3],box[0]:box[0]+10].reshape(-1,3),axis=0))
        d.rectangle(box,fill=c)
        f=ImageFont.truetype(SB,36 if len(lines)==1 else 31); lh=40
        cx=(box[0]+box[2])/2; cy=(box[1]+box[3])/2; y=cy-lh*len(lines)/2
        for l in lines:
            w=d.textlength(l,font=f); d.text((cx-w/2,y),l,font=f,fill=(25,25,25)); y+=lh
slides=[
 (1,"Bayangkan anda jual yogurt… tapi tiada siapa yang beli.",355,(150,450),44,False),
 (2,"Okey…",295,(150,430),60,False),
 (3,"Satu cawan tulis 20% lemak. Satu lagi 80% bebas lemak. Mana satu laku?",215,(100,330),44,True),
 (4,"80% bebas lemak.",290,(150,430),48,False),
 (1,"Kenapa?",355,(150,450),64,False),
 (6,"Sebab bunyinya lebih sihat.",290,(150,430),48,False),
 (7,"Padahal… ia yogurt yang sama.",220,(100,330),48,True),
 (8,"Jadi orang beli perkataan… bukan yogurt.",295,(150,430),46,False),
]
for n,(src,text,cy,blank,size,cup) in enumerate(slides,1):
    im=load(src)
    if cup: cups(im)
    title(im,text,cy,blank,size)
    im.resize((1080,1440),Image.LANCZOS).save(f'{S}/out/slide_{n}.png')
# contact sheet
ims=[Image.open(f'{S}/out/slide_{n}.png').resize((360,480)) for n in range(1,9)]
sheet=Image.new('RGB',(1440,960),'black')
for i,m in enumerate(ims): sheet.paste(m,((i%4)*360,(i//4)*480))
sheet.save(f'{S}/sheet.png')
