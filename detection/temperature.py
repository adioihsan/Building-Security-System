import cv2
import numpy as np
from utils import calc_rois

def get_tempt(frame,bbox):
    try:
        x,y,w,h = bbox
        area = frame[y:y+h,x:x+w].copy()
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(area)
        temp_max = calc_rois.calc_tempt(maxVal,unit="C")
        temp_min = calc_rois.calc_tempt(minVal,unit="C")

        ##  Todo ! count average temperature 
        # meanVal = np.mean(area)
        # temp_avg = calc_rois.temp_to_c(meanVal)

        temp_avg = 0
        
    except Exception as ex:
        print("ERROR : Get temperature failed. cause : ",ex)
    finally:
        return [temp_max,temp_avg,temp_min]


def calculate_tempt(frame,face_bboxs,forhead_bboxs):
    face_temps=[]
    forhead_temps =[]
    c_face_bboxs = calc_rois.calibrate_bboxs(face_bboxs)
    c_forhead_bboxs = calc_rois.calibrate_bboxs(forhead_bboxs)
    for bbox in c_face_bboxs:
        tempt = get_tempt(frame,bbox)
        face_temps.append(tempt)
    for bbox in c_forhead_bboxs:
        tempt =  get_tempt(frame,bbox)
        forhead_temps.append(tempt)
    

    return {"face":face_temps,"forhead":forhead_temps}
