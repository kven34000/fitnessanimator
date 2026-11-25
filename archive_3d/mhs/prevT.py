import bpy,math,sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2])
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=1400; sc.render.resolution_y=900
sc.display.shading.light='STUDIO'; sc.display.shading.color_type='SINGLE'; sc.display.shading.single_color=(0.9,0.55,0.45)
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam
cam.location=(0,-4.6,1.0); cam.rotation_euler=(math.radians(90),0,0)
sc.render.filepath=sys.argv[-1]; bpy.ops.render.render(write_still=True)
