import cv2
from device import Flir_cam
from utils import frame_transform

flir_cam = Flir_cam
flir_control = Flir_cam.start()

pictNumb=1
while True:
    frame = flir_cam.q.get(True)
    frame = cv2.resize(frame[:,:], (640, 480))
    frame = cv2.flip(frame,1)
    flir_8_bit_frame = frame_transform.raw_to_8bit(frame)

    cv2.imshow("Flir cam",flir_8_bit_frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        flir_cam.stop(*flir_control)
        break
    if key == ord('c'):
        cv2.imwrite(f"pict/data_{pictNumb}.jpg",flir_8_bit_frame)
        pictNumb = pictNumb+1



