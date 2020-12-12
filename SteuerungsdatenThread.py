import threading


class SteuerungsdatenThread:

    def __init__(self):
        self.__stepsLock = threading.Lock()
        self.__steps = []
        self.__timerIntervall = .005

    def updateSteps(self, steps):
        if len(steps) < 1:
            raise AttributeError("Steps is not allowed to be empty!")
        with self.__stepsLock:
            self.__steps = steps

    def getCurrentStep(self):
        if len(self.__steps) > 0:
            return self.__steps[0]
        return (0, 0, 0)

    def start(self):
        thread = threading.Thread(target=self.__werteLoop)
        thread.start()

    def __werteLoop(self):
        while True:
            try:
                timer = threading.Timer(self.__timerIntervall, self.__werteAnRegelung)
                timer.start()
                timer.join()
            except ValueError as e:
                pass

    def __werteAnRegelung(self):
        with self.__stepsLock:
            if len(self.__steps) > 1:
                step = self.__steps[0]
                self.__steps.pop(0)
            elif len(self.__steps) == 1:
                step = self.__steps[0]
            else:
                step = (0, 0, 0)
            #print(step)
            #Regelung
