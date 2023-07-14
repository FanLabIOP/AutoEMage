#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""


import mrcfile
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as sfft
from skimage import exposure

#用户输入的参数：路径、任务名_
A = [i for i in input().split(', ')] 
cal_dir = A[0]
job_fullname = A[1]
#cal_dir = '/work1/cyh/Documents/课题1/ABC/'
#job_fullname = 'ABC_0001'

#运动修正后的图
mrc = mrcfile.open(f"{cal_dir}MotionCorr/{job_fullname}_SumCorr_DW.mrc")
data = mrc.data
mrc.close()
im1 = exposure.equalize_hist(data)

#mean = data.mean()
#std = np.std(data)
#vmin = mean-3*std
#vmax = mean+3*std
#FT变换后的图
FT = sfft.fft2(data)
data_FT = sfft.fftshift(FT)
magnitude_spectrum = np.log(1+np.abs(data_FT))
img_eq = exposure.equalize_hist(magnitude_spectrum)
#每帧照片运动轨迹图
file = open(f"{cal_dir}MotionCorr/{job_fullname}-Patch-Full.log", 'r')
data1 = np.loadtxt(file, skiprows=3)
file.close()
#CTFFIND后的图
mrc1 = mrcfile.open(f"{cal_dir}CtfFind/{job_fullname}_ctf.mrc")
data2 = mrc1.data
mrc1.close()

x_max = np.max(data1[:,1])
y_max = np.max(data1[:,2])
x_min = np.min(data1[:,1])
y_min = np.min(data1[:,2])
point_numbers = range(len(data1))

fig, axes = plt.subplots(2,2, figsize=(6,5), gridspec_kw={'width_ratios':[1,1], 'height_ratios':[1,1]})
fig.tight_layout()
axes[0,0].imshow(im1, cmap='gray')
axes[1,0].imshow(img_eq, cmap = 'gray')
axes[0,1].plot(data1[:,1], data1[:,2], color='k', alpha=0.4)
axes[0,1].scatter(data1[:,1], data1[:,2], marker='o', c=point_numbers, cmap='cool', edgecolors='none', s=40)
axes[1,1].imshow(data2[0,:,:], cmap='gray')
axes[0,0].set_axis_off()
axes[1,0].set_axis_off()
axes[1,1].set_axis_off()
axes[0,1].set_xlim([x_min-1, x_max+1])
axes[0,1].set_ylim([y_min-1, y_max+1])
#
axes[0,1].tick_params(direction='in')
#边距设置
plt.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98, wspace=0.12, hspace=0.12)
#设置字体
#plt.rcParams['font.family'] = 'serif'
#plt.rcParams['font.serif'] = ['Times New Roman']
plt.savefig(f"{cal_dir}Display/{job_fullname}_all.png", format='png', dpi=100)

