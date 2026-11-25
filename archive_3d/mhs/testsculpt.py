import bpy,sys,numpy as np; sys.path.insert(0,'/home/claude/mhs')
from sculpt import sculpt,MUS
bpy.ops.wm.open_mainfile(filepath='/home/claude/mhs/body_T.blend')
h=bpy.data.objects['Body']; bpy.context.view_layer.objects.active=h
mod=h.modifiers.new('ss','SUBSURF'); mod.levels=1; bpy.ops.object.modifier_apply(modifier='ss')
print('verts',len(h.data.vertices))
M,INK=sculpt(h)
me=h.data; n=len(me.vertices)
c=np.ones((n,4))*np.array([0.85,0.6,0.5,1])
for k,col in [('pecs',(0,1,0)),('abs',(0,1,0.5)),('obliques',(0.3,0.6,1)),('delts',(1,1,0)),('biceps',(0,1,0)),('triceps',(1,0,1)),('quads',(0,1,0)),('calves',(0,1,1)),('glutes',(1,0.5,0)),('lats',(0.5,0.5,1)),('traps',(1,0,0)),('serratus',(1,1,0)),('forearms',(0,0.6,0.3)),('hams',(1,0,1)),('lowback',(1,1,0))]:
  c[:,:3]=c[:,:3]*(1-M[k][:,None])+np.array(col)*M[k][:,None]
c[:,:3]*= (1-INK[:,None]*0.8)
a=me.color_attributes.new('viz','FLOAT_COLOR','POINT'); a.data.foreach_set('color',c.astype(np.float32).ravel())
me.color_attributes.active_color=a
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/mhs/body_S.blend')
import math
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=1000; sc.render.resolution_y=1000
sc.display.shading.light='STUDIO'
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam
for nm,col,ang in [('g','SINGLE',0),('v','VERTEX',0),('vb','VERTEX',180),('gq','SINGLE',35)]:
  sc.display.shading.color_type=col; sc.display.shading.single_color=(0.9,0.55,0.45)
  a=math.radians(ang); cam.location=(math.sin(a)*3.2,-math.cos(a)*3.2,1.15); cam.rotation_euler=(math.radians(90),0,a)
  sc.render.filepath=f'/home/claude/mhs/s_{nm}.png'; bpy.ops.render.render(write_still=True)
