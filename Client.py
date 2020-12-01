# first of all import the socket library
import socket
import threading
import time


class Client:
    
    # ip - Die ip des Gerätes auf dem die Motorsteuerung bzw. der Server lauft.
    def __init__(self, ip):
        # put the socket into listening mode
        __hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(__hostname)
        #print("Your Computer Name is: " + hostname)
        #print("Your Computer IP Address is: " + IPAddr)
        self.__ip = ip
        # Socket für die Kommunikation mit der Motorsteuerungsbefehle.
        self.__commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Socket für die Kommunikation von Messdaten
        self.__dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TODO do you need a lock?
        self.__connectionID = 0
        self.__reconnectLock = threading.Lock()
        self.__isConnected = False
        self.__itemsToSendLock = threading.Lock()
        self.__itemsToSend = []
        self.__messagesReceivedLock = threading.Lock()
        self.__messagesReceived = []
        self.__reconnectCounter = 0
        self.__maxReconnectAttemps = 10
        self.__run = True

    # Falls der SErver beim ersten versuch eines Reconnects scheitert kann mit diesem Parameter gesteuert werden ob
    # dieser, bis ins unendliche einen Reconnect versucht.
    def setmaxReconnectAttemps(self, maxReconnectAttemps):
        self.__maxReconnectAttemps = maxReconnectAttemps

    def isIsConnected(self):
        return self.__isConnected
    # Erzeugt eine Verbindung mit einem Clienten
    # Sollte der Server nicht antworten so wird der Reconnect solange versucht bis das stopReconnect Flag auf
    # true gesetzt wird.

    def __createConnection(self):
        if not self.__isConnected and self.__run:
            #print("Client: Trying to Connection!")
            try:
                self.__commandSocket.settimeout(5)
                self.__commandSocket.connect((self.__ip, 4001))
                self.__commandSocket.settimeout(None)
                self.__dataSocket.settimeout(5)
                self.__dataSocket.connect((self.__ip, 4002))
                self.__dataSocket.settimeout(None)
                self.__isConnected = True
                # Reseten der Connection ID
                if self.__connectionID > 512:
                    self.__connectionID = 0
                self.__connectionID = self.__connectionID + 1
                self.__itemsToSendLock = threading.Lock()
                self.__messagesReceivedLock = threading.Lock()
            except (ConnectionRefusedError, OSError):
                if not self.__maxReconnectAttemps < self.__reconnectCounter:
                    time.sleep(1)
                    self.__reconnectCounter = self.__reconnectCounter + 1
                    self.createConnection()
                else:
                    self.__reconnectCounter = 0
                    raise RuntimeError("Can't connect to Server, check if Server is running. Attempted " +
                                       str(self.__maxReconnectAttemps) + " reconnects.")
            #print("Client: Connected")
        else:
            raise RuntimeError('There is already a connection to Client established.')

    #TODO:
    def runClient(self):
        serverThread = threading.Thread(target=self.__startCommunication)
        serverThread.start()

    #TODO:
    def __startCommunication(self):
        self.__createConnection()
        while self.__isConnected:
            try:
                dataCommunicationThread = threading.Thread(target=self.__dataCommunication)
                dataCommunicationThread.start()
                dataCommunicationThread.join()
            except RuntimeError:
                pass

    # Empfängt eingehende Nachrichten vom Server und bestätigt diesem diese erhalten zu haben.
    # Sollte die Verbindung unterbrochen werden beginnt diese Funktion einen Verbindungsneuaufruf mit
    # der reconnect() Funktion.
    def __dataCommunication(self):
        # Überprüfen ob eine Verbindung besteht
        while self.__isConnected and self.__run:
            try:
                # Empfangen einer Nachricht vom Server.
                command = str(self.__dataSocket.recv(1024).decode("utf-8"))
                with self.__messagesReceivedLock:
                    if command != 'None':
                        self.__messagesReceived.append(str(command))
                answer = "Recived"
                # Antwort für den Server das die Nachricht empfangen wurde. Dient auch als bestätigung für den Server
                # das der Client noch aktiv ist.
                self.__dataSocket.sendall(answer.encode('utf-8'))
            # Sollte die Verbindung getrennt werden wird ein Verbindungsneuaufbau begonnen.
            except ConnectionAbortedError:
                self.__reconnect()
            except BrokenPipeError:
                self.__reconnect()
            except ConnectionResetError:
                self.__reconnect()
            except OSError:
                self.__reconnect()
            except ConnectionResetError:
                self.__reconnect()
        if not self.__isConnected and self.__run:
            raise RuntimeError("Client is not connected to a server yet!")

    # Sendet einen Befehl an den Server, welche an die Motorsteuerung weitergegeben werden sollen.
    # Sollte das Senden in einem Error enden welcher durch die Verbindung zum Server verursacht wird, started diese
    # Funktion einen Verbindungsneuaufbau mit dem selben Server.
    def sendCommand(self, command):
        if self.__isConnected and self.__run:
            try:
                print(command)
                # Setzen eines Timeouts für die Verbindung, um zu überprüfen ob der Server in angemessener
                # Zeit antwortet. Tut dieser das nicht, wird ein Verbindungsneuaufbau begonnen.
                self.__commandSocket.settimeout(1.0)
                # Senden des übegebenen Command befehls
                self.__commandSocket.sendall(command.encode('utf-8'))
                # Warte auf Bestaetigung bzw. Fehlermeldung des Servers ob der Befehl syntaktisch Korrekt war. Desweiteren
                # enthält die Antwort eine Kommand ID für den gesendeten Kommand.
                answer = self.__commandSocket.recv(1024)
                self.__commandSocket.settimeout(None)
                # Rückgabe der Antwort des Servers
                return answer
            # Mögliche Fehler welche zu einer Neuverbindung zwischen Client und Server führen.
            except socket.timeout as e:
                # If the server didn't answer in time, the client tries to reconnect to the server.

                self.__reconnect()
            except BrokenPipeError:
                self.__reconnect()
                #print("Connection was already closed, because client didn't respond")
            except ConnectionAbortedError:
                #print("startsendingData: connectionAbortedError")
                self.__reconnect()
            except ConnectionResetError:
                #print("Error")
                self.__reconnect()
        elif not self.__isConnected and self.__run:
            raise RuntimeError("Clienten is not connected to a server yet!")
        else:
            self.endConnectionToServer()

    # Endeckt eine der Kommunikationsfunktionen das die Verbindung zum Server getrennt wurde, versucht die Funktion
    # einen Neuaufbau mit diesem.
    def __reconnect(self):
        currentConnectionID = self.__connectionID
        with self.__reconnectLock:
            # TODONE hier muss eine block eingeführt werden sodass Funktion die auf das Lock warten bei erzeugter neu
            #  verbindung nicht einen zweiten reconnect auslösen
            if self.__isConnected and self.__connectionID == currentConnectionID and self.__run:
                #print("reconnect: Create new connection")
                self.__isConnected = False
                try:
                    self.__commandSocket.shutdown(socket.SHUT_RDWR)
                    self.__dataSocket.shutdown(socket.SHUT_RDWR)
                    self.__commandSocket = socket.socket()
                    self.__dataSocket = socket.socket()
                except OSError:
                    print("OSError")
                    pass
                self.__createConnection()
                #print("Reconected")
            elif (not self.__isConnected) and self.__connectionID == currentConnectionID and self.__run:
                self.__isConnected = False
                self.__createConnection()
            else:
                pass
                #print("New connection was already created")

    # Gibt alle empfangenen Nachrichten zurück.
    def getReceivedMessages(self):
        try:
            return self.__messagesReceived
        except:
            return None

    # Resetet die empfangenen Nachrichten
    def clearReceivedMessages(self):
        with self.__messagesReceivedLock:
            self.__messagesReceived = []
    # Git die empfangenen Nachrichten zurück und
    # resetet diese dann danach.
    def getAndResetReceivedMessages(self):
        with self.__messagesReceivedLock:
            copy = self.__messagesReceived
            self.__messagesReceived = []
        try:
            return copy
        except:
            return None

    # Deletes the connection between the client and server.
    # Important this method should NOT be called after immediately after the initialization of the client object,
    # because the client is still waiting for the answer of the server.
    def endConnectionToServer(self):
        with self.__reconnectLock:
            if self.__isConnected:
                self.__isConnected = False
                try:
                    self.__dataSocket.shutdown(socket.SHUT_RDWR)
                    self.__dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.__commandSocket.shutdown(socket.SHUT_RDWR)
                    self.__commandSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.__run = False
                    print("Connection Ended")
                except OSError as e:
                    pass
            else:
                raise RuntimeError("The server isn't connected, can't end a non existing connection!")