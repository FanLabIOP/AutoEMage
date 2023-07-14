"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/24
Last Edit: 2023/06/24
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

import matplotlib.pyplot as plt

def drift_plot(data, i, job, cal_dir):
	job_fullname = f"{job}_%04d" % (i)
	mrc = mrcfile.open(f"{cal_dir}MotionCorr/{job_fullname}_SumCorr_DW.mrc")
	data1 = mrc.data
	mrc.close()
	im1 = exposure.equalize_hist(data1)
	point_numbers = range(len(data))
	fig, axes = plt.subplots(1, 2, figsize=(7,3), gridspec_kw={'width_ratios':[7,5]})
	fig.tight_layout()
	axes[0].imshow(im1, cmap='gray')
	axes[0].set_axis_off()
	axes[1].plot(data[:,1], data[:,2], color='k', alpha=0.4)
	axes[1].scatter(data[:,1], data[:,2], marker='o', c=point_numbers, cmap='cool', edgecolors='none', s=40)
	axes[1].tick_params(direction='in')
	plt.savefig(f"{cal_dir}Outliers/MotionCorr/{job_fullname}.png", format='png', dpi=100)