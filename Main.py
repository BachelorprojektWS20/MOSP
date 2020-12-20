from Motorsteuerung.MotorControl import MotorControl
import time

''' Hauptfunktion welche die Motorsteuerung sowie alle dazu gehörenden Komponenten started.
'''
if __name__ == "__main__":
    #TODO: Andere PINs

    # Pin Nummerierung für die Steuerung der Motoren. Verwendete Numerierung ist das BCM System.
    VL = (2, 3, 4)
    VR = (17, 27, 22)
    HL = (23, 24, 25)
    HR = (5, 6, 13)
    while True:
        try:
            motorSteu = MotorControl( VL, VR, HL, HR, 2)
            motorSteu.start()
        except Exception as e:
            print(e)
            time.sleep(0.5)