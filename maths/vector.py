import math 

class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar: float):
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"
    
    def normalize(self):
        l = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        return Vec3(self.x/l, self.y/l, self.z/l)
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def length(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def euler_to_vector(self, yaw, pitch, roll):
        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)

        self.x = math.cos(yaw_rad) * math.cos(pitch_rad)
        self.y = math.sin(yaw_rad) * math.cos(pitch_rad)
        self.z = math.sin(pitch_rad)

    def to_tuple(self):
        return (self.x, self.y, self.z)
    
class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
        return Vec2(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(
                self.x / (other.x if other.x != 0 else 1e-8),
                self.y / (other.y if other.y != 0 else 1e-8)
            )
        return Vec2(
            self.x / (other if other != 0 else 1e-8),
            self.y / (other if other != 0 else 1e-8)
        )

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self):
        l = self.length()
        if l == 0:
            return Vec2(0, 0)
        return self / l

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    @staticmethod
    def cross_scalar_vec(s, v):
        return Vec2(-s * v.y, s * v.x)

    @staticmethod
    def cross_vec_scalar(v, s):
        return Vec2(s * v.y, -s * v.x)