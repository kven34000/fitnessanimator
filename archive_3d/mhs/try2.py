import bpy, addon_utils
bpy.ops.extensions.repo_refresh_all() if hasattr(bpy.ops.extensions,'repo_refresh_all') else None
r=bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb'); print('EN',r)
import importlib
m=importlib.import_module('bl_ext.user_default.mpfb.services.humanservice')
HS=m.HumanService
print([x for x in dir(HS) if not x.startswith('_')])
