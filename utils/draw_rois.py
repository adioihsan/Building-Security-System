import cv2

def draw_face(frame, face_bboxs, offset=5):
	for (x, y, w, h) in face_bboxs:
		# count offset
		x = x - (w*offset/100)
		y = y - (h*offset/100)
		w = w + (w*offset*2/100)
		h = h + (h*offset*2/100)

		# makesure not width and height
		x = max(int(x),0)
		y = max(int(y),0)
		w= min(int(w), frame.shape[1] - x)
		h = min(int(h),frame.shape[0] - y)
		# draw bbx
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

def draw_landmark(frame,landmarks,calibrate=False):
	for landmark in landmarks:
		for(x,y) in landmark:
			if calibrate:
				x= x+70
				x = x if x > 0  else 0
				x = x if x < 640 else 640
				y= y-60
				y = y if y > 0 else 0
				y = y if y < 480 else 480
				
			cv2.circle(frame,(x,y),2,(0,255,0),-1)

def draw_forhead(frame,forhead_bboxs):
	for forhead in forhead_bboxs:
		x,y,w,h = forhead
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

def draw_all_rois(frame,face_bboxs,landmarks,forhead_bboxs):
	if len(face_bboxs) > 0 :draw_face(frame,face_bboxs)
	if len(landmarks) > 0 : draw_landmark(frame,landmarks)
	if len(forhead_bboxs)> 0 :draw_forhead(frame,forhead_bboxs)


# def draw_tempt(frame,face_bboxes,temperature):
# 	try:
# 		if len(face_bboxes) == len(temperature["face"]):
# 			for index,(x,y,w,h) in enumerate(face_bboxes):
# 					cv2.rectangle(frame, (x, y), (x + w, y-60), (25,25,25), -1)
# 					cv2.putText(frame,"loc : |max|avg",(x+5,y-50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (55,250,55), 1)

# 					max,avg,min = temperature["forhead"][index]
# 					cv2.putText(frame, f"fhd: {max}|{avg}", (x+5,y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (55,250,55), 1)

# 					max,avg,min = temperature["face"][index]
# 					cv2.putText(frame, f"face : {max}|{avg} ", (x+5,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (55,250,55), 1)

def draw_tempt(frame,face_bboxes,temperature):
	try:
		cv2.rectangle(frame, (0, 300), (200,480 ), (25,25,25), -1)
		if len(face_bboxes) == len(temperature["face"]):
			for index,(x,y,w,h) in enumerate(face_bboxes):
					fc_max,fc_avg,fc_min = temperature["face"][index]
					fh_max,fh_avg,fh_min = temperature["forhead"][index]

					cv2.putText(frame,"Face Temperature",(5,310), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)
					cv2.putText(frame,f"Minimum : {fc_min}",(5,330), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)
					cv2.putText(frame,f"Maximum : {fc_max}",(5,350), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)
					cv2.putText(frame,f"Average : {fc_avg}",(5,370), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)

					cv2.putText(frame,"Forhead Temperature",(5,400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)
					cv2.putText(frame,f"Minimum : {fh_min}",(5,420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)
					cv2.putText(frame,f"Maximum : {fh_max}",(5,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)
					cv2.putText(frame,f"Average : {fh_avg}",(5,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (55,250,55), 1)

		
		
				

		

	except Exception as ex:
		print(ex)

def draw_qrcode(frame,points):
	if len(points) > 0:
		for p in points:
			cv2.polylines(frame, [p.astype(int)], True, (232,223,128), 3)