import threading
from Motorsteuerung.MockRegelung import MockRegelung
from Umrechnung.UmrechnungInU import Umrechnung
from Umrechnung.PWM_Erzeugung import PWM

''' Klasse welche für die übergabe der Bewegungsschritte an die Motoren sowie die Umrechnung dieser Schritte 
    verantwortlich ist. 
'''
class controlThread:

    ''' Initialisierung aller benötigten Variablen und Klassen.
        Args:   VL: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad vorne links in der Reihenfolge PWM-Signal,
        CW/CCW,enable
                VR: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad vorne rechts in der Reihenfolge PWM-Signal,
                CW/CCW,enable
                HL: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad hinten links in der Reihenfolge PWM-Signal,
                CW/CCW,enable
                HL: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad hinten rechts in der Reihenfolge PWM-Signal,
                CW/CCW,enable
                modus: Verwendeter Schrittmodus; 1 für Ganzschritte, 2 für Halbschritte, 4 für Viertelschritte, etc.
    '''
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

    ''' Gibt die Umdrehungszahl der einezlnen Räder zurück.
        Returns:    Liste der Radumdrehungen, siehe PWM_Erzeugung
    '''
    def getU(self):
        return self.__pwm.getU()

    ''' Setzt die Bewegung auf null, d.h. führt eine Notbremsung durch.
    '''
    def stop(self):
        with self.__stopLock:
            self.__steps = [(0, 0, 0)]
            self.__stop = True
            self.mock.setMovement((0, 0, 0))

    ''' Stop der übergabe von Bewegungsbefehlen an die Regelung wenn das Stop-Flag auf True gesetzt wird.
        Um die Motorsteuerung aus dem gestoppten Zustand wieder zu aktivieren muss das Flag auf False gesetzt werden.
    '''
    def setStop(self, stop):
        with self.__stopLock:
            self.__stop = stop

    ''' Gibt den Zustand der Motorsteuerung zurück ob diese gestopt ist oder nicht.
    '''
    def isStop(self):
        return self.__stop

    ''' Aktualisiert die Bewegungsschritte welche die Motorsteuerung ausführt. 
        Args:   steps, Liste aus Tupel der Bewegungsschritten 
        Raises: AttributeError, wenn die List leer ist
                RuntimeError, wenn die Motorsteuerung gestoppt wurde
    '''
    def updateSteps(self, steps):
        if len(steps) < 1:
            raise AttributeError("Steps is not allowed to be empty!")
        elif self.__stop:
            raise RuntimeError("Der die Motorsteuerung wurde gestoppt.")
        else:
            with self.__stepsLock:
                self.__steps = steps

    ''' Gibt den Bewegungsschritt zurück der gerade ausgeführt wird
        Returns: Tupel des Bewegungsschrittes aus der aktuell aus geführt wurde
    '''
    def getCurrentStep(self):
        #return self.__pwm.getU()
        return self.__lastStep

    ''' Started die periodische Übergabe der Bewegungsschritte an die Motoren.
    '''
    def start(self):
        thread = threading.Thread(target=self.__valueLoop)
        thread.start()

    ''' Übergibt nach einer in der Variable timerIntervall definierten Zeit einen Bewegungsschritt an die Motoren.
    '''
    def __valueLoop(self):
        while True:
            try:
                timer = threading.Timer(self.__timerIntervall, self.__valuesToControl)
                timer.start()
                timer.join()
            except ValueError as e:
                pass

    ''' Übergibt einen Bewegungsschritt an die Motoren und entfernt diesen Schritt dabei aus der Liste der zu
        auszuführenden Schritte. Ist nur noch ein Schritt in der Liste enthalten wird dieser Dauerhaft übergeben,
        bis die Liste durch ein aufruf von updateSteps verändert wird. Hier werden die Schritte auch in die Umdrehungs-
        zahlen und PWM-Signale umgewandelt.
    '''
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
            pwmSignals = self.__umrechner.setEingabe(step[0]/100, step[1], step[2])
            self.__pwm.setU(pwmSignals)
            #print(step)
            self.mock.setMovement(step)
            self.__lastStep = step