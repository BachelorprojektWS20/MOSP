import threading

from readsensor import Sensor
import random
import re

class MockMotorsteuerung:

    def __init__(self, ip):

        self.sensor = Sensor()
        self.readSensor = False
        self.readInfo = False
        self.commands = []
        self.length = 0
        self.heading = 0
        self.speed = 0
        self.sensorTH = threading.Thread(target = self.sensor.startMeasurment)
        self.sensorTH.start()

    def getMovement(self):
        return self.sensor.startMeasurment()

    def addCommands(self, command):
        for command in command:
            if re.match('GetInfo\((True)\)',command):
                self.readInfo = True
            if re.match('GetInfo\((False)\)',command):
                self.readInfo = False
            if re.match('GetSpeed\((True)\)',command):
                    self.readSensor = True
            if re.match('GetSpeed\((False)\)',command):
                self.readSensor = False
            if re.match('Polygonzug\[(\([0-9]+,[0-9]+,[0-9]+,[0-9]+\))+\]', command):
                split = re.split('\[',command)
                split = re.split(',',split[1])
                for i in range(4):
                    split[i] = split[i].replace('[',"")
                    split[i] = split[i].replace(']',"")
                    split[i] = split[i].replace('(',"")
                    split[i] = split[i].replace(')',"")
                self.length = split[1]
                self.heading = split[2]
                self.speed = split[3]
            self.commands.append(command)

    def getInfo(self):
        return str( self.length, self.heading, self.speed )
    def getMessages(self):
        if random.randint(0,2) == 1:
            return "Error in Command" + str( self.commands[len(self.commands - 1)])
        else:
            return "Everything works fine."