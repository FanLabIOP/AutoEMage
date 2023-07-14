"""
Author: Yuanhao Cheng, Wei Ding
Email: chengyuanhao@iphy.ac.cn; dingwei@iphy.ac.cn
Created time: 2022/06/16
Last Edit: 2023/07/14
Group: SM6, The Institute of Physics, Chinese Academy of Sciences
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class HelpWindow(QWidget):
    """使用指南窗口 open user manual window"""
    def __init__(self, language):
        super().__init__()
        self.language = language
        self.setMinimumSize(800,1000)
        self.setWindowTitle("使用说明 - User Manual")
        filepath = os.path.realpath(__file__)
        self.path = os.path.dirname(filepath)
        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        if self.language == 1:
            self.webView.load(QUrl(f'file://{self.path}/manual.pdf' ))            
        else:
            self.webView.load(QUrl(f'file://{self.path}/manual_english.pdf' ))
        self.webView.show()
        tab_v_box = QVBoxLayout()
        tab_v_box.setContentsMargins(0,0,0,0)
        tab_v_box.addWidget(self.webView)
        self.setLayout(tab_v_box)
        self.show()
