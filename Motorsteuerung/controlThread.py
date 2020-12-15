import threading
from Motorsteuerung.MockRegelung import MockRegelung
class controlThread:

    def __init__(self):
        self.__stepsLock = threading.Lock()
        self.__steps = []
        self.__timerIntervall = 0.1
        self.mock = MockRegelung()
        self.__stop = True

    ''' Stop der übergabe von Bewegungsbefehlen an die Regelung.
        Übergibt nur noch (0, 0, 0) an die Regelung.
    '''
    def setStop(self, stop):
        self.__stop = stop

    def isStop(self):
        return self.__stop

    ''' Aktualisiert die zu 
    '''
    def updateSteps(self, steps):
        if len(steps) < 1:
            raise AttributeError("Steps is not allowed to be empty!")
        elif self.__stop:
            raise RuntimeError("Der die Motorsteuerung wurde gestoppt.")
        else:
            with self.__stepsLock:
                self.__steps = steps

    def getCurrentStep(self):
        if len(self.__steps) > 0:
            return self.__steps[0]
        return (0, 0, 0)

    def start(self):
        thread = threading.Thread(target=self.__valueLoop)
        thread.start()

    def __valueLoop(self):
        while True:
            try:
                timer = threading.Timer(self.__timerIntervall, self.__valuesToControl)
                timer.start()
                timer.join()
            except ValueError as e:
                pass

    def __valuesToControl(self):
        with self.__stepsLock:
            if len(self.__steps) > 1 and not self.__stop:
                step = self.__steps[0]
                self.__steps.pop(0)
            elif len(self.__steps) == 1 and not self.__stop:
                step = self.__steps[0]
            else:
                step = (0, 0, 0)
            #print(step)
            #Regelung
            self.mock.setMovement(step)

