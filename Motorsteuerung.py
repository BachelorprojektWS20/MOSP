import time
import numpy
import threading
from MockRegelung import MockRegelung
from Server import Server
import Commands
from BewegungsSteuerung import BewegungsSteuerung
from SteuerungsdatenThread import SteuerungsdatenThread

class Motorsteuerung:

    def __init__(self):
        self.__control = MockRegelung()
        self.__server = Server()
        self.__currentValues = (0,0,0)
        self.movementControl = BewegungsSteuerung(10, 5, 0.1, 500, 0.5)
        self.__enableGetSpeed = False
        self.__enableGetInfo = False
        self.__time = 0.05
        self.__commandToControl = SteuerungsdatenThread()

    def start(self):
        self.__server.runServer()
        self.__commandToControl.start()
        while True:
            #print("Loop")
            time.sleep(0.001)
            # self.currentValue = ....
            messagesToSend = []
            messages = self.__server.getAnswer()
            for message in messages:
                command = message[1]
                id = message[0]
                if Commands.commandIsChangeSpeed(command):
                    try:
                        steps = self.movementControl.berechneBewegungsAenderungsVerlauf(command, self.__commandToControl.getCurrentStep())
                        self.__currentValues = self.__commandToControl.getCurrentStep()
                        # regelung.... <- stepts
                        self.__commandToControl.updateSteps(steps)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                    except RuntimeError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsMode(command):
                    try:
                        self.movementControl.changeMode(command)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsGetSpeed(command):
                    try:
                        self.__enableGetSpeed = Commands.convertGetSpeed(command)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsGetInfo(command):
                    try:
                        self.__enableGetInfo = Commands.convertGetInfo(command)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))

            if self.__enableGetSpeed:
                step = self.__commandToControl.getCurrentStep()
                if step[0] > 500:
                    print("Error:"+ str(step))
                if step[1] > 360:
                    print("Error:"+ str(step))
                if abs(step[2]) > 0.5:
                    print("Error:"+ str(step))
                messagesToSend.append(step)
                #messagesToSend.append(self.__control.getMovement())
            if self.__enableGetInfo:
                #messagesToSend.append("Info")
                messagesToSend.append("Info"+str(self.__control.getInfo()))
            for messageToSend in messagesToSend:
                self.__server.addItemToSend(messageToSend)







