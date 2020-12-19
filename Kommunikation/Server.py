# first of all import the socket library
import socket
import threading
import fcntl
import struct
import uuid
from Motorsteuerung import MotorControl
from Motorsteuerung.Commands import checkCommand, commandIsStop, convertStop
#TODO: Beobachter für die Motorsteuerung!?

'''Source: https://circuitdigest.com/microcontroller-projects/display-ip-address-of-raspberry-pi
'''
def get_interface_ipaddress(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', network[:15])
    )[20:24])

""" Servermodul für die Motorsteuerung.
"""
class Server:

    def __init__(self, motorControl):
        #wlan0
        ip = get_interface_ipaddress(b'wlan0')
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
        if not isinstance(self.__motorControl, MotorControl.MotorControl):
            raise AttributeError("Der übergabe Parameter muss vom Typ Motorkontrolle sein")
        self.__motorControl = motorControl

    """ Gibt zurück ob eine Verbindung zu einem Clienten besteht.    
    """
    def isConnected(self):
        return self.__isConnected

    """ Erzeugt eine Verbindung mit einem Clienten.
        Desweiteren werden die List für die eingegangenen Befehle und Nachrichten zurückgesetzt.
    """
    def __createConnection(self):
        if not self.__isConnected:
            print("Server: Waiting for Connection!")
            # Warten auf eine neue Verbindung von einem CLienten.
            self.__commandSocket.listen()
            self.__dataSocket.listen()
            self.__commandConnection, commandAddress = self.__commandSocket.accept()
            self.__dataConnection, dataAddress = self.__dataSocket.accept()
            self.__isConnected = True
            self.__connectionID = id(self.__commandConnection)
            #TODO: Benötigt?
            #self.__itemsToSendLock = threading.Lock()
            #self.__messagesReceivedLock = threading.Lock()
            # Reseten der empfangenen Befehle und Nachrichten
            self.__messagesReceived = []
            self.itemsToSend = []
            print("Server: Connected")
        else:
            raise RuntimeError('There is already a connection to Client established.')

    """ Started des Kommunikations Thread.
    """
    def runServer(self):
        serverThread = threading.Thread(target=self.__startCommunication)
        serverThread.start()

    """ Started die Threads für die Kommunikation und ist eine endlosschleife, da der Server dauerhaft in Betrieb sein 
        soll. Werden die Kommunikation Threads beendet, wird wieder eine Neuverbindungs versuch begonnen. Ist dies 
        erfolgreich werden die Threads für die Kommunikation neugestarted.
    """
    def __startCommunication(self):
        # Erzeugen der ersten Verbindung zu einem Clienten.
        self.__createConnection()
        while True:
            # Überprüfen ob eine Verbindung zu einem CLienten besteht.
            if self.__isConnected:
                # Starten der Threads für die Kommunikation.
                commandThread = threading.Thread(target=self.__commandCommunication)
                sendThread = threading.Thread(target=self.__startSendingData)
                commandThread.start()
                sendThread.start()
                commandThread.join()
                sendThread.join()
            else:
                # Falls keine Verbindung besteht wird auf eine Verbindung eines CLienten gewarted.
                self.__reconnect()

    """ Funktion welche für das Empfangen von Kommandos für die Motorsteuerung zuständig ist.
        Bei eingehendem Kommando, wird dieses auf syntaktische Korrektheit überprüft.
        Sollte es zu einem Verbindungsausfall kommen so wird eine Neuverbindung mit einem Clienten vorgenommen( siehe
        __reconnect() Funktion )
        Werden mehr als 512 Befehle übermittelt, wird das erste Element der List entfernt um die Listenlänge nicht über
        512 wachsen zu lassen, um bei langem Betrieb keine in Speicherprobleme zu verursachen.
        Als Antwort erhält der Klient entweder die Fehlermeldung oder eine ID welche zu Identifikation des Kommandos
        dient, damit wenn die Motorsteuerung eine Fehlermeldung sendet das Kommando identifiziert werden kann welches für
        diesen Verantwortlich ist.
        Die korrekten Kommandos werden an die messagesReceived Liste angehängt.
    """
    def __commandCommunication(self):
        # Überprüfen ob eine Verbindung besteht
        while self.__isConnected:
            try:
                # Empfangen eines Komandos für die Motorsteuerung.
                command = str(self.__commandConnection.recv(1024).decode("utf-8"))
                # Überprüfung des Commandos auf syntaktische Korrektheit
                if not checkCommand(command):
                    answer = "Invalid Command: " + command
                else:
                    # Anfügen des Komandos an die Komandoliste
                    with self.__messagesReceivedLock:
                        # Entfernen von Elemente aus der Kommando List falls diese die Länge von 512 überschreitet.
                        if len(self.__messagesReceived) > 512:
                            self.__messagesReceived.pop(0)
                        # Zuweisen einer ID für ein Kommando, welches zu Identifikation eines Befehles dient.
                        id = uuid.uuid4()
                        self.__messagesReceived.append((id, str(command)))
                        # Sollte das Kommando ein Stop Signal sein wird dieses direkt an die Motorsteuerung weiter
                        # gegeben, um ein schnellst mögliches anhalten zu erlauben.
                        if commandIsStop(str(command)):
                            if convertStop(str(command)):
                                self.__motorControl.stop()
                    answer = str(id)
                # Antwort für den Clienten ob das Kommando korrekt war. Falls das Kommando korrekt ist und an die
                # Motorsteuerung weitergegeben wird, wird eine ID zurückgegeben.
                self.__commandConnection.sendall(answer.encode('utf-8'))
            # Sollte die Verbindung getrennt werden wird ein Verbindungsaufbau begonnen.
            except ConnectionAbortedError:
                self.__reconnect()
            except BrokenPipeError:
                self.__reconnect()
            except ConnectionResetError:
                self.__reconnect()

    """ Sendet die Daten an den verbundenen Clienten. Hier zu zählen zum eine Warnungen oder
        Fehlermeldungen welche von der Motorsteuerung gemeldet werden. Desweiteren gehören dazu
        auch alle Daten welche den Zustand der Motorsteuerung beschreiben. Die zu Sendenden Nachrichten befinden sich
        hierfür in er itemsToSend Liste.
    """
    def __startSendingData(self):
        while self.__isConnected:
            try:
                # Setzen eines Timeouts für die dataconnection Verbindung, um zu überprüfen ob die Client in
                # angemessener Zeit antwortet. Antworted dieser nicht, wird ein Verbindungsneuaufbau begonnen.
                self.__dataConnection.settimeout(1.0)
                if len(self.__itemsToSend) > 0:
                    item = self.__itemsToSend[0]
                    # Senden der Nachricht an den CLienten.
                    self.__dataConnection.sendall(item.encode('utf-8'))
                    # Warte auf die Bestaetigung des Clientens.
                    answer = self.__dataConnection.recv(1024)
                    # Entfernen der gesendeten Nachricht aus der List der zu sendenden Nachrichten.
                    if answer == b'Recived':
                        with self.__itemsToSendLock:
                            self.__itemsToSend.pop(0)
                else:
                    item = "None"
                    self.__dataConnection.sendall(item.encode('utf-8'))
                    answer = self.__dataConnection.recv(1024)
                self.__dataConnection.settimeout(None)
            # Abfangen aller Fehler welche beim Senden durch einen Verbindungsabbruch auftreten können. Tritt ein
            # Verbindungsabbruch auf wird ein Verbindungsneuaufbau begonnen.
            except socket.timeout as e:
                self.__reconnect()
            except BrokenPipeError:
                self.__reconnect()
            except ConnectionAbortedError:
                self.__reconnect()
            except ConnectionResetError:
                self.__reconnect()
            except OSError:
                self.__reconnect()

    """ Fügt eine Nachricht an die Liste der Zusendenden Nachrichten an.
        Args:   item, die Nachricht als String.
    """
    def addItemToSend(self, item):
        with self.__itemsToSendLock:
            self.__itemsToSend.append(str(item))

    """ Beide Threads welche für die Kommunikation zwischen dem Server und Client zu ständig sind wechseln in diesen
        Zustand bzw. Funktion wenn eine Verbindung zum Clienten nicht mehr verfügbar ist. In dieser Funktion started den
        Verbindungsvorgang neu und warted auf eine neue Verbindung. Durch das Lock wird verhindert das meherere Funktion
        gleichzeitig eine Neuverbindung warten.
    """
    def __reconnect(self):
        if isinstance(self.__motorControl, MotorControl.MotorControl):
            self.__motorControl.stop()
        currentConnectionID = self.__connectionID
        with self.__reconnectLock:
            if self.__isConnected and self.__connectionID == currentConnectionID:
                self.__isConnected = False
                try:
                    self.__dataConnection.shutdown(socket.SHUT_RDWR)
                except OSError as e:
                    pass
                try:
                    self.__dataConnection.close()
                except OSError as e:
                    pass
                try:
                    self.__commandConnection.shutdown(socket.SHUT_RDWR)
                except OSError as e:
                    pass
                try:
                    self.__commandConnection.close()
                except OSError as e:
                    pass
                self.__createConnection()
            else:
                pass

    """ Abrufen der Nachrichten, welche vom Clienten gesendet wurden und löscht die gesamte List der Empfangenen
        Nachrichten. Eine Nachricht besteht dabei aus einem Tupel: (ID, Befehl)
        Return: Liste der Nachrichten
    """
    def getAnswer(self):
        with self.__messagesReceivedLock:
            mess = self.__messagesReceived
            self.__messagesReceived = []
        try:
            return mess
        except:
            return None
