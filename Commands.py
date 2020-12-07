import re

""" Überprüft ob die Befehle Syntaktisch korrekt sind.
    Args: command, der zu überprüfende Befehl als String.
    Return: Boolean des Ergebnisses.
"""
def checkCommand(self, command):
    # Accepts the following Command; ChangeSpeed(Number,Number,Number)
    if commandIsChangeSpeed(command):
        return True
    # Accepts the following Command: Polygonzug[(ID,Strecke,Richtung,Max Geschwindigkeit)(..)..]
    elif commandIsPolygonzug(command):
        return True
    # Accepts the followong Command: StopPolygonzug()
    elif commandIsStopPolygonzug(command):
        return True
    # Accepts the following Command: Polygonzug(ID,Strecke,Richtung,Max Geschwindigkeit)
    elif commandIsChangePolygonzug(command):
        return True
    # Accepts the following Command: AddPolygonzug[(ID,Strecke,Richtung,Max Geschwindigkeit)(..)..]
    elif commandIsAddPolygonzug(command):
        return True
    elif commandIsMode(command):
        return True
    # Accepts the following Command: GetSpeed(True/False)
    elif commandIsGetSpeed(command):
        return True
    # Accepts the following Command: GetPolygonzug
    elif commandIsGetPolygonzug(command):
        return True
    # Accepts the following Command: GetInfo(True\False)
    elif commandIsGetInfo(command):
        return True
    elif commandIsStop(command):
        return True
    else:
        return False

''' Überprüft ein String dem Befehl Stop entspricht.
    Args: command, der zu überprüfendende Befehl
'''
def commandIsStop(command):
    if re.match('STOP', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl ChangeSpeed entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsChangeSpeed(command):
    if re.match('ChangeSpeed\([0-9]+,[0-9]+,-?[0-9]+.[0-9]+\)', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl Polygonzug entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsPolygonzug(command):
    if re.match('Polygonzug\[(\([0-9]+,[0-9]+,[0-9]+,[0-9]+\))+\]', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl StopPolygonzug entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsStopPolygonzug(command):
    if re.match('StopPolygonzug\(\)', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl ChangePolygonzug entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsChangePolygonzug(command):
    if re.match('ChangePolygonzug\([0-9]+,[0-9]+,[0-9]+,[0-9]+\)', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl AddPolygonzug entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsAddPolygonzug(command):
    if re.match('AddPolygonzug\[(\([0-9]+,[0-9]+,[0-9]+,[0-9]+\))+\]', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl Mode entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsMode(command):
    if re.match('Mode\((Polygonzug|Direkt)\)', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl GetSpeed entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsGetSpeed(command):
    if re.match('GetSpeed\((True|False)\)', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl GetPolygonzug entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsGetPolygonzug(command):
    if re.match('GetPolygonzug\(\)', command) is not None:
        return True
    else:
        return False

''' Überprüft ein String dem Befehl GetInfo entspricht.
    Args: command, der zu überprüfendende Befehl
    Returns: Boolean ob der String dem Befehl enstpricht
'''
def commandIsGetInfo(command):
    if re.match('GetInfo\((True|False)\)', command) is not None:
        return True
    else:
        return False

''' Konvertiert den übergebenen Befehl ChangeSpeed in ein Tupel aus den drei Steuerungswerten.
    Args: command, ChangeSpeed Kommando welches als String vorliegt
    Returns: Tupel aus drei Steuerungswerten.
    Raises: ValueError, wenn der Kommand nicht dem ChangeSpeed-Kommandoformat entspricht
'''
def convertChangeSpeed(command):
    if commandIsChangeSpeed(command):
        commandSplit = re.split('\(', command)
        commandValue = re.split(',', commandSplit[1])
        for i in range(len(commandValue)):
            commandValue[i] = commandValue[i].replace(')', '')
            commandValue[i] = float(commandValue[i])
        zielWert = (commandValue[0], commandValue[1],commandValue[2])
        return zielWert
    else:
        raise ValueError("Command is not in the right format.")

''' Konvertiert den übergebenen Befehl GetInfo und liefert den übergebenen Parameter zurück.
    Args: command, GetInfo Kommando welches als String vorliegt
    Returns: Boolean
    Raises: ValueError, wenn der Kommand nicht dem ChangeSpeed-Kommandoformat entspricht
'''
def convertGetInfo(command):
    if commandIsGetInfo(command):
        commandSplit = re.split('\(', command)
        commandValue = commandSplit[1].replace(')','')
        zielWert = eval(commandValue)
        return zielWert
    else:
        raise ValueError("Command is not in the right format.")

''' Konvertiert den übergebenen Befehl Mode und extrahiert den Parameter des Befehls.
    Args: command, Mode Kommando welches als String vorliegt.
    Returns: String des gewünschten Moduses.
    Raises: ValueError, wenn der Kommand nicht dem ChangeSpeed-Kommandoformat entspricht.
'''
def convertMode(command):
    if commandIsMode(command):
        commandSplit = re.split('\(', command)
        commandValue = commandSplit[1].replace(')','')
        zielWert = commandValue
        return zielWert
    else:
        raise ValueError("Command is not in the right format.")

''' Konvertiert den übergebenen Befehl GetSpeed und extrahiert den Parameter des Befehls.
    Args: command, GetSpeed Kommando welches als String vorliegt
    Returns: Den Parameter des Befehls GetSpeed als Boolean.
    Raises: ValueError, wenn der Kommand nicht dem ChangeSpeed-Kommandoformat entspricht
'''
def convertGetSpeed(command):
    if commandIsGetSpeed(command):
        commandSplit = re.split('\(', command)
        commandValue = commandSplit[1].replace(')','')
        zielWert = eval(commandValue)
        return zielWert
    else:
        raise ValueError("Command is not in the right format.")