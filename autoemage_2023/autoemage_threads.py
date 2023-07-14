"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
import numpy as np
import os
import time
import glob
from PyQt6.QtCore import QThread, pyqtSignal
from calculate_z import calculate_z
from time_to_data_trans import time_to_data_trans
from drift_monitor import drift_monitor
import shutil
import subprocess
import time

class Worker1(QThread):
    """第一个线程检查四格图是否画完，并检查漂移修正结果"""
    image_update_signal = pyqtSignal(int)
    motion_test_fail = pyqtSignal()

    def __init__(self, directory, job, n):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num = n

    def run(self):
        time.sleep(250)
        i = 1
        m = 0
        n_outlier = 0 #漂移修正异常照片张数
        while i <= int(self.num):
            if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (i)):
                self.image_update_signal.emit(i)
                time.sleep(20)
                i += 1
            else:
                print("Waiting for 4-plots...")
                time.sleep(30)
                m += 1
                if m > 50000:
                    break


class Worker2(QThread):
    """第二个线程检查数据并更新"""
    graph_update_signal = pyqtSignal(list)
    progress_update_signal = pyqtSignal(int)
    low_score_signal = pyqtSignal(int)
    large_drift_signal = pyqtSignal(int)
    
    def __init__(self, directory, job, n):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num = n

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        time.sleep(250)
        i = 1
        n_start = 50 #ctf测试
        n_start1 = 50 #drift测试
        if os.path.exists(f"{self.dir}Outliers/CtfFind") == False:
            os.mkdir(f"{self.dir}Outliers/CtfFind")
        if os.path.exists(f"{self.dir}Outliers/MotionCorr") == False:
            os.mkdir(f"{self.dir}Outliers/MotionCorr")

        while i <= int(self.num):
            if os.path.exists(f"{self.dir}CtfFind/{self.job}_DataFile1.txt"):
                m = 0
                with open(f"{self.dir}CtfFind/{self.job}_DataFile1.txt") as data_f:
                    data_lines = data_f.readlines()

                if len(data_lines) > i:
                    new_data = time_to_data_trans(data_lines)
                    self.graph_update_signal.emit(new_data)
                    if i >= n_start:
                        Data = np.array(new_data)
                        if np.sum(Data[(i-50):,-4] < 0.1) >= 10:
                            n_start = len(data_lines)+50
                            low_score_array = np.where(Data[(i-50):,-4] < 0.1)[0]
                            low_score_number = len(low_score_array)
                            for index in low_score_array:
                                while True:
                                    if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1)):
                                        shutil.copy(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1), f"{self.dir}Outliers/CtfFind/{self.job}_%04d_all.png" % (index+1))
                                        break
                                    else:
                                        time.sleep(10)
                            self.low_score_signal.emit(low_score_number)
                    if i >= n_start1:
                        Data = np.array(new_data)
                        if np.sum(Data[(i-50):,-1] > 24) >= 10:
                            n_start1 = len(data_lines)+50
                            large_drift_array = np.where(Data[(i-50):,-1] > 24)[0]
                            large_drift_number = len(large_drift_array)
                            for index in large_drift_array:
                                while True:
                                    if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1)):
                                        shutil.copy(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1), f"{self.dir}Outliers/MotionCorr/{self.job}_%04d_all.png" % (index+1))
                                        break
                                    else:
                                        time.sleep(10)
                            self.large_drift_signal.emit(large_drift_number)
                    i = len(data_lines)
                    self.progress_update_signal.emit(i)
                    i += 1
                    time.sleep(10)
                elif len(data_lines) == i:
                    new_data = time_to_data_trans(data_lines)
                    self.graph_update_signal.emit(new_data)
                    if i >= n_start:
                        Data = np.array(new_data)
                        #50张照片中有10张CTF得分较低
                        if np.sum(Data[(i-50):,-4] < 0.1) >= 10:
                            n_start = i+50
                            low_score_array = np.where(Data[(i-50):,-4] < 0.1)[0]
                            low_score_number = len(low_score_array)
                            for index in low_score_array:
                                while True:
                                    if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1)):
                                        shutil.copy(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1), f"{self.dir}Outliers/CtfFind/{self.job}_%04d_all.png" % (index+1))
                                        break
                                    else:
                                        time.sleep(10)
                            self.low_score_signal.emit(low_score_number)
                    if i >= n_start1:
                        Data = np.array(new_data)
                        #50张照片中有10张drift较大
                        if np.sum(Data[(i-50):,-1] > 24) >= 10:
                            n_start1 = i+50
                            large_drift_array = np.where(Data[(i-50):,-1] > 24)[0]
                            large_drift_number = len(large_drift_array)
                            for index in large_drift_array:
                                while True:
                                    if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1)):
                                        shutil.copy(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1), f"{self.dir}Outliers/MotionCorr/{self.job}_%04d_all.png" % (index+1))
                                        break
                                    else:
                                        time.sleep(10)
                            self.large_drift_signal.emit(large_drift_number)
                    self.progress_update_signal.emit(i)
                    i += 1
                    time.sleep(15)
                else:
                    print("Waiting for data...")
                    time.sleep(30)
                    m += 1
                    if m > 50000:
                        break
            else:
                time.sleep(10)


