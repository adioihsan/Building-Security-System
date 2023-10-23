import cv2
import os
import sys
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input
import tensorflow as tf
import numpy as np
from multiprocessing import Process
from utils.face_alignment import face_alignment

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
# from verification.models.inception_resnet_v1 import InceptionResNetV1
from verification.models.inception_resnet_v2 import InceptionResNetV2
from database import es_query

class Face(Process):
    def __init__(self,q_faces,face_results):
        self.model = None
        self.q_faces = q_faces
        self.face_results = face_results
        self.running =True

        super(Face, self).__init__()

    def __load_model(self):
        try:
            print("INFO:","Load Face embedded model")
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)

            self.model = InceptionResNetV2(dimension=512)
            root_path = os.getcwd()
            model_path = f"{root_path}/verification/models/facenet512_weights.h5"
            self.model.load_weights(model_path)
            print("INFO:","Face embedded model loaded")

            self.__first_interference()
        except Exception as ex :
            print("ERROR","Cant load Face embedded model. reason:")
            print(ex)

    def __first_interference(self):
        try:
            print("INFO:","Doing first interference for - Face embedded")
            img = image.load_img('first_face.jpg', target_size=(160, 160))
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis=0)
            img = preprocess_input(img)
            self.model.predict(img, verbose=0)[0].tolist()
            print("INFO:","First interference for - Face embedded DONE ")

        except Exception as ex:
            print("ERROR:","Initial Face emededded FAILED. reason:")
            print(ex)
    
    def createEmbedding(self,face):
        try:
            img = cv2.resize(face,(160,160))
            img = np.expand_dims(img, axis=0)
            img = preprocess_input(img)
            # Encode the face to obtain face embeddings
            face_embedding =self.model.predict(img, verbose=0)[0].tolist()
            return face_embedding
        except Exception as ex:
            raise Exception(f"ERROR:Failed to create face embedding,reason{ex}")
        
    def find_face(self,face):
        face_name = "Unknown"
        private_id = "-"
        face_embedding = []
        aligned_face = []
        try:
            aligned_face = face_alignment(face)
            face_embedding = self.createEmbedding(aligned_face)
            res = es_query.match_face_vector(face_embedding,index_name="face_biometric_512")

            score = res["hits"]["hits"][0]["_score"]
            if float(score) >= 0.05:
                face_name = res["hits"]["hits"][0]["_source"]["full_name"]
                private_id = res["hits"]["hits"][0]["_source"]["private_id"]
        except Exception as ex:
            print(f"ERROR:{ex}")
        finally:
            return (face_name,str(private_id),face_embedding,aligned_face)
    
    def stop(self):
        self.running  = False
        self.terminate()
        
    def run(self):
        print("INFO: ","Preparing face verification")
        self.__load_model()
        print("INFO: ","Face verification ready")
        while self.running:
                if not self.q_faces.empty():
                    faces = self.q_faces.get()
                    verification_result = []
                    for face in faces:
                        face_name,private_id,face_embedding,aligned_face = self.find_face(face)
                        verification_result.append([face_name,private_id,face_embedding,aligned_face])
                    self.face_results[0] = verification_result

                          
# if __name__ == "__main__":
#     from multiprocessing import Queue
#     import time
#     q_faces = Queue(2)
#     q_face_results = Queue(2)

#     face_p = Face(q_faces,q_face_results)
#     face_p.start()
#     while True:
#         if not q_faces.full():
#             img = image.load_img('first_face.jpg', target_size=(160, 160))
#             img = image.img_to_array(img)
#             q_faces.put([img])
#             time.sleep(2)



