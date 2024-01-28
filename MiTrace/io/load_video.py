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
from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog

from MiTrace.gui.image_dialog import Ui_image_dialog
from MiTrace.gui.main import Ui_MiTrace
from MiTrace.trace.analysis import Analysis
from MiTrace.trace.detection import Detection
from MiTrace.utils.utils import decorate_image


class load_gui(QMainWindow, Ui_MiTrace):
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

        self.video_adjust = None

        self.ResizeVideoBt.clicked.connect(self.resize_video)
        self.detection = Detection
        self.analysis = Analysis

        self.RunBt.clicked.connect(self.run)

        self.saveBt.setDisabled(True)
        self.saveBt.clicked.connect(self.save_results)
        self.first_image = None
        self.addROIBt.clicked.connect(self.add_roi)
        self.roi_lst = []
        self.roi_name_lst = []
        self.roi_lst_slm = QStringListModel()
        self.roi_lst_slm.dataChanged.connect(self.rename_roi)

        self.removeROIBt.clicked.connect(self.remove_roi)

        # Change the threshold of cv2.inRange
        self.threshold = 30
        self.thresholdBt.clicked.connect(self.set_threshold)
        self.image_dialog = image_dialog(threshold=self.threshold)

    def load_video(self):
        """
        Load video from explore, trigger by loadVideoBt
        """

        video_path, _ = QFileDialog.getOpenFileName(self, 'Select a video',
                                                    r'', 'Video File (*.mp4 *.wmv)')
        if video_path != "":
            self.video_path = video_path
        self.VideoPathEditor.setText(self.video_path)

        try:
            self.cv_capture = cv2.VideoCapture(self.video_path)
            self.frame_count = int(self.cv_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.startFrameEditor.setValue(0)
            self.endFrameEditor.setValue(self.frame_count)
            self.startFrameEditor.setMaximum(self.frame_count)
            self.endFrameEditor.setMaximum(self.frame_count)

        except:
            self.VideoPathEditor.setText("")
            return

    def resize_video(self):
        """
        Resize video by cv2.selectroi function, trigger by resizeVideoBt
        Returns
        -------

        """
        if self.video_path == "":
            self.statusLabel.setText('Please select a video file first!')
            self.statusLabel.setStyleSheet("color: red")
            return None

        try:
            success, self.first_image = self.cv_capture.read()
            if success:
                self.ResizeVideoBt.setDisabled(True)
                self.addROIBt.setDisabled(True)
                self.video_adjust = cv2.selectROI(
                    "select the area, press ENTER to confirm and ESC for quit",
                    self.first_image)
                cv2.destroyWindow("select the area, press ENTER to confirm and ESC for quit")
                # Resize the image for roi selection
                self.first_image = self.first_image[
                                   self.video_adjust[1]: self.video_adjust[1] + self.video_adjust[3],
                                   self.video_adjust[0]: self.video_adjust[0] + self.video_adjust[2]]
                self.cv_capture = cv2.VideoCapture(self.video_path)

                # Remove the roi
                self.roi_lst = []
                self.refresh_listview()
                self.update_image()
                self.ResizeVideoBt.setDisabled(False)
                self.addROIBt.setDisabled(False)
        except AttributeError as e:
            print(e)
            self.statusLabel.setText('Please select a video file first!')
            self.statusLabel.setStyleSheet("color: red")

    def update_image(self):
        """
        Update the image in the label field
        Returns
        -------

        """

        image = cv2.cvtColor(self.first_image, cv2.COLOR_BGR2RGB)
        image = decorate_image(image, self.roi_lst, self.roi_name_lst)
        # Show the resized image in the label field
        image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 3,
                       QImage.Format_RGB888)
        image = QPixmap(image)
        self.imageLabel.setMinimumWidth(self.first_image.shape[1])
        self.imageLabel.setMinimumHeight(self.first_image.shape[0])
        self.imageLabel.setPixmap(image)

    def add_roi(self):
        """
        Add a roi, trigger by add roi
        Returns
        -------

        """
        if self.detect_for_add_roi_set_threshold():

            self.ResizeVideoBt.setDisabled(True)
            self.addROIBt.setDisabled(True)
            roi = cv2.selectROI(
                "select the area, press ENTER to confirm and ESC for quit",
                self.first_image)
            cv2.destroyWindow("select the area, press ENTER to confirm and ESC for quit")
            if roi != (0, 0, 0, 0):
                self.roi_lst.append([int(each) for each in roi])
                self.roi_name_lst.append(str(roi))
                self.refresh_listview()
            self.ResizeVideoBt.setDisabled(False)
            self.addROIBt.setDisabled(False)

    def remove_roi(self):
        """
        Remove the roi selected
        Returns
        -------

        """
        selected_roi = [each.row() for each in self.ROIListView.selectedIndexes()]

        if selected_roi:
            self.roi_lst = [each for idx, each in
                            enumerate(self.roi_lst) if idx not in selected_roi]
            self.roi_name_lst = [each for idx, each in
                                 enumerate(self.roi_name_lst) if idx not in selected_roi]
            # for each in selected_roi:
            #     self.roi_lst.pop(each)
            self.refresh_listview()
        else:
            self.statusLabel.setText('You have no roi yet')
            self.statusLabel.setStyleSheet("color: red")

    def rename_roi(self):
        """
        Double click the roi in the roi list, rename the element
        Returns
        -------

        """
        self.roi_name_lst = self.roi_lst_slm.stringList()
        self.refresh_listview()

    def refresh_listview(self):
        """
        Refresh the list view, when resize the video, or add/remove roi, refresh the image at the same time
        Returns
        -------

        """
        self.roi_lst_slm.setStringList(self.roi_name_lst)
        self.ROIListView.setModel(self.roi_lst_slm)
        self.update_image()

    def set_threshold(self):
        """
        Set the threshold of cv2.inRange
        Returns
        -------

        """

        if self.detect_for_add_roi_set_threshold():
            self.image_dialog.show()
            self.image_dialog.show_image(image=self.first_image,
                                         threshold=self.threshold)
            self.image_dialog.exec()
            if self.image_dialog.ok:
                self.threshold = self.image_dialog.threshold

    def detect_for_add_roi_set_threshold(self):
        """
        Detection before add_roi and set_threshold
        Returns
        -------

        """
        if self.VideoPathEditor.text() == "":
            self.statusLabel.setText('Please select a video file first')
            self.statusLabel.setStyleSheet("color: red")
            return False
        if self.first_image is None:
            success, self.first_image = self.cv_capture.read()
            if success:
                self.cv_capture = cv2.VideoCapture(self.video_path)
                return True
        return True

    def run(self):
        """
        Run the detection and analysis, trigger by runBt
        Returns
        -------

        """

        self.setDisabled(True)
        self.StopBt.setEnabled(True)

        self.statusLabel.setText('Running...')
        self.statusLabel.setStyleSheet('color:green')

        # Didn't do the video resize
        if not self.video_adjust:
            self.video_adjust = [0, 0, -1, -1]

        self.start_frame = self.startFrameEditor.value()
        self.end_frame = self.endFrameEditor.value()

        self.detection = Detection(cv_capture=self.cv_capture, video_adjust=self.video_adjust,
                                   roi_lst=self.roi_lst, start_frame=self.start_frame,
                                   end_frame=self.end_frame, threshold=self.threshold,
                                   roi_name_lst=self.roi_name_lst)

        info = self.detection.detect_video()

        self.analysis = Analysis(x_lst=self.detection.x_lst, y_lst=self.detection.y_lst,
                                 roi_lst=self.roi_lst, roi_name_lst=self.roi_name_lst,
                                 video_adjust=self.video_adjust)

        self.statusLabel.setText(info)
        self.statusLabel.setStyleSheet('color:green')
        self.save_results()

        # Finish detection
        # self.VideoPathEditor.setText("")
        self.cv_capture.release()
        cv2.destroyAllWindows()
        self.cv_capture = cv2.VideoCapture(self.video_path)
        self.setDisabled(False)
        self.saveBt.setEnabled(True)

    def save_results(self):
        """
        Save results analyzed
        Returns
        -------

        """

        path_ = QFileDialog.getExistingDirectory(self, "Select a folder to save results", "")
        if path_ == '':
            return

        self.analysis.save_results(folder_path=path_)
        image = decorate_image(self.first_image, self.roi_lst, self.roi_name_lst)
        cv2.imwrite(filename=f'{path_}/img_for_calibration.png', img=image)


