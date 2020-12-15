import numpy
from Motorsteuerung.Modes import Modes
from Motorsteuerung.Commands import convertChangeSpeed
#TODO: Übersetzten ins Englishe!

class MotionControl:

    def __init__(self, maximumAcceleration, maximumDirectionChange, maximumAngularAcceleration,
                 maximumSpeed, maximumRotation):
        self.__maximumAcceleration = maximumAcceleration
        self.__maximumDirectionChange = maximumDirectionChange
        self.__maximumAngularAcceleration = maximumAngularAcceleration
        self.maximumSpeed = maximumSpeed
        self.maximumRotation = maximumRotation
        self.mode = Modes.DIRECT

    ''' Verändert den Steuermodus des Roboers. Aktuell nur die direkte Kontrolle implementiert
        Args: mode, den Modus in den die Bewegungssteuerung wechseln soll. Variable muss ein Enum des Types Modes sein.
    '''
    def changeMode(self, mode):
        if isinstance(mode, Modes):
            self.mode = mode
        else:
            raise ValueError("Mode muss ein Enum vom Type Mode sein.")

    ''' Berechnet aus dem übergebenen ChangeSpeed Kommando und den aktuellen Bewegungswerten den Verlauf um von dem 
        aktuellen Zustand in den Gewünschten zu gelangen.
        Args:   command, das Kommando welches Ausgewertet und Ausgeführt werden soll.
                aktuellerWert, der aktuelle Zustand des Roboters d.h. ein Tupel aus (aktueller Geschwindigkeit, Richtung
                , Winkelgeschwindigkeit)
        Returns:    Liste aus Tupeln welche den Zustand des Robotersbeschreiben
        Raises: ValueError, wenn der zielWert oder aktuellerWert nicht im Definitionsbereich liegen oder das Kommando 
                    nicht im Format ChangeSpeed(...,...,...) vorliegt.
                RuntimeError, wenn versucht wird den Polygonzug Modus der Bewegungssteuerung aufzurufen.     
    '''
    def calculateMovementChange(self, command, currentValue):
        if self.mode == Modes.DIRECT:
            targetValue = convertChangeSpeed(command)
            courseOfChange = []
            courseOfChange.append(self.calculateNewMovementValues(currentValue, targetValue))
            while courseOfChange[(len(courseOfChange) - 1)] != targetValue:
                courseOfChange.append(
                    self.calculateNewMovementValues(courseOfChange[(len(courseOfChange) - 1)], targetValue))
            return courseOfChange
        else:
            raise RuntimeError("Die Bewegungssteuerung für den Polygonzug ist nocht nicht implementiert!")

    # TODO: Festlegen der Parameter
    ''' 
        Args: zielWerte, ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die gewünschte Bewegung dse Fahrzeugs
                aktuelleWerte, ist ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die aktuelle Bewegung des Fahrzeugs.
        Raises: ValueError, wenn der zielWert oder aktuellerWert nicht im Definitionsbereich liegen.
    '''
    def calculateNewMovementValues(self, currentValue, targetValue):
        try:
            self.__checkValues(targetValue)
            self.__checkValues(currentValue)
        except ValueError as e:
            raise e
        # Berechnung der neuen Geschwindigkeit
        if abs(targetValue[0] - currentValue[0]) > self.__maximumAcceleration:
            newSpeed = currentValue[0] + numpy.sign(
                targetValue[0] - currentValue[0]) * self.__maximumAcceleration
        else:
            newSpeed = targetValue[0]
        newDirection = self.__calculateChangeOfDirection(currentValue, targetValue)
        if abs(targetValue[2] - currentValue[2]) > self.__maximumAngularAcceleration:
            newAngularVelocity = currentValue[2] + numpy.sign(
                targetValue[2] - currentValue[2]) * self.__maximumAngularAcceleration
        else:
            newAngularVelocity = targetValue[2]
        return (newSpeed, newDirection, newAngularVelocity)

    ''' Berechnung der neunen Richtung des Geschwindigkeitsvektores.
        Args: targetValue, ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die gewünschte Bewegung dse Fahrzeugs
                aktuelleWerte, ist ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die aktuelle Bewegung des Fahrzeugs.
        Returns: Ein Tupel 
    '''
    def __calculateChangeOfDirection(self, currentValue, targetValue):
        if currentValue[0] == 0:
            return targetValue[1]
        else:
            if abs(((targetValue[1] - currentValue[1]) + 180) % 360 - 180) > self.__maximumDirectionChange:
                if (((targetValue[1] - currentValue[1]) + 180) % 360 - 180) >= 0:
                    newValue = currentValue[1] + self.__maximumDirectionChange
                else:
                    newValue = currentValue[1] - self.__maximumDirectionChange
                return newValue % 360
            else:
                return targetValue[1]

    ''' Überprüft das übergebene Tupel ob die Werte im erlaubten Bereich liegen.
        Args: werte, ist ein Tupel aus drei Werten in folgender Reihenfolge:
            ( Geschwindigkeit, Richtung, Rotation)
        Returns: None, wenn kein Fehler gefunden wurde.
        Raises: ValueError, wenn die Werte außerhalb des erlaubten Bereiches liegen.
    '''
    def __checkValues(self, values):
        if self.maximumSpeed < values[0]:
            raise ValueError("Die Geschwindigkeit überschreitet das erlaubte Maximum.")
        if values[0] < 0:
            raise ValueError("Die Geschwindigkeit darf nicht negativ sein.")
        if 360 < values[1] or values[1] < 0:
            raise ValueError("Die Richtung muss im bereich ziwschen 0 und 360 Grad liegen.")
        if abs(values[2]) > self.maximumRotation:
            raise ValueError("Die Rotationsgeschwindigkeit überschreitet das erlaubte Maximum.")
