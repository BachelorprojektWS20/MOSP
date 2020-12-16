from PWM_Erzeugung import PWM
import RPi.GPIO as GPIO
import math
from UmrechnungInU import Umrechnung

test1 = Umrechnung(100)
test2 = PWM((5,7,3),(11,13,15,),(8,10,12),(19,21,23,),2)

u = test1.setEingabe(1,10,2)
test2.setU(u)
print('ok')




