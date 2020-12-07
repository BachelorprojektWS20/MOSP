
def convertRecivedCommand:
    if re.match('ChangeSpeed\([0-9]+,[0-9]+,[0-9]+\)', command) is not None:
        commandSplit = re.split('\(', command)
        commandValue = re.split(',', commandSplit[1])
        for i in range(len(commandValue)):
            commandValue[i] = commandValue[i].replace(')', '')
            commandValue[i] = float(commandValue[i])
        zielWert = (commandValue[0], commandValue[1],commandValue[2])