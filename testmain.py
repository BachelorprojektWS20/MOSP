import socket
import time
from client import startSocket
from Server import Server
#from readsensor import Sensor
import threading
#import fcntl
#import struct

#sensor = Sensor()
server = Server()
serverTH = threading.Thread(target = server.runServer)
#sensorTH = threading.Thread(target = sensor.startMeasurment)
serverTH.start()
#sensorTH.start()
time.sleep(5)
while True:
   # item = str(sensor.getMeasurment())
    server.addItemToSend( item )
    time.sleep(3)
    answer = server.getAnswer()
    print(answer[len(answer)-1])
#clientTH = threading.Thread(target = startSocket, args=(1,))
#clientTH.start()
#time.sleep(10)
#time.sleep(15)
#clientTH = threading.Thread(target = startSocket, args=(1,))
#clientTH.start()
