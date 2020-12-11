import re
import threading
import time
from Client import Client
import matplotlib.pyplot as plt

class Test:
    def __init__(self):
        self.speed = [0]
        self.direction = [0]
        self.rot = [0]

    def graph(self):
        while True:
            time.sleep(1)
            plt.figure()
            plt.subplot(311)
            plt.plot(self.speed, 'k--')
            plt.title("Speed")
            plt.subplot(312)
            plt.plot(self.direction, 'r--')
            plt.title("Direction")
            plt.subplot(313)
            plt.plot(self.rot, 'g--')
            plt.title("Rotation")
            plt.show()

    def run(self):

        plotThread = threading.Thread(target=self.graph)
        plotThread.start()
        client = Client('127.0.0.1')
        clientTH = threading.Thread(target=client.runClient)
        clientTH.start()
        time.sleep(0.1)
        cmdList = [ "ChangeSpeed(100,180,0.45)","ChangeSpeed(100,90,0.45)"]

        while True:
            print("Command:")
            cmd = input()
            serverAnswer = client.sendCommand(cmd)
            print("Server answer:")
            print(serverAnswer)
            messages = client.getAndResetReceivedMessages()
            print("Messages:")
            print(messages)
            for message in messages:
                if re.match('\([0-9]+.[0-9]+,\s[0-9]+.[0-9]+,\s(-?[0-9]+.[0-9]+|0)\)', message) is not None:
                    commandSplit = re.split('\(', message)
                    commandValue = re.split(',', commandSplit[1])
                    for i in range(len(commandValue)):
                        commandValue[i] = commandValue[i].replace(' ', '')
                        commandValue[i] = commandValue[i].replace(')','')
                        commandValue[i] = float(commandValue[i])
                    self.speed.append(commandValue[0])
                    self.direction.append(commandValue[1])
                    self.rot.append(commandValue[2])

test = Test()
test.run()


