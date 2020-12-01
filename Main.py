import time
from Server import Server
from MockMotorsteuerung import MockMotorsteuerung
import threading

motorsteuerung = MockMotorsteuerung()
server = Server()
serverTH = threading.Thread(target = server.runServer)
serverTH.start()
while True:
    if motorsteuerung.isReadSensor():
        server.addItemToSend( str( motorsteuerung.getMovement() ) )
    if motorsteuerung.isReadInfo():
        server.addItemToSend( motorsteuerung.getInfo() )
    #if motorsteuerung.getMessages() != None:
        #for mes in motorsteuerung.getMessages():
            #server.addItemToSend( mes )
    answers = server.getAnswer()
    time.sleep(1)
    for answer in answers:
        print(answer)
        motorsteuerung.addCommands(answer)
