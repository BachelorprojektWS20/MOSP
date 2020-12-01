import random
import threading
import uuid

from Server import Server
import time
from Client import Client


client = Client('169.254.36.181')
clientTH = threading.Thread(target=client.runClient)
clientTH.start()
while not client.isConnected:
    time.sleep(0.1)
i = 0
while True:
    ti="Polygonzug[(" +str(i)+","+str(random.randint(0,200))+","+str(random.randint(0,200))+","+str(random.randint(0,200))+")]"
    time.sleep(0.25)
    try:
        if i == 0:
            id = uuid.uuid4()
            client.sendCommand("GetInfo(True)")
            client.sendCommand("GetSpeed(True)")
        client.sendCommand(ti)
    except RuntimeError as e:
        print(e)
    messages = client.getAndResetReceivedMessages()
    print(messages)

    i += 1
    time.sleep(2)
    if i > 1024:
        i = 0