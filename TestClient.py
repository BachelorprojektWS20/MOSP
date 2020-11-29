# Import socket module
import socket
import random
import threading
import time
from datetime import datetime


def listen():
    s2 = socket.socket()
    ip = '169.254.36.181'
    s2.connect((ip,4002))
    while True:
        print( str(s2.recv(1024) ) + " : " + str(datetime.now() ))
        s2.send(b'Recived')
        time.sleep(0.1)


def startSocket( seed ):
    # Create a socket object
    s = socket.socket()

    # Define the port on which you want to connect
    port = 4001
    ip = '169.254.36.181'
    # connect to the server on local computer
    #s.settimeout(10)
    s.connect((ip, port))
    listenTH = threading.Thread(target=listen)
    listenTH.start()
    # receive data from the server
    command = b'polygonZug'
    command = b'polygonZug(1,0,5)'
    i = 0
    while True:
        time.sleep(0.6)
        s.sendall(command)
        data = s.recv(1024)
        if i == 0:
            command = b'polygonZug(1,0,5)'
            i=1
        else:
            command = b'polygonZug(8,8,8)'
            i=0
    time.sleep(0.1)
    command = b'polygonZug(1,0,5)'
    s.sendall(command)
    time.sleep(0.1)
    data = s.recv(1024)
    time.sleep(10)
    print("Client Done")



