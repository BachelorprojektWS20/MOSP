import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import animateResult
from client import startSocket
from Server import Server
import threading

l = threading.Lock()
l.acquire()


def plot():
    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = []
    ys = []
    ani = animation.FuncAnimation(fig, animateResult.animate, fargs=(xs, ys, ax, server), interval=1500)
    plt.show()


server = Server()
myList = [1,2,3]
print( myList )
clientTH = threading.Thread(target = startSocket, args=(1,))
clientTH.start()

server.createConnection()
server.addItemToSend("/polyStart/")
server.addItemToSend("T2")
server.addItemToSend("stop")
server.startCommunication()
server.addItemToSend("T2")
time.sleep(10)
print( server.getAnswer() )
server.addItemToSend("stop")
#plot()
#serverTH.join()
#clientTH.join()
print( "Ende Main\n" )

