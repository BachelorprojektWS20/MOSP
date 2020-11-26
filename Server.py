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
        self.commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commandSocket.bind(('127.0.0.1', 4001))
        # Socket für die Kommunikation von Messdaten
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.bind(('127.0.0.1', 4002))
        self.conn = ''
        self.answer = '0'
        self.exitLock = threading.Lock()
        self.isConnected = False
        self.itemsToSendLock = threading.Lock()
        self.itemsToSend = []
        self.messagesReceivedLock = threading.Lock()
        self.messagesReceived = []

    # Erzeugt eine Verbindung mit einem Clienten
    # Resetet die eingegangenen Befehle und Nachrichten zum Senden(Macht das überhaupt sinn???)
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

    #TODO:
    def runServer(self):
        serverThread = threading.Thread(target=self.startCommunication())
        serverThread.start()
    #TODO:
    def startCommunication(self):
        self.createConnection()
        if self.isConnected:
            listeningThread = threading.Thread(target=self.commandCommunication())
            listeningThread.start()
            #sendThread = threading.Thread(target=self.startSendingData)
            #sendThread.start()
            print("End of startComm")
        else:
            raise RuntimeError('There is no connection to Client established')
            #self.createConnection()

    # Funktion welche für das Empfangen von Kommandos für die Motorsteuerung zuständig ist.
    # Bei eingehendem Kommando, wird dieses auf Korrektheit im Syntaktischen überprüft.
    # Sollte es zu einem Verbindungsausfall kommen so wird eine Neuverbindung mit einem Clienten vorgenommen( siehe
    # exit() Funktion )
    def commandCommunication(self):
        # Überprüfen ob eine Verbindung besteht
        while self.isConnected:
            try:
                # Empfangen eines Komandos für die Motorsteuerung
                command = str(self.commandConnection.recv(1024).decode("utf-8"))
                # Überprüfen des Commandos auf Syntaktische Korrektheit
                if ~self.checkCommand(command):
                    answer = "Invalid Command: " + command
                else:
                    # Anfügen des Komandos an die Komandoliste
                    with self.messagesReceivedLock:
                        self.messagesReceived.append(str(command))
                    answer = "Command added to command list."
                # Antwort für den Clienten ob das Kommando korrekt war.
                self.commandConnection.sendall(answer.encode('utf-8'))
            # Sollte die Verbindung getrennt werden wird ein Verbindungsaufbau begonnen.
            except ConnectionAbortedError:
                self.reconnect()


    ### TODO:
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
                try:
                    self.dataconnection.settimeout(1.0)
                    self.dataconnection.sendall(item.encode('utf-8'))
                    answer = self.dataconnection.recv(1024)
                    self.dataconnection.settimeout(None)
                except socket.timeout as e:
                    # If the client didnt answer in time the server assumes the client is dead.
                    # This results in a stop command and the server opens up for a new client to connect
                    self.exit()
                except BrokenPipeError:
                    print("Connection was already closed, because client didn't respond")


    def addItemToSend(self,item):
        with self.itemsToSendLock:
            self.itemsToSend.append(item)


    # Beide Threads welche für die Kommunikation zwischen dem Server und Client zu ständig sind wechseln in diesen
    # Zustand bzw. Funktion wenn eine Verbindung zum Clienten nicht mehr verfügbar ist. In dieser Funktion started den
    # Verbindungsvorgang neu und warted auf eine neue Verbindung. Durch das Lock wird verhindert das meherere Funktion
    # gleichzeitig eine Neuverbindung warten.
    def reconnect(self):
        print("Exit")
        with self.exitLock:
            if self.isConnected:
                self.isConnected = False
                self.dataconnection.shutdown(socket.SHUT_RDWR)
                self.commandConnection.shutdown(socket.SHUT_RDWR)
                self.createConnection()

    #TODO:
    def checkCommand(self, command):
        return False
    #TODO:
    def getAnswer(self):
        try:
            return self.messagesReceived
        except:
            print("Error"+"\n")


