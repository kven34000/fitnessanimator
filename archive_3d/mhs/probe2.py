import bpy,numpy as np
bpy.ops.wm.open_mainfile(filepath='/home/claude/mx/out/hero_rig.blend')
for o in bpy.data.objects: print(o.name,o.type,o.parent.name if o.parent else None, [m.type for m in getattr(o,'modifiers',[])])
h=bpy.data.objects['Hero']; co=np.array([h.matrix_world@v.co for v in h.data.vertices])
print('z range',co[:,2].min(),co[:,2].max(), 'uv',len(h.data.uv_layers), 'mats',[m.name for m in h.data.materials])
for z in np.arange(1.40,1.62,0.02):
  m=abs(co[:,2]-z)<0.01; print(round(z,2),'x',co[m,0].min().round(3),co[m,0].max().round(3),'y',co[m,1].min().round(3),co[m,1].max().round(3))
