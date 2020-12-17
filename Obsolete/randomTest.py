import socket
import fcntl
import struct
'''
from  Modes import Modes
from BewegungsSteuerung import BewegungsSteuerung
print(type(Modes.DIREKT))
bew = BewegungsSteuerung(1,1,1,0,0)
bew.berechneBewegungsAenderungsVerlauf("ChangeSpeed(10,11,12)")

#print(Mode(1))
#Negativ Richtungsanderung
print(((100-270)+180)%360-180)
#Positive Richtungsanderung
print(((80-270)+180)%360-180)
'''
#item = (str(uuid.uuid4()),"TEst")
#print(str(item).encode('utf-8'))

#steps = []
#steps.append((0, 0, 0))
#steps.append((1, 0, 0))
#print([steps])
#thread = controlThread()
#thread.start()
#thread.updateSteps(steps)
#time.sleep(5)
#thread.updateSteps([(2, 0, 0), (3, 0, 0)])
def get_interface_ipaddress(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', network[:15])
    )[20:24])

print(get_interface_ipaddress(b'wlan0'))
