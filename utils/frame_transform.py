import cv2
import numpy as np
import simplejpeg
import base64
import io

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def _8bit_to_base64(frame,quality=50):
	frame_buffer =  simplejpeg.encode_jpeg(image=frame,quality=quality,colorspace='BGR',fastdct=True)
	frame_64 = base64.encodebytes(frame_buffer).decode("utf-8")
	return frame_64

def _8bit_to_ioBytes(frame,quality=50):
	frame_buffer =  simplejpeg.encode_jpeg(image=frame,quality=quality,colorspace='BGR',fastdct=True)
	frame_bytesIO = io.BytesIO(frame_buffer)
	return frame_bytesIO

def imgfile_to_base64(img_path):
	frame = cv2.imread(img_path,-1)
	frame_64 = _8bit_to_base64(frame)
	return frame_64

def center_rgb_frame(frame):
	scale = 40
	height, width, channels = frame.shape
	#prepare the crop
	centerX,centerY=int(height/2),int(width/2)
	radiusX,radiusY= int(scale*height/100),int(scale*width/100)

	minX,maxX=centerX-radiusX,centerX+radiusX
	minY,maxY=centerY-radiusY,centerY+radiusY

	cropped = frame[minX:maxX, minY:maxY]
	frame = cv2.resize(cropped, (640, 480)) 
	return frame

def blank_image():
	return np.zeros((480, 640, 3), dtype=np.uint8)

