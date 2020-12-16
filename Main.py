from Motorsteuerung.MotorControl import MotorControl

if __name__ == "__main__":
    #TODO: Andere PINs
    VL = (3, 5, 7)
    VR = (8, 10, 11)
    HL = (13, 15, 16)
    HR = (36, 38, 40)
    motorSteu = MotorControl( VL, VR, HL, HR, 2)
    motorSteu.start()