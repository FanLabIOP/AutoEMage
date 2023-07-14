"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
from PyQt6.QtWidgets import QWidget, QLineEdit, QFormLayout
from PyQt6.QtCore import Qt

class EMWindow(QWidget):
    """对于不同电镜，首次使用需要进行参数调整（未完成）"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300,500)
        self.setWindowTitle("电镜参数设置 - EM Settings")
        self.setUpSettings()
        self.show()

    def setUpSettings(self):
        """参数设置界面"""
        self.camera_name_edit = QLineEdit()
        self.file_name_edit = QLineEdit()
        self.voltage_edit = QLineEdit()
        self.sphe_aber_edit = QLineEdit()
        self.amp_contra_edit = QLineEdit()
        self.thread_num_edit = QLineEdit()
        self.magnification_edit = QLineEdit()
        self.thickness_edit = QLineEdit()
        self.distor_ang = QLineEdit()
        self.major_scale = QLineEdit()
        self.minor_scale = QLineEdit()
        input_form = QFormLayout()
        input_form.setFieldGrowthPolicy(input_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        input_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        input_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        input_form.addRow("相机名称 Camera name", self.camera_name_edit)
        input_form.addRow("文件名称格式 File name format", self.file_name_edit)
        input_form.addRow("加速电压 (kV) Acceleration Voltage", self.voltage_edit)
        input_form.addRow("球面像差 Spherical aberration", self.sphe_aber_edit)
        input_form.addRow("幅度衬度 Amplitude contrast", self.amp_contra_edit)
        input_form.addRow("放大倍数和像素尺寸的关系 Magnification and pixel sizes", self.magnification_edit)
        input_form.addRow("扭曲角度 Distortion angle", self.distor_ang)
        input_form.addRow("Major scale", self.major_scale)
        input_form.addRow("Minor scale", self.minor_scale)
        input_form.addRow("可用 GPU 数量 Number of GPU", self.thread_num_edit)
        input_form.addRow("冰厚计算 Ice thickness", self.thickness_edit)
        self.setLayout(input_form)
