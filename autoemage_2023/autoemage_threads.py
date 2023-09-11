"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/09/06
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
from functools import reduce
import shutil
import subprocess
import time

class WorkerKilledException(Exception):
    pass

class Worker1(QThread):
    """第一个线程检查四格图是否画完，并检查漂移修正结果"""
    image_update_signal = pyqtSignal(int, int)
    motion_test_fail = pyqtSignal()

    def __init__(self, directory, job, n):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num = n
        self.is_killed = False

    def stopRunning(self):
        self.terminate()
        self.wait()

    def kill(self):
        self.is_killed = True

    def run(self):
        time.sleep(60)
        i = 1
        m = 0
        while i <= int(self.num):
            if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (i)):
                l = 0
                while l < 1:
                    if os.path.exists(f"{self.dir}Autopick/CtfFind/{self.job}_%04d_SumCorr_DW_autopick_%04d.star" % (i,i)):
                        with open(f"{self.dir}Autopick/CtfFind/{self.job}_%04d_SumCorr_DW_autopick_%04d.star" % (i,i)) as f:
                            particle_n = len(f.readlines()) - 12
                        pid4 = subprocess.Popen(f"relion_preprocess --i CtfFind/micrograph_%04d_ctf.star --coord_list Autopick/autopick_%04d.star --part_star Extract/particles_%04d.star --part_dir Extract/ --extract --extract_size 256 --float16  --scale 64 --norm --bg_radius 25 --white_dust -1 --black_dust -1 --invert_contrast >> Extract/{self.job}_auto_extract.txt" % (i,i,i), shell = True).pid
                        time.sleep(2)
                        subprocess.run(f"plot_particles.py {self.dir} {self.job}_%04d" % (i), shell=True)
                        self.image_update_signal.emit(i, particle_n)
                        time.sleep(15)
                        l += 1
                    else:
                        time.sleep(15)
                        print(f"Waiting for autopicking results of No.{i} image...")
                i += 1
            elif self.is_killed:
                raise WorkerKilledException
            elif os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (i+1)):
                i += 1
            else:
                print(f"Waiting for 4-plots of No.{i} image...")
                time.sleep(45)
                m += 1
                if m > 50000:
                    break


class Worker2(QThread):
    """第二个线程检查数据并更新"""
    graph_update_signal = pyqtSignal(list, list)
    progress_update_signal = pyqtSignal(int)
    
    def __init__(self, directory, job, n, postfix):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num = n
        self.postfix = postfix
        self.is_killed = False

    def stopRunning(self):
        self.terminate()
        self.wait()

    def kill(self):
        self.is_killed = True

    def run(self):
        time.sleep(60)
        i = 1
        if os.path.exists(f"{self.dir}Outliers/CtfFind") == False:
            os.mkdir(f"{self.dir}Outliers/CtfFind")
        if os.path.exists(f"{self.dir}Outliers/MotionCorr") == False:
            os.mkdir(f"{self.dir}Outliers/MotionCorr")

        while i <= int(self.num):
            if os.path.exists(f"{self.dir}CtfFind/{self.job}_DataFile1.txt"):
                m = 0
                with open(f"{self.dir}CtfFind/{self.job}_DataFile1.txt") as data_f:
                    data_lines = data_f.readlines()

                if len(data_lines) >= i:
                    new_data = time_to_data_trans(data_lines)
                    Data = np.array(new_data)
                    low_score_list = list(np.nonzero(Data[:,-4] < 0.08)[0])
                    large_drift_list = list(np.nonzero(Data[:,-1] > 30)[0])
                    low_resolution_list = list(np.nonzero(Data[:,-3] > 6)[0])
                    outlier_list = list(reduce(np.union1d, (low_score_list, large_drift_list, low_resolution_list)))
                    for a in outlier_list:
                        if os.path.exists(f"{self.dir}{self.job}_%04d.{self.postfix}" % (a+1)):
                            shutil.move(f"{self.dir}{self.job}_%04d.{self.postfix}" % (a+1), f"{self.dir}Outliers/{self.job}_%04d_.{self.postfix}" % (a+1))
                            print(f"Remove outlier No.%04d" % (a+1))
                    self.graph_update_signal.emit(new_data, outlier_list)
                    i = len(data_lines)
                    self.progress_update_signal.emit(i)
                    i += 1
                    time.sleep(10)
                else:
                    print(f"Waiting for data of No.{i} image...")
                    time.sleep(45)
                    m += 1
                    if m > 40000:
                        break
            elif self.is_killed:
                raise WorkerKilledException        
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
    """定义异常数据监测的线程"""
    low_score_signal = pyqtSignal(int)
    large_drift_signal = pyqtSignal(int)
    def __init__(self, directory, job, num, data, start1, start2):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num = num
        self.data = np.array(data)
        self.motion_start = start1
        self.ctf_start = start2

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        os.chdir(f"{self.dir}")
        if self.num == self.ctf_start:
            if np.sum(self.data[(self.num-50):,-4] < 0.08) >= 10:
                low_score_array = np.where(self.data[(self.num-50):,-4] < 0.08)[0]
                low_score_number = len(low_score_array)
                for index in low_score_array:
                    while True:
                        if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1)):
                            shutil.copy(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1), f"{self.dir}Outliers/CtfFind/{self.job}_%04d_all.png" % (index+1))
                            break
                        else:
                            time.sleep(10)
                self.low_score_signal.emit(low_score_number)
        if self.num >= self.motion_start:
            if np.sum(self.data[(self.num-50):,-1] > 30) >= 10:
                large_drift_array = np.where(self.data[(self.num-50):,-1] > 30)[0]
                large_drift_number = len(large_drift_array)
                for index in large_drift_array:
                    while True:
                        if os.path.exists(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1)):
                            shutil.copy(f"{self.dir}Display/{self.job}_%04d_all.png" % (index+1), f"{self.dir}Outliers/MotionCorr/{self.job}_%04d_all.png" % (index+1))
                            break
                        else:
                            time.sleep(10)
                self.large_drift_signal.emit(large_drift_number)

