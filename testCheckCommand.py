import socket
import time
from TestClient import startSocket
from Server import Server
import threading

server = Server()
assert server.checkCommand("ChangeSpeed(100,100,100000)") is True
assert server.checkCommand("ChangeSpeed(100,100,100A00)") is False

assert server.checkCommand("Polygonzug[(1,100,100,100)(2,101,101,101)]") is True
assert server.checkCommand("Polygonzug[(1,100,100,100)(2,101,101,101)(asdfgb)]") is False

assert server.checkCommand("StopPolygonzug()") is True
assert server.checkCommand("StopPolygonzug(Stop)") is False

assert server.checkCommand("ChangePolygonzug(1,22,22,22)") is True

assert server.checkCommand("AddPolygonzug[(1,100,100,100)(2,101,101,101)]") is True
assert server.checkCommand("AddPolygonzug[(1,100,100,100)(2,101,101,101)(1,1,2,)]") is False

assert server.checkCommand("Mode(Polygonzug)") is True
assert server.checkCommand("Mode(Direct)") is True
assert server.checkCommand("Mode(Schieben)") is False

assert server.checkCommand("GetSpeed(True)") is True
assert server.checkCommand("GetSpeed(False)") is True
assert server.checkCommand("GetSpeed(Flase)") is False
assert server.checkCommand("GetSpeed(false)") is False

assert server.checkCommand("GetPolygonzug()") is True

assert server.checkCommand("GetInfo(True)") is True
assert server.checkCommand("GetInfo(False)") is True
print("Ende, CheckCommand-test erfolgreich.")
