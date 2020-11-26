import socket
import time
from client import startSocket
from Server import Server
import threading

l = threading.Lock()
l.acquire()


server = Server()
clientTH = threading.Thread(target = startSocket, args=(1,))
clientTH.start()
serverTH = threading.Thread(target = server.runServer)
serverTH.start()
print("Server is Running")
#server.createConnection()
#server.addItemToSend("M1")
#server.addItemToSend("stop")
#server.startCommunication()
#server.addItemToSend("M2")
#time.sleep(10)
#print( server.getAnswer() )
#server.addItemToSend("stop")
#plot()
#serverTH.join()
#clientTH.join()
time.sleep(5)
print("Mainconnect")
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
time.sleep(2)
del s, s2
print( "Ende Main\n" )

