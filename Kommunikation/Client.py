# first of all import the socket library
import socket
import threading
import time


class Client:
    
    """ Konstruktor der Client-Klasse.

        Args:
            ip: Die IP des Servers zu dem der Client eine Verbindung aufbauen wird.
    """
    def __init__(self, ip):
        __hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(__hostname)
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

    """ Falls der Client beim ersten versuch eines Reconnects scheitert kann mit diesem Parameter gesteuert werden wie 
        oft dieser einen Reconnect versucht. Standardeinstellung sind 10.
        
        Args:   
            maxReconnectAttemps: Intger welche die Anzahl an Verbindungsveruschen beschreibt, wenn kleiner Null werden 
                                    keine weiteren Verbindungsversuche unternommen.
    """
    def setmaxReconnectAttemps(self, maxReconnectAttemps):
        self.__maxReconnectAttemps = maxReconnectAttemps

    """"Gibt zurück ob der Client mit dem Server verbunden ist.
        
        Returns: 
            Boolean if connected or not. 
    """
    def isIsConnected(self):
        return self.__isConnected

    """ Erzeugt eine Verbindung mit einem Server
        Sollte der Server nicht antworten so wird der Reconnect versucht bis die maximale Anzahl an Verbindungsversuchen
        ereicht wird(siehe setmaxReconnectAttemps).
    """
    def __createConnection(self):
        if not self.__isConnected and self.__run:
            try:
                self.__commandSocket.settimeout(5)
                self.__commandSocket.connect((self.__ip, 4001))
                self.__commandSocket.settimeout(None)
                self.__dataSocket.settimeout(5)
                self.__dataSocket.connect((self.__ip, 4002))
                self.__dataSocket.settimeout(None)
                self.__isConnected = True
                if self.__connectionID > 512:
                    self.__connectionID = 0
                self.__connectionID = self.__connectionID + 1
                self.__itemsToSendLock = threading.Lock()
                self.__messagesReceivedLock = threading.Lock()
            except (ConnectionRefusedError, OSError):
                if not self.__maxReconnectAttemps < self.__reconnectCounter:
                    time.sleep(1)
                    self.__reconnectCounter = self.__reconnectCounter + 1
                    self.__createConnection()
                else:
                    self.__reconnectCounter = 0
                    raise RuntimeError("Can't connect to Server, check if Server is running. Attempted " +
                                       str(self.__maxReconnectAttemps) + " reconnects.")
        else:
            raise RuntimeError('There is already a connection to Client established.')

    """ Started den Clienten, d.h Verbindungsaufbau zum angegebenen Server. Danach ist es möglich Befehle zu senden und
        zu empfangen.
    """
    def runClient(self):
        serverThread = threading.Thread(target=self.__startCommunication)
        serverThread.start()

    """ Beginnt die Kommunikation zwischen dem Clienten und dem Server, d.h. das Empfangen der Nachrichten welche vom
        Server kommen.
    """
    def __startCommunication(self):
        self.__createConnection()
        while self.__isConnected:
            try:
                dataCommunicationThread = threading.Thread(target=self.__dataCommunication)
                dataCommunicationThread.start()
                dataCommunicationThread.join()
            except RuntimeError:
                pass

    """ Empfängt eingehende Nachrichten vom Server und bestätigt diesem diese erhalten zu haben.
        Sollte die Verbindung unterbrochen werden beginnt diese Funktion einen Verbindungsneuaufruf mit
        der reconnect() Funktion.
    """
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

    """ Sendet einen Befehl an den Server, welche an die Motorsteuerung weitergegeben werden soll. 
        Kommt es beim Senden zu einem Fehler beginnt der Client mit einem Verbindungsneuaufbau.
        Args:
            command: String welcher das Kommando enthält, welches an den Server gesendet wird. Darf nicht über 950 
                Zeichen besitzten.
            
        Returns:
            Ein String indem die Antwort des Servers bzw. der Motorsteuerung steht. Ist der Befehl Syntaktisch Korrekt
            so wird ein Tupel welches aus einer Id und dem Befehl besteht zurückgegeben. Die ID ist hierbei wichtig 
            falls die Motorsteuerung Fehler sendet, können die Kommandos anhand von der ID idenifiziert werden.
        
        Raises: 
            RunTimeError: Wenn der Client noch nicht zu einem Server verbunden ist.
            ValueError: Wenn der übergebene Befehl länger als 950 Zeichen enthält.
            
    """
    def sendCommand(self, command):
        if len(command) > 950:
            raise ValueError("Der übergebene Befehl überschreitet die Maximale länge von 950.")
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
                return answer.decode('utf-8')
            # Mögliche Fehler welche zu einer Neuverbindung zwischen Client und Server führen.
            except socket.timeout as e:
                self.__reconnect()
            except BrokenPipeError:
                self.__reconnect()
            except ConnectionAbortedError:
                self.__reconnect()
                answer = "Server wasn't rechable"
            except ConnectionResetError:
                self.__reconnect()
        elif not self.__isConnected and self.__run:
            raise RuntimeError("Clienten is not connected to a server yet!")
        else:
            self.endConnectionToServer()

    """ Endeckt eine der Kommunikationsfunktionen das die Verbindung zum Server getrennt wurde, versucht die Funktion
        einen Neuaufbau mit diesem.
    """
    def __reconnect(self):
        currentConnectionID = self.__connectionID
        with self.__reconnectLock:
            # TODONE hier muss eine block eingeführt werden sodass Funktion die auf das Lock warten bei erzeugter neu
            #  verbindung nicht einen zweiten reconnect auslösen
            if self.__isConnected and self.__connectionID == currentConnectionID and self.__run:
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
            elif (not self.__isConnected) and self.__connectionID == currentConnectionID and self.__run:
                self.__isConnected = False
                self.__createConnection()
            else:
                pass

    """ Gibt alle empfangenen Nachrichten zurück.
        Returns:
                Gibt eine Liste aller empfangener Nachrichten zurück.
    """
    def getReceivedMessages(self):
        try:
            return self.__messagesReceived
        except:
            return None

    """ Löscht alle empfangenen Nachrichten aus der Liste.
    """
    def clearReceivedMessages(self):
        with self.__messagesReceivedLock:
            self.__messagesReceived = []

    """ Gibt die empfangenen Nachrichten zurück und löscht alle empfangenen Nachrichten aus der Liste.
        resetet diese dann danach.
    """
    def getAndResetReceivedMessages(self):
        with self.__messagesReceivedLock:
            copy = self.__messagesReceived
            self.__messagesReceived = []
        try:
            return copy
        except:
            return None

    """ Beendet die Verbindung zwischen dem Clienten und dem Server.
        Wichtig: Diese Methode darf nicht direkt nach der Initialisierung des Client Objektes aufgerufen werden, da
        sonst diese gegeineinander Konflikte auslösen.
    """
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