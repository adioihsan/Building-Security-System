import cv2
import sys
from detection import face_detection,temperature,qrcode
from verification import face_verification, real_face_verification
from device import Rgb_cam,Flir_cam
from threading import Thread , Event
from multiprocessing import Manager,Queue
import configparser
from utils import frame_transform,calc_rois

class ProcessManager:
    def __init__(self,rgb_callback=None,flir_callback=None):
        manager = Manager()
        self.event = Event()

        self.rgb_frame = frame_transform.blank_image()
        self.rgb_cam =  Rgb_cam.Camera()
        self.face_detection = face_detection.Face()

        self.flir_cam = Flir_cam
        self.flir_control = Flir_cam.start()
        self.flir_frame =   None
        # self.flir_8bit_frame = None
        self.flir_callback = flir_callback
        self.temperature = [{'face':[],'forhead':[]}]

        self.face_bboxs = []
        self.c_face_bboxs = []
        self.c_forhead_bboxs = []
        self.forhead_bboxs = []
        self.landmarks = []
        self.rgb_callback = rgb_callback
        self.reset_face_after = 10 #frame

        self.q_faces_flir = Queue(2)
        self.is_real_face_results = manager.list([0])
        self.is_real_face_results[0] = None
        # self.real_face_verification = real_face_verification.Face(self.q_faces_flir,self.is_real_face_results)
        

        self.q_faces = Queue(2)
        self.face_results =manager.list([0])
        self.face_results[0] = [[None,None,[],[]]]
        # self.face_verification = face_verification.Face(self.q_faces,self.face_results)


        self.detect_qr = qrcode.QrCode()
        self.qr_points = []
        self.qr_decoded = None

        self.t_rgb = Thread(target=self.rgb_worker)
        self.t_flir = Thread(target=self.flir_worker)
        self.t_qrCode = Thread(target=self.qr_worker)
        self.t_rgb.daemon = True
        self.t_flir.daemon = True
        self.t_qrCode.daemon = True

        self.__load_config()
    
    def __load_config(self):
        parser = configparser.ConfigParser()
        parser.read("config.ini")
        config_face = parser["FaceDetection"]
        self.SHOW_LANDMARK = config_face.getboolean("landmark")

    def rgb_worker(self):
        try:  
            while not self.event.is_set():
                grab,frame = self.rgb_cam.get_frame()
                frame = frame_transform.center_rgb_frame(frame)

                self.rgb_frame = frame
                self.face_detection.update_frame(frame)
                
                self.face_bboxs = self.face_detection.detect_face()
      
                if self.SHOW_LANDMARK:
                    self.landmarks = self.face_detection.detect_landmark()
                self.forhead_bboxs = self.face_detection.detect_forhead()

                if not self.q_faces.full():
                    faces =  calc_rois.cut_face(self.rgb_frame.copy(),self.face_bboxs)
                    self.q_faces.put(faces,500)

                self.detect_qr.update_frame(frame.copy())

                if self.rgb_callback is not None:
                    self.rgb_callback(frame,self.face_bboxs,self.landmarks,self.forhead_bboxs)
            print("INFO: rgb worker stopped")

        except Exception as ex:
            print("Error:",f"Face detection services error. cause:{ex}")
    
    def flir_worker(self):
        try:
            while not self.event.is_set():
                 frame = self.flir_cam.q.get(True)
                 frame = cv2.resize(frame[:,:], (640, 480))
                 frame = cv2.flip(frame,1)
                 self.flir_frame = frame
                #  c_forhead_bboxs = calc_rois.calibrate_bboxs(self.forhead_bboxs)
                 self.c_face_bboxs = calc_rois.calibrate_bboxs(self.face_bboxs)
                 self.c_forhead_bboxs = calc_rois.calibrate_bboxs(self.forhead_bboxs)
                 self.temperature =  temperature.calculate_tempt(frame,self.c_face_bboxs,self.c_forhead_bboxs)
                 
                 if not self.q_faces_flir.full():
                    flir_8bit_frame = frame_transform.raw_to_8bit(frame)
                    faces = calc_rois.cut_face(flir_8bit_frame,self.c_face_bboxs)
                    self.q_faces_flir.put(faces,500)

                 if self.flir_callback is not None:
                     self.flir_callback(frame,self.temperature)

            print("INFO: flir worker stopped")

        except Exception as ex:
            print("Error:",f"temperature services error. cause:{ex}")
        
    def qr_worker(self):
        while not self.event.is_set():
            try:
                ret,decoded,points= self.detect_qr.detectAndDecode()
                self.qr_points = points
                if(ret):
                    self.qr_decoded = decoded
                else:
                    self.qr_decoded = None
            except Exception as ex:
                print("Error:",f"QR detection services error. cause:{ex}")
        print("INFO: qr worker stopped")
    
    def start(self):
        self.t_rgb.start()
        self.t_flir.start()
        # self.t_qrCode.start()
        # self.face_verification.start()
        # self.real_face_verification.start()


    def stop(self):
        print("INFO:","Stopping all services")
        self.event.set()
        self.rgb_cam.stop()
        self.flir_cam.stop(*self.flir_control)
        self.t_rgb.join()
        self.t_flir.join()
        # self.t_qrCode.join()
        # self.real_face_verification.stop()
        # self.face_verification.stop()
        print("INFO:","All services stopped successfully :)")
        sys.exit()
        