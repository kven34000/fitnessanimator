import bpy, numpy as np
bpy.ops.wm.open_mainfile(filepath='/home/claude/mhs/body_T.blend')
h=bpy.data.objects['Body']; me=h.data
co=np.array([v.co[:] for v in me.vertices]); co=co@np.array(h.matrix_world.to_3x3()).T+np.array(h.matrix_world.translation)
gi={g.name:g.index for g in h.vertex_groups}
nip=[v.index for v in me.vertices if any(g.group==gi['nipple'] and g.weight>0.5 for g in v.groups)]
p=co[nip]; print('nipples', p[p[:,0]>0].mean(0), p[p[:,0]<0].mean(0))
for z in np.arange(0.95,1.62,0.05):
  m=(abs(co[:,2]-z)<0.01)&(abs(co[:,0])<0.03); 
  m2=(abs(co[:,2]-z)<0.01)&(abs(co[:,1])<0.06)&(abs(co[:,0])<0.35)
  print(round(z,2),'front y',round(co[m,1].min(),3) if m.any() else None,'back y',round(co[m,1].max(),3) if m.any() else None,'halfwidth',round(co[m2,0].max(),3) if m2.any() else None)
