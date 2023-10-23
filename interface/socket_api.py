import os
import sys
import socketio
import eventlet
import signal

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from utils import draw_rois , frame_transform,calc_rois
from storage import ram,file_server
from manager.process_manager import ProcessManager
from database import mysql_query,es_query

pm = ProcessManager()
pm.start()
sio = socketio.Server(cors_allowed_origins="*")  # Enable CORS for all origins
clients = []
fileServer = file_server.FileServer()

@sio.event
def connect(sid, environ):
    clients.append(sid)
    print(f"Connected: {sid}")

@sio.event
def disconnect(sid):
    clients.remove(sid)
    print(f"Disconnected: {sid}")

@sio.event
def req_rgb_video(sid):
    while sid in clients:
        try:
            if pm.rgb_frame is not None:
                draw_rois.draw_face(pm.rgb_frame,pm.face_bboxs,5)
                draw_rois.draw_qrcode(pm.rgb_frame,pm.qr_points)
                frame_rgb_stream =  frame_transform._8bit_to_base64(pm.rgb_frame)
                sio.emit("res_rgb_video",frame_rgb_stream)
                sio.sleep()
        except Exception as ex:
            print("ERROR: ",f"Cant stream rgb video. reason:{ex}")
            break

@sio.event
def req_flir_video(sid):
    while sid in clients:
        try:
            if pm.flir_frame is not None:
                flir_8bit_frame = frame_transform.raw_to_8bit(pm.flir_frame)
                c_face_bboxs = calc_rois.calibrate_bboxs(pm.face_bboxs)
                draw_rois.draw_face(flir_8bit_frame,c_face_bboxs)
                # draw_rois.draw_tempt(frame=pm.flir_frame,face_bboxes=c_face_bboxs,temperature=pm.temperature)
                frame_flir_stream = frame_transform._8bit_to_base64(flir_8bit_frame)
                sio.emit("res_flir_video",frame_flir_stream)
                sio.sleep()
        except Exception as ex:
            print("ERROR: ",f"Cant stream flir video. reason:{ex}")
            break

@sio.event
def req_current_face(sid):
    while sid in clients:
        if len(pm.face_bboxs) > 0:
            face_results =pm.face_results._getvalue()[0]
            face_and_id = [fnc[0:2] for fnc in face_results]
            sio.emit("res_current_face",face_and_id)
            sio.sleep()
        else:
            sio.emit("res_current_face",[[None,None]])
            sio.sleep()

@sio.event
def req_current_tempt(sid):
    while sid in clients:
        sio.emit("res_current_tempt",pm.temperature)
        sio.sleep()

@sio.event
def req_capture_face(sid,data):
    if sid in clients:
        try:
            face_results =pm.face_results._getvalue()[0][0]
            action = data["action"]
            full_name = data["full_name"]
            if len(face_results) == 4 :
                name,private_id,face_emb,face_img = face_results
                if action == "register" and name !=  "Unknown":
                    return {"status":409,"message":f"Already registered as : {name}"}
                elif action == "update" and name != full_name and name != "Unknown":
                     return {"status":409,"message":f"Already registered as : {name}"}
                else:
                    ram.temp_face_embedded[sid] = face_emb
                    face_64 = frame_transform._8bit_to_base64(face_img,quality=95)
                    return {"status":201,"message":"Photo captured","image":face_64}
        except IndexError:
            return {"status":404,"message":"Cant find  a face in the capture !"}


# @sio.event
# def req_captured_face(sid):
#     if sid in clients:
#         try:
#             face_img = ram.temp_face_img[sid]
#             face_64 = frame_transform._8bit_to_base64(face_img,quality=95)
#             return {"status":200,"message":"success","data":{"image":face_64}}
#         except KeyError:
#             print("ERROR:","Captured face requested but dict empty")

# @sio.event
# def req_captured_frame(sid):
#     if sid in clients:
#         try:
#             full_frame = ram.temp_full_frame[sid]
#             frame_64 = frame_transform._8bit_to_base64(full_frame,quality=95)
#             sio.emit("res_captured_frame",frame_64)
#         except KeyError:
#             print("ERROR: ","Captured frame requested but dict empty")

@sio.event
def req_current_qr(sid):
    while sid in clients:
        if pm.qr_decoded is not None:
            sio.emit("res_current_qr",pm.qr_decoded)
        sio.sleep(1)

@sio.event
def req_verify_qr(sid,data):
    if sid in clients:
            private_id = data["private_id"]
            qr_string = data["qr_string"]
            print("private_id :",private_id)
            print("qr_string:", pm.qr_decoded)
            qr_verify_result = pm.verif_qr.verify_qr_string(private_id,qr_string)
            print("result",qr_verify_result)
            return qr_verify_result
       
