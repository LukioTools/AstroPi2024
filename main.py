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
#from sense_hat import SenseHat
#sense = SenseHat()

#raw = sense.get_compass_raw()

#print(sense.compass_raw)

from MagneticField import pyIGRF
mag = pyIGRF.MagneticField
date, alt, lat, colat, lon, itype, sd, cd = mag.GetData(0,0,7000,2024)
print(mag.GetMagneticFieldVector(date, alt, lat, colat, lon, itype, sd, cd))