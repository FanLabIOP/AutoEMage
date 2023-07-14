#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/06/16
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

import sys
from autoemage_login import LoginWindow
from PyQt6.QtWidgets import QApplication, QLabel, QCheckBox

style_sheet = """
    QLabel{color:black}
    QCheckBox{color:black}
"""
                
if __name__ == '__main__': #若以此文件为主文件执行，则
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet) #界面风格，需要根据系统界面颜色作出调整
    window0 = LoginWindow()
    sys.exit(app.exec())
