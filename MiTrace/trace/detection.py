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


def drawTrackLine(frame, x_lst, y_lst, history):
    """
    Parameters
    ----------
    frame : Array
        Frame will draw a line on it
    x_lst, y_lst : List
        line track positions
    history : int
        Define the history positions length

    Returns
    -------

    """
    try:
        for i in range(1, history):
            if x_lst[-i] != -1 and x_lst[-i - 1] != -1:
                cv2.line(frame, (x_lst[-i], y_lst[-i]), (x_lst[-i - 1], y_lst[-i - 1]), (255, 255, 255), 2)
    except IndexError as e:
        print(e)
        pass


def detect_frame(frame):
    """
    Detect a single frame of the video, do tracking and return the x, y of object

    Parameters
    ----------
    frame : A frame of the whole video

    Returns
    -------
    x : int
        object's x position
    y : int
        object's y position
    largest_contour : Array
        contour of object

    """

    contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    try:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
    except ZeroDivisionError as e:
        print(e)
        x = -1
        y = -1
        largest_contour = []
    except ValueError as e:
        print(e)
        x = -1
        y = -1
        largest_contour = []

    return x, y, largest_contour


def frame_producer(original_frame, resize, threshold):
    """
    Produce a frame for detection from the original frame from video

    Parameters
    ----------
    original_frame : 3-D array
        Frame from video, is a ndarray object
    resize : List
        a list to resize the frame into a property size, same with the video_adjust in Detection
        [x, y, width, height]
    threshold : int
        adjust the cv2.inRange threshold

    Returns
    -------
    frame : Array
        Resized frame by roi
    frame_thresh : 2-D array
        Frame in threshold range
    """

    # Grab from top left
    # Resize the frame of the original frame
    if resize:
        frame = original_frame[
                resize[1]: resize[1] + resize[3],
                resize[0]: resize[0] + resize[2]
                ]
    else:
        frame = original_frame

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_blur = cv2.GaussianBlur(frame_gray, (7, 7), 5, 5)
    frame_thresh = cv2.inRange(frame_blur, 0, threshold)

    return frame, frame_thresh


class Detection:

    def __init__(self, cv_capture, video_adjust=None, roi_lst=None, start_frame=0, end_frame=-1,
                 threshold=30):
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

                cv2.imshow('Original video roi', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        # detection finish
        self.cv_capture.release()
        cv2.destroyAllWindows()

        end_time = time.time()

        return f'Done! Analyzed {len(self.x_lst)} frames, used {round(end_time - start_time, 2)} seconds'
