# Import socket module
import socket
import random
import threading
import time

def listen():
    s2 = socket.socket()
    ip = '169.254.8.125'
    s2.connect((ip,4002))
    while True:
        print( s2.recv(1024) )
        s2.send(b'Recived')
        time.sleep(0.2)


def startSocket( seed ):
    # Create a socket object
    s = socket.socket()

    # Define the port on which you want to connect
    port = 4001
    ip = '169.254.8.125'
    # connect to the server on local computer
    s.settimeout(1)
    s.connect((ip, port))
    listenTH = threading.Thread(target=listen)
    listenTH.start()
    # receive data from the server
    command = b'polygonZug'
    s.sendall(command)
    time.sleep(0.1)
    data = s.recv(1024)
    time.sleep(0.1)
    command = b'polygonZug(1,0,5)'
    s.sendall(command)
    time.sleep(0.1)
    data = s.recv(1024)
    time.sleep(10)
    print("Client Done")



