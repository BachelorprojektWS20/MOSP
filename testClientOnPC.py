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
    time.sleep(0.25)
    try:
        if i == 0:
            id = uuid.uuid4()
            client.sendCommand("GetInfo(True)")
            client.sendCommand("GetSpeed(True)")
        client.sendCommand("Polygonzug[(" +str(id)+str(random.int(0,200))+str(random.int(0,200))+str(random.int(0,200))+")]")
    except RuntimeError as e:
        print(e)
    messages = client.getAndResetReceivedMessages()
    for message in messages:
        print(message)
    i += 1
    if i > 1024:
        i = 0