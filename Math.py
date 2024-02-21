import math

# Custom 3d vector class
class Vector:
    x = 0
    y = 0
    z = 0

    # converts itself into dictionary
    def toDict(self):
        return { "x": str(self.x), "y": str(self.y), "z": str(self.z)}

    #calculates magnitude of the vector
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unitVector(self):
        return self/self.magnitude()

    def Angle(self, other):
        return math.acos(self.Dot(other)/(self.magnitude()*other.magnitude()))

    def Dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def dict(cls, dict):
        print("moi")

    def angle_yx(self):
        return (math.atan2(self.y, self.x)*180)/3.14159

    def angle_xz(self):
        return (math.atan2(self.z, self.x)*180)/3.14159
    
    #addition of two vectors
    def __add__(self, other):
        return Vector( self.x + other.x, self.y + other.y, self.z + other.z)

    #multiplication of vector and number
    def __mul__(self, other):
        return Vector( self.x * other, self.y * other, self.z * other)

    #division of vector and number
    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    #for printing
    def __str__(self):
        return str(self.x) + " : " + str(self.y) + " : " + str(self.z)