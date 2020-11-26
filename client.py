# Import socket module
import socket
import random
import threading
import time


def startSocket( seed ):
    # Create a socket object
    s = socket.socket()
    s2 = socket.socket()
    # Define the port on which you want to connect
    print( "Start connecting" )
    port = 4001
    ip = '127.0.0.1'
    # connect to the server on local computer
    s.settimeout(1)
    s.connect((ip, port))
    s2.connect((ip,4002))
    # receive data from the server
    command = b'polygonZug'
    s.sendall(command)
    time.sleep(0.1)
    data = s.recv(1024)
    print( "Server says: " + data.decode("utf-8") )
    time.sleep(0.1)
    command = b'polygonZug(1,0,5)'
    s.sendall(command)
    time.sleep(0.1)
    data = s.recv(1024)
    print( "Server says: " + data.decode("utf-8") )
    del s
    del s2
    s = socket.socket()
    s.settimeout(5)
    s.connect((ip, 4002))
    s.send(b'Hallo')

    print("Ende")
