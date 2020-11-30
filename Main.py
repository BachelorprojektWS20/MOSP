import socket
import time
from TestClient import startSocket
from Server import Server
from readsensor import Sensor
from MockMotorsteuerung import MockMotorsteuerung
import threading

motorsteuerung = MockMotorsteuerung()
server = Server()
serverTH = threading.Thread(target = server.runServer)
serverTH.start()
while True:
    if motorsteuerung.readSensor:
        server.addItemToSend( str( motorsteuerung.getMovement() ) )
    if motorsteuerung.readInfo:
        server.itemsToSend( motorsteuerung.getInfo() )
    server.itemsToSend( motorsteuerung.getMessages() )
    answers = server.getAnswer()
    for answer in answers:
        motorsteuerung.addCommands(answer)
