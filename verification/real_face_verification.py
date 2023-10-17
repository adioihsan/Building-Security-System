import cv2
import os
from multiprocessing import Process
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

class Face(Process):
    def __init__(self,q_faces_flir,is_real_face_results):
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.running = True
        self.q_faces_flir = q_faces_flir
        self.is_real_face_results = is_real_face_results

        super(Face, self).__init__()

    def __load_interpreter(self):
        print("INFO:","Load Real face checking interpreter")
        root_path = os.getcwd()
        model_path = f"{root_path}/verification/models/real_face_thermal.tflite"
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        print("INFO:","Real face checking interpreter loaded")
        self.__first_interference()
    
    def __first_interference(self):
        print("INFO:","Doing first interference for - Real face checking")
        img = image.load_img('first_real_face.jpg', target_size=(224, 224))
        img = image.img_to_array(img)
        img = img.astype('uint8')
        img = np.expand_dims(img, axis=0)
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        print("INFO:","First interference for - Real face checking DONE ")

    def do_invoke(self,face):
        is_real = True
        try:
            if face is not None:
                img = cv2.resize(face, (224, 224))
                img = np.expand_dims(img, axis=0)
                self.interpreter.set_tensor(self.input_details[0]['index'], img)
                self.interpreter.invoke()
                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
                result = output_data[0]
                fake,real = result
                is_real = bool(real > fake)
        except Exception as  ex:
            print(f"ERROR: Real Face verification fail. cause: {ex}")
        finally:
            return is_real
    
    def stop(self):
        self.running = False
        self.terminate()

    def run(self):
        print("INFO: ","Preparing Real face checking")
        self.__load_interpreter()
        print("INFO: ","Real face checking ready")
        while self.running:
            if not self.q_faces_flir.empty():
                faces = self.q_faces_flir.get()
                is_real_results = []
                for face in faces:
                    is_real = self.do_invoke(face)
                    is_real_results.append(is_real)
                self.is_real_face_results[0] = is_real_results




