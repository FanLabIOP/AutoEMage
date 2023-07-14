"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/24
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
from PyQt6.QtWidgets import QMainWindow, QLabel, QCheckBox, QButtonGroup, QSlider, QSpinBox, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QToolBar, QMessageBox, QSizePolicy, QStatusBar
from PyQt6.QtGui import QFont, QAction, QIcon
from PyQt6.QtCore import Qt, QSize

import os, signal
import time
import glob

from autoemage_canvas import MplCanvas
from autoemage_help import HelpWindow
from autoemage_settings import EMWindow
from autoemage_input import InputWindow
from autoemage_classification import ClassifyWindow
from autoemage_threads import Worker1, Worker2, Worker3

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as img
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage



matplotlib.use("QtAgg") #绘制图形界面所用的后端

class MainWindow(QMainWindow):
    def __init__(self, user, name, language): 
        super().__init__()
        self.setMinimumSize(950, 500)
        self.setWindowTitle("得息镜 - AutoEMage")
        self.center()
        #定义一些核心变量 define several core variables
        #语言 language
        self.language = language
        #文件路径 directory
        filepath = os.path.realpath(__file__)
        self.path = os.path.dirname(filepath)
        #计算文件夹 calculation directory
        #self.cal_dir = f"users/{name}/"
        #任务名称
        self.job_name = ''
        if self.language == 1:
            self.sample_name = "未命名" #样品名称
        else:
            self.sample_name = "Unknown"
        #相机名称
        self.camera_name = "K3"
        #放大倍数
        self.magnification = ""
        #像素尺寸
        self.pixel_size = "0.0"
        #总剂量
        self.total_dose = "0"
        #照片总张数
        self.image_num = "0"
        #当前照片（编号）the number of the current image
        self.current_n = 0
        #最新照片（编号）the number of the latest image
        self.max_n = 0
        #照片数据
        self.data = []
        #计算路径
        self.cal_dir1 = ""
        #画图选项（编号）
        self.option = 0
        #转移文件进程pid
        self.mv_process = 0
        #ctf计算进程pid
        self.ctf_process = 0
        #邮箱服务器
        self.mail_host = 'smtp.163.com'
        #发送邮箱用户名
        self.mail_user = 'cryo_EM_2022'
        #发送邮箱授权码
        self.mail_pass = 'KFJAVPYMKHEOTZRO'
        #发送邮箱
        self.sender = 'cryo_EM_2022@163.com'
        self.receiver = user
        #画图时间起点 time start
        self.time_s = 0
        #画图时间终点 time end
        self.time_e = 20
        #异常数据计数 
        self.count = 0
        #异常打分计数
        self.low_score_count = 0
        self.setUpMainWindow()
        self.createActions() #工具
        self.createMenu() #菜单栏
        self.createToolBar() #工具栏
        self.setStatusBar(QStatusBar()) #状态栏

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setUpMainWindow(self):
        """设置主界面"""
        if self.language == 1:
            #样品信息栏
            sample_label = QLabel("样品名称：")
            sample_label.setFont(QFont('Times',12))
            self.sample_label_value = QLabel()
            self.sample_label_value.setFont(QFont('Times',12))
            self.sample_label_value.setText(f"{self.sample_name}")
            camera_label = QLabel("相机名称：")
            camera_label.setFont(QFont('Times',12))
            self.camera_label_value = QLabel()
            self.camera_label_value.setFont(QFont('Times',12))
            self.camera_label_value.setText(f"{self.camera_name}")
            pixel_label = QLabel("像素尺寸：")
            pixel_label.setFont(QFont('Times',12))
            self.pixel_label_value = QLabel()
            self.pixel_label_value.setFont(QFont('Times',12))
            self.pixel_label_value.setText(f"{self.pixel_size}")
            mag_label = QLabel("放大倍数：")
            mag_label.setFont(QFont('Times',12))
            self.mag_label_value = QLabel()
            self.mag_label_value.setFont(QFont('Times',12))
            self.mag_label_value.setText(f"{self.magnification}")
            dose_label = QLabel("总剂量 (e/A2)：")
            dose_label.setFont(QFont('Times',12))
            self.dose_label_value = QLabel()
            self.dose_label_value.setFont(QFont('Times',12))
            self.dose_label_value.setText(f"{self.total_dose}")
            #左侧散点图
            self.l_canvas = MplCanvas(self, width=4, height=3.5, dpi=100)
            l_toolbar = NavigationToolbar2QT(self.l_canvas, self)
            #物理量展示勾选框
            display_cb0 = QCheckBox("欠焦值 (um)")
            display_cb0.setChecked(True)
            display_cb1 = QCheckBox("像散 (Angstrom)")
            display_cb2 = QCheckBox("像散角 (度)")
            display_cb3 = QCheckBox("像移 (rad)")
            display_cb4 = QCheckBox("CTF 打分")
            display_cb5 = QCheckBox("CTF 拟合分辨率 (Angstrom)")
            display_cb6 = QCheckBox("硬盘使用 (%)")
            display_cb7 = QCheckBox("总漂移 (Angstrom)")
            display_cb0.setFont(QFont('Times',12))
            display_cb1.setFont(QFont('Times',12))
            display_cb2.setFont(QFont('Times',12))
            display_cb3.setFont(QFont('Times',12))
            display_cb4.setFont(QFont('Times',12))
            display_cb5.setFont(QFont('Times',12))
            display_cb6.setFont(QFont('Times',12))
            display_cb7.setFont(QFont('Times',12))
            display_group = QButtonGroup(self)
            display_group.addButton(display_cb0)
            display_group.addButton(display_cb1)
            display_group.addButton(display_cb2)
            display_group.addButton(display_cb3)
            display_group.addButton(display_cb4)
            display_group.addButton(display_cb5)
            display_group.addButton(display_cb6)
            display_group.addButton(display_cb7)            
            display_cb0.toggled.connect(lambda: self.setParaPlot(0))
            display_cb0.setStatusTip("绘制欠焦值图")
            display_cb1.toggled.connect(lambda: self.setParaPlot(1))
            display_cb1.setStatusTip("绘制像散图")
            display_cb2.toggled.connect(lambda: self.setParaPlot(2))
            display_cb2.setStatusTip("绘制像散角图")
            display_cb3.toggled.connect(lambda: self.setParaPlot(3))
            display_cb3.setStatusTip("绘制像移图")
            display_cb4.toggled.connect(lambda: self.setParaPlot(4))
            display_cb4.setStatusTip("绘制CTF打分 (CTF拟合好坏) 图")
            display_cb5.toggled.connect(lambda: self.setParaPlot(5))
            display_cb5.setStatusTip("绘制CTF拟合分辨率图")
            display_cb6.toggled.connect(lambda: self.setParaPlot(6))
            display_cb6.setStatusTip("绘制硬盘使用图")
            display_cb7.toggled.connect(lambda: self.setParaPlot(7))
            display_cb7.setStatusTip("绘制总漂移图")
            #时间轴滑块
            time_start = QLabel("时间起点")
            time_start.setFont(QFont('Times',12))
            self.time_slider1 = QSlider(Qt.Orientation.Horizontal)
            self.time_slider1.setSliderPosition(0)
            time_end = QLabel("时间终点")
            time_end.setFont(QFont('Times',12))
            self.time_slider2 = QSlider(Qt.Orientation.Horizontal)
            self.time_slider2.setSliderPosition(20)
            #右侧展示图
            self.r_canvas = MplCanvas(self, width=6, height=5, dpi=100)
            r_toolbar = NavigationToolbar2QT(self.r_canvas, self)
            #照片信息展示栏
            current_image = QLabel("当前照片：")
            current_image.setFont(QFont('Times',12))
            self.cur_image_value = QLabel()
            image_defocus = QLabel('欠焦值 (um)：')
            image_defocus.setFont(QFont('Times',12))
            self.defocus_value = QLabel()
            phase_shift = QLabel("像散 (A)：")
            phase_shift.setFont(QFont('Times',12))
            self.astigmatism_value = QLabel()
            #照片查看按钮栏
            self.image_num_sb = QSpinBox()
            self.image_num_sb.setStatusTip("选择并展示所选照片")
            self.image_num_sb.setRange(0,12000)
            ok_button2 = QPushButton("确定")
            ok_button2.clicked.connect(self.chooseImage)
            ok_button2.setStatusTip("选择并展示所选照片")
            previous_button = QPushButton("前一张")
            previous_button.setStatusTip("展示前一张照片")
            previous_button.clicked.connect(lambda: self.shiftImage(-1))
            next_button = QPushButton("后一张")
            next_button.clicked.connect(lambda: self.shiftImage(1))
            next_button.setStatusTip("展示后一张照片")
            refresh_button = QPushButton("刷新")
            refresh_button.clicked.connect(self.updateImage)
            refresh_button.setStatusTip("展示最新照片")
        else:
            #sample information labels
            sample_label = QLabel("Sample:")
            sample_label.setFont(QFont('Times',12))
            self.sample_label_value = QLabel()
            self.sample_label_value.setFont(QFont('Times',12))
            self.sample_label_value.setText(f"{self.sample_name}")
            camera_label = QLabel("Camera:")
            camera_label.setFont(QFont('Times',12))
            self.camera_label_value = QLabel()
            self.camera_label_value.setFont(QFont('Times',12))
            self.camera_label_value.setText(f"{self.camera_name}")
            pixel_label = QLabel("Pixel size:")
            pixel_label.setFont(QFont('Times',12))
            self.pixel_label_value = QLabel()
            self.pixel_label_value.setFont(QFont('Times',12))
            self.pixel_label_value.setText(f"{self.pixel_size}")
            mag_label = QLabel("Magnification:")
            mag_label.setFont(QFont('Times',12))
            self.mag_label_value = QLabel()
            self.mag_label_value.setFont(QFont('Times',12))
            self.mag_label_value.setText(f"{self.magnification}")
            dose_label = QLabel("Total dose (e/A2):")
            dose_label.setFont(QFont('Times',12))
            self.dose_label_value = QLabel()
            self.dose_label_value.setFont(QFont('Times',12))
            self.dose_label_value.setText(f"{self.total_dose}")
            #variables plot on the left
            self.l_canvas = MplCanvas(self, width=4, height=3.5, dpi=100)
            l_toolbar = NavigationToolbar2QT(self.l_canvas, self)
            #variables checkbox for display
            display_cb0 = QCheckBox("Defocus (um)")
            display_cb0.setChecked(True)
            display_cb1 = QCheckBox("Astigmatism (Angstrom)")
            display_cb2 = QCheckBox("Astigmatism angle (degree)")
            display_cb3 = QCheckBox("Phase shift (rad)")
            display_cb4 = QCheckBox("CTF score")
            display_cb5 = QCheckBox("CTF max resolution (Angstrom)")
            display_cb6 = QCheckBox("Disk usage (%)")
            display_cb7 = QCheckBox("Total drift (Angstrom)")
            display_cb0.setFont(QFont('Times',12))
            display_cb1.setFont(QFont('Times',12))
            display_cb2.setFont(QFont('Times',12))
            display_cb3.setFont(QFont('Times',12))
            display_cb4.setFont(QFont('Times',12))
            display_cb5.setFont(QFont('Times',12))
            display_cb6.setFont(QFont('Times',12))
            display_cb7.setFont(QFont('Times',12))
            display_group = QButtonGroup(self)
            display_group.addButton(display_cb0)
            display_group.addButton(display_cb1)
            display_group.addButton(display_cb2)
            display_group.addButton(display_cb3)
            display_group.addButton(display_cb4)
            display_group.addButton(display_cb5)
            display_group.addButton(display_cb6)
            display_group.addButton(display_cb7)
            display_cb0.toggled.connect(lambda: self.setParaPlot(0))
            display_cb1.toggled.connect(lambda: self.setParaPlot(1))
            display_cb2.toggled.connect(lambda: self.setParaPlot(2))
            display_cb3.toggled.connect(lambda: self.setParaPlot(3))
            display_cb4.toggled.connect(lambda: self.setParaPlot(4))
            display_cb5.toggled.connect(lambda: self.setParaPlot(5))
            display_cb6.toggled.connect(lambda: self.setParaPlot(6))
            display_cb7.toggled.connect(lambda: self.setParaPlot(7))
            #time sliders
            time_start = QLabel("Time start")
            time_start.setFont(QFont('Times',12))
            self.time_slider1 = QSlider(Qt.Orientation.Horizontal)
            self.time_slider1.setSliderPosition(0)
            time_end = QLabel("Time end  ")
            time_end.setFont(QFont('Times',12))
            self.time_slider2 = QSlider(Qt.Orientation.Horizontal)
            self.time_slider2.setSliderPosition(20)
            #display on the right side
            self.r_canvas = MplCanvas(self, width=5.5, height=4.5, dpi=100)
            r_toolbar = NavigationToolbar2QT(self.r_canvas, self)
            #Image information
            current_image = QLabel("Current image:")
            current_image.setFont(QFont('Times',12))
            self.cur_image_value = QLabel()
            image_defocus = QLabel('Defocus (um):')
            image_defocus.setFont(QFont('Times',12))
            self.defocus_value = QLabel()
            phase_shift = QLabel("Astigmatism (A):")
            phase_shift.setFont(QFont('Times',12))
            self.astigmatism_value = QLabel()
            #Image display buttons
            self.image_num_sb = QSpinBox()
            self.image_num_sb.setStatusTip("Choose and display a specific image")
            self.image_num_sb.setRange(0,12000)
            ok_button2 = QPushButton("OK")
            ok_button2.clicked.connect(self.chooseImage)
            ok_button2.setStatusTip("Choose and display a specific image")
            previous_button = QPushButton("Previous")
            previous_button.clicked.connect(lambda: self.shiftImage(-1))
            next_button = QPushButton("Next")
            next_button.clicked.connect(lambda: self.shiftImage(1))
            refresh_button = QPushButton("Update")
            refresh_button.clicked.connect(self.updateImage)
        #界面格式设置 layout setting
        #左侧界面 left side
        grid = QGridLayout()
        grid.addWidget(sample_label, 0, 0)
        grid.addWidget(self.sample_label_value, 0, 1, 1, 2)
        grid.addWidget(camera_label, 1, 0)
        grid.addWidget(self.camera_label_value, 1, 1)
        grid.addWidget(mag_label, 1, 2)
        grid.addWidget(self.mag_label_value, 1, 3, 1, 2)
        grid.addWidget(pixel_label, 2, 0)
        grid.addWidget(self.pixel_label_value, 2, 1)
        grid.addWidget(dose_label, 2, 2)
        grid.addWidget(self.dose_label_value, 2, 3)
        l_v_box = QVBoxLayout()
        l_v_box.addStretch()
        l_v_box.addWidget(display_cb0)
        l_v_box.addWidget(display_cb1)
        l_v_box.addWidget(display_cb2)
        l_v_box.addWidget(display_cb3)
        l_v_box.addWidget(display_cb4)
        l_v_box.addWidget(display_cb5)
        l_v_box.addWidget(display_cb6)
        l_v_box.addWidget(display_cb7)
        l_v_box.addStretch()
        ll_v_box = QVBoxLayout()
        ll_v_box.addWidget(l_toolbar, Qt.AlignmentFlag.AlignCenter)
        ll_v_box.addWidget(self.l_canvas)
        lside_h_box = QHBoxLayout()
        lside_h_box.addLayout(ll_v_box)
        lside_h_box.addLayout(l_v_box)
        lside_h_box1 = QHBoxLayout()
        lside_h_box1.addSpacing(10)
        lside_h_box1.addWidget(time_start)
        lside_h_box1.addSpacing(13)
        lside_h_box1.addWidget(self.time_slider1)
        lside_h_box1.addStretch()
        lside_h_box2 = QHBoxLayout()
        lside_h_box2.addSpacing(10)
        lside_h_box2.addWidget(time_end)
        lside_h_box2.addSpacing(13)
        lside_h_box2.addWidget(self.time_slider2)
        lside_h_box2.addStretch()
        lside_v_box = QVBoxLayout()
        lside_v_box.addSpacing(15)
        lside_v_box.addLayout(grid)
        lside_v_box.addSpacing(15)
        lside_v_box.addLayout(lside_h_box)
        lside_v_box.addLayout(lside_h_box1)
        lside_v_box.addLayout(lside_h_box2)
        #右侧界面 right side
        rside_h_box1 = QHBoxLayout()
        rside_h_box1.addWidget(current_image, Qt.AlignmentFlag.AlignLeft)
        rside_h_box1.addWidget(self.cur_image_value, Qt.AlignmentFlag.AlignLeft)
        rside_h_box1.addWidget(image_defocus, Qt.AlignmentFlag.AlignLeft)
        rside_h_box1.addWidget(self.defocus_value, Qt.AlignmentFlag.AlignLeft)
        rside_h_box1.addWidget(phase_shift, Qt.AlignmentFlag.AlignLeft)
        rside_h_box1.addWidget(self.astigmatism_value, Qt.AlignmentFlag.AlignLeft)
        rside_h_box2 = QHBoxLayout()
        rside_h_box2.addWidget(self.image_num_sb, Qt.AlignmentFlag.AlignLeft)
        rside_h_box2.addWidget(ok_button2, Qt.AlignmentFlag.AlignLeft)
        rside_h_box2.addWidget(previous_button, Qt.AlignmentFlag.AlignLeft)
        rside_h_box2.addWidget(next_button, Qt.AlignmentFlag.AlignLeft)
        rside_h_box2.addWidget(refresh_button, Qt.AlignmentFlag.AlignLeft)
        rside_v_box = QVBoxLayout()
        rside_v_box.addStretch()
        rside_v_box.addWidget(r_toolbar, Qt.AlignmentFlag.AlignRight)
        rside_v_box.addWidget(self.r_canvas, Qt.AlignmentFlag.AlignLeft)
        rside_v_box.addStretch()
        rside_v_box.addLayout(rside_h_box1)
        rside_v_box.addStretch()
        rside_v_box.addLayout(rside_h_box2)
        #主界面 main window
        main_h_box = QHBoxLayout()
        main_h_box.addLayout(lside_v_box)
        main_h_box.addSpacing(25)
        main_h_box.addLayout(rside_v_box)
        self.main_widget = QWidget()
        self.main_widget.setLayout(main_h_box)
        self.setCentralWidget(self.main_widget)

    def createActions(self):
        """功能设置 function setting"""
        if self.language == 1:
            #文件转移功能
            self.input_values_act = QAction(QIcon(f"{self.path}/images/input_values.png"), "转移文件")
            self.input_values_act.setStatusTip("输入参数并开始自动转移文件")
            self.input_values_act.triggered.connect(self.setUpInputWindow)
            #终止任务功能
            self.kill_act = QAction(QIcon(f"{self.path}/images/kill.png"), "终止")
            self.kill_act.setStatusTip("终止转移文件")
            self.kill_act.triggered.connect(self.killTransfer)
            self.kill_act.setDisabled(True)
            #暂停任务功能
            self.stop_act = QAction(QIcon(f"{self.path}/images/stop.png"), "暂停")
            self.stop_act.setStatusTip("暂停转移文件")
            self.stop_act.triggered.connect(self.stopTransfer)
            self.stop_act.setDisabled(True)
            #继续任务功能
            self.play_act = QAction(QIcon(f"{self.path}/images/play.png"), "继续")
            self.play_act.setStatusTip("继续转移文件")
            self.play_act.triggered.connect(self.contTransfer)
            self.play_act.setDisabled(True)
            #粒子挑选与分类功能
            self.classify_act = QAction(QIcon(f"{self.path}/images/tag.png"), "粒子分类")
            self.classify_act.setStatusTip("粒子挑选与分类")
            self.classify_act.triggered.connect(self.setUpClassifyWindow)
            #帮助功能
            self.about_act = QAction("使用说明")
            self.about_act.triggered.connect(self.aboutDialog)
            #电镜设置功能（未完成）
            self.EMsetting_act = QAction("电镜设置")
            self.EMsetting_act.triggered.connect(self.setEM)
        else:
            #file transfer
            self.input_values_act = QAction(QIcon(f"{self.path}/images/input_values.png"), "File Transfer")
            self.input_values_act.setStatusTip("Input values and start file transfer")
            self.input_values_act.triggered.connect(self.setUpInputWindow)
            #kill job
            self.kill_act = QAction(QIcon(f"{self.path}/images/kill.png"), "Kill")
            self.kill_act.setStatusTip("Kill Job")
            self.kill_act.triggered.connect(self.killTransfer)
            self.kill_act.setDisabled(True)
            #stop job
            self.stop_act = QAction(QIcon(f"{self.path}/images/stop.png"), "Stop")
            self.stop_act.setStatusTip("Stop Job")
            self.stop_act.triggered.connect(self.stopTransfer)
            self.stop_act.setDisabled(True)
            #continue job
            self.play_act = QAction(QIcon(f"{self.path}/images/play.png"), "Continue")
            self.play_act.setStatusTip("Continue Job")
            self.play_act.triggered.connect(self.contTransfer)
            self.play_act.setDisabled(True)
            #help
            self.about_act = QAction("User Manual")
            self.about_act.triggered.connect(self.aboutDialog)
            #particle picking and 2D classification
            self.classify_act = QAction(QIcon(f"{self.path}/images/tag.png"), "Particle Classification")
            self.classify_act.setStatusTip("Particle Picking and Classification")
            self.classify_act.triggered.connect(self.setUpClassifyWindow)
            #electron microscope settings (incomplete)
            self.EMsetting_act = QAction("EM settings")
            self.EMsetting_act.triggered.connect(self.setEM)

    def createMenu(self):
        """菜单栏设置 Menu settings"""
        self.menuBar().setNativeMenuBar(False)
        if self.language == 1:
            set_menu = self.menuBar().addMenu("设置")
            help_menu = self.menuBar().addMenu("帮助")
        else:
            set_menu = self.menuBar().addMenu("Settings")
            help_menu = self.menuBar().addMenu("Help")
        set_menu.addAction(self.EMsetting_act)
        help_menu.addAction(self.about_act)

    def createToolBar(self):
        '''工具栏设置 toolbar setting'''
        self.progress_bar = QProgressBar()
        if self.language == 1:
            self.progress_bar.setStatusTip("转移文件进度条")
        else:
            self.progress_bar.setStatusTip("Progress bar for the job")
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        tool_bar = QToolBar("cryo-EM Toolbar")
        tool_bar.setIconSize(QSize(24,24)) #图标大小设置 
        self.addToolBar(tool_bar)
        tool_bar.addAction(self.input_values_act)
        tool_bar.addWidget(self.progress_bar)
        tool_bar.addSeparator()
        tool_bar.addAction(self.kill_act)
        tool_bar.addAction(self.play_act)
        tool_bar.addAction(self.stop_act)
        tool_bar.addSeparator()
        tool_bar.addAction(self.classify_act)

    def setEM(self):
        '''打开设置窗口 open EM setting window'''
        self.EMwindow = EMWindow()

    def aboutDialog(self):
        """打开使用说明 open user manual"""
        self.help_window = HelpWindow(self.language)

    def setUpInputWindow(self):
        """打开输入参数窗口 open input window"""
        self.inputwindow = InputWindow(self.language)
        self.inputwindow.input_values_signal.connect(self.checkFile)
        self.inputwindow.processes_signal.connect(self.updateProcess)

    def setUpClassifyWindow(self):
        """打开粒子分类窗口 open classify window"""
        if self.max_n < 10:
            if self.language == 1:
                QMessageBox.information(self, "提示","照片数量不足，请等待", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Insufficient images, please wait", QMessageBox.StandardButton.Ok)
        else:            
            self.classify_window = ClassifyWindow(self.cal_dir1, self.language, self.job_name, self.image_num)

    def stopTransfer(self):
        """暂停转移"""
        os.kill(self.mv_process, signal.SIGSTOP)
        os.kill(self.ctf_process, signal.SIGSTOP)
        self.play_act.setEnabled(True)
        self.stop_act.setDisabled(True)

    def contTransfer(self):
        """继续转移"""
        os.kill(self.mv_process, signal.SIGCONT)
        os.kill(self.ctf_process, signal.SIGCONT)
        self.play_act.setDisabled(True)
        self.stop_act.setEnabled(True)

    def killTransfer(self):
        """终止转移"""
        os.kill(self.mv_process, signal.SIGKILL)
        os.kill(self.ctf_process, signal.SIGKILL)
        #self.worker1.stopRunning()
        #self.worker2.stopRunning()
        #self.worker3.stopRunning()
        self.kill_act.setDisabled(True)
        self.play_act.setDisabled(True)
        self.stop_act.setDisabled(True)
        self.input_values_act.setEnabled(True)
        self.progress_bar.reset()

    def updateProcess(self, p1, p2):
        """更新进程"""
        self.input_values_act.setDisabled(True)
        self.kill_act.setEnabled(True)
        self.stop_act.setEnabled(True)
        self.mv_process = p1 + 1
        self.ctf_process = p2 + 1

    def checkFile(self, job, num, dose, psize, directory):
        """开始线程 start threads"""
        self.data = []
        self.r_canvas.axes.cla()
        self.cal_dir1 = directory
        self.job_name = job
        self.image_num = num
        self.pixel_size = psize
        self.total_dose = dose
        self.sample_label_value.setText(f"{self.job_name}")
        self.pixel_label_value.setText(f"{self.pixel_size}")
        self.dose_label_value.setText(f"{self.total_dose}")
        self.time_slider1.setRange(0,self.time_e)
        self.time_slider1.valueChanged.connect(self.timeStart)
        self.time_slider2.setRange(0,int(num))
        self.time_slider2.valueChanged.connect(self.timeEnd)
        self.progress_bar.setMaximum(int(num))
        self.worker1 = Worker1(self.cal_dir1, self.job_name, self.image_num)
        self.worker1.image_update_signal.connect(self.updateNum)
        self.worker1.finished.connect(self.worker1.deleteLater)
        self.worker1.start()
        self.worker2 = Worker2(self.cal_dir1, self.job_name, self.image_num)
        self.worker2.graph_update_signal.connect(self.updateData)
        self.worker2.progress_update_signal.connect(self.updateProgress)
        self.worker2.low_score_signal.connect(self.lowScoreEmail)
        self.worker2.large_drift_signal.connect(self.motion_fail_Email)
        self.worker2.finished.connect(self.worker2.deleteLater)
        self.worker2.start()

    def updateNum(self, n):
        """更新最新照片（编号） update the number of image"""
        self.max_n = n
        self.updateRWindow(n)
        if self.max_n == 5000:
            self.halfFinished()
        if self.max_n == int(self.image_num):
            time.sleep(5)
            self.taskFinished()

    def updateProgress(self, n):
        """更新任务进度"""
        if n > int(self.image_num):
            n = int(self.image_num)
        self.progress_bar.setValue(n)

    def updateData(self, data):
        """更新数据并检查 update data and check outliers"""
        self.data = data
        self.paraPlot()
        self.worker3 = Worker3(self.data, self.cal_dir1, self.job_name)
        self.worker3.alert_signal.connect(self.alertF)
        self.worker3.disk_signal.connect(self.diskEmail)
        self.worker3.finished.connect(self.worker3.deleteLater)
        self.worker3.start()

    def alertF(self):
        """数据检查 counting outliers"""
        self.count += 1 
        if self.count >= 10:
            Data = np.array(self.data)
            x1 = Data[-40:,0]
            y1 = Data[-40:,1]
            fig, axes = plt.subplots(1,1)
            axes.plot_date(x1, y1, c='red')
            locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
            formatter = mdates.ConciseDateFormatter(locator)
            axes.xaxis.set_major_locator(locator)
            axes.xaxis.set_major_formatter(formatter)
            plt.close()
            fig.savefig(f"{self.cal_dir1}{self.job_name}_alert.png")
            self.alertEmail()
            self.count = 0  #异常数据归零 restart counting the number of outliers

    def alertEmail(self):
        """发送异常提示邮件 send reminding Emails for outliers"""
        if self.language == 1:
            content = """尊敬的科研工作者,\n\n您好！您的数据出现异常值，请及时检查电镜设置！\n\n得息镜"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = '异常提示'
            message['From'] = self.sender
            message['To'] = self.receiver
            with open (f"{self.cal_dir1}{self.job_name}_alert.png", 'rb') as imf:
                picture = MIMEImage(imf.read())
                picture.add_header('Content-Disposition', f'attachment;filename="{self.cal_dir1}{self.job_name}_alert.png"')
            message.attach(part1)
            message.attach(picture)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
        else:
            content = """Dear scientists,\n\nOutliers show up in your data. Please examine EM settings in time.\n\nAutoEMage"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = 'Outliers warning'
            message['From'] = self.sender
            message['To'] = self.receiver
            with open (f"{self.cal_dir1}{self.job_name}_alert.png", 'rb') as imf:
                picture = MIMEImage(imf.read())
                picture.add_header('Content-Disposition', 'attachment;filename=alert.png')
            message.attach(part1)
            message.attach(picture)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)

    def diskEmail(self):
        """发送提示邮件 send warning Emails on disk space"""
        if self.language == 1:
            content = """尊敬的科研工作者,\n\n您好！您的硬盘容量不足，已为您终止文件转移，请及时检查！\n\n得息镜"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = '硬盘使用提示'
            message['From'] = self.sender
            message['To'] = self.receiver
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
            self.killTransfer()
        else:
            content = """Dear scientists,\n\nYour disk space is almost full, so file transfer is stopped. Please check in time.\n\nAutoEMage"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = 'Full disk warning'
            message['From'] = self.sender
            message['To'] = self.receiver
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
            self.killTransfer()

    def taskFinished(self):
        """任务完成 job complete"""
        if self.language == 1:      
            QMessageBox.information(self, "提示",f"任务 {self.job_name} 已完成！", QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, "Information",f"Job {self.job_name} is finished!", QMessageBox.StandardButton.Ok)
        self.input_values_act.setEnabled(True)
        self.stop_act.setDisabled(True)
        self.play_act.setDisabled(True)
        self.kill_act.setDisabled(True)
        self.finishedEmail()

    def finishedEmail(self):
        """发送任务完成邮件 send job complete Email"""
        if self.language == 1:
            content = f"""尊敬的科研工作者,\n\n您好！任务 {self.job_name} 已完成！祝科研顺利！\n\n得息镜"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = '任务完成'
            message['From'] = self.sender
            message['To'] = self.receiver
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
        else:
            content = f"""Dear scientists,\n\nJob {self.job_name} is finished! Have a happy day!\n\nAutoEMage"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = 'Job complete'
            message['From'] = self.sender
            message['To'] = self.receiver
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)

    def halfFinished(self):
        """发送任务完成邮件 send job complete Email"""
        if self.language == 1:
            content = f"""尊敬的科研工作者,\n\n您好！任务 {self.job_name} 已传输5000张照片！祝科研顺利！\n\n得息镜"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = '任务进度更新'
            message['From'] = self.sender
            message['To'] = self.receiver
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
        else:
            content = f"""Dear scientists,\n\nJob {self.job_name} has transferred 5000 stacks! Have a happy day!\n\nAutoEMage"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = 'Job progress update'
            message['From'] = self.sender
            message['To'] = self.receiver
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
    def motion_fail_Email(self, n):
        """发送异常提示邮件 send reminding Emails for outliers"""
        filepath = f"{self.cal_dir1}Outliers/MotionCorr/*_all.png"
        files = glob.glob(filepath)
        files.sort()
        if self.language == 1:
            content = """尊敬的科研工作者,\n\n您好！您的数据做完漂移修正后出现异常值，请及时检查电镜设置或样品！\n\n得息镜"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = '异常提示'
            message['From'] = self.sender
            message['To'] = self.receiver
            for i in files[-n:]:
                with open (i, 'rb') as imf:
                    picture = MIMEImage(imf.read())
                    picture.add_header('Content-Disposition', f'attachment;filename={i}')
                message.attach(picture)
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
        else:
            content2 = """Dear scientists,\n\nOutliers show up in your data after motion correction. Please examine EM settings or your samples in time.\n\nAutoEMage"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content2}','plain','utf-8')
            message['Subject'] = 'Outliers warning'
            message['From'] = self.sender
            message['To'] = self.receiver
            for i in files[-n:]:
                with open (f"{self.cal_dir1}Outliers/MotionCorr/*_all.png", 'rb') as imf:
                    picture = MIMEImage(imf.read())
                    picture.add_header('Content-Disposition', f'attachment;filename={i}')
                message.attach(picture)
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)

    def lowScoreEmail(self, n):
        """发送异常提示邮件 send reminding Emails for outliers"""
        filepath = f"{self.cal_dir1}Outliers/CtfFind/*_all.png"
        files = glob.glob(filepath)
        files.sort()
        if self.language == 1:
            content = """尊敬的科研工作者,\n\n您好！您的数据的CTF得分出现异常值，请及时检查电镜设置或样品！\n\n得息镜"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = '异常提示'
            message['From'] = self.sender
            message['To'] = self.receiver
            for i in files[-n:]:
                with open (i, 'rb') as imf:
                    picture = MIMEImage(imf.read())
                    picture.add_header('Content-Disposition', f'attachment;filename={i}')
                message.attach(picture)
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)
        else:
            content = """Dear scientists,\n\nLow-score data shows up after CtfFind. Please examine EM settings or your samples in time.\n\nAutoEMage"""
            message = MIMEMultipart()
            part1 = MIMEText(f'{content}','plain','utf-8')
            message['Subject'] = 'Outliers warning'
            message['From'] = self.sender
            message['To'] = self.receiver
            for i in files[-10:]:
                with open (i, 'rb') as imf:
                    picture = MIMEImage(imf.read())
                    picture.add_header('Content-Disposition', f'attachment;filename={i}')
                message.attach(picture)
            message.attach(part1)
            try:
                smtpObj = smtplib.SMTP()
                smtpObj.connect(self.mail_host,25)
                smtpObj.login(self.mail_user, self.mail_pass)
                smtpObj.sendmail(self.sender, self.receiver, message.as_string())
                smtpObj.quit()
            except smtplib.SMTPException as e:
                print('error', e)

    def setParaPlot(self, n):
        """画图选项 ploting options"""
        self.option = n
        self.paraPlot()

    def paraPlot(self, start=0, end=0):
        """数据散点图 scatter plot"""
        if len(self.data) == 0:
            if self.language == 1:
                QMessageBox.information(self, "提示","照片计算中，请等待", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Calculation in process, please wait", QMessageBox.StandardButton.Ok)
        else:
            colorlist = ['red', 'darkorange', 'gold', 'chartreuse', 'aqua', 'dodgerblue', 'blueviolet','fuchsia']
            #plotnamelist = ['azi_astig', 'astigmatism']
            Data = np.array(self.data)
            if len(self.data) <= 30:
                self.x1 = Data[:,0]
                self.y1 = Data[:, self.option+1]
            elif (len(self.data) > 30) and (start == 0) and (end == 0):
                self.x1 = Data[-30:,0]
                self.y1 = Data[-30:,self.option+1]
            else:
                self.x1 = Data[start:end,0]
                self.y1 = Data[start:end, self.option+1]
            self.l_canvas.axes.cla()
            self.l_canvas.axes.plot_date(self.x1, self.y1, c=colorlist[self.option])
            locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
            formatter = mdates.ConciseDateFormatter(locator)
            self.l_canvas.axes.xaxis.set_major_locator(locator)
            self.l_canvas.axes.xaxis.set_major_formatter(formatter)
            self.l_canvas.fig.subplots_adjust(left=0.12, bottom=0.15, right=0.96, top=0.96)
            self.l_canvas.axes.tick_params(direction='in')
            #plt.rcParams['font.family'] = 'serif'
            #plt.rcParams['font.serif'] = ['Times New Roman']
            self.l_canvas.draw()

    def timeStart(self, value):
        """时间起点设置"""
        self.time_s = value
        self.time_slider2.setRange(self.time_s+1, int(self.image_num))
        self.paraPlot(self.time_s, self.time_e)

    def timeEnd(self, value):
        """时间终点设置"""
        self.time_e = value
        self.time_slider1.setRange(0, self.time_e-1)        
        self.paraPlot(self.time_s, self.time_e)

    def updateRWindow(self, n):
        """四格图 update window on the right side"""
        if len(self.data) >= n:
            self.defocus_value.setText(str(self.data[n-1][1]))
            self.astigmatism_value.setText(str(self.data[n-1][2])) 
        else:
            self.defocus_value.setText("")
            self.astigmatism_value.setText("")
        self.current_n = n
        self.cur_image_value.setText("%04d" % (n))
        image = img.imread(f'{self.cal_dir1}Display/{self.job_name}_%04d_all.png' % (n))
        self.r_canvas.axes.imshow(image)
        self.r_canvas.axes.set_axis_off()
        self.r_canvas.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.r_canvas.draw()

    def chooseImage(self):
        """照片选择"""
        number = self.image_num_sb.value()
        if os.path.exists(f"{self.cal_dir1}Display/{self.job_name}_%04d_all.png" % (number)):
            self.updateRWindow(number)
        else: 
            if self.language == 1:
                QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)

    def shiftImage(self, n):
        """前一张/后一张展示"""
        m = self.current_n + n
        if os.path.exists(f"{self.cal_dir1}Display/{self.job_name}_%04d_all.png" % (m)):
            self.updateRWindow(m)
        else: 
            if self.language == 1:
                QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)

    def updateImage(self):
        """展示最新照片"""
        if self.max_n != 0:
            self.updateRWindow(self.max_n)
        else:
            if self.language == 1:
                QMessageBox.information(self, "提示","照片计算中，请等待", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Calculation in process, please wait", QMessageBox.StandardButton.Ok)
