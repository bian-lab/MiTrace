import cv2
import numpy as np

# Read image
image = cv2.imread("for_size_calibration_use.jpg")

# Select ROI
r = cv2.selectROI("select the area", image)

# Crop image
cropped_image = image[int(r[1]):int(r[1] + r[3]),
                int(r[0]):int(r[0] + r[2])]

# Display cropped image
cv2.imshow("Cropped image", cropped_image)
cv2.waitKey(0)

