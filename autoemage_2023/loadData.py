#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2023/08/28
Last Edit: 2023/08/28
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

from time_to_data_trans import time_to_data_trans
import numpy as np

def loadData(directory):
	with open(f"{directory}_DataFile1.txt") as data_f:
	    data_lines = data_f.readlines()
	new_data = time_to_data_trans(data_lines)
	return np.array(new_data)