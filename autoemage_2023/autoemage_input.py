"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtWidgets import QWidget, QRadioButton, QHBoxLayout, QButtonGroup, QLineEdit, QPushButton, QFormLayout, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt

import os
import subprocess

class InputWindow(QWidget):
    """输入窗口 Input window"""
    input_values_signal = pyqtSignal(str, str, str, str, str)
    processes_signal = pyqtSignal(int,int)

    def __init__(self, language):
        super().__init__()
        self.setMinimumSize(320,360)
        self.setWindowTitle("实验数据输入 - Input Experimental Values")
        self.center()
        self.language = language
        self.setUpInputValues()
        self.show()

    def setUpInputValues(self):
        """参数输入界面"""
        if self.language == 1:
            mode1_rb = QRadioButton("counting") #电镜的counting模式
            mode2_rb = QRadioButton("super resolution") #电镜的super resolution模式
            mode_h_box = QHBoxLayout()
            mode_h_box.addWidget(mode1_rb)
            mode_h_box.addWidget(mode2_rb)
            self.mode_group = QButtonGroup()
            self.mode_group.addButton(mode1_rb)
            self.mode_group.addButton(mode2_rb)
            self.dose_edit = QLineEdit()
            self.psize_edit = QLineEdit()
            self.directory_edit1 = QLineEdit()
            self.directory_edit2 = QLineEdit()
            select_button1 = QPushButton("选择", self)
            select_button2 = QPushButton("选择", self)
            select_button1.clicked.connect(lambda:self.chooseDirectory(1))
            select_button2.clicked.connect(lambda:self.chooseDirectory(2))
            self.job_edit = QLineEdit()
            self.num_edit = QLineEdit()
            ok_button1 = QPushButton("确定")
            ok_button1.clicked.connect(lambda:self.inputValues())
            cancel_button1 = QPushButton("取消")
            cancel_button1.clicked.connect(self.close)
            directory_h_box1 = QHBoxLayout()
            directory_h_box1.addWidget(self.directory_edit1)
            directory_h_box1.addWidget(select_button1)
            directory_h_box2 = QHBoxLayout()
            directory_h_box2.addWidget(self.directory_edit2)
            directory_h_box2.addWidget(select_button2)
            button_box1 = QHBoxLayout()
            button_box1.addWidget(ok_button1)
            button_box1.addWidget(cancel_button1)
            input_form = QFormLayout()
            input_form.setFieldGrowthPolicy(input_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            input_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            input_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            input_form.addRow("电镜模式", mode_h_box)
            input_form.addRow("剂量 (e/A2)", self.dose_edit)
            input_form.addRow("像素尺寸 (A)", self.psize_edit)
            input_form.addRow("电镜文件夹", directory_h_box1)
            input_form.addRow("目标文件夹", directory_h_box2)
            input_form.addRow("新建文件名称", self.job_edit)
            input_form.addRow("照片张数", self.num_edit)
            input_form.addRow(button_box1)
            self.setLayout(input_form)
        else:
            mode1_rb = QRadioButton("counting") #counting mode
            mode2_rb = QRadioButton("super resolution") #super resolution mode
            mode_h_box = QHBoxLayout()
            mode_h_box.addWidget(mode1_rb)
            mode_h_box.addWidget(mode2_rb)
            self.mode_group = QButtonGroup()
            self.mode_group.addButton(mode1_rb)
            self.mode_group.addButton(mode2_rb)
            self.dose_edit = QLineEdit()
            self.psize_edit = QLineEdit()
            self.directory_edit1 = QLineEdit()
            self.directory_edit2 = QLineEdit()
            select_button1 = QPushButton("select", self)
            select_button2 = QPushButton("select", self)
            select_button1.clicked.connect(lambda:self.chooseDirectory(1))
            select_button2.clicked.connect(lambda:self.chooseDirectory(2))
            self.job_edit = QLineEdit()
            self.num_edit = QLineEdit()
            ok_button1 = QPushButton("OK")
            ok_button1.clicked.connect(lambda:self.inputValues())
            cancel_button1 = QPushButton("Cancel")
            cancel_button1.clicked.connect(self.close)
            directory_h_box1 = QHBoxLayout()
            directory_h_box1.addWidget(self.directory_edit1)
            directory_h_box1.addWidget(select_button1)
            directory_h_box2 = QHBoxLayout()
            directory_h_box2.addWidget(self.directory_edit2)
            directory_h_box2.addWidget(select_button2)
            button_box1 = QHBoxLayout()
            button_box1.addWidget(ok_button1)
            button_box1.addWidget(cancel_button1)
            input_form = QFormLayout()
            input_form.setFieldGrowthPolicy(input_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            input_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            input_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            input_form.addRow("EM mode", mode_h_box)
            input_form.addRow("Total dose (e/A2)", self.dose_edit)
            input_form.addRow("Pixel size (A)", self.psize_edit)
            input_form.addRow("EM directory", directory_h_box1)
            input_form.addRow("USB directory", directory_h_box2)
            input_form.addRow("Job name", self.job_edit)
            input_form.addRow("Number of images", self.num_edit)
            input_form.addRow(button_box1)
            self.setLayout(input_form)

    def inputValues(self):
        """提取用户输入的参数"""
        if self.mode_group.checkedButton():
            mode_number = -1*self.mode_group.checkedId()-1
        dose = self.dose_edit.text()
        psize = self.psize_edit.text()
        dir1 = self.directory_edit1.text()
        dir2 = self.directory_edit2.text()
        job = self.job_edit.text()
        dir3 = f"{dir2}{job}/"
        image_n = self.num_edit.text()
        if image_n == "":
            image_n = 12000
        elif len(job) == 0 or (" " in job) == True:
            if self.language == 1:
                QMessageBox.warning(self, "提示", """<p>新建文件夹名称最好使用字母、数字和下划线_的组合</p>"""
                                , QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", """<p>Job name should consist of characters, numbers or _</p>"""
                                , QMessageBox.StandardButton.Ok)
        
        elif os.path.exists(f"{dir2}{job}") == True:
            if self.language == 1:
                QMessageBox.warning(self, "提示", """<p>目标文件夹中已存在同名文件夹!</p>"""
                                , QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", """<p>Folder exists in the destination directory!</p>"""
                                , QMessageBox.StandardButton.Ok)
        elif os.path.exists(f"{dir1}reference") == False:
            if self.language == 1:
                QMessageBox.warning(self, "提示", """<p>电镜文件夹中不存在reference文件夹!</p>""" , QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", """<p>Reference folder does NOT exist in the EM directory!</p>"""
                                , QMessageBox.StandardButton.Ok)
        else:
            os.mkdir(f"{dir2}{job}")             
            #用另一个进程执行文件转移
            pid1 = subprocess.Popen(f"Auto_mv.pl -mode {mode_number} -EM_dir {dir1} -USB_dir {dir2} -job {job} -raw_n 1 -rmi 1 -psize {psize} -total_dose {dose} >> {dir3}{job}_auto_mv.txt", shell = True).pid
            #用另一个进程执行CTF计算
            pid2 = subprocess.Popen(f"Auto_ctf.pl -mode {mode_number} -USB_dir {dir2} -job {job} -rmi 1 -psize {psize} -total_dose {dose} >> {dir3}{job}_auto_ctf.txt", shell = True).pid
            self.input_values_signal.emit(job, image_n, dose, psize, dir3)
            self.processes_signal.emit(pid1, pid2)
            self.close()

    def chooseDirectory(self, n):
        """选择文件夹"""
        if self.language == 1:
            if n == 1:
                directory_name = QFileDialog.getExistingDirectory(self,"选择电镜文件夹")
                self.directory_edit1.setText(f'{directory_name}/')
            elif n == 2:
                directory_name = QFileDialog.getExistingDirectory(self,"选择目标文件夹")
                self.directory_edit2.setText(f'{directory_name}/')
        else:
            if n == 1:
                directory_name = QFileDialog.getExistingDirectory(self,"Select EM directory")
                self.directory_edit1.setText(f'{directory_name}/')
            elif n == 2:
                directory_name = QFileDialog.getExistingDirectory(self,"Select USB directory")
                self.directory_edit2.setText(f'{directory_name}/')

    def center(self):
        """将窗口移至屏幕中心"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
