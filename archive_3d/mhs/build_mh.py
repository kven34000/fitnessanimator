import bpy, json, os, sys
from mathutils import Vector
OUT='/home/claude/mhs/out'; os.makedirs(OUT,exist_ok=True)
J={k:Vector(v) for k,v in json.load(open('/home/claude/mhs/joints.json')).items()}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath='/home/claude/mx/Air Squat.fbx')
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; arm.name='Hero_Armature'
for o in list(bpy.data.objects):
  if o.type=='MESH': bpy.data.objects.remove(o,do_unlink=True)
sq=arm.animation_data.action; sq.name='AirSquat'
with bpy.data.libraries.load('/home/claude/mhs/body_S.blend') as (src,dst): dst.objects=['Body']
body=dst.objects[0]; bpy.context.scene.collection.objects.link(body)
for m in list(body.modifiers): body.modifiers.remove(m)
body.parent=None
if 'viz' in body.data.color_attributes: body.data.color_attributes.remove(body.data.color_attributes['viz'])
# ---- head transplant from Tripo hero ----
with bpy.data.libraries.load('/home/claude/mx/out/hero_rig.blend') as (src,dst2): dst2.objects=['Hero']
hero=dst2.objects[0]; bpy.context.scene.collection.objects.link(hero)
for m in list(hero.modifiers): hero.modifiers.remove(m)
hero.parent=None; hero.matrix_world=hero.matrix_world  # keep
bpy.context.view_layer.update()
import bmesh
from mathutils import Vector as V
OFF=V((0,-0.043,0.043)); CUT=1.515
bm=bmesh.new(); bm.from_mesh(hero.data); bm.transform(hero.matrix_world)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<CUT],context='VERTS')
PIV=V(J['Head'])
for v in bm.verts:
  v.co+=OFF; v.co=PIV+(v.co-PIV)*0.86
me=bpy.data.meshes.new('HeadMesh'); bm.to_mesh(me); bm.free()
head=bpy.data.objects.new('HeadMesh',me); bpy.context.scene.collection.objects.link(head)
bpy.data.objects.remove(hero,do_unlink=True)
for p in head.data.polygons: p.use_smooth=True
gH=head.vertex_groups.new(name='mixamorig:Head'); gN=head.vertex_groups.new(name='mixamorig:Neck')
for v in head.data.vertices:
  t=min(1,max(0,(v.co.z-(PIV.z-0.055))/0.05)); gH.add([v.index],t,'REPLACE'); gN.add([v.index],1-t,'REPLACE')
# remove MH head
bm=bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>1.60],context='VERTS'); bm.to_mesh(body.data); bm.free()
for p in body.data.polygons: p.use_smooth=True
bpy.context.view_layer.update()
# targets
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=arm; arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); eb=arm.data.edit_bones; inv=arm.matrix_world.inverted()
par={b.name:(b.parent.name if b.parent else None) for b in eb}
def tgt(name):
  n=name.replace('mixamorig:','')
  if n in J: return J[n]
  p=par[name]
  if p and p.replace('mixamorig:','')+'_tail' in J: return J[p.replace('mixamorig:','')+'_tail']
  return None
info={b.name:((b.tail-b.head).normalized(),b.roll,b.length,[c.name for c in b.children]) for b in eb}
miss=[]
for b in eb: b.use_connect=False
for b in eb:
  H=tgt(b.name)
  if H is None: miss.append(b.name); continue
  d,roll,ln,ch=info[b.name]; hl=inv@H; L=ln
  for c in ch:
    T=tgt(c)
    if T is not None: L=max((inv@T-hl).length,ln*0.2); break
  b.head=hl; b.tail=hl+d*L; b.roll=roll
print('missing',miss)
bpy.ops.object.mode_set(mode='OBJECT')
arm.animation_data.action=None
for pb in arm.pose.bones:
  pb.location=(0,0,0); pb.rotation_quaternion=(1,0,0,0); pb.rotation_euler=(0,0,0); pb.scale=(1,1,1)
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); head.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active=arm
bpy.ops.object.parent_set(type='ARMATURE_NAME')
bn={b.name for b in arm.data.bones}
for g in list(body.vertex_groups):
  if g.name not in bn: body.vertex_groups.remove(g)
print('groups',len(body.vertex_groups), 'unweighted',sum(1 for v in body.data.vertices if not v.groups))
mat=bpy.data.materials.new('skin'); body.data.materials.clear(); body.data.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/mh_rig.blend')
clips={'AirSquat':sq}
for fn,name in (('Idle.fbx','Idle'),('Taunt.fbx','Flex'),('Mutant Flexing Muscles.fbx','MutantFlex'),('Running Up Stairs.fbx','Stairs'),('Standing Thumbs Up.fbx','ThumbsUp'),('Pointing Gesture.fbx','Point')):
  before=set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath='/home/claude/mx/'+fn)
  new=[o for o in bpy.data.objects if o not in before]; act=None
  for o in new:
    if o.animation_data and o.animation_data.action: act=o.animation_data.action
  act.name=name; act.use_fake_user=True; clips[name]=act
  for o in new: bpy.data.objects.remove(o,do_unlink=True)
only=sys.argv[-1].split(',') if sys.argv[-1]!='all' else list(clips)
for name in only:
  act=clips[name]
  bpy.ops.object.select_all(action='DESELECT'); arm.animation_data.action=act
  try:
    if act.slots: arm.animation_data.action_slot=act.slots[0]
  except Exception as e: print('slot',e)
  bpy.context.scene.frame_start=int(act.frame_range[0]); bpy.context.scene.frame_end=int(act.frame_range[1])
  body.select_set(True); head.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active=arm
  bpy.ops.export_scene.gltf(filepath=f'{OUT}/mh_{name}.glb',export_format='GLB',use_selection=True,export_animations=True,
    export_animation_mode='ACTIVE_ACTIONS',export_skins=True,export_yup=True,export_apply=False,export_attributes=True)
  print('exported',name)
