import sys; sys.path.insert(0,'/home/claude/mh/mpfb2/src')
import bpy
import mpfb
try:
    mpfb.register()
except Exception as ex: print('REG ERR',ex)
from mpfb.services.humanservice import HumanService
import inspect as ins
print([m for m in dir(HumanService) if not m.startswith('_')])
