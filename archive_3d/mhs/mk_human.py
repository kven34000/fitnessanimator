import bpy, importlib, os, sys
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
P='bl_ext.user_default.mpfb.services.'
HS=importlib.import_module(P+'humanservice').HumanService
TS=importlib.import_module(P+'targetservice').TargetService
LS=importlib.import_module(P+'locationservice').LocationService
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
macro=TS.get_default_macro_info_dict()
macro.update(gender=1.0,age=0.5,muscle=1.0,weight=0.55,proportions=1.0,height=0.6)
macro['race']={'asian':0.4,'caucasian':0.5,'african':0.1}
h=HS.create_human(macro_detail_dict=macro, feet_on_ground=True, scale=0.1)
T=LS.get_mpfb_data('targets')
extra={'torso/torso-muscle-pectoral-incr':0.9,'torso/torso-muscle-dorsi-incr':0.8,'torso/torso-vshape-incr':0.6,
 'stomach/stomach-tone-incr':1.0,'torso/measure-shoulder-dist-incr':0.8,'torso/torso-scale-horiz-incr':0.25,'neck/measure-neck-circ-incr':0.7,'neck/neck-scale-horiz-incr':0.4,'torso/measure-waist-circ-decr':0.3}
for s in ['l','r']:
  extra.update({f'arms/{s}-upperarm-muscle-incr':1.0,f'arms/{s}-upperarm-shoulder-muscle-incr':1.0,f'arms/{s}-lowerarm-muscle-incr':1.0,
   f'legs/{s}-upperleg-muscle-incr':1.0,f'legs/{s}-lowerleg-muscle-incr':1.0,f'legs/{s}-lowerleg-scale-horiz-incr':0.6,f'legs/{s}-lowerleg-scale-depth-incr':0.6,f'legs/{s}-upperleg-scale-horiz-incr':0.3,f'arms/{s}-lowerarm-scale-depth-incr':0.7,f'arms/{s}-upperarm-scale-depth-incr':0.6})
for k,w in extra.items():
  f=os.path.join(T,k+'.target.gz')
  if os.path.isfile(f): TS.load_target(h,f,weight=w)
  else: print('MISSING',k)
print('verts',len(h.data.vertices),'groups',len(h.vertex_groups))
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/mhs/human.blend')
