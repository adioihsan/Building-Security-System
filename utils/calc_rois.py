import numpy as np

def convert_and_trim_bb(image, rect):
	# extract the starting and ending (x, y)-coordinates of the
	# bounding box
	startX = rect.left()
	startY = rect.top()
	endX = rect.right()
	endY = rect.bottom()
	# ensure the bounding box coordinates fall within the spatial
	# dimensions of the image
	startX = max(0, startX)
	startY = max(0, startY)
	endX = min(endX, image.shape[1])
	endY = min(endY, image.shape[0])
	# compute the width and height of the bounding box
	w = endX - startX
	h = endY - startY
	# return our bounding box coordinates
	return (startX, startY, w, h)

def get_ssd_bbox(frame,detections):
	h, w = frame.shape[:2]
	scores = detections[:,2]
	boxes = []
	for (_, _, score, x1, y1, x2, y2) in detections[scores > 0.7]:
		box = np.array([x1, y1, x2, y2]) * np.array([w, h, w, h])
		(x1, y1, x2, y2) = box.astype("int") 
		x1 = int(x1)
		y1 = int(y1)
		x2 = int(x2)
		y2 = int(y2)
		boxes.append([x1,y1,x2-x1,y2-y1])
	return boxes

def calibrate_bboxs(bboxs, offset_x=60, offset_y=-40, frame_width=640, frame_height=480,shrink=1):
	c_bboxs = []

	for (x, y, w, h) in bboxs:
		x = (x+offset_x) - (w*shrink/100)
		y = (y+offset_y) - (h*shrink/100)
		w = w - (w*shrink*2/100)
		h = h - (h*shrink*2/100)

		x = max(int(x),0)
		y = max(int(y),0)
		w= min(int(w),frame_width - x)
		h = min(int(h),frame_height - y)
		
		c_bboxs.append((x, y, w, h))

	return c_bboxs

	
def forhead_ROI_static(x,y,w,h):
	ROI_x = round(x + 2*(w/6))
	ROI_y =round(y + 2*(h/9))
	ROI_w = round(2*(w/6))
	ROI_h = round(h/9)
	return [ROI_x,ROI_y,ROI_w,ROI_h]

def forhead_ROI_dynamic(x1,y1,x2,y2,face_height):
	#(x1,y1) is a point above left eyebrow and x2,y2 is a point above right eyebrow
	ROI_h  = int( face_height/10 )
	ROI_x = x1
	ROI_y = y1-ROI_h
	ROI_w = x2-x1
	return [ROI_x,ROI_y,ROI_w,ROI_h]


def cut_face(frame,face_bboxs):
	faces =[]
	for (x, y, w, h) in face_bboxs:
		face = frame[y:y + h, x:x + w]
		faces.append(face)
	return faces


def calc_tempt(val_16b,unit="C"):
	val_k=val_16b/100
	if unit == "C":
		val = (val_k - 273.15 ) 
	elif unit == "F":
		val = ((val_k - 273.15)*9/5 + 32) 
	elif unit == "R":
		val = ((val_k - 273.15)*4/5) 
	else:
		val = val_k
	return round(val,1)