class Worker5(QThread):
    """定义二维分类的线程"""
    classification_signal = pyqtSignal(int, int)
    def __init__(self, directory, job, num_s, num_e, outliers):
        super().__init__()
        self.dir = directory
        self.job = job
        self.num_s = num_s
        self.num_e = num_e
        self.outliers = outliers

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        t0 = time.time()
        os.chdir(f"{self.dir}")
        start_n = 1
        #将之前照片里的颗粒坐标提取出来
        for i in range(self.num_s, self.num_e+1):
            if i-1 in self.outliers:
                if i == start_n:
                    start_n += 1
                    continue
                else:
                    continue
            else:
                m = 0
                while m < 1:
                    if os.path.exists(f"Extract/particles_%04d.star" % (i)):
                        if i == start_n:
                            with open(f"Extract/particles_%04d.star" % (i), 'r') as firstfile, open(f"Extract/particles_{self.num_s}to{self.num_e}.star", 'w') as secondfile:
                                lines = firstfile.readlines()
                                secondfile.writelines(lines[:-1])
                        else:
                            with open(f"Extract/particles_%04d.star" % (i), 'r') as firstfile, open(f"Extract/particles_{self.num_s}to{self.num_e}.star", 'a') as secondfile:
                                lines = firstfile.readlines()
                                secondfile.writelines(lines[40:-1])
                        m += 1
                    else:
                        time.sleep(2)
                        print(f"Waiting for extract results of No.{i} image...")
        if os.path.exists(f"Class2D/run{self.num_s}to{self.num_e}/") == False:
            os.mkdir(f"Class2D/run{self.num_s}to{self.num_e}/")
        #对所有颗粒进行二维分类
        pid5 = subprocess.Popen(f"relion_refine --o Class2D/run{self.num_s}to{self.num_e}/ --iter 25 --i Extract/particles_{self.num_s}to{self.num_e}.star --dont_combine_weights_via_disc --preread_images  --pool 30 --pad 2  --ctf  --tau2_fudge 2 --particle_diameter 200 --K 50 --flatten_solvent  --zero_mask  --center_classes  --oversampling 1 --psi_step 12 --offset_range 5 --offset_step 2 --norm --scale  --j 32 >> Class2D/{self.job}_auto_class2D_{self.num_s}to{self.num_e}.txt", shell = True).pid
        time.sleep(300)
        n = 0
        while n < 1:
            if os.path.exists(f"Class2D/run{self.num_s}to{self.num_e}/_it025_optimiser.star"):
                t1 = time.time()
                td1 = t1-t0
                with open(f"timer_2D_classification.txt", 'a') as f:
                    print(f"2D classification of reference took: {td1}", file=f)
                if os.path.exists(f"Select/run{self.num_s}to{self.num_e}/") == False:
                    os.mkdir(f"Select/run{self.num_s}to{self.num_e}/")
                #对二维分类打分
                pid6 = subprocess.Popen(f"relion_class_ranker --opt Class2D/run{self.num_s}to{self.num_e}/_it025_optimiser.star --o Select/run{self.num_s}to{self.num_e}/ --fn_sel_parts particles.star --fn_sel_classavgs class_averages.star --python python3 --fn_root rank --do_granularity_features  --auto_select  --min_score 0.04", shell=True).pid
                n += 1
                time.sleep(3)
                subprocess.run(f"plot_classes.py {self.num_s} {self.num_e} {self.dir} 25", shell = True)
                self.classification_signal.emit(self.num_s, self.num_e)
            else:
                time.sleep(20)
                print(f"Waiting for 2D classification results of No.{self.num_s} to {self.num_e}...")
        

