import time
import matplotlib.pyplot as plt
import threading
from Motorsteuerung.MockRegelung import MockRegelung
from Kommunikation.Server import Server
from Motorsteuerung import Commands
from Motorsteuerung.MotionControl import MotionControl
from Motorsteuerung.controlThread import SteuerungsdatenThread

class MotorControl:

    def __init__(self):
        self.__control = MockRegelung()
        self.__server = Server()
        self.__currentValues = (0,0,0)
        self.movementControl = MotionControl(10, 5, 0.1, 500, 0.5)
        self.__enableGetSpeed = False
        self.__enableGetInfo = False
        self.__time = 0.05
        self.__commandToControl = SteuerungsdatenThread()

    def start(self):
        #plotThread = threading.Thread(target=self.graph)
        #plotThread.start()
        self.__server.runServer()
        self.__commandToControl.start()
        while True:
            time.sleep(0.001)
            messagesToSend = []
            messages = self.__server.getAnswer()
            self.__currentValues = self.__commandToControl.getCurrentStep()
            for message in messages:
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

            if self.__enableGetSpeed and self.__server.isConnected():
                step = self.__commandToControl.getCurrentStep()
                if step[0] > 500:
                    print("Error:"+ str(step))
                if step[1] > 360:
                    print("Error:"+ str(step))
                if abs(step[2]) > 0.5:
                    print("Error:"+ str(step))
                messagesToSend.append(step)
            if self.__enableGetInfo and self.__server.isConnected():
                messagesToSend.append("Info"+str(self.__control.getInfo()))
            for messageToSend in messagesToSend:
                self.__server.addItemToSend(messageToSend)



    def graph(self):
        speed = [0]
        dire = [0]
        rot = [0]
        t = 0
        while True:
            curr = self.__currentValues
            speed.append(curr[0])
            dire.append(curr[1])
            rot.append(curr[2])
            t+=1
            time.sleep(0.01)
            if t == 5000:
                plt.figure()
                plt.subplot(311)
                plt.plot(speed, 'k--')
                plt.title("Speed")
                plt.subplot(312)
                plt.plot(dire, 'r--')
                plt.title("Direction")
                plt.subplot(313)
                plt.plot(rot, 'g--')
                plt.show()
                t=0




