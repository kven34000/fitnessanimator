#!/bin/bash
cd /home/claude/w3d
(python3 render3d.py run 0 23 parts/p1.mp4 > parts/l1.txt 2>&1; python3 render3d.py run 46 69 parts/p3.mp4 > parts/l3.txt 2>&1) &
(python3 render3d.py run 23 46 parts/p2.mp4 > parts/l2.txt 2>&1; python3 render3d.py run 69 92 parts/p4.mp4 > parts/l4.txt 2>&1) &
wait
echo DONE > parts/done.txt
