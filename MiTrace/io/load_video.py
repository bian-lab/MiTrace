# -*- coding: UTF-8 -*-
"""
@Project: MiTrace 
@File: load_video.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/26 15:20 
@Description:  
"""
import sys

import cv2
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from MiTrace.gui.main import Ui_MainWindow
from MiTrace.trace.analysis import Analysis
from MiTrace.trace.detection import Detection


class load_gui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(load_gui, self).__init__(parent)
        self.cv_capture = None
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

        self.setupUi(self)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

        self.video_path = ''
        self.VideoPathBt.clicked.connect(self.load_video)
        self.frame_count = 0
        self.start_frame = 0
        self.end_frame = 0

        self.view_adjust = None

        self.ResizeVideoBt.clicked.connect(self.resize_video)
        self.detection = Detection
        self.analysis = Analysis

        self.RunBt.clicked.connect(self.run)

        self.saveBt.setDisabled(True)
        self.saveBt.clicked.connect(self.save_results)

    def load_video(self):
        """
        Load video from explore, trigger by loadVideoBt
        """

        self.video_path, _ = QFileDialog.getOpenFileName(self, 'Select a video',
                                                         r'', 'Video File (*.mp4 *.wmv)')
        self.VideoPathEditor.setText(self.video_path)

        self.cv_capture = cv2.VideoCapture(self.video_path)
        self.frame_count = self.cv_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.startFrameEditor.setValue(0)
        self.endFrameEditor.setValue(self.frame_count)

    def resize_video(self):
        """
        Resize video by cv2.selectroi function, trigger by resizeVideoBt
        Returns
        -------

        """
        success, first_img = self.cv_capture.read()
        if success:
            self.view_adjust = cv2.selectROI("select the area, press ENTER to confirm", first_img)
            self.cv_capture = cv2.VideoCapture(self.video_path)

    def run(self):
        """
        Run the detection and analysis, trigger by runBt
        Returns
        -------

        """

        self.statusLabel.setText('Running...')

        # Didn't do the video resize
        if not self.view_adjust:
            self.view_adjust = [0, 0, -1, -1]

        self.start_frame = self.startFrameEditor.value()
        self.end_frame = self.endFrameEditor.value()

        self.detection = Detection(cv_capture=self.cv_capture, view_adjust=self.view_adjust,
                                   start_frame=self.start_frame, end_frame=self.end_frame)

        self.detection.detect_video()

        self.analysis = Analysis(x_lst=self.detection.x_lst, y_lst=self.detection.y_lst, view_adjust=self.view_adjust)

        self.statusLabel.setText('Done!')
        self.saveBt.setDisabled(False)
        self.save_results()

    def save_results(self):
        """
        Save results analyzed
        Returns
        -------

        """

        path_ = QFileDialog.getExistingDirectory(self, "Select a folder to save 4 stages' data", "")
        if path_ == '':
            return

        self.analysis.save_results(folder_path=path_)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = load_gui()
    myWin.show()
    sys.exit(app.exec_())


