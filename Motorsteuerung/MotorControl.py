import time
#import matplotlib.pyplot as plt
import threading
from Motorsteuerung.MockRegelung import MockRegelung
from Kommunikation.Server import Server
from Motorsteuerung import Commands
from Motorsteuerung.MotionControl import MotionControl
from Motorsteuerung.controlThread import controlThread

class MotorControl:

    ''' Konstruktor der Motor Kontrolle.
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
        self.__control = MockRegelung()
        self.__server = Server(self)
        self.__currentValues = (0,0,0)
        self.movementControl = MotionControl(1, 0.1, 0.01, 500, 0.5)
        self.__enableGetSpeed = False
        self.__enableGetInfo = False
        self.__time = 0.05
        self.__commandToControl = controlThread( VL, VR, HL, HR, modus)
        self.__messages = []

    ''' Starten der Motorkontrolle, d.h erzeugen und starten des Servers für die Kommunikation. Desweiteren das erzeugen
        und starten der Bewegungskontrolle welche die Bewegungswerte an die Motoren weitergibt. Diese Funktion läuft in
        einer Endlosschleife.
    '''
    def start(self):
        self.__server.runServer()
        self.__commandToControl.start()
        laststep = (0, 0, 0)
        while True:
            time.sleep(0.1)
            messagesToSend = []
            self.__messages = self.__server.getAnswer()
            self.__currentValues = self.__commandToControl.getCurrentStep()
            for message in self.__messages:
                command = message[1]
                id = message[0]
                if Commands.commandIsChangeSpeed(command):
                    try:
                        steps = self.movementControl.calculateMovementChange(command, self.__commandToControl.getCurrentStep())
                        self.__commandToControl.updateSteps(steps)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                    except RuntimeError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsMode(command):
                    try:
                        self.movementControl.changeMode(command)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsGetSpeed(command):
                    try:
                        self.__enableGetSpeed = Commands.convertGetSpeed(command)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsGetInfo(command):
                    try:
                        self.__enableGetInfo = Commands.convertGetInfo(command)
                    except ValueError as error:
                        messagesToSend.append((str(id), str(error)))
                if Commands.commandIsStop(command):
                    self.__commandToControl.setStop(Commands.convertStop(command))
            if self.__server.isConnected():
                step = self.__commandToControl.getCurrentStep()
                messagesToSend.append(step)
                laststep = step
            if self.__enableGetInfo and self.__server.isConnected():
                messagesToSend.append("Info"+str(self.__control.getInfo()))
            for messageToSend in messagesToSend:
                self.__server.addItemToSend(messageToSend)
            u = self.__commandToControl.getU()
            self.__server.addItemToSend(u)

    ''' Führt einen Not-Stop der Plattform durch.
    '''
    def stop(self):
        self.__messages = []
        self.__commandToControl.stop()