class Worker3(QThread):
    """第三个线程检查数据是否异常"""
    alert_signal = pyqtSignal()
    normal_signal = pyqtSignal()
    disk_signal = pyqtSignal()

    def __init__(self, data, directory, job):
        super().__init__()
        self.data = data
        self.dir = directory
        self.job = job

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        Data = np.array(self.data)
        if Data[-1,-2] > 96: #硬盘使用超过96%，则停止转移文件
            self.disk_signal.emit()
        if len(self.data) > 20:
            Z = calculate_z(Data[:,1])
            if Z[-1] > 1.5: #大于1.5个标准差被认定为异常数据
                self.alert_signal.emit()
            else:
                self.normal_signal.emit()



class Worker4(QThread):
    """定义颗粒挑选与二维分类的线程"""
    images_update_signal = pyqtSignal(int)
    def __init__(self, directory, job, num, dmin, dmax):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num = num
        self.dmin = dmin
        self.dmax = dmax

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        os.chdir(f"{self.dir}")
        i = 10
        while i <= int(self.num):
            j = i - 9 #每十张照片计算一次二维分类
            if os.path.exists(f"CtfFind/{self.job}_%04d_ctf.mrc" % (i)):
                pid3 = subprocess.Popen(f"relion_autopick --i CtfFind/micrographs_{j}to{i}_ctf.star --odir Autopick/ --pickname autopick_{j}to{i} --LoG  --LoG_diam_min {self.dmin} --LoG_diam_max {self.dmax} --shrink 0 --lowpass 20 --LoG_adjust_threshold 0 --LoG_upper_threshold 5 >> Autopick/{self.job}_auto_picking_{j}to{i}.txt", shell = True).pid
                time.sleep(25)
                k = 0
                while k < 1:
                    if os.path.exists(f"Autopick/autopick_{j}to{i}.star"):
                        pid4 = subprocess.Popen(f"relion_preprocess --i CtfFind/micrographs_{j}to{i}_ctf.star --coord_list Autopick/autopick_{j}to{i}.star --part_star Extract/particles_{j}to{i}.star --part_dir Extract/ --extract --extract_size 256 --float16  --scale 64 --norm --bg_radius 25 --white_dust -1 --black_dust -1 --invert_contrast >> Extract/{self.job}_auto_extract_{j}to{i}.txt", shell = True).pid
                        time.sleep(6)
                        k += 1
                    else:
                        time.sleep(5)
                l = 0
                while l < 1:
                    if os.path.exists(f"Extract/particles_{j}to{i}.star"):
                        pid5 = subprocess.Popen(f"relion_refine --o Class2D/run{j}to{i}/ --iter 20 --i Extract/particles_{j}to{i}.star --dont_combine_weights_via_disc --preread_images  --pool 30 --pad 2  --ctf  --tau2_fudge 2 --particle_diameter 200 --K 50 --flatten_solvent  --zero_mask  --center_classes  --oversampling 1 --psi_step 12 --offset_range 5 --offset_step 2 --norm --scale  --j 32 >> Class2D/{self.job}_auto_class2D_{j}to{i}.txt", shell = True).pid
                        time.sleep(480)
                        l += 1
                    else:
                        time.sleep(5)
                m = 0 
                while m < 1:
                    if os.path.exists(f"Class2D/run{j}to{i}/_it020_classes.mrcs"):
                        subprocess.run(f"plot_classes.py", input=f"{j}, {i}, {self.dir}", text=True, shell = True)
                        self.images_update_signal.emit(i)
                        m += 1
                    else:
                        time.sleep(10)
                time.sleep(5)
                i += 10
            else:
                time.sleep(10)
