import threading
import time
#from Sensor.readsensor import Sensor
#import matplotlib.pyplot as plt

''' Attrappe für die Regelung zum Testen von Funktionen, wie z.B. das Auslesen des Bewegungssensores.
'''
class MockRegelung:

    ''' Konstruktor fur die relevanten Variablen und Objekte.
    '''
    def __init__(self):

        #self.sensor = Sensor()
        self.__readSensor = False
        self.__readInfo = False
        self.__mcommands = []
        self.__length = 0
        self.__heading = 0
        self.__speed = 0
        self.__speedList = [0]
        self.__direList = [0]
        self.__rotList = [0]
        self.timerCounter = True

    #deprecated
    def isReadSensor(self):
        return self.__readSensor

    #deprecated
    def isReadInfo(self):
        return self.__readInfo

    ''' Gibt den Messwert des Sensors zurück.
        Returns: Tupel aus Zeit, X-Beweugng, Y-Bewegung.
    '''
    def getMovement(self):
        #return self.sensor.getMeasurment()
        return(0.0, 0, 0)

    ''' Setzten des Bewegungswerte des Roboters.
        Args:   Tupel aus den Bewegungswerten.
    '''
    def setMovement(self, movement):
        #print(movement)
        self.__length = movement[0]
        self.__heading = movement[1]
        self.__speed = movement[2]
            
    ''' Gibt die Bewegungsinformation welche der Sensor erstellt zurück.
        Returns: Tupel aus Zeit, X-Beweugng, Y-Bewegung.
    '''
    def getInfo(self):
        #return str(self.sensor.getMeasurment())
        return str((0.0, 0, 0))


