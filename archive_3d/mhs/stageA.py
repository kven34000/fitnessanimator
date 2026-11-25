import bpy, importlib, math, json
from mathutils import Vector, Matrix
bpy.ops.wm.open_mainfile(filepath='/home/claude/mhs/human.blend')
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
P='bl_ext.user_default.mpfb.services.'
HS=importlib.import_module(P+'humanservice').HumanService
TS=importlib.import_module(P+'targetservice').TargetService
h=[o for o in bpy.data.objects if o.type=='MESH'][0]
TS.bake_targets(h)
rig=HS.add_builtin_rig(h,'mixamo',import_weights=True)
print('rig',rig.name,len(rig.data.bones))
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='POSE')
def raise_arm(bn):
  pb=rig.pose.bones[bn]
  b=rig.data.bones[bn]
  v=(rig.matrix_world.to_3x3()@ (pb.tail-pb.head)).normalized()
  tgt=Vector((1 if v.x>0 else -1,0,0))
  ang=v.angle(tgt); ax=v.cross(tgt).normalized()
  # rotation in world -> bone local
  Rw=Matrix.Rotation(ang,4,ax)
  M=rig.matrix_world@pb.matrix
  newM=Matrix.Translation(M.to_translation())@Rw@Matrix.Translation(-M.to_translation())@M
  pb.matrix=rig.matrix_world.inverted()@newM
  bpy.context.view_layer.update()
  print(bn,'deg',math.degrees(ang))
for s in ['Left','Right']:
  raise_arm(f'mixamorig:{s}Arm'); raise_arm(f'mixamorig:{s}ForeArm'); raise_arm(f'mixamorig:{s}Hand')
bpy.ops.object.mode_set(mode='OBJECT')
# apply armature on mesh -> T-pose mesh
bpy.context.view_layer.objects.active=h
for m in h.modifiers:
  if m.type=='ARMATURE': bpy.ops.object.modifier_apply(modifier=m.name)
# smooth shoulder transition zone
import bmesh, numpy as np
me=h.data; n=len(me.vertices)
gi={g.name:g.index for g in h.vertex_groups}
mask=np.zeros(n)
for v in me.vertices:
  w={g.group:g.weight for g in v.groups}
  for s in ('Left','Right'):
    a=w.get(gi.get(f'mixamorig:{s}Arm'),0); b=w.get(gi.get(f'mixamorig:{s}Shoulder'),0)+w.get(gi.get('mixamorig:Spine2'),0)
    mask[v.index]=max(mask[v.index],min(1,4*min(a,b)+0.0))
mask=np.clip(mask,0,1)
nb=[[] for _ in range(n)]
for e in me.edges:
  a,b=e.vertices; nb[a].append(b); nb[b].append(a)
co=np.array([v.co[:] for v in me.vertices])
# grow mask a bit
for it in range(3):
  m2=mask.copy()
  for i in np.nonzero(mask>0)[0]:
    for j in nb[i]: m2[j]=max(m2[j],mask[i]*0.7)
  mask=m2
for it in range(10):
  avg=np.array([co[l].mean(0) if l else co[i] for i,l in enumerate(nb)])
  co=co+(avg-co)*(0.35*mask)[:,None]
for v in me.vertices: v.co=co[v.index]
me.update(); print('smoothed',int((mask>0.05).sum()))
# joint heads in posed world
J={}
for pb in rig.pose.bones:
  M=rig.matrix_world@pb.matrix
  J[pb.name.replace('mixamorig:','')]=list(M.to_translation())
  J[pb.name.replace('mixamorig:','')+'_tail']=list(rig.matrix_world@pb.tail)
bpy.data.objects.remove(rig)
for m in list(h.modifiers):
  if m.type=='MASK': h.modifiers.remove(m)
# delete helpers
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
gi={g.name:g.index for g in h.vertex_groups}
hel={gi['HelperGeometry'],gi['JointCubes']}
for v in h.data.vertices:
  v.select=any(g.group in hel and g.weight>0.5 for g in v.groups)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT')
for g in list(h.vertex_groups):
  if not g.name.startswith('mixamorig:') and g.name not in ('nipple','fingernails','toenails','scalp','genitals','lips','ears'): h.vertex_groups.remove(g)
zs=[ (h.matrix_world@v.co).z for v in h.data.vertices]; print('height',max(zs)-min(zs),'verts',len(h.data.vertices))
json.dump(J,open('/home/claude/mhs/joints.json','w'))
h.name='Body'
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/mhs/body_T.blend')
