#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/09/06
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""


import mrcfile
import matplotlib.pyplot as plt
import numpy as np
from skimage import exposure
import sys

cal_dir = sys.argv[1]
job_fullname = sys.argv[2]

mrc = mrcfile.open(f"{cal_dir}MotionCorr/{job_fullname}_SumCorr_DW.mrc")
data = mrc.data
mrc.close
im1 = exposure.equalize_hist(data)

coordinates_list = []
with open("/work/Pictures/test11/Extract/CtfFind/test11_0016_SumCorr_DW_extract.star") as f:
    lines = f.readlines()[22:]
    non_blank_lines = list(filter(lambda x: x.strip(), lines))
    for i in non_blank_lines:
        new_line = " ".join(i.split())
        x = float(new_line.split()[0])
        y = float(new_line.split()[1])
        coordinates_list.append([x,y])

coordinates = np.array(coordinates_list)
fig, axe = plt.subplots(1,1,figsize=(5,5))
axe.imshow(im1, cmap='gray')
axe.scatter(coordinates[:,0], coordinates[:,1], s=1, c='yellow')
axe.set_axis_off()
plt.savefig(f"{cal_dir}Display/{job_fullname}_particles.png", format='png', dpi=100)