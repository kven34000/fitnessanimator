import bpy,numpy as np
bpy.ops.wm.open_mainfile(filepath='/home/claude/mhs/body_T.blend')
h=bpy.data.objects['Body']; co=np.array([v.co[:] for v in h.data.vertices]); ax=np.abs(co[:,0])
q=co.copy(); q[:,0]=ax
for nm,p0,p1 in [('thigh',(0.113,0.008,0.997),(0.151,-0.027,0.529)),('shin',(0.151,-0.027,0.529),(0.202,-0.012,0.076))]:
  p0=np.array(p0);p1=np.array(p1);d=p1-p0;L=np.linalg.norm(d);d/=L
  rel=q-p0;t=rel@d/L;perp=rel-np.outer(rel@d,d)
  for tt in (0.3,0.5,0.8):
    m=(abs(t-tt)<0.02)&(co[:,2]<1.02)&(ax>0.02)&(np.linalg.norm(perp,axis=1)<0.15)
    print(nm,tt,'fw range',(-perp[m,1]).min().round(3),(-perp[m,1]).max().round(3),'out range',perp[m,0].min().round(3),perp[m,0].max().round(3))
