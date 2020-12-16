import RPi.GPIO as GPIO


class PWM(object):
    
    ## Konstruktor
    # Eingabeparameter:
    #  VL: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad vorne links in der Reihenfolge PWM-Signal,CW/CCW,enable
    #  VR: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad vorne rechts in der Reihenfolge PWM-Signal,CW/CCW,enable
    #  HL: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad hinten links in der Reihenfolge PWM-Signal,CW/CCW,enable
    #  HL: 3er Tupel mit den Pin Nummern der Anschlüsse fürs Rad hinten rechts in der Reihenfolge PWM-Signal,CW/CCW,enable
    #  modus: Verwendeter Schrittmodus; 1 für Ganzschritte, 2 für Halbschritte, 4 für Viertelschritte, etc.
    
    def __init__ (self,VL,VR,HL,HR,modus):
        
        
        ## Set Pins
    
        # Pins für PWM-Signal
        
        self.__signalVL = VL[0]
        self.__signalVR = VR[0]
        self.__signalHL = HL[0]
        self.__signalHR = HR[0]
        
        #Pins für CW/CCW Rotation
        
        self.__rotVL = VL[1]
        self.__rotVR = VR[1]
        self.__rotHL = HL[1]
        self.__rotHR = HR[1]
        self.__rotList = (self.__rotVL,self.__rotVR,self.__rotHL,self.__rotHR)
        
        #Pins für enable
        
        self.__enableVL = VL[2]
        self.__enableVR = VR[2]
        self.__enableHL = HL[2]
        self.__enableHR = HR[2]
        self.__enableList = (self.__enableVL,self.__enableVR,self.__enableHL,self.__enableHR)
        
        ## Definiere Variablen für die Umdrehungen pro s
        
        self.__uVL = 0
        self.__uVR = 0
        self.__uHL = 0
        self.__uHR = 0
        
        ## Bestimme Anzahl der Schritte pro Umdrehung
        
        self.__schritte = 200 * modus
        
        ## Setup für Pin-Ausgabe
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)        #Allgemeine Pin-Nummerierung; von oben-links nach unten rechts durchnummeriert von 1 - 40
        
        # Setzen der Output-Channel
        
        GPIO.setup(self.__signalVL,GPIO.OUT,initial=0)
        GPIO.setup(self.__signalVR,GPIO.OUT,initial=0)
        GPIO.setup(self.__signalHL,GPIO.OUT,initial=0)
        GPIO.setup(self.__signalHR,GPIO.OUT,initial=0)
        
        GPIO.setup(self.__rotVL,GPIO.OUT,initial=1)
        GPIO.setup(self.__rotVR,GPIO.OUT,initial=0)
        GPIO.setup(self.__rotHL,GPIO.OUT,initial=1)
        GPIO.setup(self.__rotHR,GPIO.OUT,initial=0)
        
        GPIO.setup(self.__enableVL,GPIO.OUT,initial=0)
        GPIO.setup(self.__enableVR,GPIO.OUT,initial=0)
        GPIO.setup(self.__enableHL,GPIO.OUT,initial=0)
        GPIO.setup(self.__enableHR,GPIO.OUT,initial=0)
        
        # Erstellung der PWM-Objekte
        
        self.__pwmVL = GPIO.PWM(self.__signalVL,1)
        self.__pwmVR = GPIO.PWM(self.__signalVR,1)
        self.__pwmHL = GPIO.PWM(self.__signalHL,1)
        self.__pwmHR = GPIO.PWM(self.__signalHR,1)
        self.__pwmList = [self.__pwmVL,self.__pwmVR,self.__pwmHL,self.__pwmHR]
        self.enableAll()

    ## Schaltet alle Motoren an/aus; Hat kein Einfluss auf die Signalerzeugung!!

    def enableAll(self):
        GPIO.output(self.__enableList,1)
        
    def disableAll(self):
        GPIO.output(self.__enableList,0)
        
    ## Startet/Endet alle PWM-Signale (duty cycle: 50%)
    
    def startSignals(self):
        self.__pwmVL.start(50)
        self.__pwmVR.start(50)
        self.__pwmHL.start(50)
        self.__pwmHR.start(50)
        
    def endSignals(self):
        self.__pwmVL.stop()
        self.__pwmVR.stop()
        self.__pwmHL.stop()
        self.__pwmHR.stop()
    
    ## Setzt neuen Schrittmodus
    # Eingabeparameter:
    # modus: 1 für Ganzschritte, 2 für Halbschritte, 4 für Viertelschritte, etc.
    
    def setStepMode(self,modus):
        self.__schritte = 200 * modus
        
    ##Gibt aktuelle Umdrehungszahlen zurück
    # Rückgabeparameter:
    # u: 4er Tupel in der Reihenfolge VL,VR,HL,HR
    
    def getU(self):
        return (self.__uVL,self.__uVR,self.__uHL,self.__uHR)
    
    ## Liest neue Umdrehungszahlen ein, rechnet sie um und erzeugt das PWM-Signale.
    ## Setzt außerdem die CW/CCW Signale entsprechend der Vorzeichen der Umdrehungssignale
    # Eingabeparameter:
    # u: 4er Tupel der Umdrehungszahlen in Umdrehungen pro s in der Reihenfolge VL,VR,HL,HR
    
    def setU(self,u):
        self.__uVL = u[0]
        self.__uVR = u[1]
        self.__uHL = u[2]
        self.__uHR = u[3]
        
        # Umrechnung von Umdrehung in Frequenz
        
        f = []
        for element in u:
            f.append(element * self.__schritte)
        
        # Setzen der Frequenz
        
        for i in range(4):
            
            if f[i] == 0:
                self.__pwmList[i].stop()
            elif f[i] < 0:
                if i%2 == 0:
                    GPIO.output(self.__rotList[i],0)
                elif i%2 == 1 :
                    GPIO.output(self.__rotList[i],1)
                self.__pwmList[i].ChangeFrequency(-f[i])
                self.__pwmList[i].start(50)
            elif f[i] > 0:
                if i%2 == 0:
                    GPIO.output(self.__rotList[i],1)
                elif i%2 == 1 :
                    GPIO.output(self.__rotList[i],0)
                self.__pwmList[i].ChangeFrequency(f[i])
                self.__pwmList[i].start(50)


