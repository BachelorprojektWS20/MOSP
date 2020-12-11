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
        self.sensorTH = threading.Thread(target = self.sensor.startMeasurment)
        self.sensorTH.start()

    def isReadSensor(self):
        return self.__readSensor
    def isReadInfo(self):
        return self.__readInfo
    def getMovement(self):
        return self.sensor.getMeasurment()

    def addCommands(self, commandWithID):
        command = commandWithID[1]
        if re.match('GetInfo\((True)\)',command):
            self.__readInfo = True
        if re.match('GetInfo\((False)\)',command):
            self.__readInfo = False
        if re.match('GetSpeed\((True)\)',command):
                self.__readSensor = True
        if re.match('GetSpeed\((False)\)',command):
            self.__readSensor = False
        if re.match('Polygonzug\[(\([0-9]+,[0-9]+,[0-9]+,[0-9]+\))+\]', command):
            split = re.split('\[',command)
            split = re.split(',',split[1])
            for i in range(4):
                split[i] = split[i].replace('[',"")
                split[i] = split[i].replace(']',"")
                split[i] = split[i].replace('(',"")
                split[i] = split[i].replace(')',"")
            self.__length = split[1]
            self.__heading = split[2]
            self.__speed = split[3]
        self.__mcommands.append(commandWithID)

    def getInfo(self):
        return str( self.__length)+";"+ str(self.__heading)+";"+ str(self.__speed )

    def getMessages(self):
        if len(self.__mcommands) > 0:
            if random.randint(0,2) == 1:
                return "Error in Command: " + str( self.__mcommands[len(self.__mcommands)- 1][0] )
            else:
                return "Everything works fine."