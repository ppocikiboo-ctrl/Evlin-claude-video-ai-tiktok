import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
S=sys.argv[1]
SB='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
def load(i): return Image.open(f'{S}/crop/{i}.png').convert('RGB').resize((1100,1464))
def cups(im):
    a=np.array(im); d=ImageDraw.Draw(im)
    for box,lines in [((225,515,425,595),['20% lemak']),((655,505,865,610),['80%','bebas lemak'])]:
        c=tuple(int(v) for v in np.median(a[box[1]:box[3],box[0]:box[0]+10].reshape(-1,3),axis=0))
        d.rectangle(box,fill=c)
        f=ImageFont.truetype(SB,36 if len(lines)==1 else 31); lh=40
        cx=(box[0]+box[2])/2; cy=(box[1]+box[3])/2; y=cy-lh*len(lines)/2
        for l in lines:
            w=d.textlength(l,font=f); d.text((cx-w/2,y),l,font=f,fill=(25,25,25)); y+=lh
for src,blank,cup in [(1,450,False),(2,430,False),(3,330,True),(4,430,False),(6,430,False),(7,330,True),(8,430,False)]:
    im=load(src)
    ImageDraw.Draw(im).rectangle((0,0,1100,blank),fill='white')
    if src==6: ImageDraw.Draw(im).line((1099,0,1099,1464),fill='white',width=3)
    if cup: cups(im)
    L=im.convert('L')
    m=L.point(lambda v:255 if v>212 else 0)
    for seed in [(0,0),(1099,0),(0,1463),(1099,1463),(550,5),(5,700),(1094,700)]+([(780,1250)] if src in (2,4,6,8) else []):
        if m.getpixel(seed)==255: ImageDraw.floodfill(m,seed,128)
    bg=(np.array(m)==128)
    bgimg=Image.fromarray((bg*255).astype('uint8'))
    near=np.array(bgimg.filter(ImageFilter.MaxFilter(5)))>0
    band=near & ~bg
    l=np.array(L).astype(float)
    alpha=np.where(bg,0,255).astype(float)
    rgb=np.array(im).astype(float)
    soft=band & (l>165)
    alpha[soft]=np.clip((255-l[soft])/(255-165),0,1)*255
    rgb[soft]=np.minimum(rgb[soft],150)
    out=np.dstack([rgb,alpha]).astype('uint8')
    Image.fromarray(out,'RGBA').save(f'{S}/vid/layer_{src}.png')
print('ok')
