"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/23
Last Edit: 2023/06/23
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
import numpy as np

def drift_monitor(data):
    #检查照片的漂移大小，若每帧照片位移大于，或总位移大于，则标记为异常数据
    a1 = data[1:, 1:]
    a2 = data[:-1, 1:]
    a3 = np.sum(np.square(a1-a2), axis=1) #每帧照片的位移
    a = np.sum(a3 > 5) > 1 #每帧照片位移大于5 Angstrom
    #a = np.sum(a3 > 5)
    b = np.sum(a3) > 25 #总位移大于25 Angstrom
    #b = np.sum(a3)
    return (a or b)