import socket
import time
from TestClient import startSocket
from Server import Server
from readsensor import Sensor
import threading

server = Server()
sensor = Sensor()
serverTH = threading.Thread(target = server.runServer)
sensorTH = threading.Thread(target = sensor.startMeasurment)
serverTH.start()
sensorTH.start()
time.sleep(5)
while True:
    item = str(sensor.getMeasurment())
    server.addItemToSend( item )
    time.sleep(1)
    answer = server.getAnswer()
    if len(answer)> 0:
        print(answer[len(answer)-1])