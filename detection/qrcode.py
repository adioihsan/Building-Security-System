import cv2

class QrCode():
    def __init__(self):
        self.qcd = cv2.QRCodeDetector()
        self.frame = None

    def detectAndDecode(self):
        if self.frame is not None:
            decoded_info, points, _ = self.qcd.detectAndDecode(self.frame)
            if len(decoded_info) > 0 :
                width = self.frame.shape[1]
                points[:, :, 0] = width - points[:, :, 0]
                return (True,decoded_info,points)
            else:
                return (False,"0",[])
        else:
            return (False,"0",[])
            
    def update_frame(self,frame):
        if frame is not None:
            self.frame = cv2.flip(frame,1)
    