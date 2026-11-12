from PIL import Image; import numpy as np
from scipy import ndimage as ni
S=720
im=Image.open('/mnt/user-data/uploads/c6493b63-image.png').convert('RGB').resize((S,S),Image.LANCZOS)
a=np.asarray(im).astype(int); R,G,B=a[...,0],a[...,1],a[...,2]
lum=(0.3*R+0.59*G+0.11*B)
yy,xx=np.mgrid[0:S,0:S]; k=S/825
pink=(R-G>40)&(R>130)
pink=ni.binary_closing(pink,iterations=3)
inside=ni.binary_fill_holes(pink)
inside=ni.binary_opening(inside,iterations=2)
lab=np.zeros((S,S),np.uint8)  # 0 outside
BG,BORDER,TEXT,HEAD,LIPS,TEETH,SUIT=1,2,3,4,5,6,7
lab[inside]=BG
dark=lum<95
textbox=(xx>440*k)&(yy<135*k)&(yy>60*k)&(xx<770*k)
grey=((lum<168)|((lum<214)&(R-B<5)))&(abs(R-B)<16)&inside&~pink
mouth=(xx>215*k)&(xx<556*k)&(yy>485*k)&(yy<572*k)
teeth=(R-B>17)&(lum>120)&(lum<232)&mouth&~pink
teeth=ni.binary_opening(teeth,iterations=2); teeth=ni.binary_closing(teeth,iterations=4); teeth=ni.binary_fill_holes(teeth)
# keep biggest comp
l,n=ni.label(teeth); 
sz=ni.sum(teeth,l,range(1,n+1)); teeth=np.isin(l,[i+1 for i in range(n) if sz[i]>120])
body=(grey|(dark&~textbox))&inside&~pink
body=ni.binary_closing(body,iterations=2)
l,n=ni.label(body); sz=ni.sum(body,l,range(1,n+1)); body=l==(1+int(np.argmax(sz)))
body|=teeth
lens=(np.abs(yy-517*k) < 76*k*(1-((xx-388*k)/(190*k))**2))&(np.abs(xx-388*k)<190*k)
body|=lens
inv=~body&inside; l2,n2=ni.label(inv); sz2=ni.sum(inv,l2,range(1,n2+1))
body|=np.isin(l2,[i+1 for i in range(n2) if sz2[i]<260])
lab[body]=HEAD
lab[body&((yy>650*k)|((yy>606*k)&(xx>305*k)&(xx<445*k)))]=SUIT
lips=lens
lab[lips]=LIPS
lab[teeth]=TEETH
EYES=8
inv=(lab==BG); l3,n3=ni.label(inv); sz3=ni.sum(inv,l3,range(1,n3+1)); com=ni.center_of_mass(inv,l3,range(1,n3+1))
for i in range(n3):
    if 300<sz3[i]<20000 and com[i][0]<440*k and com[i][0]>250*k: lab[l3==i+1]=EYES
txt=dark&textbox&inside; txt=ni.binary_dilation(txt,iterations=1)
lab[txt]=TEXT
lab[pink&inside | (pink)]=BORDER
lab[~inside & ~pink]=0
np.save('lab.npy',lab)
pal=np.array([[40,40,60],[245,240,230],[230,90,140],[0,0,0],[150,150,155],[90,160,220],[240,210,120],[90,200,120],[240,60,60]],np.uint8)
Image.fromarray(((pal[lab].astype(int)+np.asarray(im).astype(int)*2)//3).astype(np.uint8)).save('labviz.png')
im.save('src.jpg',quality=86)
P=Image.fromarray(lab,'P'); P.putpalette(sum([[i*30,i*30,i*30] for i in range(9)],[])+[0]*(247*3)); P.save('lab.png',optimize=True)
import os; print(os.path.getsize('src.jpg'),os.path.getsize('lab.png'))
for i in range(8): print(i,(lab==i).sum(), np.percentile(lum[lab==i],[50,85]) if (lab==i).any() else '')
