import random
import threading
import uuid

from Server import Server
import time
from Client import Client


client = Client('169.254.36.181')
clientTH = threading.Thread(target=client.runClient)
clientTH.start()
idCommands = []
while not client.isIsConnected():
    time.sleep(0.1)
i = 0
while True:
    ti="Polygonzug[(" +str(i)+","+str(random.randint(0,200))+","+str(random.randint(0,200))+","+str(random.randint(0,200))+")]"
    time.sleep(0.25)
    try:
        if i == 0:
            id = uuid.uuid4()
            cmd = "GetInfo(True)"
            idCommands.append((cmd, client.sendCommand(cmd)))
            cmd = "GetSpeed(True)"
            idCommands.append((cmd, client.sendCommand(cmd)))
        idCommands.append((ti, client.sendCommand(ti)))
        if i == 5:
            cmd = "GetInfo(False)"
            idCommands.append((cmd, client.sendCommand(cmd)))
            cmd = "GetSpeed(False)"
            idCommands.append((cmd, client.sendCommand(cmd)))
    except RuntimeError as e:
        print(e)
    messages = client.getAndResetReceivedMessages()
    print("Nachrichten:")
    print(messages)
    print("Commands:")
    print(idCommands)
    i += 1
    time.sleep(2)
    if i > 10:
        idCommands = []
        i = 0