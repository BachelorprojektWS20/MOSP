import threading
from Motorsteuerung.MockRegelung import MockRegelung
from Umrechnung.UmrechnungInU import Umrechnung
from Umrechnung.PWM_Erzeugung import PWM

class controlThread:

    def __init__(self, VL, VR, HL, HR, modus):
        self.__stepsLock = threading.Lock()
        self.__steps = []
        self.__timerIntervall = 0.1
        self.mock = MockRegelung()
        self.__stopLock = threading.Lock()
        self.__stop = True
        self.__lastStep = (0, 0, 0)
        self.__umrechner = Umrechnung(10)
        self.__pwm = PWM(VL, VR, HL, HR, modus)

    ''' Setzt die Bewegung auf null, d.h. führt eine Notbremsung durch.
    '''
    def stop(self):
        with self.__stopLock:
            self.__stop = True
            self.mock.setMovement((0, 0, 0))

    ''' Stop der übergabe von Bewegungsbefehlen an die Regelung.
        Übergibt nur noch (0, 0, 0) an die Regelung.
    '''
    def setStop(self, stop):
        with self.__stopLock:
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
        return self.__pwm.getU()
        #return self.__lastStep

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
            pwmSignals = self.__umrechner.setEingabe(step[0], step[1], step[2])
            self.__pwm.setU(pwmSignals)
            #self.mock.setMovement(step)
            #self.__lastStep = step