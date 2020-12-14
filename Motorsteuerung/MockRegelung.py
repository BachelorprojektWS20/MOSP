import threading

from Sensor.readsensor import Sensor


class MockRegelung:

    def __init__(self):

        self.sensor  = Sensor()
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
    def setMovement(self, movement):
        self.__length = movement[0]
        self.__heading = movement[1]
        self.__speed = movement[2]
    def getInfo(self):
        return str(self.sensor.getMeasurment())


