import os
import sys
import cv2

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from utils import draw_rois,calc_rois,frame_transform
from manager.process_manager import ProcessManager

pm = ProcessManager()
pm.start()

try:
    while True:
        if pm.rgb_frame is not None:
            draw_rois.draw_all_rois(pm.rgb_frame,pm.face_bboxs,pm.landmarks,pm.forhead_bboxs)
            cv2.imshow("rgb",pm.rgb_frame)
        else: 
            print("Waiting for RGB frame...")
        if pm.flir_frame is not None:
            flir_8_bit_frame = frame_transform.raw_to_8bit(pm.flir_frame)
            # flir_colored_frame = cv2.applyColorMap(flir_8_bit_frame, cv2.COLORMAP_TURBO)
            draw_rois.draw_all_rois(flir_8_bit_frame,pm.c_face_bboxs,[],pm.c_forhead_bboxs)
            # draw_rois.draw_landmark(flir_8_bit_frame,pm.landmarks,True)
            draw_rois.draw_tempt(flir_8_bit_frame,pm.c_face_bboxs,pm.temperature)
            cv2.imshow("flir",flir_8_bit_frame)
        else:
             print("Waiting for FLIR frame...")

        key = cv2.waitKey(1) & 0xFF
        # Check if the "q" key is pressed
        if key == ord('q'):
            pm.stop()
            break

except KeyboardInterrupt:
    pm.stop()
 

cv2.destroyAllWindows()
sys.exit()
