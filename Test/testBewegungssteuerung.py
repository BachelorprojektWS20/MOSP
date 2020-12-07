from BewegungsSteuerung import BewegungsSteuerung
import Commands
test = BewegungsSteuerung(1, 1, 0.1, 100, 0.5)
try:
    test.berechneNeueBewegungswerte((0, 0, 0), (10, -355, -0.1))
except ValueError as e:
    print(e)
try:
    test.berechneNeueBewegungswerte((0, 0, 0), (10, 355, 100))
except ValueError as e:
    print(e)

print(Commands.convertGetInfo("GetInfo(True)"))
print(Commands.convertGetInfo("GetInfo(False)"))
print(Commands.convertMode("Mode(Direkt)"))
print(Commands.convertGetSpeed("GetSpeed(True)"))
print(Commands.convertGetSpeed("GetSpeed(False)"))

aktuellerWert = (1,0,0)
verlauf = test.berechneBewegungsAenderungsVerlauf("ChangeSpeed(100,180,-0.5)", aktuellerWert)
print(verlauf)
verlauf = test.berechneBewegungsAenderungsVerlauf("ChangeSpeed(0,0,0.0)", verlauf[len(verlauf)-1])
print(verlauf)


