import sys, numpy as np
from PIL import Image
from scipy.signal import fftconvolve
from scipy import ndimage as ndi
n=sys.argv[1]; S='sheets'
O=np.asarray(Image.open(f'{S}/{n}.png').convert('RGB')).astype(np.float32)
N=np.asarray(Image.open(f'{S}/{n}_noeq.png').convert('RGB').resize((O.shape[1],O.shape[0]))).astype(np.float32)
M=np.asarray(Image.open(f'{S}/{n}_plateM.png').convert('RGB').resize((O.shape[1],O.shape[0]))).astype(np.float32)
key=lambda a:1-np.clip((a[...,1]-np.maximum(a[...,0],a[...,2])-25)/65,0,1)
import os; CH,CW=int(os.environ.get("CH",896)),int(os.environ.get("CW",600))
c=lambda a:a[0:CH,0:CW]
E=(key(c(O))>0.5)&~ndi.binary_dilation(key(c(N))>0.3,iterations=6)
Md=key(M)>0.5
cor=fftconvolve(Md.astype(np.float32),E[::-1,::-1].astype(np.float32),mode='same')
iy,ix=np.unravel_index(np.argmax(cor),cor.shape)
y0,x0=iy-CH//2,ix-CW//2
print('offset',y0,x0,'score',cor.max()/E.sum())
P=np.full_like(O,0); P[...,1]=255
sub=M[max(0,y0):y0+CH,max(0,x0):x0+CW]
P[0:sub.shape[0],0:sub.shape[1]]=sub
# keep only components overlapping E (remove neighbouring cells' bars)
pm=key(P[0:CH,0:CW])>0.5; lab,k=ndi.label(pm)
keep=[i for i in range(1,k+1) if ((lab==i)&ndi.binary_dilation(E,iterations=8)).sum()>200]
bad=pm&~np.isin(lab,keep); P[0:CH,0:CW][bad]=[0,255,0]
Image.fromarray(P.astype(np.uint8)).save(f'{S}/{n}_plate.png')
Image.fromarray(np.concatenate([c(O),P[0:CH,0:CW]],1).astype(np.uint8)).resize((600,448)).save(f'/tmp/fp_{n}.png')
