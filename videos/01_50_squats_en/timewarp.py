import sys, numpy as np
sys.path.insert(0,'/home/claude/work'); sys.path.insert(0,'/home/claude/en')
import words as RW
from words_en import W as EW
A=[(0,0),(8,9),(10,11),(12,13),(17,18),(20,22),(26,30),(35,39),(36,42),(37,43),(38,44),(41,48),(42,50),(47,58),(49,59),(51,60),(53,62),(57,68),(58,69),(60,72),(64,77),(65,78),(67,80),(74,90),(77,94),(79,96),(80,97),(82,99),(87,105),(94,114),(95,115),(97,117),(102,124),(105,133),(110,134),(114,138),(115,140),(117,142),(118,144),(122,149),(123,151),(124,152),(125,153),(127,155),(129,157),(130,158),(133,162),(134,163),(141,172),(142,173),(146,177),(150,182),(152,183),(154,186),(157,190),(159,192),(163,197),(166,202),(171,207),(178,218),(182,222),(183,223)]
RU=[0.0]+[RW.W[r][1] for r,e in A]+[92.0]
EN=[0.0]+[EW[e][1] for r,e in A]+[82.6]
# ensure monotonic
RU=np.array(RU); EN=np.array(EN)
assert (np.diff(RU)>0).all() and (np.diff(EN)>0).all(), (np.diff(RU), np.diff(EN))
EN_DUR=82.6
def to_ru(t): return float(np.interp(t,EN,RU))
def to_en(t): return float(np.interp(t,RU,EN))
if __name__=='__main__':
  for r,e in zip(RU,EN): print(round(r,2),round(e,2),round((r-e),2))
