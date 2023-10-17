import os
import sys
import cv2
from vidgear.gears import NetGear
from vidgear.gears import VideoGear
from threading import Thread,Event

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from utils import draw_rois, frame_transform
from manager.process_manager import ProcessManager


pm = ProcessManager()
pm.start()

running = True
def server_rgb(event):
    # activate multiserver_mode
    options = {"flag": 0, "copy": False, "track": False, "multiserver_mode" :True}

    # Define NetGear Server at Client's IP address and assign a unique port address and other parameters
    # !!! change following IP address '192.168.x.xxx' with yours !!!
    server = NetGear(
        address="192.168.1.2",
        port="5577",
        protocol="tcp",
        pattern=2,
        logging=False,
        max_retries=100,
        **options
    )

    # loop over until Keyboard Interrupted
    while True:
        try:
            if pm.rgb_frame is not None:
                target_message = {"face_bboxs":pm.face_bboxs}
                server.send(pm.rgb_frame, message=target_message)
            if event.is_set():
                break
        except Exception as ex:
            print(ex)
            server.close()
            break


def server_flir(event):
    # Define NetGear Server at Client's IP address and assign a unique port address and other parameters
    # !!! change following IP address '192.168.x.xxx' with yours !!!
    options = {"flag": 0, "copy": False, "track": False, "multiserver_mode" :True}
    server = NetGear(
        address="192.168.1.2",
        port="5578",
        protocol="tcp",
        pattern=2,
        logging=False,
        max_retries=100,
        **options
    )

    # loop over until Keyboard Interrupted
    while True:
        try:
            # read frames from stream
            if pm.flir_frame is not None:
                # utils.draw_all_rois(pm.flir_frame,pm.face_bboxs,pm.landmarks,pm.forhead_bboxs,"flir")
                flir_8_bit_frame = frame_transform.raw_to_8bit(pm.flir_frame)
                target_message = {"temperature":pm.temperature}
                server.send(flir_8_bit_frame, message=target_message)
            if event.is_set():
                break
        except Exception as ex:
            print(ex)
            server.close()
 

if __name__ == "__main__":
    event = Event()

    t_api_rgb = Thread(target=server_rgb,args=(event,))
    t_api_flir = Thread(target=server_flir,args=(event,))
    t_api_rgb.daemon = True
    t_api_flir.daemon = True
    t_api_rgb.start()
    t_api_flir.start()

    running = True
    try:
        while running:
            if not running:
                break

    except KeyboardInterrupt:
        event.set()
        running = False
        t_api_rgb.join()
        t_api_flir.join()
        pm.stop()
        sys.exit()


        
