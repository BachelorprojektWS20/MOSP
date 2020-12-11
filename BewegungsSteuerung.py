import numpy
from Modes import Modes
from Commands import convertChangeSpeed
#TODO: Übersetzten ins Englishe!

class BewegungsSteuerung:

    def __init__(self, maximaleBeschleunigung, maximaleRichtungsänderung, maximaleWinkelbeschleunigung,
                 maximaleGeschwindigkeit, maximaleRotation):
        self.__maximaleBeschleunigung = maximaleBeschleunigung
        self.__maximaleRichtungsänderung = maximaleRichtungsänderung
        self.__maximaleWinkelbeschleunigung = maximaleWinkelbeschleunigung
        self.maxV = maximaleGeschwindigkeit
        self.maxRotation = maximaleRotation
        self.mode = Modes.DIREKT

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
    def berechneBewegungsAenderungsVerlauf(self, command, aktuellerWert):
        if self.mode == Modes.DIREKT:
            zielWert = convertChangeSpeed(command)
            aenderungsVerlauf = []
            aenderungsVerlauf.append(self.berechneNeueBewegungswerte(aktuellerWert, zielWert))
            while aenderungsVerlauf[(len(aenderungsVerlauf) - 1)] != zielWert:
                aenderungsVerlauf.append(
                    self.berechneNeueBewegungswerte(aenderungsVerlauf[(len(aenderungsVerlauf) - 1)], zielWert))
            return aenderungsVerlauf
        else:
            raise RuntimeError("Die Bewegungssteuerung für den Polygonzug ist nocht nicht implementiert!")

    # TODO: Festlegen der
    ''' 
        Args: zielWerte, ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die gewünschte Bewegung dse Fahrzeugs
                aktuelleWerte, ist ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die aktuelle Bewegung des Fahrzeugs.
        Raises: ValueError, wenn der zielWert oder aktuellerWert nicht im Definitionsbereich liegen.
    '''
    def berechneNeueBewegungswerte(self, aktuellerWert, zielWert):
        try:
            self.__ueberpruefenWerte(zielWert)
            self.__ueberpruefenWerte(aktuellerWert)
        except ValueError as e:
            raise e
        # Berechnung der neuen Geschwindigkeit
        if abs(zielWert[0] - aktuellerWert[0]) > self.__maximaleBeschleunigung:
            neueGeschwindigkeit = aktuellerWert[0] + numpy.sign(
                zielWert[0] - aktuellerWert[0]) * self.__maximaleBeschleunigung
        else:
            neueGeschwindigkeit = zielWert[0]
        neueRichtung = self.__berechneRichtungsAenderung(aktuellerWert, zielWert)
        if abs(zielWert[2] - aktuellerWert[2]) > self.__maximaleWinkelbeschleunigung:
            neueWinkelgeschwindigkeit = aktuellerWert[2] + numpy.sign(
                zielWert[2] - aktuellerWert[2]) * self.__maximaleWinkelbeschleunigung
        else:
            neueWinkelgeschwindigkeit = zielWert[2]
        return (neueGeschwindigkeit, neueRichtung, neueWinkelgeschwindigkeit)

    ''' Berechnung der neune Richtung des Geschwindigkeitsvektores.
        Args: zielWerte, ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die gewünschte Bewegung dse Fahrzeugs
                aktuelleWerte, ist ist ein Tupel mit drei Werten in folgender Reihenfolge:
                (zielGeschwindigkeit, zielRichtung, zielRotation)
                Diese beschreiben die aktuelle Bewegung des Fahrzeugs.
        Returns: Ein Tupel 
    '''
    def __berechneRichtungsAenderung(self, aktuellerWert, zielWert):
        if aktuellerWert[0] == 0:
            return zielWert[1]
        else:
            if abs(((zielWert[1] - aktuellerWert[1]) + 180) % 360 - 180) > self.__maximaleRichtungsänderung:
                if (((zielWert[1] - aktuellerWert[1]) + 180) % 360 - 180) >= 0:
                    neuerWert = aktuellerWert[1] + self.__maximaleRichtungsänderung
                else:
                    neuerWert = aktuellerWert[1] - self.__maximaleRichtungsänderung
                return neuerWert % 360
            else:
                return zielWert[1]

    ''' Überprüft das übergebene Tupel ob die Werte im erlaubten Bereich liegen.
        Args: werte, ist ein Tupel aus drei Werten in folgender Reihenfolge:
            ( Geschwindigkeit, Richtung, Rotation)
        Returns: None, wenn kein Fehler gefunden wurde.
        Raises: ValueError, wenn die Werte außerhalb des erlaubten Bereiches liegen.
    '''
    def __ueberpruefenWerte(self, werte):
        if self.maxV < werte[0]:
            raise ValueError("Die Geschwindigkeit überschreitet das erlaubte Maximum.")
        if werte[0] < 0:
            raise ValueError("Die Geschwindigkeit darf nicht negativ sein.")
        if 360 < werte[1] or werte[1] < 0:
            raise ValueError("Die Richtung muss im bereich ziwschen 0 und 360 Grad liegen.")
        if abs(werte[2]) > self.maxRotation:
            raise ValueError("Die Rotationsgeschwindigkeit überschreitet das erlaubte Maximum.")
