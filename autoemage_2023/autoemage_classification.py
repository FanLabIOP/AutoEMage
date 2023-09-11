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
    def __init__(self, directory, language, num_s, num_e):
        super().__init__()
        self.setMinimumSize(1300,800)
        self.setWindowTitle("颗粒分类 - 2D Class averages")
        self.cal_dir2 = directory
        self.language = language
        self.num_s = num_s
        self.num_e = num_e
        self.c_num_s = num_s
        self.c_num_e = num_e
        #self.checkFile1(dmin, dmax)
        self.class_list = [f"{self.num_s} to {self.num_e}"]
        self.setUpDisplay()
        self.updateMWindow(num_s, num_e)
        self.show()

    def setUpDisplay(self):
        self.m_canvas = MplCanvas(self, width=12, height=7, dpi=100)
        m_toolbar = NavigationToolbar2QT(self.m_canvas, self)
        if self.language == 1:
            #照片信息展示栏
            current_image1 = QLabel("当前照片：")
            current_image1.setFont(QFont('Times',12))
            self.cur_image_values = QLabel()
            #照片查看按钮栏
            self.image_num_sb1 = QComboBox()
            self.image_num_sb1.addItem(f"{self.num_s} to {self.num_e}")
            self.image_num_sb1.setFont(QFont('Times',12))
            self.image_num_sb1.setToolTip("选择并展示所选照片组的类")
            self.image_num_sb1.textActivated.connect(self.chooseImages)
            #ok_button3 = QPushButton("确定")
            #ok_button3.clicked.connect(self.chooseImages)
            #ok_button3.setStatusTip("选择并展示所选照片组的类")
            previous_button1 = QPushButton("前一组")
            previous_button1.setFont(QFont('Times',12))
            previous_button1.clicked.connect(lambda: self.shiftImages(-10))
            next_button1 = QPushButton("后一组")
            next_button1.setFont(QFont('Times',12))
            next_button1.clicked.connect(lambda: self.shiftImages(10))
            #next_button1.setStatusTip("展示后一组照片的类")
            refresh_button1 = QPushButton("刷新")
            refresh_button1.setFont(QFont('Times',12))
            refresh_button1.clicked.connect(self.updateImages)
            #refresh_button1.setStatusTip("展示最新照片的类")
            #kill_button1 = QPushButton("终止")
            #kill_button1.clicked.connect(self.worker4.stopRunning)
        else:
            #Images information display
            current_image1 = QLabel("Current images:")
            current_image1.setFont(QFont('Times',12))
            self.cur_image_values = QLabel()
            #Images display buttons
            self.image_num_sb1 = QComboBox()
            #self.image_num_sb1.setStatusTip("Choose and display selected classes")
            self.image_num_sb1.addItem(f"{self.num_s} to {self.num_e}")
            self.image_num_sb1.setFont(QFont('Times',12))
            self.image_num_sb1.setToolTip("Choose and display selected class averages")
            self.image_num_sb1.textActivated.connect(self.chooseImages)
            #ok_button3 = QPushButton("OK")
            #ok_button3.clicked.connect(self.chooseImages)
            #ok_button3.setStatusTip("Choose and display selected classes")
            previous_button1 = QPushButton("Previous")
            previous_button1.setFont(QFont('Times',12))
            previous_button1.setToolTip("Previous set of class averages")
            previous_button1.clicked.connect(lambda: self.shiftImages(-1))
            next_button1 = QPushButton("Next")
            next_button1.setFont(QFont('Times',12))
            next_button1.clicked.connect(lambda: self.shiftImages(1))
            next_button1.setToolTip("Next set of class averages")
            refresh_button1 = QPushButton("Update")
            refresh_button1.setFont(QFont('Times',12))
            refresh_button1.clicked.connect(self.updateImages)
            refresh_button1.setToolTip("Update class averages")
            #kill_button1 = QPushButton("Kill")
            #kill_button1.clicked.connect(self.worker4.stopRunning)
        m_h_box = QHBoxLayout()
        m_h_box.addStretch()
        m_h_box.addWidget(self.image_num_sb1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(previous_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(next_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addWidget(refresh_button1, Qt.AlignmentFlag.AlignLeft)
        #m_h_box.addWidget(kill_button1, Qt.AlignmentFlag.AlignLeft)
        m_h_box.addStretch()
        m_grid = QGridLayout()
        m_grid.addWidget(m_toolbar,0,0,1,12)
        m_grid.addWidget(self.m_canvas, 1,0,7,12)
        m_grid.addWidget(current_image1,8,5,1,1)
        m_grid.addWidget(self.cur_image_values,8,6,1,1)
        m_grid.addLayout(m_h_box,9,2,2,8)
        self.setLayout(m_grid)

#    def checkFile1(self, dmin, dmax): 
 #       """运行分类线程"""
  #      self.worker4 = Worker4(self.cal_dir2, self.job_name, self.image_num, dmin, dmax)
   #     self.worker4.images_update_signal.connect(self.updateNumber)
    #    self.worker4.finished.connect(self.worker4.deleteLater)
     #   self.worker4.start()

    def updateNumber(self, num_s, num_e):
        """更新最新照片组（编号） update the number of images"""
        self.num_s = num_s
        self.num_e = num_e
        self.image_num_sb1.addItem(f"{num_s} to {num_e}")
        self.class_list.append(f"{num_s} to {num_e}")
        self.updateMWindow(num_s, num_e)

    def updateMWindow(self, num_s, num_e):
        """四格图 update the window"""
        self.c_num_s = num_s
        self.c_num_e = num_e
        self.cur_image_values.setText("%04d - %04d" % (int(num_s), int(num_e)))
        m = 0
        while m < 1:
            if os.path.exists(f"{self.cal_dir2}Class2D/run{num_s}to{num_e}/classes{num_s}to{num_e}.png"):
                image = img.imread(f'{self.cal_dir2}Class2D/run{num_s}to{num_e}/classes{num_s}to{num_e}.png')
                self.m_canvas.axes.imshow(image, cmap='gray')
                self.m_canvas.axes.set_axis_off()
                self.m_canvas.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
                self.m_canvas.draw()
                m += 1
            else:
                time.sleep(2)
                print("Waiting for classes plot...")

    def chooseImages(self, text):
        """照片选择"""
        text_elements = text.split(' to ')
#        if (self.image_num_sb1.value() % 10) != 0:
 #           if self.language == 1:
  #              QMessageBox.information(self, "提示","请输入10的倍数", QMessageBox.StandardButton.Ok)
   #         else:
    #            QMessageBox.information(self, "Information","Please input multiples of 10", QMessageBox.StandardButton.Ok)
     #   else:
        self.updateMWindow(text_elements[0], text_elements[1])
    
    def shiftImages(self, n):
        """前一张/后一张展示"""
        text = f"{self.c_num_s} to {self.c_num_e}"
        c_index = self.class_list.index(text)
        if c_index+n > -1 and c_index+n < len(self.class_list):
            text_new = self.class_list[c_index+n]
            text_elements = text_new.split(' to ')
            self.updateMWindow(text_elements[0], text_elements[1])
        else: 
            if self.language == 1:
                QMessageBox.information(self, "提示","照片不存在", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Image does not exist", QMessageBox.StandardButton.Ok)
    
    def updateImages(self):
        """展示最新照片"""
        if self.num_s != 0 and self.num_e != 0:
            self.updateMWindow(self.num_s, self.num_e)
        else:
            if self.language == 1:
                QMessageBox.information(self, "提示","照片计算中，请等待", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, "Information","Calculation in process, please wait", QMessageBox.StandardButton.Ok)


        
