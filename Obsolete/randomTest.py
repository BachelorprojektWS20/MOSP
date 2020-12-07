import re
import uuid
from  Modes import Modes
from BewegungsSteuerung import BewegungsSteuerung
print(type(Modes.DIREKT))
bew = BewegungsSteuerung(1,1,1,0,0)
bew.berechneBewegungsAenderungsVerlauf("ChangeSpeed(10,11,12)")

#print(Mode(1))
#Negativ Richtungsanderung
print(((100-270)+180)%360-180)
#Positive Richtungsanderung
print(((80-270)+180)%360-180)