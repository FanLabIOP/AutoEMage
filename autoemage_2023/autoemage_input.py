"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/09/06
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtWidgets import QWidget, QRadioButton, QHBoxLayout, QButtonGroup, QLineEdit, QPushButton, QFormLayout, QMessageBox, QFileDialog, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import os
import subprocess

class InputWindow(QWidget):
    """输入窗口 Input window"""
    input_values_signal = pyqtSignal(str, str, str, str, int, str, str, str)
    processes_signal = pyqtSignal(int,int)

    def __init__(self, language):
        super().__init__()
        filepath = os.path.realpath(__file__)
        self.path = os.path.dirname(filepath)
        self.setMinimumSize(320,360)
        self.setWindowTitle("实验设置 - Experiment Settings")
        self.center()
        self.language = language
        self.setUpInputValues()
        self.show()

    def setUpInputValues(self):
        """参数输入界面"""
        if self.language == 1:
            image_label = QLabel("照片")
            image_label.setFont(QFont("Times", 16, weight=700))
            self.mode3_rb = QRadioButton("EPU") 
            self.mode4_rb = QRadioButton("SerialEM") 
            mode_h_box1 = QHBoxLayout()
            mode_h_box1.addWidget(self.mode3_rb)
            mode_h_box1.addWidget(self.mode4_rb)
            self.mode_group1 = QButtonGroup()
            self.mode_group1.addButton(self.mode3_rb)
            self.mode_group1.addButton(self.mode4_rb)
            self.directory_edit1 = QLineEdit()
            self.directory_edit2 = QLineEdit()
            self.directory_edit3 = QLineEdit()
            select_button1 = QPushButton("select", self)
            select_button2 = QPushButton("select", self)
            select_button3 = QPushButton("select", self)
            select_button1.clicked.connect(lambda:self.chooseDirectory(1))
            select_button2.clicked.connect(lambda:self.chooseDirectory(2))
            select_button3.clicked.connect(lambda:self.chooseFile())
            self.job_edit = QLineEdit()
            self.num_edit = QLineEdit()
            parameter_label = QLabel("参数")
            parameter_label.setFont(QFont("Times",16, weight=700))
            load_button = QPushButton("加载配置")
            load_button.setToolTip("载入之前保存的实验配置")
            load_button.clicked.connect(lambda:self.loadProfile())
            save_button = QPushButton("保存配置")
            save_button.setToolTip("保存当前的实验配置")
            save_button.clicked.connect(lambda:self.saveProfile())
            self.mode1_rb = QRadioButton("counting") #counting mode
            self.mode2_rb = QRadioButton("super resolution") #super resolution mode
            mode_h_box = QHBoxLayout()
            mode_h_box.addWidget(self.mode1_rb)
            mode_h_box.addWidget(self.mode2_rb)
            self.mode_group = QButtonGroup()
            self.mode_group.addButton(self.mode1_rb)
            self.mode_group.addButton(self.mode2_rb)
            self.name_edit = QLineEdit()
            self.dose_edit = QLineEdit()
            self.psize_edit = QLineEdit()
            self.av_edit = QLineEdit() #acceleration voltage
            self.sa_edit = QLineEdit() #spherical aberration
            self.ac_edit = QLineEdit() #amplitude contrast
            self.min_d_edit = QLineEdit() #minimum diameter
            self.max_d_edit = QLineEdit() #maximum diameter
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
            directory_h_box3 = QHBoxLayout()
            directory_h_box3.addWidget(self.directory_edit3)
            directory_h_box3.addWidget(select_button3)
            button_box1 = QHBoxLayout()
            button_box1.addWidget(ok_button1)
            button_box1.addWidget(cancel_button1)
            button_box2 = QHBoxLayout()
            button_box2.addWidget(load_button)
            button_box2.addWidget(save_button)
            input_form = QFormLayout()
            input_form.setFieldGrowthPolicy(input_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            input_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            input_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            input_form.addRow(image_label)
            input_form.addRow("收集软件", mode_h_box1)
            input_form.addRow("电镜文件夹", directory_h_box1)
            input_form.addRow("Gain 文件", directory_h_box3)
            input_form.addRow("USB 文件夹", directory_h_box2)
            input_form.addRow("任务名称", self.job_edit)
            input_form.addRow("照片总数", self.num_edit)
            input_form.addRow(parameter_label)
            input_form.addRow(button_box2)
            input_form.addRow("命名规则", self.name_edit)
            input_form.addRow("EM mode", mode_h_box)
            input_form.addRow("总剂量 (e/A2)", self.dose_edit)
            input_form.addRow("像素尺寸 (A)", self.psize_edit)
            input_form.addRow("加速电压", self.av_edit)
            input_form.addRow("球面像差", self.sa_edit)
            input_form.addRow("幅度衬度", self.ac_edit)
            input_form.addRow("颗粒最小直径", self.min_d_edit)
            input_form.addRow("颗粒最大直径", self.max_d_edit)
            input_form.addRow(button_box1)
            self.setLayout(input_form)
        else:
            image_label = QLabel("Images")
            image_label.setFont(QFont("Times",16, weight=700))
            self.mode3_rb = QRadioButton("EPU") 
            self.mode4_rb = QRadioButton("SerialEM") 
            mode_h_box1 = QHBoxLayout()
            mode_h_box1.addWidget(self.mode3_rb)
            mode_h_box1.addWidget(self.mode4_rb)
            self.mode_group1 = QButtonGroup()
            self.mode_group1.addButton(self.mode3_rb)
            self.mode_group1.addButton(self.mode4_rb)
            self.directory_edit1 = QLineEdit()
            self.directory_edit1.setToolTip("For EPU data, choose the directory where 'Images-Disc' folders are stored. For SerialEM data, choose the directory where images are stored.")
            self.directory_edit2 = QLineEdit()
            self.directory_edit3 = QLineEdit()
            select_button1 = QPushButton("select", self)
            select_button1.setToolTip("For EPU data, choose the directory where 'Images-Disc' folders are stored. For SerialEM data, choose the directory where images are stored.")
            select_button2 = QPushButton("select", self)
            select_button3 = QPushButton("select", self)
            select_button1.clicked.connect(lambda:self.chooseDirectory(1))
            select_button2.clicked.connect(lambda:self.chooseDirectory(2))
            select_button3.clicked.connect(lambda:self.chooseFile())
            self.job_edit = QLineEdit()
            self.num_edit = QLineEdit()
            parameter_label = QLabel("Parameters")
            parameter_label.setFont(QFont("Times",16, weight=700))
            load_button = QPushButton("Load Profile")
            load_button.clicked.connect(lambda:self.loadProfile())
            load_button.setToolTip("Load saved profile")
            save_button = QPushButton("Save Profile")
            save_button.setToolTip("Save current profile")
            save_button.clicked.connect(lambda:self.saveProfile())
            self.name_edit = QLineEdit()
            self.mode1_rb = QRadioButton("counting") #counting mode
            self.mode2_rb = QRadioButton("super resolution") #super resolution mode
            mode_h_box = QHBoxLayout()
            mode_h_box.addWidget(self.mode1_rb)
            mode_h_box.addWidget(self.mode2_rb)
            self.mode_group = QButtonGroup()
            self.mode_group.addButton(self.mode1_rb)
            self.mode_group.addButton(self.mode2_rb)
            self.dose_edit = QLineEdit()
            self.psize_edit = QLineEdit()
            self.av_edit = QLineEdit() #acceleration voltage
            self.sa_edit = QLineEdit() #spherical aberration
            self.ac_edit = QLineEdit() #spherical aberration
            self.min_d_edit = QLineEdit() #minimum diameter
            self.max_d_edit = QLineEdit() #maximum diameter
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
            directory_h_box3 = QHBoxLayout()
            directory_h_box3.addWidget(self.directory_edit3)
            directory_h_box3.addWidget(select_button3)
            button_box1 = QHBoxLayout()
            button_box1.addWidget(ok_button1)
            button_box1.addWidget(cancel_button1)
            button_box2 = QHBoxLayout()
            button_box2.addWidget(load_button)
            button_box2.addWidget(save_button)
            input_form = QFormLayout()
            input_form.setFieldGrowthPolicy(input_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            input_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            input_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            input_form.addRow(image_label)
            input_form.addRow("Software", mode_h_box1)
            input_form.addRow("EM directory", directory_h_box1)
            input_form.addRow("Gain file", directory_h_box3)
            input_form.addRow("USB directory", directory_h_box2)
            input_form.addRow("Job name", self.job_edit)
            input_form.addRow("Number of images", self.num_edit)
            input_form.addRow(parameter_label)
            input_form.addRow(button_box2)
            input_form.addRow("Naming convention", self.name_edit)
            input_form.addRow("EM mode", mode_h_box)
            input_form.addRow("Total dose (e/A2)", self.dose_edit)
            input_form.addRow("Raw pixel size (A)", self.psize_edit)
            input_form.addRow("Accelerating voltage", self.av_edit)
            input_form.addRow("Spherical aberration", self.sa_edit)
            input_form.addRow("Amplitude contrast", self.ac_edit)
            input_form.addRow("Minimum particle diameter", self.min_d_edit)
            input_form.addRow("Maximum particle diameter", self.max_d_edit)
            input_form.addRow(button_box1)
            self.setLayout(input_form)

    def inputValues(self):
        """提取用户输入的参数"""
        '''
        elif os.path.exists(f"{dir1}reference") == False:
            if self.language == 1:
                QMessageBox.warning(self, "提示", """<p>电镜文件夹中不存在reference文件夹!</p>""" , QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", """<p>Reference folder does NOT exist in the EM directory!</p>"""
                                , QMessageBox.StandardButton.Ok)
        '''
        if self.mode_group.checkedButton():
            mode_number = -1*self.mode_group.checkedId()-1
        if self.mode_group1.checkedButton():
            mode_number1 = -1*self.mode_group1.checkedId()-1
        name_convention = self.name_edit.text()
        postfix = name_convention.split('.')[-1]
        dose = self.dose_edit.text()
        psize = self.psize_edit.text()
        ac_voltage = int(self.av_edit.text())
        sp_aberration = self.sa_edit.text()
        am_contrast = self.ac_edit.text()
        min_d = int(self.min_d_edit.text())
        max_d = int(self.max_d_edit.text())
        dir1 = self.directory_edit1.text()
        dir2 = self.directory_edit2.text()
        gain_file = self.directory_edit3.text()
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
        elif gain_file == "":
            if self.language == 1:
                QMessageBox.warning(self, "提示", """<p>请选择 gain 文件！</p>"""
                                , QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", """<p>Please choose a gain file</p>"""
                                , QMessageBox.StandardButton.Ok)
        elif dose == "" or psize == "" or ac_voltage == "" or sp_aberration == "" or am_contrast == "" or min_d == "" or max_d == "" or dir1 == "" or dir2 == "" or name_convention == "":
            if self.language == 1:
                QMessageBox.warning(self, "提示", """<p>请输入所需参数！</p>"""
                                , QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(self, "Warning", """<p>Please input all parameters and directories!</p>"""
                                , QMessageBox.StandardButton.Ok)
        else:
            os.mkdir(f"{dir2}{job}")             
            #用另一个进程执行文件转移
            pid1 = subprocess.Popen(f"Auto_mv.pl -mode {mode_number} -collection_mode {mode_number1} -EM_dir {dir1} -USB_dir {dir2} -job {job} -raw_n 1 -rmi 1 -psize {psize} -total_dose {dose} -acv {ac_voltage} -gain {gain_file} -name {name_convention}  >> {dir3}{job}_auto_mv.txt", shell = True).pid
            #用另一个进程执行CTF计算
            pid2 = subprocess.Popen(f"Auto_ctf.pl -mode {mode_number} -USB_dir {dir2} -job {job} -rmi 1 -psize {psize} -total_dose {dose} -acv {ac_voltage} -SpA {sp_aberration} -ac {am_contrast} -dmin {min_d} -dmax {max_d} >> {dir3}{job}_auto_ctf.txt", shell = True).pid
            self.input_values_signal.emit(job, image_n, dose, psize, ac_voltage, sp_aberration, dir3, postfix)
            self.processes_signal.emit(pid1, pid2)
            self.close()

    def chooseDirectory(self, n):
        """选择文件夹"""
        if self.language == 1:
            if n == 1:
                directory_name = QFileDialog.getExistingDirectory(self,"选择电镜文件夹", "", QFileDialog.Option.ShowDirsOnly)
                self.directory_edit1.setText(f'{directory_name}/')
            elif n == 2:
                directory_name = QFileDialog.getExistingDirectory(self,"选择目标文件夹", "", QFileDialog.Option.ShowDirsOnly)
                self.directory_edit2.setText(f'{directory_name}/')
        else:
            if n == 1:
                directory_name = QFileDialog.getExistingDirectory(self,"Select EM directory", "", QFileDialog.Option.ShowDirsOnly)
                self.directory_edit1.setText(f'{directory_name}/')
            elif n == 2:
                directory_name = QFileDialog.getExistingDirectory(self,"Select USB directory", "", QFileDialog.Option.ShowDirsOnly)
                self.directory_edit2.setText(f'{directory_name}/')

    def chooseFile(self):
        """选择gain文件"""
        if self.language == 1:
            file_name, ok = QFileDialog.getOpenFileName(self, "选择 gain 文件")
            if file_name:
                self.directory_edit3.setText(f"{file_name}")
        else:
            file_name, ok = QFileDialog.getOpenFileName(self,"Select gain file")
            if file_name:
                self.directory_edit3.setText(f"{file_name}")

    def saveProfile(self):
        if self.mode_group.checkedButton():
            mode_number = -1*self.mode_group.checkedId()-1
        name_convention = self.name_edit.text()
        dose = self.dose_edit.text()
        psize = self.psize_edit.text()
        ac_voltage = self.av_edit.text()
        sp_aberration = self.sa_edit.text()
        am_contrast = self.ac_edit.text()
        min_d = self.min_d_edit.text()
        max_d = self.max_d_edit.text()
        file_name, ok = QFileDialog.getSaveFileName(self, "Save Profile", f"{self.path}/files", "Text Files (*.txt)")
        if file_name:
            with open(file_name,'w') as f:
                f.write(str(mode_number) + " " + name_convention + " " + dose + " " + psize + " " + ac_voltage + " " + sp_aberration + " " + am_contrast + " " + min_d + " " + max_d)
        if self.language == 1:
            QMessageBox.information(self, "Information", "配置已保存！", QMessageBox.StandardButton.Ok)    
        else:
            QMessageBox.information(self, "Information", "Profile saved", QMessageBox.StandardButton.Ok)

    def loadProfile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Profile", f"{self.path}/files", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "r") as f:
                for line in f:
                    para_info = line.split(" ")
                    mode_number = para_info[0]
                    name_convention = para_info[1]
                    dose = para_info[2]
                    psize = para_info[3]
                    ac_voltage = para_info[4]
                    sp_aberration = para_info[5]
                    am_contrast = para_info[6]
                    min_d = para_info[7]
                    max_d = para_info[8]
            self.dose_edit.setText(dose)
            self.name_edit.setText(name_convention)
            if int(mode_number) == 1:
                self.mode1_rb.setChecked(True)
            else:
                self.mode2_rb.setChecked(True)
            self.psize_edit.setText(psize)
            self.av_edit.setText(ac_voltage)
            self.sa_edit.setText(sp_aberration)
            self.ac_edit.setText(am_contrast)
            self.min_d_edit.setText(min_d)
            self.max_d_edit.setText(max_d)

    def center(self):
        """将窗口移至屏幕中心"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
