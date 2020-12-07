import threading
from Server import Server
import time
from Client import Client

client = Client('127.0.0.1')
clientTH = threading.Thread(target=client.runClient)
server = Server()
serverTH = threading.Thread(target=server.runServer)
serverTH.start()
clientTH.start()
time.sleep(0.1)
cmd = 951*"i"
print( client.sendCommand(cmd) )
time.sleep(0.1)
try:
    print( client.getAndResetReceivedMessages() )
except:
    pass
time.sleep(1)
client.endConnectionToServer()
client = Client('127.0.0.1')
clientTH = threading.Thread(target=client.runClient)
clientTH.start()
#time.sleep(1)
if client.isIsConnected():
    print( "1: " + str(client.sendCommand("Are ya winning?") ))
    print( client.getAndResetReceivedMessages() )
#print("Ende")
#print( "2:" + str(client.sendCommand("Are ya winning?") ))
#client.endConnectionToServer()