import socket
import logging
from PIL import Image, ImageTk
from tkinter import Tk, Label
from io import BytesIO
from threading import Thread
import time

logger = logging.getLogger('server')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 42000))
sock.listen(1)
sock.settimeout(10)

options = {
    "SCR_INTERVAL": 2,
    "UPD_INTERVAL": 0.4,
    "CAPTURE_SIZE": (1280, 720)
}

Clients = []

class Client:
    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr

def process(conn: socket.socket, addr):
    Clients.append(Client(conn, addr))
    while True:
        data = conn.recv(20*2**20)
        