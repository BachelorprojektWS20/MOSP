import time
#import matplotlib.pyplot as plt
import threading
from Motorsteuerung.MockRegelung import MockRegelung
from Kommunikation.Server import Server
from Motorsteuerung import Commands
from Motorsteuerung.MotionControl import MotionControl
from Motorsteuerung.controlThread import controlThread

class MotorControl:

    def __init__(self, VL, VR, HL, HR, modus):
        self.__control = MockRegelung()
        self.__server = Server(self)
        self.__currentValues = (0,0,0)
        self.movementControl = MotionControl(10, 5, 0.1, 500, 0.5)
        self.__enableGetSpeed = False
        self.__enableGetInfo = False
        self.__time = 0.05
        self.__commandToControl = controlThread( VL, VR, HL, HR, modus)
        self.__messages = []

    def start(self):
        #plotThread = threading.Thread(target=self.graph)
        #plotThread.start()
        self.__server.runServer()
        self.__commandToControl.start()
        while True:
            time.sleep(0.1)
            messagesToSend = []
            self.__messages = self.__server.getAnswer()
            self.__currentValues = self.__commandToControl.getCurrentStep()
            for message in self.__messages:
                command = message[1]
                id = message[0]
                if Commands.commandIsChangeSpeed(command):
                    try:
                        steps = self.movementControl.calculateMovementChange(command, self.__commandToControl.getCurrentStep())
                        #TODO:
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
                if Commands.commandIsStop(command):
                    self.__commandToControl.setStop(Commands.convertStop(command))

            if self.__enableGetSpeed and self.__server.isConnected():
                step = self.__commandToControl.getCurrentStep()
                #print(step)
                #if step[0] > 500:
                 #   print("Error:"+ str(step))
                #if step[1] > 360:
                 #   print("Error:"+ str(step))
                #if abs(step[2]) > 0.5:
                 #   print("Error:"+ str(step))
                messagesToSend.append(step)
            if self.__enableGetInfo and self.__server.isConnected():
                messagesToSend.append("Info"+str(self.__control.getInfo()))
            for messageToSend in messagesToSend:
                self.__server.addItemToSend(messageToSend)
            u = self.__commandToControl.getU()
            self.__server.addItemToSend(u)
            #print(u)

    def stop(self):
        self.__messages = []
        self.__commandToControl.stop()



