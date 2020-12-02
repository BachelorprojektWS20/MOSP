# first of all import the socket library
import socket
import threading
import re
import time
import uuid

# Servermodul für die Motorsteuerung.
class Server:
    
    
    def __init__(self):
        # put the socket into listening mode
        __hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(__hostname)
        #print("Your Computer Name is: " + __hostname)
        #print("Your Computer IP Address is: " + IPAddr)
        ip = '169.254.36.181'
        #ip = ''
        # Socket für die Kommunikation mit der Motorsteuerungsbefehle.
        self.__commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__commandSocket.bind((ip, 4001))
        # Socket für die Kommunikation von Messdaten
        self.__dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__dataSocket.bind((ip, 4002))
        self.__conn = ''
        self.__answer = '0'
        self.__reconnectLock = threading.Lock()
        self.__isConnected = False
        self.__itemsToSendLock = threading.Lock()
        self.__itemsToSend = []
        self.__messagesReceivedLock = threading.Lock()
        self.__messagesReceived = []

    # Erzeugt eine Verbindung mit einem Clienten
    # Resetet die eingegangenen Befehle und Nachrichten zum Senden(Macht das überhaupt sinn???)
    def __createConnection(self):
        if not self.__isConnected:
            print("Server: Waiting for Connection!")
            self.__commandSocket.listen()
            self.__dataSocket.listen()
            self.__commandConnection, commandAddress = self.__commandSocket.accept()
            self.__dataconnection, dataAddress = self.__dataSocket.accept()
            self.__isConnected = True
            self.__connectionID = id(self.__commandConnection)
            self.__itemsToSendLock = threading.Lock()
            self.__messagesReceivedLock = threading.Lock()
            # Reseten der empfangenen Befehle
            self.__messagesReceived = []
            #self.itemsToSend = []
            print("Server: Connected")
        else:
            raise RuntimeError('There is already a connection to Client established.')

    # Started den Kommunikations Thread.
    def runServer(self):
        serverThread = threading.Thread(target=self.__startCommunication)
        serverThread.start()

    # Started die Threads für die Kommunikation und ist eine endlosschleife, da der Server dauerhaft laufen soll.
    def __startCommunication(self):
        self.__createConnection()
        while True:
            if self.__isConnected:
                commandThread = threading.Thread(target=self.__commandCommunication)
                sendThread = threading.Thread(target=self.__startSendingData)
                commandThread.start()
                sendThread.start()
                commandThread.join(
                sendThread.join()
                )
            else:
                #print('There is no connection to Client established, waiting for a reconnect')
                self.__reconnect()

    # Funktion welche für das Empfangen von Kommandos für die Motorsteuerung zuständig ist.
    # Bei eingehendem Kommando, wird dieses auf Korrektheit im Syntaktischen überprüft.
    # Sollte es zu einem Verbindungsausfall kommen so wird eine Neuverbindung mit einem Clienten vorgenommen( siehe
    # exit() Funktion )
    # Werden mehr als 512 Befehle übermittelt, wird das erste Element der List entfernt um die Listenlänge nicht über
    # 512 wachsen zu lassen.
    def __commandCommunication(self):
        # Überprüfen ob eine Verbindung besteht
        while self.__isConnected:
            try:
                # Empfangen eines Komandos für die Motorsteuerung.
                command = str(self.__commandConnection.recv(1024).decode("utf-8"))
                # Überprüfen des Commandos auf Syntaktische Korrektheit
                if not self.__checkCommand(command):
                    answer = "Invalid Command: " + command
                else:
                    # Entfernen von Elemente aus der Kommando List
                    # Anfügen des Komandos an die Komandoliste
                    with self.__messagesReceivedLock:
                        if len(self.__messagesReceived) > 512:
                            self.__messagesReceived.pop(0)
                        id = uuid.uuid4()
                        self.__messagesReceived.append((id, str(command)))
                    answer = "Command added to command list, with ID:" + str(id)
                # Antwort für den Clienten ob das Kommando korrekt war.
                self.__commandConnection.sendall(answer.encode('utf-8'))
            # Sollte die Verbindung getrennt werden wird ein Verbindungsaufbau begonnen.
            except ConnectionAbortedError:
                #print("commandComm: ConnectionAbortedError")
                self.__reconnect()
            except BrokenPipeError:
                #print("commandComm: BrokenPipeEroor")
                self.__reconnect()
            except ConnectionResetError:
                self.__reconnect()

    # Sendet die Daten an den verbundenen Clienten. Hier zu zählen zum eine Warnungen oder
    # Fehlermeldungen welche von der Motorsteuerung gemeldet werden. Desweiteren gehören dazu
    # auch alle Daten welche den Zustand der Motorsteuerung beschreiben.
    def __startSendingData(self):
        while self.__isConnected:
            try:
                # Setzen eines Timeouts für die dataconnection Verbindung, um zu überprüfen ob die Client in
                # angemessener Zeit antwortet. Tut dieser das nicht, wird ein Verbindungsneuaufbau begonnen.
                self.__dataconnection.settimeout(1.0)
                if len(self.__itemsToSend) > 0:
                    item = self.__itemsToSend[0]
                    # Sende Daten.
                    self.__dataconnection.sendall(item.encode('utf-8'))
                    # Warte auf Bestaetigung.
                    answer = self.__dataconnection.recv(1024)
                    # Entferne gesendete Daten aus der List der zu Sendenden Daten.
                    if answer == b'Recived':
                        with self.__itemsToSendLock:
                            self.__itemsToSend.pop(0)
                else:
                    item = "None"
                    self.__dataconnection.sendall(item.encode('utf-8'))
                    #print("Wait for Answer")
                    answer = self.__dataconnection.recv(1024)
                self.__dataconnection.settimeout(None)
            except socket.timeout as e:
                # If the client didnt answer in time the server assumes the client is dead.
                # This results in a stop command and the server opens up for a new client to connect
                self.__reconnect()
            except BrokenPipeError:
                self.__reconnect()
            except ConnectionAbortedError:
                self.__reconnect()
            except ConnectionResetError:
                self.__reconnect()


    def addItemToSend(self,item):
        with self.__itemsToSendLock:
            self.__itemsToSend.append(item)


    # Beide Threads welche für die Kommunikation zwischen dem Server und Client zu ständig sind wechseln in diesen
    # Zustand bzw. Funktion wenn eine Verbindung zum Clienten nicht mehr verfügbar ist. In dieser Funktion started den
    # Verbindungsvorgang neu und warted auf eine neue Verbindung. Durch das Lock wird verhindert das meherere Funktion
    # gleichzeitig eine Neuverbindung warten.
    def __reconnect(self):
        #print("Exit")
        currentConnectionID = self.__connectionID
        with self.__reconnectLock:
            if self.__isConnected and self.__connectionID == currentConnectionID:
                self.__isConnected = False
                try:
                    self.__dataconnection.shutdown(socket.SHUT_RDWR)
                    self.__commandConnection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.__createConnection()
            else:
                pass

    # Überprüft ob die Befehle korrekt syntaktisch sind.
    def __checkCommand(self, command):
        # Accepts the following Command; ChangeSpeed(Number,Number,Number)
        if re.match('ChangeSpeed\([0-9]+,[0-9]+,[0-9]+\)', command) is not None:
            return True
        # Accepts the following Command: Polygonzug[(ID,Strecke,Richtung,Max Geschwindigkeit)(..)..]
        elif re.match('Polygonzug\[(\([0-9]+,[0-9]+,[0-9]+,[0-9]+\))+\]', command) is not None:
            return True
        # Accepts the followong Command: StopPolygonzug()
        elif re.match('StopPolygonzug\(\)', command) is not None:
            return True
        # Accepts the following Command: Polygonzug(ID,Strecke,Richtung,Max Geschwindigkeit)
        elif re.match('ChangePolygonzug\([0-9]+,[0-9]+,[0-9]+,[0-9]+\)', command) is not None:
            return True
        # Accepts the following Command: AddPolygonzug[(ID,Strecke,Richtung,Max Geschwindigkeit)(..)..]
        elif re.match('AddPolygonzug\[(\([0-9]+,[0-9]+,[0-9]+,[0-9]+\))+\]', command) is not None:
            return True
        elif re.match('Mode\((Polygonzug|Direct)\)',command) is not None:
            return True
        # Accepts the following Command: GetSpeed(True/False)
        elif re.match('GetSpeed\((True|False)\)',command) is not None:
            return True
        # Accepts the following Command: GetPolygonzug
        elif re.match('GetPolygonzug\(\)',command) is not None:
            return True
        # Accepts the following Command: GetInfo(True\False)
        elif re.match('GetInfo\((True|False)\)',command) is not None:
            return True
        else:
            return False
    #TODO:?
    def getAnswer(self):
        with self.__messagesReceivedLock:
            mess = self.__messagesReceived
            self.__messagesReceived = []
        try:
            return mess
        except:
            return None


