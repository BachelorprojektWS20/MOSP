import socket
import time
from client import startSocket
from Server import Server
import threading


server = Server()
serverTH = threading.Thread(target = server.runServer)
serverTH.start()
clientTH = threading.Thread(target = startSocket, args=(1,))
clientTH.start()
for i in range(5):
    server.addItemToSend("Guten Morgen")
    time.sleep(0.1)
time.sleep(15)
clientTH = threading.Thread(target = startSocket, args=(1,))
clientTH.start()