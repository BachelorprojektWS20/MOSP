import threading
import time
from Sensor.readsensor import Sensor
import matplotlib.pyplot as plt

class MockRegelung:

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
        return self.sensor.getMeasurment()
    
    def setMovement(self, movement):
        #print(movement)
        self.__length = movement[0]
        self.__heading = movement[1]
        self.__speed = movement[2]
        self.__speedList.append(movement[0])
        self.__direList.append(movement[1])
        self.__rotList.append(movement[2])
        if self.timerCounter:
            self.timerCounter = False
            timer = threading.Timer(60.0, self.graph)
            timer.start()
            

    def getInfo(self):
        return str(self.sensor.getMeasurment())

    def graph(self):
        #print("Graph")
        self.timerCounter = True
        plt.figure()
        plt.subplot(311)
        plt.plot(self.__speedList, 'k--')
        plt.title("Speeeed")
        plt.subplot(312)
        plt.plot(self.__direList, 'r--')
        plt.title("Direction")
        plt.subplot(313)
        plt.plot(self.__rotList, 'g--')
        plt.show()


