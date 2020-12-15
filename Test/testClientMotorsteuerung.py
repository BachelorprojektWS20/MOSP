import random
import re
import threading
import time
from Kommunikation.Client import Client
import matplotlib.pyplot as plt

class Test:
    def __init__(self):
        self.__T = 0
        self.speed = [0]
        self.direction = [0]
        self.rot = [0]
        self.timeSensor = [0]
        self.xSensor = [0]
        self.ySensor = [0]
        self.speedSend = [0]
        self.directionSend = [0]
        self.rotSend = [0]
        self.client = Client('169.254.36.181')
        #self.client = Client('192.168.178.50')
        self.client.setmaxReconnectAttemps(50)

    def graph(self):
        #print("Graph")
        while True:
            messages = self.client.getAndResetReceivedMessages()
            print(messages)
            for message in messages:
                if re.match('\((-?[0-9]+.[0-9]+|[0-9]+),\s(-?[0-9]+.[0-9]+|[0-9]+),\s(-?[0-9]+.[0-9]+|[0-9]+)\)', message) is not None:
                    commandSplit = re.split('\(', message)
                    commandValue = re.split(',', commandSplit[1])
                    for i in range(len(commandValue)):
                        commandValue[i] = commandValue[i].replace(' ', '')
                        commandValue[i] = commandValue[i].replace(')','')
                        commandValue[i] = float(commandValue[i])
                    self.speed.append(commandValue[0])
                    self.direction.append(commandValue[1])
                    self.rot.append(commandValue[2])
                elif re.match('Info\((-?[0-9]+.[0-9]+|[0-9]+),\s(-?[0-9]+.[0-9]+|[0-9]+),\s(-?[0-9]+.[0-9]+|[0-9]+)\)', message) is not None:
                    message.replace('Info', '')
                    commandSplit = re.split('\(', message)
                    commandValue = re.split(',', commandSplit[1])
                    for i in range(len(commandValue)):
                        commandValue[i] = commandValue[i].replace(' ', '')
                        commandValue[i] = commandValue[i].replace(')','')
                        commandValue[i] = float(commandValue[i])
                    self.timeSensor.append(commandValue[0])
                    self.xSensor.append(commandValue[1])
                    self.ySensor.append(commandValue[2])
                else:
                    print(message)
            time.sleep(1)
            plt.figure()
            plt.subplot(611)
            plt.plot(self.speed, 'k--')
            plt.title("Speed")
            plt.subplot(612)
            plt.plot(self.direction, 'r--')
            plt.title("Direction")
            plt.subplot(613)
            plt.plot(self.rot, 'g--')
            plt.title("Rotation")
            plt.subplot(614)
            plt.plot(self.speedSend, 'k--')
            plt.title("Time-Sensor")
            plt.subplot(615)
            plt.plot(self.directionSend, 'r--')
            plt.title("X-Sensor")
            plt.subplot(616)
            plt.plot(self.rotSend, 'g--')
            plt.title("Y-Sensor")
            plt.show()

    def run(self):

        plotThread = threading.Thread(target=self.graph)
        plotThread.start()
        clientTH = threading.Thread(target=self.client.runClient)
        clientTH.start()
        time.sleep(0.1)
        #cmdList = [ "ChangeSpeed(100,180,0.45)","ChangeSpeed(100,90,0.45)"]
        #print("Server answer:")
        self.client.sendCommand("GetInfo(True)")
        self.client.sendCommand("GetSpeed(True)")
        self.client.sendCommand("STOP(False)")

        while True:

            speed = random.randint(0, 49) * 10
            direc = random.randint(0, 359)
            rot = random.randint(-49, 49) * 0.01
            self.speedSend.append(speed)
            self.directionSend.append(direc)
            self.rotSend.append(rot)
            cmd = "ChangeSpeed(" + str(speed) + "," + str(direc) + "," + str(rot) + ")"
            #print("Command:" + cmd)
            #cmd = input()
            serverAnswer = self.client.sendCommand(cmd)
            #print("Server answer:")
            #rint(serverAnswer)
            time.sleep(1)
            self.speedSend.append(speed)
            self.directionSend.append(direc)
            self.rotSend.append(rot)
            self.__T += 1
            if self.__T == 3:
                self.client.sendCommand("STOP(True)")
            #if self.__T > 15:
                #print(self.client.sendCommand("STOP(False)"))
                #self.__T = 0


test = Test()
test.run()


