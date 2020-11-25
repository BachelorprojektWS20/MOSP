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
    s.connect((ip, port))
    s2.connect((ip, 4002))
    # receive data from the server
    data = b''
    send = threading.Thread(target = sendData, args=(s,))
    send.start()
    while data != b'stop':
        time.sleep(2)
        data = s2.recv(1024)
        if not data: break
        print( "Server says: " + data.decode("utf-8") )
        s2.sendall(b'Ok')
    #del s2
    #del s
    print("Client done")
def sendData( s ):
   try:
        t = 0
        while t<5:
            answer = "/polyStart/"
            s.send(answer.encode('utf-8'))
            time.sleep(1)
        answer = "/endComuication/"
        s.send(answer.encode('utf-8'))
   except OSError:
       print("End of Com")