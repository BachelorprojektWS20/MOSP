# first of all import the socket library
import socket
import threading
import time


class Client:
    
    # ip - Die ip des Gerätes auf dem die Motorsteuerung bzw. der Server lauft.
    def __init__(self, ip):
        # put the socket into listening mode
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        #print("Your Computer Name is: " + hostname)
        #print("Your Computer IP Address is: " + IPAddr)
        self.ip = ip
        # Socket für die Kommunikation mit der Motorsteuerungsbefehle.
        self.commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Socket für die Kommunikation von Messdaten
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TODO do you need a lock?
        self.connectionID = 0
        self.reconnectLock = threading.Lock()
        self.isConnected = False
        self.itemsToSendLock = threading.Lock()
        self.itemsToSend = []
        self.messagesReceivedLock = threading.Lock()
        self.messagesReceived = []
        self.reconnectCounter = 0
        self.maxReconnectAttemps = 10
        self.run = True

    # Falls der SErver beim ersten versuch eines Reconnects scheitert kann mit diesem Parameter gesteuert werden ob
    # dieser, bis ins unendliche einen Reconnect versucht.
    def setmaxReconnectAttemps(self, maxReconnectAttemps):
        self.maxReconnectAttemps = maxReconnectAttemps

    def getIsConnected(self):
        return self.isConnected
    # Erzeugt eine Verbindung mit einem Clienten
    # Sollte der Server nicht antworten so wird der Reconnect solange versucht bis das stopReconnect Flag auf
    # true gesetzt wird.
    def createConnection(self):
        if not self.isConnected and self.run:
            #print("Client: Trying to Connection!")
            try:
                self.commandSocket.settimeout(5)
                self.commandSocket.connect((self.ip,4001))
                self.commandSocket.settimeout(None)
                self.dataSocket.settimeout(5)
                self.dataSocket.connect((self.ip,4002))
                self.dataSocket.settimeout(None)
                self.isConnected = True
                # Reseten der Connection ID
                if self.connectionID > 512:
                    self.connectionID = 0
                self.connectionID = self.connectionID + 1
                self.itemsToSendLock = threading.Lock()
                self.messagesReceivedLock = threading.Lock()
            except ConnectionRefusedError:
                if not self.maxReconnectAttemps < self.reconnectCounter:
                    time.sleep(1)
                    self.reconnectCounter = self.reconnectCounter + 1
                    self.createConnection()
                else:
                    self.reconnectCounter = 0
                    raise RuntimeError("Can't connect to Server, check if Server is running. Attempted "+
                                       str(self.maxReconnectAttemps) + " reconnects.")
            #print("Client: Connected")
        else:
            raise RuntimeError('There is already a connection to Client established.')

    #TODO:
    def runClient(self):
        serverThread = threading.Thread(target=self.startCommunication())
        serverThread.start()

    #TODO:
    def startCommunication(self):
        self.createConnection()
        while self.isConnected:
            try:
                dataCommunicationThread = threading.Thread(target=self.dataCommunication)
                dataCommunicationThread.start()
                dataCommunicationThread.join()
            except RuntimeError:
                pass

    # Empfängt eingehende Nachrichten vom Server und bestätigt diesem diese erhalten zu haben.
    # Sollte die Verbindung unterbrochen werden beginnt diese Funktion einen Verbindungsneuaufruf mit
    # der reconnect() Funktion.
    def dataCommunication(self):
        # Überprüfen ob eine Verbindung besteht
        while self.isConnected and self.run:
            try:
                # Empfangen einer Nachricht vom Server.
                command = str(self.dataSocket.recv(1024).decode("utf-8"))
                with self.messagesReceivedLock:
                    if command != 'None':
                        self.messagesReceived.append(str(command))
                answer = "Recived"
                # Antwort für den Server das die Nachricht empfangen wurde. Dient auch als bestätigung für den Server
                # das der Client noch aktiv ist.
                self.dataSocket.sendall(answer.encode('utf-8'))
            # Sollte die Verbindung getrennt werden wird ein Verbindungsneuaufbau begonnen.
            except ConnectionAbortedError:
                self.reconnect()
            except BrokenPipeError:
                self.reconnect()
            except ConnectionResetError:
                self.reconnect()
            except OSError:
                self.reconnect()
        if not self.isConnected and self.run:
            raise RuntimeError("Client is not connected to a server yet!")


    # Sendet einen Befehl an den Server, welche an die Motorsteuerung weitergegeben werden sollen.
    # Sollte das Senden in einem Error enden welcher durch die Verbindung zum Server verursacht wird, started diese
    # Funktion einen Verbindungsneuaufbau mit dem selben Server.
    def sendCommand(self, command):
        if self.isConnected and self.run:
            try:
                # Setzen eines Timeouts für die Verbindung, um zu überprüfen ob der Server in angemessener
                # Zeit antwortet. Tut dieser das nicht, wird ein Verbindungsneuaufbau begonnen.
                self.commandSocket.settimeout(1.0)
                # Senden des übegebenen Command befehls
                self.commandSocket.sendall(command.encode('utf-8'))
                # Warte auf Bestaetigung bzw. Fehlermeldung des Servers ob der Befehl syntaktisch Korrekt war. Desweiteren
                # enthält die Antwort eine Kommand ID für den gesendeten Kommand.
                answer = self.commandSocket.recv(1024)
                self.commandSocket.settimeout(None)
                # Rückgabe der Antwort des Servers
                return answer
            # Mögliche Fehler welche zu einer Neuverbindung zwischen Client und Server führen.
            except socket.timeout as e:
                # If the server didn't answer in time, the client tries to reconnect to the server.
                #print("startsendingData: timeout")
                self.reconnect()
            except BrokenPipeError:
                self.reconnect()
                #print("Connection was already closed, because client didn't respond")
            except ConnectionAbortedError:
                #print("startsendingData: connectionAbortedError")
                self.reconnect()
            except ConnectionResetError:
                #print("Error")
                self.reconnect()
        elif not self.isConnected and self.run:
            raise RuntimeError("Clienten is not connected to a server yet!")
        else:
            self.endConnectionToServer()

    # Endeckt eine der Kommunikationsfunktionen das die Verbindung zum Server getrennt wurde, versucht die Funktion
    # einen Neuaufbau mit diesem.
    def reconnect(self):
        currentConnectionID = self.connectionID
        with self.reconnectLock:
            # TODONE hier muss eine block eingeführt werden sodass Funktion die auf das Lock warten bei erzeugter neu
            #  verbindung nicht einen zweiten reconnect auslösen
            if self.isConnected and self.connectionID == currentConnectionID and self.run:
                #print("reconnect: Create new connection")
                self.isConnected = False
                try:
                    self.commandSocket.shutdown(socket.SHUT_RDWR)
                    self.dataSocket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.createConnection()
                #print("Reconected")
            elif (not self.isConnected) and self.connectionID == currentConnectionID and self.run:
                self.isConnected = False
                self.createConnection()
            else:
                pass
                #print("New connection was already created")

    # Gibt alle empfangenen Nachrichten zurück.
    def getReceivedMessages(self):
        try:
            return self.messagesReceived
        except:
            return None

    # Resetet die empfangenen Nachrichten
    def clearReceivedMessages(self):
        with self.messagesReceivedLock:
            self.messagesReceived = []
    # Git die empfangenen Nachrichten zurück und
    # resetet diese dann danach.
    def getAndResetReceivedMessages(self):
        with self.messagesReceivedLock:
            copy = self.messagesReceived
            self.messagesReceived = []
        try:
            return copy
        except:
            return None

    # Deletes the connection between the client and server.
    # Important this method should NOT be called after immediately after the initialization of the client object,
    # because the client is still waiting for the answer of the server.
    def endConnectionToServer(self):
        with self.reconnectLock:
            if self.isConnected:
                self.isConnected = False
                try:
                    self.dataSocket.shutdown(socket.SHUT_RDWR)
                    self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.commandSocket.shutdown(socket.SHUT_RDWR)
                    self.commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.run = False
                    print("Connection Ended")
                except OSError as e:
                    pass
            else:
                raise RuntimeError("The server isn't connected, can't end a non existing connection!")