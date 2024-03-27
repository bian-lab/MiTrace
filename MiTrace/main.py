# -*- coding: UTF-8 -*-
"""
@Project: MiTrace 
@File: main.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/29 13:50 
@Description:  
"""
import os
import sys
sys.path.append(os.getcwd())
print(os.getcwd())
from PyQt5.QtWidgets import QApplication
from MiTrace.io.load_video import load_gui

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = load_gui()
    myWin.show()
    sys.exit(app.exec_())
