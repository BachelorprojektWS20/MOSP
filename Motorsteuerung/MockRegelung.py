import threading
import time
#from Sensor.readsensor import Sensor
#import matplotlib.pyplot as plt

class MockRegelung:

    def __init__(self):

        #self.sensor = Sensor()
        self.__readSensor = False
        self.__readInfo = False
        self.__mcommands = []
        self.__length = 0
        self.__heading = 0
        self.__speed = 0
        #self.sensorTH = threading.Thread(target = self.sensor.startMeasurment)
        #self.sensorTH.start()
        #self.graphThread = threading.Thread(target = self.graph)
        #self.graphThread.start()
        self.__speedList = [0]
        self.__direList = [0]
        self.__rotList = [0]
        self.timerCounter = True

    def isReadSensor(self):
        return self.__readSensor
    def isReadInfo(self):
        return self.__readInfo
    def getMovement(self):
        #return self.sensor.getMeasurment()
        return(0.0, 0, 0)
    
    def setMovement(self, movement):
        #print(movement)
        self.__length = movement[0]
        self.__heading = movement[1]
        self.__speed = movement[2]
            

    def getInfo(self):
        #return str(self.sensor.getMeasurment())
        return str((0.0, 0, 0))


