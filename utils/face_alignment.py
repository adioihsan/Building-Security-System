import os
import cv2
from PIL import Image
# from tensorflow.keras.preprocessing import image
import numpy as np
from matplotlib import pyplot as plt
import math

root_path = os.getcwd()
model_path = f"{root_path}/utils/models/haarcascade_eye.xml"
eye_detector = cv2.CascadeClassifier(model_path)

def face_alignment(face):

    img = face.copy()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    eyes = eye_detector.detectMultiScale(img_gray)
    if len(eyes) == 2:
        index = 0
        for (eye_x, eye_y, eye_w, eye_h) in eyes:
            if index == 0:
                eye_1 = (eye_x, eye_y, eye_w, eye_h)
            elif index == 1:
                eye_2 = (eye_x, eye_y, eye_w, eye_h)
                
            index = index + 1 

        if eye_1[0] < eye_2[0]:
            left_eye = eye_1
            right_eye = eye_2
        else:
            left_eye = eye_2
            right_eye = eye_1

        left_eye_center = (int(left_eye[0] + (left_eye[2] / 2)), int(left_eye[1] + (left_eye[3] / 2)))
        left_eye_x = left_eye_center[0]; left_eye_y = left_eye_center[1]
        
        right_eye_center = (int(right_eye[0] + (right_eye[2]/2)), int(right_eye[1] + (right_eye[3]/2)))
        right_eye_x = right_eye_center[0]; right_eye_y = right_eye_center[1]

        if left_eye_y > right_eye_y:
            point_3rd = (right_eye_x, left_eye_y)
            direction = -1 #rotate same direction to clock
        else:
            point_3rd = (left_eye_x, right_eye_y)
            direction = 1 #rotate inverse direction of clock

        def euclidean_distance(a, b):
            x1 = a[0]; y1 = a[1]
            x2 = b[0]; y2 = b[1]
            return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))
        a = euclidean_distance(left_eye_center, point_3rd)
        b = euclidean_distance(right_eye_center, left_eye_center)
        c = euclidean_distance(right_eye_center, point_3rd)

        cos_a = (b*b + c*c - a*a)/(2*b*c)
        angle = np.arccos(cos_a)
        angle = (angle * 180) / math.pi

        if direction == -1:
            angle = 90 - angle

        normal_image = Image.fromarray(face)
        rotated_image = np.array(normal_image.rotate(direction * angle))
        return rotated_image
    else:
        return face

if __name__ == "__main__":
    face = cv2.imread("mba_taylor.jpg")
    aligned_face = face_alignment(face)

    while True:
        cv2.imshow("face ",aligned_face)
        cv2.waitKey(1)