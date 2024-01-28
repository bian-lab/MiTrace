# -*- coding: UTF-8 -*-
"""
@Project: MiTrace 
@File: detection.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/26 15:22 
@Description:  
"""

import cv2
import time

from MiTrace.utils.utils import frame_producer, detect_frame, drawTrackLine, decorate_image


class Detection:

    def __init__(self, cv_capture, video_adjust=None, roi_lst=None, start_frame=0, end_frame=-1,
                 threshold=30, roi_name_lst=None):
        """
        Detect the object with white-balance threshold frame by frame, analyze the result

        Parameters
        ----------
        cv_capture : cv2.VideoCapture object
            capture object
        video_adjust : List
            [x, y, width, height] for resize the video view
        roi_lst : List
            [x, y, width, height] for roi
        start_frame : int, optional
            Detect video from which frame. Default is 0
        end_frame : int, optional
            End frame of frame detection. Default is -1, for no limit
        threshold : int
            Threshold for cv2.inRange
        roi_name_lst : List
            Name of rois

        """

        if video_adjust is None:
            video_adjust = [1, 1, 10, 10]

        self.cv_capture = cv_capture
        self.start_frame = start_frame
        self.end_frame = end_frame  # -1 for no limit

        # cv capture from the start frame
        self.cv_capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)

        # Adjust (resize) the view of video, [x, y, width, height], can be select manually
        self.video_adjust = video_adjust
        self.roi_lst = roi_lst
        self.roi_name_lst = roi_name_lst

        # Threshold of object
        self.threshold = threshold

        # results position of objects
        self.x_lst = []
        self.y_lst = []

    def detect_video(self):
        """

        Returns
        -------

        """

        # If no x and y were detected, use the most previous one
        temp_x = 0
        temp_y = 0

        frame_counter = self.start_frame

        ret = self.cv_capture.isOpened()
        start_time = time.time()

        while ret:
            if self.end_frame != -1 and frame_counter >= self.end_frame:
                break
            frame_counter += 1

            # ret is a boolean represent whether the read() function is done successfully
            ret, frame = self.cv_capture.read()
            if ret:
                frame, frame_thresh = frame_producer(original_frame=frame, resize=self.video_adjust,
                                                     threshold=self.threshold)
                cv2.imshow('Threshold', frame_thresh)

                x, y, contour = detect_frame(frame=frame_thresh)

                if x != -1:
                    temp_x = x
                    temp_y = y
                if x == -1:
                    x = temp_x
                    y = temp_y

                self.x_lst.append(x)
                self.y_lst.append(y)

                cv2.circle(frame, (x, y), 3, (255, 255, 255), -1)
                cv2.drawContours(frame, contour, -1, (255, 255, 255), 2)
                drawTrackLine(frame, self.x_lst, self.y_lst, 80)

                frame = decorate_image(frame, self.roi_lst, self.roi_name_lst)

                cv2.imshow('Original video roi', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        # detection finish
        self.cv_capture.release()
        cv2.destroyAllWindows()

        end_time = time.time()

        return f'Done! Analyzed {len(self.x_lst)} frames, used {round(end_time - start_time, 2)} seconds'
