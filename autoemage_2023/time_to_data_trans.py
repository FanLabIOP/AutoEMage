"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/09/06
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
import numpy as np

def time_to_data_trans(data_lines):
    """将时间转变为可以画图的数据结构"""
    new_data = []
    for line in data_lines:
        line_l = (line.rstrip()).split(', ')
        line_l[0] = np.datetime64(line_l[0]) #将时间字符串转化为可以画图的数据类型
        for j in range(1, len(line_l)):
            line_l[j] = float(line_l[j]) #将字符串转化float类型的数据，可用于计算、画图
        new_data.append(line_l)
    return new_data