class Worker6(QThread):
    """定义二维分类和三维建模的线程"""
    update_classification_signal = pyqtSignal(int, int)
    def __init__(self, directory, num_s, num_e, num_r, outliers):
        super().__init__()
        self.dir = directory
        self.num_s = num_s
        self.num_e = num_e
        self.num_r = num_r
        self.outliers = outliers

    def stopRunning(self):
        self.terminate()
        self.wait()

    def run(self):
        t0 = time.time()
        os.chdir(f"{self.dir}")
        l = 0 
        while l < 1:
            if os.path.exists(f"Select/run1to{self.num_r}/class_averages.star"):
                start_n = self.num_s
                for i in range(self.num_s, self.num_e+1):
                    if i-1 in self.outliers:
                        if i == start_n:
                            start_n += 1
                            continue
                        else:
                            continue
                    else:
                        if i == start_n:
                            with open(f"CtfFind/micrograph_%04d_ctf.star" % (i), 'r') as firstfile, open(f"CtfFind/micrographs_{self.num_s}to{self.num_e}_ctf.star", 'w') as secondfile:
                                lines = firstfile.readlines()
                                secondfile.writelines(lines)
                        else:
                            with open(f"CtfFind/micrograph_%04d_ctf.star" % (i), 'r') as firstfile, open(f"CtfFind/micrographs_{self.num_s}to{self.num_e}_ctf.star", 'a') as secondfile:
                                lines = firstfile.readlines()
                                secondfile.writelines(lines[-1])
                #用模板挑颗粒
                pid7 = subprocess.Popen(f"relion_autopick --i CtfFind/micrographs_{self.num_s}to{self.num_e}_ctf.star --odir AutoPick/ --pickname autopick_{self.num_s}to{self.num_e} --ref Select/run1to{self.num_r}/class_averages.star --invert  --ctf  --ang 5 --shrink 0 --lowpass 20 --angpix_ref 3.54 --threshold 0.8 --min_distance 100 --max_stddev_noise -1 --gpu '0' --only_do_unfinished", shell = True).pid
                time.sleep(8)
                l += 1
            else:
                time.sleep(3)
                print(f"Waiting for class ranker results of No.1 to {self.num_r}...")
        o = 0
        while o < 1:
            if os.path.exists(f"AutoPick/autopick_{self.num_s}to{self.num_e}.star"):
                #提取用模板挑出来的颗粒坐标
                t1 = time.time()
                td1 = t1-t0
                with open(f"timer_autopicking_r.txt", 'a') as f:
                    print(f"reference-based autopicking took: {td1}", file=f)
                pid8 = subprocess.Popen(f"relion_preprocess --i CtfFind/micrographs_{self.num_s}to{self.num_e}_ctf.star --coord_list AutoPick/autopick_{self.num_s}to{self.num_e}.star --part_star Extract/particles_{self.num_s}to{self.num_e}.star --part_dir Extract/ --extract --extract_size 256 --float16  --scale 64 --norm --bg_radius 25 --white_dust -1 --black_dust -1 --invert_contrast  --only_do_unfinished", shell = True).pid
                time.sleep(3)
                o += 1
            else:
                time.sleep(10)
                print(f"Waiting for reference-based autopicking results of No.{self.num_s} to {self.num_e}...")
        p = 0
        while p < 1:
            if os.path.exists(f"Extract/particles_{self.num_s}to{self.num_e}.star"):
                if os.path.exists(f"Class2D/run{self.num_s}to{self.num_e}/") == False:
                    os.mkdir(f"Class2D/run{self.num_s}to{self.num_e}/")
                #二维分类
                pid9 = subprocess.Popen(f"relion_refine --o Class2D/run{self.num_s}to{self.num_e}/ --grad --class_inactivity_threshold 0.1 --grad_write_iter 10 --iter 100 --i Extract/particles_{self.num_s}to{self.num_e}.star --dont_combine_weights_via_disc --preread_images  --pool 30 --pad 2  --ctf  --tau2_fudge 2 --particle_diameter 200 --K 100 --flatten_solvent  --zero_mask  --center_classes  --oversampling 1 --psi_step 12 --offset_range 5 --offset_step 2 --norm --scale  --j 24 --gpu '0' ", shell=True).pid
                p += 1
                time.sleep(300)
            else:
                time.sleep(3)
                print(f"Waiting for reference-based extract results of No.{self.num_s} to {self.num_e}...")        
        q = 0
        while q < 1:
            if os.path.exists(f"Class2D/run{self.num_s}to{self.num_e}/_it100_optimiser.star"):
                t2 = time.time()
                td2 = t2-t1
                with open(f"timer_2D_classification_r.txt", 'a') as f:
                    print(f"reference-based 2D classification took: {td2}", file=f)
                if os.path.exists(f"Select/run{self.num_s}to{self.num_e}/") == False:
                    os.mkdir(f"Select/run{self.num_s}to{self.num_e}/")
                #给二维分类打分
                pid10 = subprocess.Popen(f"relion_class_ranker --opt Class2D/run{self.num_s}to{self.num_e}/_it100_optimiser.star --o Select/run{self.num_s}to{self.num_e}/ --fn_sel_parts particles.star --fn_sel_classavgs class_averages.star --python python3 --fn_root rank --do_granularity_features  --auto_select  --min_score 0.05", shell=True).pid
                subprocess.run(f"plot_classes.py {self.num_s} {self.num_e} {self.dir} 100",  shell = True)
                self.update_classification_signal.emit(self.num_s, self.num_e)
                q += 1
                time.sleep(5)
            else:
                time.sleep(20)
                print(f"Waiting for reference-based 2D classification results of No.{self.num_s} to {self.num_e}...")
        r = 0
        while r < 1:
            if os.path.exists(f"Select/run{self.num_s}to{self.num_e}/particles.star"):
                if os.path.exists(f"InitialModel/run{self.num_s}to{self.num_e}/") == False:
                    os.mkdir(f"InitialModel/run{self.num_s}to{self.num_e}/")
                pid11 = subprocess.Popen(f"relion_refine --o InitialModel/run{self.num_s}to{self.num_e}/ --iter 100 --grad --denovo_3dref  --i Select/run{self.num_s}to{self.num_e}/particles.star --ctf --K 1 --sym C1  --flatten_solvent  --zero_mask  --dont_combine_weights_via_disc --preread_images  --pool 3 --pad 1  --particle_diameter 200 --oversampling 1  --healpix_order 1  --offset_range 6  --offset_step 2 --auto_sampling  --tau2_fudge 2 --j 24 --gpu '0' && relion_align_symmetry --i InitialModel/run{self.num_s}to{self.num_e}/_it100_model.star --o InitialModel/run{self.num_s}to{self.num_e}/_initial_model.mrc --sym D2 --apply_sym --select_largest_class", shell=True).pid
                r += 1
            else:
                time.sleep(5)
                print(f"Waiting for reference-based class ranker results of No.{self.num_s} to {self.num_e}...")
        s = 0
        while s < 1:
            if os.path.exists(f"InitialModel/run{self.num_s}to{self.num_e}/_initial_model.mrc"):
                t3 = time.time()
                td3 = t3-t2
                with open(f"timer_3D_modeling.txt", 'a') as f:
                    print(f"3D modeling took: {td3}", file=f)
                subprocess.run(f"chimerax {self.dir}InitialModel/run{self.num_s}to{self.num_e}/_initial_model.mrc", shell=True)
                s += 1
            else:
                time.sleep(30)
                print("Waiting for 3D initial modeling results...")
