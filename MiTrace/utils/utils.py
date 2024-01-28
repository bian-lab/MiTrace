# -*- coding: UTF-8 -*-
"""
@Project: MiTrace 
@File: utils.py
@IDE: PyCharm 
@Author: Xueqiang Wang
@Date: 2024/1/28 20:14 
@Description: Utils for MiTrace
"""
import cv2


def decorate_image(image, roi_lst, roi_name_lst):
    """
    decorate the image for displaying

    Parameters
    ----------
    image : Array
        image to be decorated
    roi_lst : List
    roi_name_lst : List
    Returns
    -------

    """

    if roi_lst:
        for idx, each in enumerate(roi_lst):
            image = cv2.rectangle(image,
                                  (each[0], each[1]),
                                  (each[0] + each[2], each[1] + each[3]),
                                  color=(255, 255, 255))
            image = cv2.putText(image,
                                roi_name_lst[idx],
                                (each[0], each[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1)

    return image


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
