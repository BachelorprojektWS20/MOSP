import threading

from readsensor import Sensor
import random
import re

class MockMotorsteuerung:

    def __init__(self):

        self.sensor = Sensor()
        self.__readSensor = False
        self.__readInfo = False
        self.__mcommands = []
        self.__length = 0
        self.__heading = 0
        self.__speed = 0
        self.__sensorTH = threading.Thread(target = self.sensor.startMeasurment)
        self.sensorTH.start()

    def getMovement(self):
        return self.sensor.getMeasurment()

    def addCommands(self, command):
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
            self.mcommands.append(command)

    def getInfo(self):
        return str( self.length)+";"+ str(self.heading)+";"+ str(self.speed )

    def getMessages(self):
        if len(self.mcommands) > 0:
            if random.randint(0,2) == 1:
                return "Error in Command" + str( self.mcommands[len(self.mcommands)- 1])
            else:
                return "Everything works fine."