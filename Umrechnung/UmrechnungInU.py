import math

class Umrechnung(object):
    
    # Radius der Meccanum-Räder in m
    __radius = 0.152/2
    
    # Senkrechter Abstand der Räder zur Mittelachse in m = Drehradius bei Rotation um Mittelpunkt (noch nicht ausgemessen!)
    __abstand = 0.17
    
    ## Konstruktor
    # Eingabeparameter:
    # uMax: maximal mögliche Umdrehungen pro s
    
    def __init__(self,uMax):
        self.__vBetrag = 0
        self.__richtung = 0
        self.__rotation = 0
        self.__uMax = uMax
        
    ## Liest neue Parameter ein und rechnet sie in Umdrehungen pro s für jedes einzelne Rad um. Berücksichtigt die maximale Umdrehungsanzahl
    # Eingabeparameter:
    # vBetrag: Geschwindigkeitsbetrag in m/s
    # richtung: Fahrtrichtung als Winkel zur Blickrichtung in Grad. Drehsinn IM Uhrzeigersinn!
    # rotation: Rotationsgeschwindigkeit um den Mittelpunkt in rad/s. Drehsinn IM Uhrzeigersinn!
        
    def setEingabe(self, vBetrag, richtung, rotation):
        self.__vBetrag = vBetrag
        self.__richtung = richtung
        self.__rotation = rotation
        
        # Umrechnung in Radialmaß
        
        winkel = richtung/180*math.pi
        
        # Berechnung der Umdrehungszahlen ohne Rotation in Umdrehungen pro s
        # Die Berchnung basiert auf folgenden Gleichungen (w = Winkelgeschwindigkeit der Räder, r = Radius der Räder):
        # vX = (w1+w2+w3+w4) * r/4
        # vY = (-w1+w2+w3-w4) * r/4
        # Ohne Rotation gilt zudem: w1 = w3 & w2 = w4
        # Zerlegung von vBetrag in vX und vY erlaubt Lösung des Gleichungssystems
        
        uVL = (math.cos(winkel)+math.sin(winkel))*vBetrag/Umrechnung.__radius
        uVR = (math.cos(winkel)-math.sin(winkel))*vBetrag/Umrechnung.__radius
        uHL = uVR
        uHR = uVL
        
        # Berechnung der Rotation und Überlagerung mit der Geschwindigkeit
        
        uRot = rotation * Umrechnung.__abstand/Umrechnung.__radius
        uVL += uRot
        uVR -= uRot
        uHL += uRot
        uHR -= uRot
        
        uList = [uVL,uVR,uHL,uHR]
        
        # Überprüfung ob maximale Umdrehungszahl überschritten wird. Wenn ja, werden alle Räder gleich proportional verlangsamt
        flag = False
        n = 0
        for i in range(4):
            if uList[i] > self.__uMax:
                if flag:
                    if uList[i] >= uList[n]:
                        n = i
                else:
                    n = i
                flag = True
        if flag:
            x = uList[n]
            for i in range(4):
                uList[i] = uList[i]*self.__uMax/x
        return uList
        
        
 