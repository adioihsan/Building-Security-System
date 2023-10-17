import cv2
from queue import Queue
import threading

# Global variable

def gstreamer_pipeline(
    capture_width=1640,
    capture_height=1232,
    display_width=1640,
    display_height=1232,
    framerate=30,
    flip_method=6
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink drop=True"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

# def gstreamer_pipeline(
#     capture_width=1640,
#     capture_height=1232,
#     display_width=1640,
#     display_height=1232,
#     framerate=30,
#     flip_method=6,
#     brightness=-0.1,
#     contrast=1.7,
#     saturation=1.2,
#     hue=0.0, #ranges from -1.0 (minimum) to 1.0 (maximum), with 0.0 representing no change in hue.
# ):
#     return (
#         "nvarguscamerasrc ! "
#         "video/x-raw(memory:NVMM), "
#         "width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
#         "nvvidconv flip-method=%d ! "
#         "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
#         "videobalance "
#         "brightness=%f contrast=%f saturation=%f hue=%f  ! "
#         "videoconvert ! "
#         "video/x-raw, format=(string)BGR ! appsink drop=True"
#         % (
#             capture_width,
#             capture_height,
#             framerate,
#             flip_method,
#             display_width,
#             display_height,
#             brightness,
#             contrast,
#             saturation,
#             hue,
#         )
#     )

class Camera:
    def __init__(self,camera_source=None):
        try:
            if camera_source is None :
                self.cam = cv2.VideoCapture(gstreamer_pipeline(),cv2.CAP_GSTREAMER)
            else :
                self.cam = cv2.VideoCapture(camera_source)
            # read intial frame
        except:
            print("ERROR : ",f"Cant open camera on given source {camera_source}")
    
    def get_frame(self):
        try:
            return self.cam.read()
        except:
            print("ERROR: ","Cant read rgb frame")

    def stop(self):
        print("INFO :","Stoping camera streaming...")
        self.cam.release()
       

if __name__ == "__main__":
    import time
    from multiprocessing import Process
    

    def cam1(): 
        camera = Camera()
        try:
            while True :
                success,frame = camera.get_frame()
                if success:
                    cv2.imshow("test frame 1",frame)
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        camera.stop()
                        cv2.destroyAllWindows()
                        break
        except KeyboardInterrupt:
            camera.stop()

    Process(target=cam1).start()

        