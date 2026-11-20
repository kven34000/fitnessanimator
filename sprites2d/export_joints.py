import asyncio, json, sys
sys.path.insert(0,'/home/claude/w3d')
from drv import Eng
import render10c as R
R.SEGS[2]=(5.64,7.45,'Flex',1.2,False)
B=['Hips','Spine2','Neck','Head','HeadTop_End']
for s in ['Left','Right']:
  B+= [f'{s}Shoulder',f'{s}Arm',f'{s}ForeArm',f'{s}Hand',f'{s}HandMiddle1',f'{s}HandMiddle4',f'{s}UpLeg',f'{s}Leg',f'{s}Foot',f'{s}ToeBase',f'{s}Toe_End']
NAMES=['mixamorig'+b for b in B]
async def main():
  e=Eng(None,'engine3.html',"()=>{window.MODEL='mh_AirSquat.glb';}"); await e.start()
  for c in ('Idle','Flex','Point'): await e.ev(f"()=>window.loadClip('{c}','mh_{c}.glb')")
  out={}
  rest=await e.ev('(a)=>window.joints({clips:[{name:"Idle",time:0.0}],fingers:"anim"},a)',NAMES)
  for i in range(int(10.5*30)):
    t=i/30; st=R.state(t)[0]
    out[i]=await e.ev('([s,a])=>window.joints(s,a)',[{'clips':st['clips'],'fingers':'anim'},NAMES])
  json.dump({'rest':rest,'frames':out},open('/home/claude/p2d/joints10.json','w'))
  await e.stop()
asyncio.run(main())
