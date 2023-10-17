import numpy as np
from queue import Queue

try:
    from libuvc_wrapper import *
except ImportError:
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    from device.libuvc_wrapper import *

BUF_SIZE = 2
q = Queue(BUF_SIZE)


def py_frame_callback(frame, userptr):

    array_pointer = cast(
        frame.contents.data,
        POINTER(c_uint16 * (frame.contents.width * frame.contents.height)),
    )
    data = np.frombuffer(array_pointer.contents, dtype=np.dtype(np.uint16)).reshape(
        frame.contents.height, frame.contents.width
    )  

    if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
        return

    if not q.full():
        q.put(data)


PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)

def setup():
    ctx = POINTER(uvc_context)()
    dev = POINTER(uvc_device)()
    devh = POINTER(uvc_device_handle)()
    ctrl = uvc_stream_ctrl()

    res = libuvc.uvc_init(byref(ctx), 0)
    if res < 0:
        print("ERROR: ","uvc_init error")
        exit(res)

    res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
    if res < 0:
        print("ERROR: ","uvc_find_device error")
        exit(res)

    res = libuvc.uvc_open(dev, byref(devh))
    if res < 0:
        print("ERROR: ",f"uvc_open error {res}")
        exit(res)

    print("INFO : ","Flir camera opened")

    print_device_info(devh)
    print_device_formats(devh)

    frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
    if len(frame_formats) == 0:
        print("ERROR: ","device does not support Y16")
        exit(1)

    libuvc.uvc_get_stream_ctrl_format_size(
        devh,
        byref(ctrl),
        UVC_FRAME_FORMAT_Y16,
        frame_formats[0].wWidth,
        frame_formats[0].wHeight,
        int(1e7 / frame_formats[0].dwDefaultFrameInterval),
    )

    res = libuvc.uvc_start_streaming(
        devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0
    )
    if res < 0:
        print("ERROR: ","uvc_start_streaming failed: {0}".format(res))
        exit(1)

    return ctx, dev, devh, ctrl

def start():
    ctx, dev, devh, ctrl = setup()
    return (ctx,dev,devh)

def stop(ctx,dev,devh):
    print("INFO:"," Stoping Flir camera...")
    try:
        libuvc.uvc_stop_streaming(devh)
        libuvc.uvc_unref_device(dev)
        libuvc.uvc_exit(ctx)
    except Exception as ex :
        print("ERROR:",f" Cant stop flir camera. reason:{ex}")

if __name__ == "__main__":
    from threading import Thread
    import cv2
    Thread(target=start,args=()).start()
    while True:
        data = q.get(True, 500)
        if data is None:
            break
        cv2.imshow("frame flir",data)
        cv2.waitKey(1)
        # print(data)


   

    





