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
import time
import os

#用户输入的参数：路径、任务名_
A = [z for z in input().split(', ')] 
j = A[0]
i = A[1]
path = A[2]

mrc = mrcfile.open(f"{path}Class2D/run{j}to{i}/_it020_classes.mrcs")
data = mrc.data
mrc.close()
a = data.shape[0]
n = a//10
r = a%10
if r != 0:
    n += 1
fig, axes = plt.subplots(n,10, figsize=(10,5))
for x in range(n):
    for y in range(10):
        axes[x,y].imshow(data[x*10+y,:,:], cmap = 'gray')
        axes[x,y].set_axis_off()
#边距设置
plt.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98, wspace=0.12, hspace=0.12)
#设置字体
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
#plt.show()
plt.savefig(f"{path}Class2D/run{j}to{i}/classes{j}to{i}.png", format='png', dpi=100)
