import threading
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
    i += 1
    try:
        client.sendCommand('Hello there!(' + str(i) + ")")
    except RuntimeError as e:
        print(e)
    messages = client.getAndResetReceivedMessages()
    for message in messages:
        print(message)
    if i > 1024:
        i = 0