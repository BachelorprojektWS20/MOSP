import time
from timeit import default_timer as timer
import threading
import argparse
from pmw3901 import PMW3901, BG_CS_FRONT_BCM, BG_CS_BACK_BCM


class Sensor:

    ''' Initialisierung des Sensors
    '''
    def __init__(self):
        
        self.meswertLock = threading.Lock()
        parser = argparse.ArgumentParser()
        parser.add_argument('--rotation', type=int,
                            default=0, choices=[0, 90, 180, 270],
                            help='Rotation of sensor in degrees.')
        parser.add_argument('--spi-slot', type=str,
                            default='front', choices=['front', 'back'],
                            help='Breakout Garden SPI slot.')

        args = parser.parse_args()

        self.flo = PMW3901(spi_port=0, spi_cs=1, spi_cs_gpio=BG_CS_FRONT_BCM if args.spi_slot == 'front' else BG_CS_BACK_BCM)
        self.flo.set_rotation(args.rotation)
        self.tx = 0
        self.ty = 0
        self.timeStart = timer()

    ''' Starten der Messwertaufnahme. Hier werden alle 0.1s die Messwerte des Sensors abgefragt und die einzel Messwerte
        aufaddiert.
    '''
    def startMeasurment(self):
        try:
            while True:
                try:
                    x, y = self.flo.get_motion()
                except RuntimeError:
                    continue
                with self.meswertLock:
                    self.tx += x
                    self.ty += y
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    ''' Gibt die x/y verschiebung des Sensors in Pixel an. Desweiteren liefert diese Funktion auch die Zeit zwischen der
        letzten und aktuellen Abfrage der Messwerte, welche Softwareseitig gemsessen wurde.
        Returns:    Tupel aus drei Weren, als erstes die Zeit in s, dann die x verschiebung des Sensor, dann die y 
                    verschiebung des Sensors.
    '''
    def getMeasurment(self):
        with self.meswertLock:
            measuretime = timer() - self.timeStart
            x = self.ty
            y = self.tx
            self.timeStart = timer()
            self.tx = 0
            self.ty = 0
        return ( measuretime, x, y )
