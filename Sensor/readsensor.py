import time
from timeit import default_timer as timer
import threading
import argparse
from pmw3901 import PMW3901, BG_CS_FRONT_BCM, BG_CS_BACK_BCM

class Sensor:
    
    #print("""motion.py - Detect flow/motion in front of the PMW3901 sensor.

    #Press Ctrl+C to exit!
    #""")
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
    def getMeasurment(self):
        with self.meswertLock:
            measuretime = timer() - self.timeStart
            x = self.ty
            y = self.tx
            self.timeStart = timer()
            self.tx = 0
            self.ty = 0
        return ( measuretime, x, y )
