from Motorsteuerung.MotorControl import MotorControl
import time

if __name__ == "__main__":
    #TODO: Andere PINs
    VL = (2, 3, 4)
    VR = (14, 15, 17)
    HL = (27, 22, 23)
    HR = (16, 20, 21)
    #while True:
        #try:
    motorSteu = MotorControl( VL, VR, HL, HR, 2)
    motorSteu.start()
        #except:
         #   time.sleep(1)