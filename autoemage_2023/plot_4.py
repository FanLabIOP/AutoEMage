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
import scipy.fft as sfft
from skimage import exposure
import sys
import matplotlib

#用户输入的参数：路径、任务名_
cal_dir = sys.argv[1]
job_fullname = sys.argv[2]
mode = int(sys.argv[3])
#cal_dir = '/work1/cyh/Documents/课题1/ABC/'
#job_fullname = 'ABC_0001'

#运动修正后的图
mrc = mrcfile.open(f"{cal_dir}MotionCorr/{job_fullname}_SumCorr_DW.mrc")
data = mrc.data
mrc.close()
im1 = exposure.equalize_hist(data)
xlim, ylim = data.shape
if xlim < ylim:
    ylim, xlim = data.shape
if mode == 2:
    xlim = xlim * 2
    ylim = ylim * 2

#mean = data.mean()
#std = np.std(data)
#vmin = mean-3*std
#vmax = mean+3*std
#FT变换后的图
#FT = sfft.fft2(data)
#data_FT = sfft.fftshift(FT)
#magnitude_spectrum = np.log(1+np.abs(data_FT))
#img_eq = exposure.equalize_hist(magnitude_spectrum)
#每帧照片漂移轨迹图
file = open(f"{cal_dir}MotionCorr/{job_fullname}-Patch-Full.log", 'r')
data1 = np.loadtxt(file, skiprows=3)
file.close()
#每块漂移轨迹图
with open(f"{cal_dir}MotionCorr/{job_fullname}-Patch-Frame.log", 'r') as f:
    lines = f.readlines()[5:]
    non_blank_lines = list(filter(lambda x: x.strip(), lines))
x_coor = []
y_coor = []
for i in non_blank_lines:
    new_line = " ".join(i.split())
    x = float(new_line.split()[1])
    y = float(new_line.split()[2])
    dx = float(new_line.split()[3])
    dy = float(new_line.split()[4])
    x_coor.append(x+20*dx)
    y_coor.append(y+20*dy)
coordinates = np.array([x_coor, y_coor]).T
#CTFFIND后的图
mrc1 = mrcfile.open(f"{cal_dir}CtfFind/{job_fullname}_ctf.mrc")
data2 = mrc1.data
mrc1.close()

x_max = np.max(data1[:,1])
y_max = np.max(data1[:,2])
x_min = np.min(data1[:,1])
y_min = np.min(data1[:,2])
point_numbers = range(len(data1))

fig, axes = plt.subplots(2,2, figsize=(7,7), gridspec_kw={'width_ratios':[6,5], 'height_ratios':[1,1]})
fig.tight_layout()
axes[0,0].imshow(im1, cmap='gray')
axes[1,1].scatter(coordinates[:,0], coordinates[:,1], marker='.', c='b', edgecolors='none', s=10)
axes[1,1].set_xlim(0, xlim-1)
axes[1,1].set_ylim(0, ylim-1)
axes[1,1].tick_params(left = False, right = False, labelleft = False, 
                 labelbottom = False, bottom = False)
axes[0,1].plot(data1[:,1], data1[:,2], color='k', alpha=0.4)
axes[0,1].scatter(data1[:,1], data1[:,2], marker='o', c=point_numbers, cmap='cool', edgecolors='none', s=40)
axes[1,0].imshow(data2[0,:,:], cmap='gray')
axes[0,0].set_axis_off()
axes[1,0].set_axis_off()
axes[0,1].set_xlim([x_min-1, x_max+1])
axes[0,1].set_ylim([y_min-1, y_max+1])
#
axes[0,1].tick_params(direction='in')
#边距设置
plt.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98, wspace=0.1, hspace=0.12)
#设置字体
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = 'Times New Roman'
plt.savefig(f"{cal_dir}Display/{job_fullname}_all.png", format='png', dpi=100)

