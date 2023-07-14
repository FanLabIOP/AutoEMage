"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QFormLayout, QLabel, QSpinBox, QGridLayout, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from autoemage_canvas import MplCanvas
from autoemage_threads import Worker4

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.image as img

import os


class ClassifyWindow(QWidget):
    """粒子挑选与分类参数输入"""
    def __init__(self, directory, language, job, num):
        super().__init__()
        self.setMinimumSize(300,180)
        self.setWindowTitle("粒子挑选设置 - Particle Picking Settings")
        self.center()
        self.dir3 = directory
        self.language = language
        self.job = job
        self.num = num
        self.setUpParticlePicking()
        self.show()

    def setUpParticlePicking(self):
        """输入参数界面"""
        if self.language == 1:
            self.min_diameter_edit = QLineEdit()
            self.max_diameter_edit = QLineEdit()        
            ok_button3 = QPushButton("确定")
            ok_button3.clicked.connect(self.setUpClassesWindow)
            cancel_button3 = QPushButton("取消")
            cancel_button3.clicked.connect(self.close)
            button_box3 = QHBoxLayout()
            button_box3.addWidget(ok_button3)
            button_box3.addWidget(cancel_button3)
            particle_form = QFormLayout()
            particle_form.setFieldGrowthPolicy(particle_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            particle_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            particle_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            particle_form.addRow("粒子最小直径 (A)", self.min_diameter_edit)
            particle_form.addRow("粒子最大直径 (A)", self.max_diameter_edit)
            particle_form.addRow(button_box3)
            self.setLayout(particle_form)
        else:
            self.min_diameter_edit = QLineEdit()
            self.max_diameter_edit = QLineEdit()        
            ok_button3 = QPushButton("OK")
            ok_button3.clicked.connect(self.setUpClassesWindow)
            cancel_button3 = QPushButton("Cancel")
            cancel_button3.clicked.connect(self.close)
            button_box3 = QHBoxLayout()
            button_box3.addWidget(ok_button3)
            button_box3.addWidget(cancel_button3)
            particle_form = QFormLayout()
            particle_form.setFieldGrowthPolicy(particle_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            particle_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            particle_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            particle_form.addRow("Smallest particle diameter (A)", self.min_diameter_edit)
            particle_form.addRow("Largest particle diameter (A)", self.max_diameter_edit)
            particle_form.addRow(button_box3)
            self.setLayout(particle_form)

    def setUpClassesWindow(self):
        """读取参数并打开分类窗口"""
        dmin = self.min_diameter_edit.text()
        dmax = self.max_diameter_edit.text()
        self.create_classes_window = ClassesWindow(self.dir3, self.language, self.job, self.num, dmin, dmax)
        self.create_classes_window.show()
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class ClassesWindow(QWidget):
    """分类窗口"""
    def __init__(self, directory, language, job, num, dmin, dmax):
        super().__init__()
        self.setMinimumSize(1100,700)
        self.setWindowTitle("粒子分类 - 2D Classes")
        self.cal_dir2 = directory
        self.language = language
        self.job_name = job
        self.image_num = num
        self.checkFile1(dmin, dmax)
        self.max_N = 0
        self.current_N = 0
        self.setUpDisplay()
        self.show()

    def setUpDisplay(self):
        self.m_canvas = MplCanvas(self, width=8, height=5, dpi=100)
        m_toolbar = NavigationToolbar2QT(self.m_canvas, self)
        if self.language == 1:
            #照片信息展示栏
            current_image1 = QLabel("当前照片：")
            current_image1.setFont(QFont('Times',12))
            self.cur_image_values = QLabel()
            #照片查看按钮栏
            self.image_num_sb1 = QSpinBox()
            self.image_num_sb1.setStatusTip("选择并展示所选照片组的类")
            self.image_num_sb1.setRange(0,12000)
            ok_button3 = QPushButton("确定")
            ok_button3.clicked.connect(self.chooseImages)
            ok_button3.setStatusTip("选择并展示所选照片组的类")
            previous_button1 = QPushButton("前一组")
            previous_button1.setStatusTip("展示前一组照片的类")
            previous_button1.clicked.connect(lambda: self.shiftImages(-10))
            next_button1 = QPushButton("后一组")
            next_button1.clicked.connect(lambda: self.shiftImages(10))
            next_button1.setStatusTip("展示后一组照片的类")
            refresh_button1 = QPushButton("刷新")
            refresh_button1.clicked.connect(self.updateImages)
            refresh_button1.setStatusTip("展示最新照片的类")
            kill_button1 = QPushButton("终止")
            kill_button1.clicked.connect(self.worker4.stopRunning)
        else:
            #Images information display
            current_image1 = QLabel("Current images:")
            current_image1.setFont(QFont('Times',12))
            self.cur_image_values = QLabel()
            #Images display buttons
            self.image_num_sb1 = QSpinBox()
            self.image_num_sb1.setStatusTip("Choose and display selected classes")
            self.image_num_sb1.setRange(0,12000)
            ok_button3 = QPushButton("OK")
            ok_button3.clicked.connect(self.chooseImages)
            ok_button3.setStatusTip("Choose and display selected classes")
            previous_button1 = QPushButton("Previous")
            previous_button1.setStatusTip("Previous 10 images")
            previous_button1.clicked.connect(lambda: self.shiftImages(-10))
            next_button1 = QPushButton("Next")
            next_button1.clicked.connect(lambda: self.shiftImages(10))
            next_button1.setStatusTip("Next 10 images")
            refresh_button1 = QPushButton("Update")
            refresh_button1.clicked.connect(self.updateImages)
            refresh_button1.setStatusTip("Update classes")
            kill_button1 = QPushButton("Kill")
            kill_button1.clicked.connect(self.worker4.stopRunning)
        m_h_box = QHBoxLayout()
        m_h_box.addStretch()
        m_h_box.addWidget(self.image_num_sb1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(ok_button3, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(previous_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(next_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(refresh_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(kill_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addStretch()
        m_grid = QGridLayout()
        m_grid.addWidget(m_toolbar,0,0,1,10)
        m_grid.addWidget(self.m_canvas, 1,0,7,10)
        m_grid.addWidget(current_image1,8,4,1,1)
        m_grid.addWidget(self.cur_image_values,8,5,1,1)
        m_grid.addLayout(m_h_box,9,2,2,6)
        self.setLayout(m_grid)

    def checkFile1(self, dmin, dmax): 
        """运行分类线程"""
        self.worker4 = Worker4(self.cal_dir2, self.job_name, self.image_num, dmin, dmax)
        self.worker4.images_update_signal.connect(self.updateNumber)
        self.worker4.finished.connect(self.worker4.deleteLater)
        self.worker4.start()

    def updateNumber(self, n):
        """更新最新照片组（编号） update the number of images"""
        self.max_N = n
        self.updateMWindow(n)

    def updateMWindow(self, n):
        """四格图 update the window"""
        self.current_N = n
        m = n - 9
        self.cur_image_values.setText("%04d - %04d" % (m, n))
        image = img.imread(f'{self.cal_dir2}Class2D/run{m}to{n}/classes{m}to{n}.png')
        self.m_canvas.axes.imshow(image, cmap='gray')
        self.m_canvas.axes.set_axis_off()
        self.m_canvas.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.m_canvas.draw()

    def chooseImages(self):
        """照片选择"""
        if (self.image_num_sb1.value() % 10) != 0:
            if self.language == 1:
                QMessageBox.information(self, "提示","请输入10的倍数", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Please input multiples of 10", QMessageBox.StandardButton.Ok)
        else:
            n = self.image_num_sb1.value()
            m = n - 9 #每十张做一次二维分类
            if os.path.exists(f"{self.cal_dir2}Class2D/run{m}to{n}/classes{m}to{n}.png"):
                self.updateMWindow(n)
            else: 
                if self.language == 1:
                    QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)
    
    def shiftImages(self, num):
        """前一张/后一张展示"""
        n = self.current_N + num
        m = n - 9
        if os.path.exists(f"{self.cal_dir2}Class2D/run{m}to{n}/classes{m}to{n}.png"):
            self.updateMWindow(n)
        else: 
            if self.language == 1:
                QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)
    
    def updateImages(self):
        """展示最新照片"""
        if self.max_N != 0:
            self.updateMWindow(self.max_N)
        else:
            if self.language == 1:
                QMessageBox.information(self, "提示","照片计算中，请等待", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Calculation in process, please wait", QMessageBox.StandardButton.Ok)


        
