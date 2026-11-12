from PIL import Image, ImageDraw; import numpy as np
from scipy import ndimage as ni
from skimage.segmentation import watershed
S=720; k=S/825
im=Image.open('src.jpg').convert('RGB'); a=np.asarray(im).astype(float)
lum=a@np.array([.3,.59,.11]); lab=np.load('lab.npy')
yy,xx=np.mgrid[0:S,0:S]
def line(pts,w):
    m=Image.new('L',(S,S),0); ImageDraw.Draw(m).line([(x*k,y*k) for x,y in pts],fill=1,width=max(1,int(w*k)),joint='curve'); return np.asarray(m)>0
def poly(pts):
    m=Image.new('L',(S,S),0); ImageDraw.Draw(m).polygon([(x*k,y*k) for x,y in pts],fill=1); return np.asarray(m)>0
def disc(x,y,r): return (xx-x*k)**2+(yy-y*k)**2<(r*k)**2
NAMES={1:'Twill',2:'Merrow border',3:'Lettering',4:'Face',5:'Left eye socket',6:'Right eye socket',7:'Left eye',8:'Right eye',9:'Upper lip',10:'Lower lip',18:'Neck',19:'Left collar',20:'Right collar',21:'Tie knot',22:'Left jacket',23:'Right jacket'}
seeds={}
seeds[5]=line([(214,328),(216,348),(230,368),(236,392),(238,415),(262,412),(290,400),(318,402),(337,412)],9)
seeds[6]=line([(452,404),(478,402),(505,396),(528,398),(548,408),(565,412)],9)|line([(558,318),(556,338),(540,360),(536,385),(540,400)],9)
seeds[9]=line([(250,485),(300,472),(350,468),(390,470),(430,468),(480,472),(530,488)],6)
seeds[10]=line([(255,540),(290,562),(330,575),(390,585),(450,580),(500,565),(535,540)],6)
for i,(x,y) in enumerate([(240,515),(272,522),(315,525),(367,532),(430,530),(485,522),(525,515)]): seeds[11+i]=disc(x,y,6)
seeds[18]=poly([(335,648),(425,648),(420,700),(345,700)])
seeds[19]=line([(290,690),(295,730),(315,755),(340,760)],6)
seeds[20]=line([(462,685),(460,730),(440,755),(420,760)],6)
seeds[21]=poly([(371,752),(387,752),(387,778),(371,778)])
seeds[22]=line([(130,768),(200,755),(250,745),(262,772)],6)
seeds[23]=line([(500,745),(530,760),(580,768),(640,774)],5)
suitpoly=poly([(275,650),(200,695),(60,755),(40,765),(40,800),(790,800),(760,790),(700,765),(600,730),(500,685),(465,645)])
eyes=lab==8
el,en=ni.label(eyes)
ce=ni.center_of_mass(eyes,el,range(1,en+1))
for i in range(en):
    h=el==i+1; ring=ni.binary_dilation(h,iterations=4)&~eyes&(lab==4)
    seeds[5 if ce[i][1]<S/2 else 6]|=ring

head=np.isin(lab,[4,5,6])
def far(m,d): return ~ni.binary_dilation(m,iterations=int(d*k))
face=ni.binary_erosion(lab==4,iterations=3)&far(seeds[5]|seeds[6],18)&far(seeds[9],24)&far(seeds[10],36)&(yy<600*k)
for t in range(11,18): face&=far(seeds[t],30)
seeds[4]=face
seeds[1]=ni.binary_erosion(lab==1,iterations=5)&~ni.binary_dilation(suitpoly,iterations=8)
mk=np.zeros((S,S),np.int32)
for i,m in seeds.items(): mk[m]=i
mask=np.isin(lab,[1,4,5,6,7])
elev=ni.gaussian_gradient_magnitude(lum,1.6)
ws=watershed(elev,mk,mask=mask)
new=lab.copy()
new[mask]=ws[mask]
# keep silhouette: original twill outside suit zone stays twill; original figure never becomes twill there
keep=(lab==1)&~ni.binary_dilation(suitpoly,iterations=10); new[keep]=1
# eyes
c=ni.center_of_mass(eyes,el,range(1,en+1))
for i in range(en): new[el==i+1]=7 if c[i][1]<S/2 else 8
ids=[i for i in np.unique(new) if i>=4 and i not in (7,8)]
fixed=~np.isin(new,ids)
votes=np.stack([ni.gaussian_filter((new==i).astype(float),1.6) for i in ids])
sm=np.array(ids)[votes.argmax(0)]
new[~fixed]=sm[~fixed]
np.save('new.npy',new)
rng=np.random.RandomState(7); pal=rng.randint(30,255,(30,3)); pal[1]=[250,250,240]
viz=(pal[new]*.55+a*.45).astype(np.uint8)
v=Image.fromarray(viz).crop((int(80*k),int(190*k),int(750*k),int(800*k))); v=v.resize((v.size[0]*2,v.size[1]*2)); v.save('seg3.png')
print({i:int((new==i).sum()) for i in np.unique(new)})

P=Image.fromarray(new.astype(np.uint8),'P'); P.putpalette(sum([[i*10,i*10,i*10] for i in range(25)],[])+[0]*(231*3)); P.save('lab2.png',optimize=True)