class image_dialog(QDialog, Ui_image_dialog):
    def __init__(self, threshold=30):
        """
        plot the threshold image in this dialog

        Parameters
        ----------
        threshold : int
            Threshold for the cv2.inRange

        """
        super().__init__()
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

        self.setupUi(self)
        self.thresholdEditor.valueChanged.connect(self.refresh_image)
        self.image_blur = None
        self.threshold = threshold
        self.ok = False
        self.okBt.clicked.connect(self.ok_press)
        self.cancelBt.clicked.connect(self.cancelEvent)

    def show_image(self, image, threshold):
        """
        Display the image

        Parameters
        ----------
        image : 3-D array
            image to be shown
        threshold : int
            Same with self.threshold
        Returns
        -------

        """
        self.threshold = threshold
        # This sentence put here will raise the
        # error: (-215:Assertion failed) ! _src.empty() in function 'cv::inRange'
        # And I really don't know why
        # self.thresholdEditor.setValue(self.threshold)

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.image_blur = cv2.GaussianBlur(image_gray, (7, 7), 5, 5)
        self.thresholdEditor.setValue(self.threshold)

    def refresh_image(self):
        """
        If the threshold change, refresh the image
        Returns
        -------

        """
        self.threshold = int(self.thresholdEditor.value())
        image = cv2.inRange(self.image_blur, 0, self.threshold)
        self.imageLabel.setMinimumWidth(image.shape[1])
        self.imageLabel.setMinimumHeight(image.shape[0])

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        image = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 3,
                       QImage.Format_RGB888)
        image = QPixmap(image)
        self.imageLabel.setPixmap(image)

    def ok_press(self):
        """
        If ok button was pressed, quit the window
        Returns
        -------

        """
        self.ok = True
        self.hide()

    def cancelEvent(self):
        """
        Click the 'Cancel' button will call this function
        :return:
        """

        self.hide()

    def closeEvent(self, event):
        """
        Rewrite the close function of QDialog, aim to hide but not close the dialog
        :param event: QDialog event
        :return:
        """
        event.ignore()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = load_gui()
    myWin.show()
    sys.exit(app.exec_())