@sio.event
def req_real_face(sid):
    while sid in clients:
        if len(pm.face_bboxs) > 0:
            sio.emit("res_real_face",pm.is_real_face_results._getvalue())
        else:
            sio.emit("res_real_face",[[None]])
        sio.sleep()


@sio.event
def req_add_user(sid,form):
    if sid in clients:
        private_id = form['private_id']
        first_name = form['first_name']
        last_name = form['last_name']
        phone_number = form["phone_number"]
        full_name = f"{first_name} {last_name}"
        face_embedding = ram.temp_face_embedded[sid]
        es_success,es_message,es_id = es_query.add_face_vector(face_embedding,private_id,full_name)
        sql_success,sql_message,_ = mysql_query.createUser(private_id,first_name,last_name,phone_number,es_id)
        if sql_success and es_success:
            qr_string = pm.verif_qr.create_qr_string(private_id)
            sio.emit("res_add_user",{"status":201,"message":"Registration success","data":qr_string})
        else:
            sio.emit("res_add_user",{"status":409,"message":f"{sql_message} and {es_message}"})
        sio.sleep()

@sio.event
def req_all_users(sid,data):
    if sid in clients:
        print("all user data requested")
        pagination = data["pagination"]
        sql_success,message,data = mysql_query.getAllUsers(pagination)
        if sql_success:
            return{"status":200,"message":message,"data":data}
        else:
            return{"status":404,"message":message,"data":data}

@sio.event
def req_save_entry_log(sid,form):
    if sid in clients:
        user_id = form["privateId"]
        timestamp = form["timestamp"]
        img_name = f'unknown-{timestamp}'
        if user_id is not None:
            img_name = f'{user_id}-{timestamp}'
        img_path = f"FaceSecurity/{img_name}"
        log_img = frame_transform._8bit_to_ioBytes(pm.rgb_frame)
        fileServer.uploadBytes(log_img,img_path)
        sql_success,message,_ = mysql_query.saveEntryLog(form)
        if sql_success:
            return {"status":201,"message":message}
        else:
            return {"status":409,"message":message}

@sio.event
def req_get_entry_log(sid,data):
    pagination = data["pagination"]
    status = data["status"]
    if sid in clients:
        sql_success,message,data = mysql_query.getEntryLog(pagination,status=status)
        if sql_success:
            return{"status":200,"message":message,"data":data}
        else:
            return{"status":404,"message":message,"data":data}
        
@sio.event
def req_img_log(sid,img_name):
    if sid in clients:
        img_path = f"FaceSecurity/{img_name}"
        img_file = fileServer.downloadFile(img_path)
        img_stream = frame_transform.imgfile_to_base64(img_file)
        return img_stream

@sio.event
def req_one_user(sid,data):
    if sid in clients:
        user_id = data["user_id"]
        sql_success,message,data = mysql_query.getOneUser(user_id)
        if sql_success:
            return{"status":200,"message":message,"data":data}
        else:
            return{"status":500,"message":message,"data":data}

@sio.event
def req_update_face_biometric(sid,data):
    if sid in clients:
        es_id = data["es_id"]
        face_embedding =  ram.temp_face_embedded[sid] 
        es_success,es_message,_= es_query.update_face_biometric(es_id,face_embedding)
        if es_success:
            return {"status":201,"message":es_message}
        else:
            return {"status":500,"message":es_message}

@sio.event
def req_update_user_info(sid,form):
    if sid in clients:
        sql_success,sql_message,data = mysql_query.updateUser(form)
        es_success,es_message,_= es_query.update_face_info(form)
        if sql_success and es_success:
            return{"status":200,"message":sql_message,}
        else:
            return{"status":500,"message":f"{sql_message} and {es_message}"}

@sio.event
def req_delete_user(sid,data):
    if sid in clients:
        private_id = data["private_id"]
        sql_success,sql_message,_ = mysql_query.deleteUser(private_id)
        es_success,es_message,_ = es_query.delete_face_vector(private_id)
        
        if sql_success and es_success:
            return{"status":200,"message":sql_message,}
        else:
            return{"status":500,"message":f"{sql_message} and {es_message}"}

@sio.event
def message(sid, data):
    print(f"Received message: {data}")
    sio.emit("response", {"data": "Server received your message"}, room=sid)

    
if __name__ == "__main__":
    # handle CTRL+C stop signal
    def handle_signal(signum, frame):
        print(f"Received signal {signum}. Stopping the server and the services gracefully.")
        pm.stop() 
        global clients
        clients.clear()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print("INF0:","Starting api")
#     static_files = {
#     '/': './interface/web_FE/index.html',
#     '/static':'./interface/web_FE/static'
# }
    # app = socketio.WSGIApp(sio,static_files=static_files)
    app = socketio.WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
    sys.exit()



