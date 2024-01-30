'''

Rules:
    No usage of threading (if not made sure they will die at end of the 10 minute, only using threading library)
    Well documented
    No errors
    does not start system processes.
    No networking
    max runtime is 10min (we have to create a timer to kill itself)
    have to use atleast one Sense HAT sensor.
    No fucking or swearing

python 3.9.2

install libraires:
- skyfield
- picamera
- gpiozero
- nympy
- logzero
- opencv-python
- sense_hat
    https://sense-hat.readthedocs.io/en/latest/api/#imu-sensor

using pip3

'''
import Math
#from sense_hat import SenseHat
#sense = SenseHat()

#raw = sense.get_compass_raw()

#print(sense.compass_raw)

from MagneticField import pyIGRF
import json

def SaveGeomagnetic():
    with open('data.json', 'rw') as datafile:
        datafile.write(json_string)
        datafile.close()

def loadGeomagnetic():
    with open('data.json', 'r') as datafile:
        return json.loads(datafile.readlines())

mag = pyIGRF.MagneticField

PreCalc = []
Done = []

#for i in range(360):
    #PreCalc.append(mag.GetMagneticFieldVector(mag.GetData(0,i,7000,2024)).unitVector().toDict())

json_string = json.dumps(PreCalc, indent=4, sort_keys=True)

