import math

# Custom 3d vector class
class Vector:
    x = 0;
    y = 0;
    z = 0;

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    #addition of two vectors
    def __add__(self, other):
        return Vector( self.x + other.x, self.y + other.y, self.z + other.z)


    #multiplication of vector and number
    def __mul__(self, other):
        return Vector( self.x * other, self.y * other, self.z * other)

    #division of vector and number
    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)