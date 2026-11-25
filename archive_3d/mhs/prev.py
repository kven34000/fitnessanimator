import bpy,sys
bpy.ops.wm.open_mainfile(filepath='/home/claude/mhs/human.blend')
h=[o for o in bpy.data.objects if o.type=='MESH'][0]
print([v.name for v in h.vertex_groups][:200])
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=1200; sc.render.resolution_y=1000
sc.display.shading.light='STUDIO'; sc.display.shading.color_type='SINGLE'; sc.display.shading.single_color=(0.9,0.55,0.45)
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam
import math
for i,(ang,fn) in enumerate([(0,'front'),(math.radians(35),'q')]):
  cam.location=(math.sin(ang)*5.5,-math.cos(ang)*5.5,1.0); cam.rotation_euler=(math.radians(90),0,ang); cam.data.lens=50
  sc.render.filepath=f'/home/claude/mhs/p_{fn}.png'; bpy.ops.render.render(write_still=True)
