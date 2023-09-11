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
import time
import os
import re
import sys
import numpy as np

b = 0
while b < 1:
    #用户输入的参数：路径、任务名_
    j = sys.argv[1]
    i = sys.argv[2]
    path = sys.argv[3]
    iteration = int(sys.argv[4])
    #A = [z for z in input().split(', ')] 
    #j = A[0]
    #i = A[1]
    #path = A[2]

    if os.path.exists(f"{path}Select/run{j}to{i}/class_averages.star"):
        class_list = []
        resolution_list = []
        np_list = []
        with open(f"{path}Select/run{j}to{i}/class_averages.star") as f:
            for line in f:
                line_elements = (line.rstrip()).split('@') #抓取包含@的字符串
                if re.search("@", line):
                    class_list.append(int(line_elements[0][-2:]))
                    resolution_list.append(int(line_elements[1][-9:-7]))
        with open(f"{path}Select/run{j}to{i}/rank_data.star") as f1:
            for line in f1:
                if re.search("ClassNumber", line):
                    class_position = int(line.split("#")[1])
                if re.search("@", line):
                    new_line = " ".join(line.split())
                    np_list.append(int(new_line.split(" ")[class_position-1]))
        np_array = np.zeros(100, dtype=int)
        for m in np_list:
            np_array[m-1] += 1
        mrc = mrcfile.open(f"{path}Class2D/run{j}to{i}/_it%03d_classes.mrcs" % (iteration))
        data = mrc.data
        mrc.close()
        a = len(class_list)
        row_n = 8
        n = a//row_n
        r = a%row_n
        if r != 0:
            n += 1

        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Times New Roman']
        angs = (r"$\mathrm{\AA}$")
        fig, axes = plt.subplots(n,row_n, figsize=(12,7))
        for x in range(n):
            for y in range(row_n):
                if x*row_n+y < a:
                    axes[x,y].imshow(data[class_list[x*row_n+y]-1,:,:], cmap = 'gray')
                    axes[x,y].set_axis_off()
                    axes[x,y].set_title(f"{np_array[x*row_n+y]} particles, {resolution_list[x*row_n+y]} {angs}")
                elif x*row_n+y >= a and x*row_n+y < n*row_n:
                    axes[x,y].set_axis_off()
                else:
                    break
        #边距设置
        plt.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.96, wspace=0.04, hspace=0.38)
        #设置字体
        #plt.show()
        plt.savefig(f"{path}Class2D/run{j}to{i}/classes{j}to{i}.png", format='png', dpi=100)
        b += 1
    else:
        time.sleep(3)
        print("Waiting for class ranker results...")
