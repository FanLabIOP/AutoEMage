#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/30
Last Edit: 2023/06/30
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
import numpy as np

def drift_cal(data):
    #检查照片的漂移大小，若每帧照片位移大于，或总位移大于，则标记为异常数据
    a1 = data[1:, 1:]
    a2 = data[:-1, 1:]
    a3 = np.sum(np.square(a1-a2), axis=1) #每帧照片的位移
    #a = np.sum(a3 > 5)
    b = np.sum(np.sqrt(a3)) #总位移
    #b = np.sum(a3)
    return b

filename = input() + "-Patch-Full.log"
file = open(filename, 'r')
data = np.loadtxt(file, skiprows=3)
file.close()
print (drift_cal(data))