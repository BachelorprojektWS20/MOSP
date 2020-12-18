from Motorsteuerung.MotorControl import MotorControl
import time

if __name__ == "__main__":
    #TODO: Andere PINs
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