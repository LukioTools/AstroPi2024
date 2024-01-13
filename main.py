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

# Custom 3d vector class
class Vector:
    x = 0;
    y = 0;
    z = 0;

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    #addition of two vectors
    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z

    #multiplication of vector and number
    def __mul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other

    #division of vector and number
    def __truediv__(self, other):
        self.x /= other
        self.y /= other
        self.z /= other


v1 = Vector(1,1,1)
