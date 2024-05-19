import pyautogui
from websockets.sync.client import connect
from io import BytesIO
from threading import Thread
import time

SERVER_IP = input("Server IP: ")
PORT = "40002"

LAST_SENT = -1

_ALERT_THREADS = []

SCR_INTERVAL = 2

RESIZE_IMAGE = True
RESIZE_TO_720p = True


captsize = []
if RESIZE_TO_720p:
    captsize = [1280, 720]

def time_calc(start, end):
    return round((end-start)*1000, 1)

# todo: tkinter로 변경
def show_alert(message):
    thread = Thread(target=pyautogui.alert, args=(message,))
    thread.daemon = True
    thread.start()
    _ALERT_THREADS.append(thread)

def sync_server():
    global LAST_SENT
    
    while True:
        try:
            with connect(f"ws://{SERVER_IP}:{PORT}", max_size=32*2**20) as ws:
                print("[INFO] Reconnected!")
                ws.send("PING|Connected")
                while True:
                    data = ws.recv()
                        
                    if data.startswith("PING|"):
                        if data == "PING|RES":
                            ws.send("PONG|")
                            
                    # str
                    if data.startswith("SCREEN|"):
                        if len(data.replace("SCREEN|", "", 1).split("x")) == 2:
                            captsize.clear()
                            captsize.extend(
                                list(map(int, data.replace("SCREEN|", "", 1).split("x")))
                            )


                    if data.startswith("SCREEN|") or LAST_SENT+SCR_INTERVAL < time.time():
                        bytesio = BytesIO()
                        start_time = time.time()
                        
                        _img = pyautogui.screenshot()
                        med_time = time.time()
                        
                        if RESIZE_IMAGE:
                            if _img.size[0] > captsize[0] or _img.size[1] > captsize[1]:
                                _img = _img.resize(tuple(captsize))
                        med2_time = time.time()
                        _img.save(bytesio, "PNG")
                        med3_time = time.time()
                        bytesio.seek(0)
                        ws.send(b"SCREEN|"+bytesio.read())
                        end_time = time.time()
                        print(f"[INFO] Screenshot Sent (Scr {time_calc(start_time, med_time)}ms / Rez {time_calc(med_time, med2_time)}ms / Save {time_calc(med2_time, med3_time)}ms / Send {time_calc(med2_time, end_time)}ms / Tot {time_calc(start_time, end_time)}ms)")
                        LAST_SENT = time.time()
                        del bytesio, _img
                        continue

                    if data.startswith("PONG|"):
                        continue

                    if data.startswith("MESSAGE|"):
                        data = data.split("|")
                        content = data[1]
                        show_alert(content)
                        continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error", e)


sync_server()