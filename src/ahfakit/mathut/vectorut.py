__all__ = [
    # Angle
    "Angle", "Angle3",

    # Vector
    "Vector", "Vector",

    # Coordination and entity
    "relative_pos", "relative_pos3", "Entity"
]

import math as _math


def relative_pos(coord, coord2):
    """相对二维坐标"""
    return coord2[0] - coord[0], coord2[1] - coord[1]


def relative_pos3(coord, coord2):
    """相对三维坐标"""
    return coord2[0] - coord[0], coord2[1] - coord[1], coord2[2] - coord[2]


class _Vec1(object):

    x = 0.0

    def __init__(self, x=0.0):
        if x:
            self.x = x

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.x)

    def __int__(self):
        return int(self.x)

    def __float__(self):
        return float(self.x)

    def __neg__(self):
        return self.__class__(-self.x)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x)
        elif isinstance(other, (int, float)):
            return self.__class__(self.x + other)
        raise TypeError

    def __eq__(self, __o):
        if isinstance(__o, self.__class__):
            return self.x == __o.x
        return self.x == __o


class _Vec2(object):

    x = 0.0
    y = 0.0

    def __init__(self, x=0.0, y=0.0):
        if x:
            self.x = x
        if y:
            self.y = y

    def __repr__(self):
        return "%s(x=%s, y=%s)" % (self.__class__.__name__, self.x, self.y)

    def __len__(self):
        return 2

    def __tuple__(self):
        return self.x, self.y

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise KeyError

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)
        raise TypeError

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y)
        raise TypeError

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x * other.x, self.y * other.y)
        if isinstance(other, (int, float)):
            return self.__class__(self.x * other, self.y * other)
        raise TypeError

    def __iadd__(self, other):
        if isinstance(other, self.__class__):
            self.x += other.x
            self.y += other.y
            return self
        raise TypeError

    def __isub__(self, other):
        if isinstance(other, self.__class__):
            self.x -= other.x
            self.y -= other.y
            return self
        raise TypeError

    def __imul__(self, other):
        if isinstance(other, self.__class__):
            self.x *= other.x
            self.y *= other.y
            return self
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            return self
        raise TypeError

    def __eq__(self, otehr):
        if isinstance(otehr, self.__class__):
            return self.x == otehr.x and self.y == otehr.y
        return (self.x, self.y) == otehr

    def add(self, other):
        return self + other

    def sub(self, other):
        return self - other

    def mul(self, other):
        return self * other


class _Vec3(object):

    x = 0.0
    y = 0.0
    z = 0.0

    def __init__(self, x=0.0, y=0.0, z=0.0):
        if x:
            self.x = x
        if y:
            self.y = y
        if z:
            self.z = z

    def __repr__(self):
        return "%s(x=%s, y=%s, z=%s)" % (self.__class__.__name__, self.x, self.y, self.z)

    def __len__(self):
        return 3

    def __tuple__(self):
        return self.x, self.y, self.z

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        if key == 2:
            return self.z
        raise KeyError

    def __neg__(self):
        return self.__class__(-self.x, -self.y, -self.z)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x * other.x, self.y * other.y, self.z * other.z)
        if isinstance(other, (int, float)):
            return self.__class__(self.x * other, self.y * other, self.z * other)
        raise TypeError

    def __iadd__(self, other):
        if isinstance(other, self.__class__):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            return self
        raise TypeError

    def __isub__(self, other):
        if isinstance(other, self.__class__):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            return self
        raise TypeError

    def __imul__(self, other):
        if isinstance(other, self.__class__):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
            return self
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
            return self
        raise TypeError

    def __eq__(self, __o):
        if isinstance(__o, self.__class__):
            return self.x == __o.x and self.y == __o.y and self.z == __o.z
        return (self.x, self.y, self.z) == __o

    def add(self, other):
        return self + other

    def sub(self, other):
        return self - other

    def mul(self, other):
        return self * other


class Angle(_Vec1):

    _x = 0.0

    def vec(self, distance: float = 1):
        return Vector(
            _math.sin(self._x * _math.pi / 180) * distance,
            _math.cos(self._x * _math.pi / 180) * distance,
        )

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        value = value % 360
        if value >= 180:
            value = -180 + value%180
        self._x = value


class Angle3(_Vec3):

    _x = 0.0
    _y = 0.0
    _z = 0.0

    def vec(self, distance: float = 1.0):
        if not distance:
            return Vector3()
        return Vector3(0, distance, 0).rotate(-self)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        value = value % 360
        if value >= 180:
            value = -180 + value%180
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        value = value % 360
        if value >= 180:
            value = -180 + value%180
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        value = value % 360
        if value >= 180:
            value = -180 + value%180
        self._z = value


class Vector(_Vec2):

    def rotate(self, angle):
        angle = -angle * _math.pi / 180
        return Vector(
            self.x*_math.cos(angle) - self.y*_math.sin(angle),
            self.y*_math.cos(angle) + self.x*_math.sin(angle),
        )

    def one(self):
        if self.y:
            angle = _math.atan(abs(self.x / self.y))
        else:
            angle = 90 * _math.pi / 180
        return Vector(
            _math.sin(angle) if self.x >= 0 else -_math.sin(angle),
            _math.cos(angle) if self.y >= 0 else -_math.cos(angle),
        )


class Vector3(_Vec3):

    def rotate(self, angle):
        x, y = Vector(self.x, self.y).rotate(angle[2])
        x, z = Vector(x, self.z).rotate(angle[1])
        z, y = Vector(z, y).rotate(angle[0])
        return Vector3(x, y, z)


class Entity(object):

    name = "Entity"
    enable = True
    visible = True
    ignore = False

    def __init__(self, **kwargs):
        self._pos = Vector3()
        self._rotation = Angle3()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "%s name=%s>" % (object.__repr__(self)[:-1], self.__class__.__name__)

    def update(self, dt):
        pass

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = Vector3(*value)

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = Angle3(*value)
