"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QFormLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

class NewUserDialog(QDialog):
    """新用户注册窗口"""
    def __init__(self, language):
        super().__init__()
        self.setModal(True)
        self.initializeUI(language)
        filepath = os.path.realpath(__file__)
        self.path = os.path.dirname(filepath) #当前文件的所在文件夹的路径

    def initializeUI(self, language):
        self.setMinimumSize(360,220)
        self.setWindowTitle("账号注册 - Registration")
        self.center() #将窗口移至屏幕中心 move the window to the center of the screen
        self.setUpWindow(language)

    def setUpWindow(self,language):
        """创建窗口"""
        if language == 1:
            signUp_label = QLabel("创建新账号",self)
            signUp_label.setFont(QFont("Times",18))
            self.name_edit = QLineEdit(self)
            self.new_pswd_edit = QLineEdit(self)
            self.new_pswd_edit.setEchoMode(QLineEdit.EchoMode.Password) #输入密码时隐藏
            self.confirm_edit = QLineEdit(self)
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            sign_up_button = QPushButton("确认", self)
            sign_up_button.clicked.connect(lambda:self.confirmSignUp(1))
            signUp_form = QFormLayout()
            signUp_form.setFieldGrowthPolicy(signUp_form.FieldGrowthPolicy.AllNonFixedFieldsGrow) #小部件缩放方式
            signUp_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop) #表格对齐方式
            signUp_form.setLabelAlignment(Qt.AlignmentFlag.AlignHCenter) #小部件对齐方式
            sign_h_box = QHBoxLayout()
            sign_h_box.addStretch() #空格
            sign_h_box.addWidget(signUp_label)
            sign_h_box.addStretch()
            signUp_form.addRow(sign_h_box)
            signUp_form.addRow("账号 (邮箱号)：", self.name_edit)
            signUp_form.addRow("密码：", self.new_pswd_edit)
            signUp_form.addRow("密码确认：", self.confirm_edit)
            signUp_form.addRow(sign_up_button)
            self.setLayout(signUp_form)
        else:
            signUp_label = QLabel("Create New Account",self)
            signUp_label.setFont(QFont("Times",18))
            self.name_edit = QLineEdit(self)
            self.new_pswd_edit = QLineEdit(self)
            self.new_pswd_edit.setEchoMode(QLineEdit.EchoMode.Password) #Hide the password
            self.confirm_edit = QLineEdit(self)
            self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
            sign_up_button = QPushButton("Sign Up", self)
            sign_up_button.clicked.connect(lambda:self.confirmSignUp(2))
            signUp_form = QFormLayout()
            signUp_form.setFieldGrowthPolicy(signUp_form.FieldGrowthPolicy.AllNonFixedFieldsGrow) #how widgets are grown
            signUp_form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop) #how tables are aligned
            signUp_form.setLabelAlignment(Qt.AlignmentFlag.AlignHCenter) #how widgets are aligned
            sign_h_box = QHBoxLayout()
            sign_h_box.addStretch() #spacing
            sign_h_box.addWidget(signUp_label)
            sign_h_box.addStretch()
            signUp_form.addRow(sign_h_box)
            signUp_form.addRow("Username (Email):", self.name_edit)
            signUp_form.addRow("Password:", self.new_pswd_edit)
            signUp_form.addRow("Confirm:", self.confirm_edit)
            signUp_form.addRow(sign_up_button)
            self.setLayout(signUp_form)

    def center(self):
        """将窗口移至屏幕中心"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def confirmSignUp(self, language):
        """确认创建的账号和密码"""
        name_text = self.name_edit.text()
        pswd_text = self.new_pswd_edit.text()
        confirm_text = self.confirm_edit.text()
        if language == 1:
            if name_text == "" or pswd_text == "":
                QMessageBox.warning(self, "错误", "请输入新建账号和密码",
                                    QMessageBox.StandardButton.Close,
                                    QMessageBox.StandardButton.Close)
            elif ("@" in name_text) == False:
                QMessageBox.warning(self, "错误", "请输入正确的邮箱号作为账号",
                                    QMessageBox.StandardButton.Close,
                                    QMessageBox.StandardButton.Close)
            elif pswd_text != confirm_text:
                QMessageBox.warning(self, "错误", "两次输入的密码不一致",
                                    QMessageBox.StandardButton.Close,
                                    QMessageBox.StandardButton.Close)
            else:
                with open(f"{self.path}/files/users.txt",'a+') as f:
                    f.write(name_text + " " + pswd_text)
                QMessageBox.information(self, "提示", "注册成功！", 
                    QMessageBox.StandardButton.Ok)
                self.close()
        else:
            if name_text == "" or pswd_text == "":
                QMessageBox.warning(self, "Error", "Please enter username or password values",
                                    QMessageBox.StandardButton.Close,
                                    QMessageBox.StandardButton.Close)
            elif ("@" in name_text) == False:
                QMessageBox.warning(self, "Error", "Please enter a correct Email address as your username",
                                    QMessageBox.StandardButton.Close,
                                    QMessageBox.StandardButton.Close)
            elif pswd_text != confirm_text:
                QMessageBox.warning(self, "Error", "The passwords you entered do not match",
                                    QMessageBox.StandardButton.Close,
                                    QMessageBox.StandardButton.Close)
            else:
                with open(f"{self.path}/files/users.txt",'a+') as f:
                    f.write(name_text + " " + pswd_text)
                QMessageBox.information(self, "Information", "Sign up successfully!", QMessageBox.StandardButton.Ok)
                self.close()
