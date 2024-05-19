from websockets.server import serve
import asyncio
from PIL import Image, ImageTk
from tkinter import Tk, Label
from io import BytesIO
from threading import Thread
import time
Clients = []

images = []

SCREENSHOT_INTERVAL = 2 # REFRESH INTERVAL을 따로 두고 SCREENSHOT INTERVAL초만큼 지났을 때만 SCREEN 보내기!
UPDATE_INTERVAL = 0.2
captsize = "1280x720"

async def process(ws):
    Clients.append(ws)
    while True:
        try:
            data = await asyncio.wait_for(ws.recv(), SCREENSHOT_INTERVAL)
        except TimeoutError:
            data = "SENDSCREEN|"
        except Exception as e:
            if not isinstance(e, TimeoutError):
                print("error:", e)
                if ws in Clients:
                    Clients.remove(ws)
                return

        if not isinstance(data, str):
            if data.startswith(b"SCREEN|"):
                img_bytes = data[7:]
                if len(img_bytes) > 20*2**20:
                    await ws.send("ERROR|ImageTooBig")
                    continue
                images.append(BytesIO(img_bytes))
                if len(images) > 1:
                    images.pop(0)
                continue
            await ws.send("ERROR|Unexpected")
            continue
        
        if data == "SENDSCREEN|":
            await ws.send(f"SCREEN|{captsize}")
            continue

        # str
        if data.startswith("PING|"):
            await ws.send("PONG|OK")
            continue
        
async def main():
    async with serve(process, "0.0.0.0", 40002, max_size=32*2**20):
        print("Server started. Listening: 0.0.0.0:40002")
        await asyncio.Future()

thread = Thread(target=asyncio.run, args=(main(),), daemon=True)
thread.start()

root = Tk()
root.geometry(captsize)

img = ImageTk.PhotoImage(Image.new("RGB", list(map(int, captsize.split("x"))), (0, 0, 0)))
panel = Label(root, image=img)
panel.pack(side="bottom", fill="both", expand="no")

def openNresize(img: BytesIO, size: tuple):
    I = Image.open(img)
    if I.size[0] == size[0] and I.size[1] == size[1]:
        return I
    return I.resize(size)

while True:
    if images:
        captsize = root.geometry().split("+")[0]
        scrsize = list(map(int, captsize.split("x")))
        img = ImageTk.PhotoImage(openNresize(images[0], scrsize))
        panel.configure(image=img)
    time.sleep(UPDATE_INTERVAL)
    root.update()