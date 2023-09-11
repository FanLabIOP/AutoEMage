"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/09/06
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QFormLayout, QLabel, QSpinBox, QGridLayout, QMessageBox, QComboBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from autoemage_canvas import MplCanvas
from autoemage_threads import Worker4

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.image as img

import os
import time


class ParticleWindow(QWidget):
    """分类窗口"""
    def __init__(self, directory, language, job, n, pn):
        super().__init__()
        self.setMinimumSize(1000,1000)
        self.setWindowTitle("颗粒挑选 - Particle picking results")
        self.cal_dir = directory
        self.language = language
        self.job = job
        self.pn_list = []
        self.setUpDisplay()
        self.updateNumber(n, pn)
        self.show()

    def setUpDisplay(self):
        self.m_canvas = MplCanvas(self, width=8, height=8, dpi=100)
        m_toolbar = NavigationToolbar2QT(self.m_canvas, self)
        if self.language == 1:
            #照片信息展示栏
            current_image1 = QLabel("当前照片：")
            current_image1.setFont(QFont('Times',12))
            self.cur_image_values = QLabel()
            #照片查看按钮栏
            self.image_num_sb = QSpinBox()
            self.image_num_sb.setFont(QFont('Times',12))
            self.image_num_sb.setRange(0,30000)
            self.image_num_sb.setToolTip("选择并展示所选照片中的颗粒")
            ok_button = QPushButton("确定")
            ok_button.setFont(QFont('Times',12))
            ok_button.clicked.connect(self.chooseImages)
            ok_button.setToolTip("选择并展示所选照片中的颗粒")
            previous_button = QPushButton("前一张")
            previous_button.setFont(QFont('Times',12))
            previous_button.clicked.connect(lambda: self.shiftImage(-1))
            next_button = QPushButton("后一张")
            next_button.setFont(QFont('Times',12))
            next_button.clicked.connect(lambda: self.shiftImage(1))
            refresh_button = QPushButton("刷新")
            refresh_button.setFont(QFont('Times',12))
            refresh_button.clicked.connect(self.updateImage)
            particle_n = QLabel("颗粒数:")
            particle_n.setFont(QFont('Times',12))
            self.particle_n_value = QLabel()
        else:
            #Images information display
            current_image1 = QLabel("Current images:")
            current_image1.setFont(QFont('Times',12))
            self.cur_image_values = QLabel()
            #Image display buttons
            self.image_num_sb = QSpinBox()
            self.image_num_sb.setFont(QFont('Times',12))
            self.image_num_sb.setToolTip("Choose and display a specific image")
            self.image_num_sb.setRange(0,30000)
            ok_button = QPushButton("OK")
            ok_button.setFont(QFont('Times',12))
            ok_button.clicked.connect(self.chooseImage)
            ok_button.setToolTip("Choose and display a specific image")
            previous_button = QPushButton("Previous")
            previous_button.setFont(QFont('Times',12))
            previous_button.clicked.connect(lambda: self.shiftImage(-1))
            next_button = QPushButton("Next")
            next_button.setFont(QFont('Times',12))
            next_button.clicked.connect(lambda: self.shiftImage(1))
            refresh_button = QPushButton("Update")
            refresh_button.setFont(QFont('Times',12))
            refresh_button.clicked.connect(self.updateImage)
            particle_n = QLabel("N particles:")
            particle_n.setFont(QFont('Times',12))
            self.particle_n_value = QLabel()
        m_h_box = QHBoxLayout()
        m_h_box.addStretch()
        m_h_box.addWidget(self.image_num_sb, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(ok_button, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(previous_button, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(next_button, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(refresh_button, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addStretch()
        m_h_box1 = QHBoxLayout()
        m_h_box1.addWidget(current_image1, Qt.AlignmentFlag.AlignLeft)
        m_h_box1.addWidget(self.cur_image_values, Qt.AlignmentFlag.AlignLeft)
        m_h_box1.addWidget(particle_n, Qt.AlignmentFlag.AlignLeft)
        m_h_box1.addWidget(self.particle_n_value, Qt.AlignmentFlag.AlignLeft)
        m_grid = QGridLayout()
        m_grid.addWidget(m_toolbar,0,0,1,8)
        m_grid.addWidget(self.m_canvas, 1,0,8,8)
        m_grid.addLayout(m_h_box1,9,1,1,6)
        m_grid.addLayout(m_h_box,10,0,2,8)

        self.setLayout(m_grid)

    def updateNumber(self, num, pn):
        """更新最新照片组（编号） update the number of images"""
        self.max_n = num
        self.pn_list.append(pn)
        self.updateMWindow(num)

    def updateMWindow(self, n):
        """update the window"""
        self.current_n = n
        self.cur_image_values.setText("%04d" % (n))
        self.particle_n_value.setText(str(self.pn_list[n-1]))
        m = 0
        while m < 1:
            if os.path.exists(f"{self.cal_dir}Display/{self.job}_%04d_particles.png" % (n)):
                image = img.imread(f"{self.cal_dir}Display/{self.job}_%04d_particles.png" % (n))
                self.m_canvas.axes.imshow(image, cmap='gray')
                self.m_canvas.axes.set_axis_off()
                self.m_canvas.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
                self.m_canvas.draw()
                m += 1
            else:
                time.sleep(2)
                print("Waiting for particles plot...")

    def chooseImage(self):
        """照片选择"""
        number = self.image_num_sb.value()
        if os.path.exists(f"{self.cal_dir}Display/{self.job}_%04d_particles.png" % (number)):
            self.updateMWindow(number)
        else: 
            if self.language == 1:
                QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)

    def shiftImage(self, n):
        """前一张/后一张展示"""
        m = self.current_n + n
        if os.path.exists(f"{self.cal_dir}Display/{self.job}_%04d_particles.png" % (m)):
            self.updateMWindow(m)
        else: 
            if self.language == 1:
                QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)

    def updateImage(self):
        """展示最新照片"""
        if self.max_n != 0:
            self.updateMWindow(self.max_n)
        else:
            if self.language == 1:
                QMessageBox.information(self, "提示","照片计算中，请等待", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Calculation in process, please wait", QMessageBox.StandardButton.Ok)

        
