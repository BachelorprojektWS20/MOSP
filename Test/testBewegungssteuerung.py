from BewegungsSteuerung import BewegungsSteuerung

test = BewegungsSteuerung(1, 1, 0.1, 100, 0.5)
try:
    test.berechneNeueBewegungswerte((0, 0, 0), (10, -355, -0.1))
except ValueError as e:
    print(e)
try:
    test.berechneNeueBewegungswerte((0, 0, 0), (10, 355, 100))
except ValueError as e:
    print(e)
aktuellerWert = (0,0,0)
aktuellerWert = test.berechneNeueBewegungswerte(aktuellerWert, (0, 355, 0))
for i in range(10):
    aktuellerWert = test.berechneNeueBewegungswerte(aktuellerWert, (10, 345, -0.45))
    print(aktuellerWert)

if aktuellerWert != (20,345,-0.45):
    print("Fail:" + str(aktuellerWert))

