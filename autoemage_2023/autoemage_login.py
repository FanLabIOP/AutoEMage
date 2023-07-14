#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""
import os

from PyQt6.QtWidgets import QWidget, QTabWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox, QPushButton, QFormLayout, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from autoemage_main import MainWindow
from autoemage_new_user import NewUserDialog

class LoginWindow(QWidget):
    """登录窗口"""
    def __init__(self):
        super().__init__()
        self.initializeUI()
        filepath = os.path.realpath(__file__)
        self.path = os.path.dirname(filepath)

    def initializeUI(self):
        self.setMinimumSize(360,220)
        self.setWindowTitle("得息镜 - AutoEMage")
        self.center()
        self.setUpWindow()
        self.show()

    def center(self):
        """将窗口移至屏幕中心"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setUpWindow(self):
        self.tab_bar = QTabWidget()
        self.Chinese_tab = QWidget()
        self.English_tab = QWidget()
        self.tab_bar.addTab(self.Chinese_tab, "中文")
        self.tab_bar.addTab(self.English_tab, "English")
        self.chineseTab()
        self.englishTab()
        login_h_box = QHBoxLayout()
        login_h_box.addWidget(self.tab_bar)
        self.setLayout(login_h_box)

    def chineseTab(self):
        """中文页面"""
        login_label = QLabel("用户登录")
        login_label.setFont(QFont("Times",18))
        login_label.setStyleSheet("""color: black""")
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password_cb = QCheckBox("显示密码")
        self.show_password_cb.toggled.connect(self.displayPassword)
        login_button = QPushButton("登录", self)
        login_button.clicked.connect(lambda:self.clickLogin(1))
        sign_up_button = QPushButton("注册", self)
        sign_up_button.clicked.connect(lambda:self.createNewUser(1))
        login_form1 = QFormLayout()
        login_form1.setFieldGrowthPolicy(login_form1.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        login_form1.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        login_form1.setLabelAlignment(Qt.AlignmentFlag.AlignHCenter)
        header_h_box = QHBoxLayout()
        header_h_box.addStretch()
        header_h_box.addWidget(login_label)
        header_h_box.addStretch()
        pw_h_box = QHBoxLayout()
        pw_h_box.addSpacing(110) #添加固定空格
        pw_h_box.addWidget(self.show_password_cb)
        pw_h_box.addStretch()
        login_form1.addRow(header_h_box)
        login_form1.addRow("账号 (邮箱号)：", self.username_edit)
        login_form1.addRow("密码：", self.password_edit)
        login_form1.addRow(pw_h_box)
        login_form1.addRow(login_button)
        login_form1.addRow("没有账号？", sign_up_button)
        self.Chinese_tab.setLayout(login_form1)

    def englishTab(self):
        """英文页面"""
        login_label2 = QLabel("User Login")
        login_label2.setFont(QFont("Times",18))
        self.username_edit2 = QLineEdit()
        self.password_edit2 = QLineEdit()
        self.password_edit2.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password_cb2 = QCheckBox("Show Password")
        self.show_password_cb2.toggled.connect(self.displayPassword)
        login_button2 = QPushButton("Login", self)
        login_button2.clicked.connect(lambda:self.clickLogin(2))
        sign_up_button2 = QPushButton("Sign Up", self)
        sign_up_button2.clicked.connect(lambda:self.createNewUser(2))
        login_form2 = QFormLayout()
        login_form2.setFieldGrowthPolicy(login_form2.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        login_form2.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        login_form2.setLabelAlignment(Qt.AlignmentFlag.AlignHCenter)
        header_h_box = QHBoxLayout()
        header_h_box.addStretch()
        header_h_box.addWidget(login_label2)
        header_h_box.addStretch()
        pw_h_box = QHBoxLayout()
        pw_h_box.addSpacing(130) #添加固定空格
        pw_h_box.addWidget(self.show_password_cb2)
        pw_h_box.addStretch()
        login_form2.addRow(header_h_box)
        login_form2.addRow("Username (Email):", self.username_edit2)
        login_form2.addRow("Password:", self.password_edit2)
        login_form2.addRow(pw_h_box)
        login_form2.addRow(login_button2)
        login_form2.addRow("Not a member?", sign_up_button2)
        self.English_tab.setLayout(login_form2)

    def clickLogin(self, language):
        """确认登录"""
        users = {}
        file = f"{self.path}/files/users.txt"
        self.language = language
        try:
            with open(file, 'r') as f:
                for line in f:
                    user_info = line.split(" ")
                    username_info = user_info[0]
                    password_info = user_info[1].strip("\n")
                    users[username_info] = password_info
            if self.language == 1:
                username = self.username_edit.text()
                password = self.password_edit.text()
                if (username, password) in users.items():
                    user_list = username.split("@")
                    name = user_list[0]
                    if os.path.exists(f"{self.path}/users/{name}/"):
                        QMessageBox.information(self, "欢迎",f"欢迎 {name}！", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "欢迎",f"欢迎 {name}！", QMessageBox.StandardButton.Ok)
                        os.mkdir(f"{self.path}/users/{name}/") #创建新的文件路径
                    self.close()
                    self.openApplicationWindow(username, name)
                else:
                    QMessageBox.warning(self, "错误信息", "账号/密码不正确", QMessageBox.StandardButton.Close, QMessageBox.StandardButton.Close)
            else:
                username = self.username_edit2.text()
                password = self.password_edit2.text()
                if (username, password) in users.items():
                    user_list = username.split("@")
                    name = user_list[0]
                    if os.path.exists(f"{self.path}/users/{name}/"):
                        QMessageBox.information(self, "Welcome",f"Welcome {name}！", QMessageBox.StandardButton.Ok)
                    else:
                        QMessageBox.information(self, "Welcome",f"Welcome {name}！", QMessageBox.StandardButton.Ok)
                        os.mkdir(f"{self.path}/users/{name}/") #create new file path
                    self.close()
                    self.openApplicationWindow(username, name)
                else:
                    QMessageBox.warning(self, "Error Message", "The username/password is incorrect.", QMessageBox.StandardButton.Close, QMessageBox.StandardButton.Close)
        except FileNotFoundError as error:
            QMessageBox.warning(self, "错误 - Error", f"""<p>文件不存在！File does not exist!</p><p>Error: {error}</p>""", QMessageBox.StandardButton.Ok)
    
    def displayPassword(self, checked):
        """显示输入的密码"""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal) #显示密码 display password
        elif checked == False:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def displayPassword2(self, checked):
        if checked:
            self.password_edit2.setEchoMode(QLineEdit.EchoMode.Normal) #显示密码 display password
        elif checked == False:
            self.password_edit2.setEchoMode(QLineEdit.EchoMode.Password)

    def createNewUser(self, language):
        self.create_new_user_window = NewUserDialog(language)
        self.create_new_user_window.show()

    def openApplicationWindow(self, user, name):
        self.main_window = MainWindow(user, name, self.language)
        self.main_window.show()
