# first of all import the socket library
import socket
import threading
import time


class Server:

    #
    def __init__(self):
        # put the socket into listening mode
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        print("Your Computer Name is:" + hostname)
        print("Your Computer IP Address is:" + IPAddr)
        print("Waiting for Connection!")
        # Socket für die Kommunikation mit der Motorsteuerungsbefehle.
        self.commandSocket = socket.socket()
        self.commandSocket.bind(('', 4001))
        self.commandSocket.settimeout(1)
        # Socket für die Kommunikation von Messdaten
        self.dataSocket = socket.socket()
        self.dataSocket.bind(('', 4002))
        self.dataSocket.settimeout(1)
        self.conn = ''
        self.answer = '0'
        self.isConnected = False
        self.itemsToSendLock = threading.Lock()
        self.itemsToSend = []
        self.messagesReceivedLock = threading.Lock()
        self.messagesReceived = []

    #
    def createConnection(self):
        if ~self.isConnected:
            print("Waiting for Connection!")
            self.commandSocket.listen()
            self.dataSocket.listen()
            self.commandConnection, commandAddress = self.commandSocket.accept()
            self.dataconnection, dataAddress = self.dataSocket.accept()
            self.isConnected = True
            self.itemsToSendLock = threading.Lock()
            self.messagesReceivedLock = threading.Lock()
            self.messagesReceived = []
            self.itemsToSend = []
            print("Connected")
        else:
            raise RuntimeError('There is already a connection to Client established.')

    def startCommunication(self):

        if self.isConnected:
            listeningThread = threading.Thread(target=self.startListening)
            sendThread = threading.Thread(target=self.startSendingData)
            listeningThread.start()
            sendThread.start()
        else:
            raise RuntimeError('There is no connection to Client established')

    # Sendet die Daten an den verbundenen Clienten. Hier zu zählen zum eine Warnungen oder
    # Fehlermeldungen welche von der Motorsteuerung gemeldet werden. Desweiteren gehören dazu
    # auch alle Daten welche den Zustand der Motorsteuerung beschreiben.
    def startSendingData(self):
        while self.isConnected:
            # Create copy of List, so it isn't locked for the duration of the for-loop
            with self.itemsToSendLock:
                itemsToSendCopy = self.itemsToSend
                self.itemsToSend = []
            # Sending the items to the client
            for item in itemsToSendCopy:
                self.dataconnection.sendall(item.encode('utf-8'))
                answer = self.dataconnection.recv(1024)

    def startListening(self):
        while self.isConnected:
            answer = self.commandConnection.recv(1024).decode("utf-8")
            print(answer)
            if answer == b'/endComuication/':
                print("End Com server")
                self.isConnected = False
                self.dataSocket.close()
                self.commandSocket.close()
            with self.messagesReceivedLock:
                self.messagesReceived.append(str(answer))


    def addItemToSend(self,item):
        with self.itemsToSendLock:
            self.itemsToSend.append(item)



    def watchDog(self):
        self.dataSocket.getsockname()

    def getAnswer(self):
        try:
            return self.messagesReceived
        except:
            print("Error"+"\n")


