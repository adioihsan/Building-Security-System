import os
import cv2
import configparser
import dlib
from imutils import face_utils
import numpy as np
from utils import calc_rois

class Face :
    def __init__(self):
        self.root_path = os.getcwd()
        self.frame = None
        self.__load_config()
        self.face_bboxs = []
        self.landmarks = []
        self.forhead_bboxs = []
        self.landmark_detector = self.__load_landmark_det()
 

    def __load_config(self):
        parser = configparser.ConfigParser()
        parser.read("config.ini")
        config = parser["FaceDetection"]
        self.FACE_DETECTOR = config["detector"]
        self.MAX_FACE = int(config["max_face"])


        if self.FACE_DETECTOR ==  'dlib_hog':
            self.__load_dlib_hog()
        else:
            self.__load_resnet_ssd()
            #do first interference
            print("INFO : Doing first Interference -  Face detection")
            img = cv2.imread("first_face.jpg")
            self.frame = img
            self.__detect_face_resnet_ssd()
            print("INFO : First Interference Done")

    def __load_landmark_det(self):
        landmark_model_path = f"{self.root_path}/detection/models/shape_predictor_68_face_landmarks.dat"
        return dlib.shape_predictor(landmark_model_path)
   
    def __load_dlib_hog(self):
        self.detector = dlib.get_frontal_face_detector()

    def __load_resnet_ssd(self):
        try:
            model_path = f"{self.root_path}/detection/models/caffe/res10_300x300_ssd_iter_140000.caffemodel"
            proto_path = f"{self.root_path}/detection/models/caffe/deploy.prototxt.txt"
            self.net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        except Exception as ex:
            print("ERROR: Cant load resnet model. reason :",ex)
    
    def __detect_face_dlib_hog(self):
        gray_frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
        face_det = self.detector(gray_frame)
        face_boxes = [calc_rois.convert_and_trim_bb(gray_frame, r) for r in face_det]
        return face_boxes

    def __detect_face_resnet_ssd(self):
        blob = cv2.dnn.blobFromImage(
        cv2.resize(self.frame, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0)
        )
        self.net.setInput(blob)
        detections = self.net.forward()
        # overlay
        detections = np.squeeze(detections)

        face_boxes = calc_rois.get_ssd_bbox(self.frame,detections)
        return face_boxes
    

    
    def detect_face(self):
        self.face_bboxs = []
        if self.FACE_DETECTOR == "dlib_hog":
            self.face_bboxs = self.__detect_face_dlib_hog()
        else :
            self.face_bboxs = self.__detect_face_resnet_ssd()
        if len(self.face_bboxs) > self.MAX_FACE:
            self.face_bboxs = self.face_bboxs[0:self.MAX_FACE]

        return self.face_bboxs
    
    def detect_landmark(self):
        self.landmarks = []
        for (x,y,w,h) in self.face_bboxs:
            gray_frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
            face_ROI = dlib.rectangle(x,y,(x+w),(y+h))
            landmark = self.landmark_detector(gray_frame,face_ROI)
            landmark = face_utils.shape_to_np(landmark)
            self.landmarks.append(landmark)

        return self.landmarks

    def detect_forhead(self):
        self.forhead_bboxs = []
        for index,(x,y,w,h) in enumerate(self.face_bboxs):
            forhead_ROI = []
            if len(self.landmarks) == 0 :
                forhead_ROI = calc_rois.forhead_ROI_static(x,y,w,h)
            else:
                xl1,yl1 = self.landmarks[index][20]
                xl2,yl2 = self.landmarks[index][23]
                forhead_ROI = calc_rois.forhead_ROI_dynamic(xl1,yl1,xl2,yl2,h)
            self.forhead_bboxs.append(forhead_ROI)
            
        return self.forhead_bboxs
    
    def update_frame(self,frame):
        self.frame = frame