"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
import numpy as np

def calculate_z(data):
	"""计算Z得分"""
	mean = np.mean(data)
	#计算标准差
	std = np.std(data)
    #计算Z得分
	z = np.abs((data - mean) / std)
	return z
