import math
from utils.maths.matrix import Matrix


class Point:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_str(s, function=int):
        if '(' not in s or ')' not in s or not (1 <= s.count(',') <= 2):
            raise ValueError
        s = s.replace('(', '')
        s = s.replace(')', '')
        if s.count(',') == 1:
            s += ',0'
        s = s.replace(',', ' ')
        s = s.split()
        return Point(function(s[0]), function(s[1]), function(s[2]))

    def __add__(self, other):
        if isinstance(other, Vector):
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        raise ValueError(f'unsupported operand type(s) for +: "Point" and "{other.__class__.__name__}"')

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def is_on(self, other):
        if isinstance(other, Line):
            return Vector(self, other.point) | other.vector
        if isinstance(other, Plane):
            return abs(other.normal.x * self.x + other.normal.y * self.y + other.normal.z * self.z + other.d) < 1e-10
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    def projection_xy(self):
        return Point(self.x, self.y, 0)

    def projection_xz(self):
        return Point(self.x, 0, self.z)


class Vector:
    def __init__(self, x, y, z=0):
        if isinstance(x, Point) and isinstance(y, Point):
            self.x = y.x - x.x
            self.y = y.y - x.y
            self.z = y.z - x.z
        else:
            self.x = x
            self.y = y
            self.z = z

    @staticmethod
    def from_str(s, function=int):
        s = s.replace('{', '')
        s = s.replace('}', '')
        s = s.replace(',', ' ')
        s = s.split()
        return Vector(function(s[0]), function(s[1]), function(s[2]))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return Vector(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return Vector(self.x * other, self.y * other, self.z * other)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        raise ValueError(f'unsupported operand type(s) for +: "Vector" and "{other.__class__.__name__}"')

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        raise ValueError(f'unsupported operand type(s) for -: "Vector" and "{other.__class__.__name__}"')

    def __and__(self, other):
        if isinstance(other, Vector):
            return Vector(self.y * other.z - self.z * other.y,
                          self.z * other.x - self.x * other.z,
                          self.x * other.y - self.y * other.x)
        raise ValueError(f'unsupported operand type(s) for &: "Vector" and "{other.__class__.__name__}"')

    def __str__(self):
        return '{' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + '}'

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __or__(self, other):
        if isinstance(other, Vector):
            return abs((self.x * other.y) - (self.y * other.x)) < 1e-10 and \
                   abs((self.x * other.z) - (self.z * other.x)) < 1e-10 and \
                   abs((self.y * other.z) - (self.z * other.y)) < 1e-10
        raise ValueError(f'unsupported operand type(s) for |: "Vector" and "{other.__class__.__name__}"')

    def is_null_vector(self):
        return not (self.x or self.y or self.z)


class Line:
    def __init__(self, obj1, obj2):
        if isinstance(obj1, Plane) and isinstance(obj2, Plane):
            line = obj1.intersection(obj2)
            self.point = line.point
            self.vector = line.vector
        elif isinstance(obj1, Point) and isinstance(obj2, Vector):
            self.point = obj1
            if isinstance(obj2, Point):
                self.vector = Vector(obj1, obj2)
            else:
                self.vector = obj2
        elif isinstance(obj1, Point) and isinstance(obj2, Point):
            self.point = obj1
            self.vector = Vector(obj1, obj2)
        else:
            raise ValueError(
                f'unsupported operand type(s) for Line: "{obj1.__class__.__name__}" and "{obj2.__class__.__name__}"')

    def __str__(self):
        return f'(x - {self.point.x}) / {self.vector.x} = (y - {self.point.y}) /' \
               f'{self.vector.y} = (z - {self.point.z}) / {self.vector.z}'

    def __or__(self, other):
        if isinstance(other, Line):
            return self.vector | other.vector
        if isinstance(other, Plane):
            return abs(self.vector * other.normal) < 1e-10
        if isinstance(other, Vector):
            return self.vector | other
        raise ValueError(f'unsupported operand type(s) for |: "Line" and "{other.__class__.__name__}"')

    def intersection(self, other, eps=1e-10):
        if isinstance(other, Plane):
            if self | other:
                return None
            k = -(other.normal.x * self.point.x + other.normal.y * self.point.y + other.normal.z * self.point.z +
                  other.d) / \
                (other.normal.x * self.vector.x + other.normal.y * self.vector.y + other.normal.z * self.vector.z)
            x = self.point.x + self.vector.x * k
            y = self.point.y + self.vector.y * k
            z = self.point.z + self.vector.z * k
            return Point(x, y, z)
        if isinstance(other, Line):
            if abs((self.vector & other.vector) * Vector(self.point, other.point)) > eps or self | other:
                return None
            if self.vector.x == 0 and other.vector.x == 0:
                if self.vector.y != 0 and other.vector.y != 0:
                    y = (self.vector.z / self.vector.y * self.point.y - other.vector.z / other.vector.y * other.point.y
                         - self.point.z + other.point.z) / (
                                self.vector.z / self.vector.y - other.vector.z / other.vector.y)
                    return Point(self.point.x, y, self.z(y=y))
                else:
                    z = (self.vector.y / self.vector.z * self.point.z - other.vector.y / other.vector.z * other.point.z
                         - self.point.y + other.point.y) / (
                                    self.vector.y / self.vector.z - other.vector.y / other.vector.z)
                    return Point(self.point.x, self.y(z=z), z)
            if self.vector.y == 0 and other.vector.y == 0:
                if self.vector.x != 0 and other.vector.x != 0:
                    x = (self.vector.z / self.vector.x * self.point.x - other.vector.z / other.vector.x * other.point.x
                         - self.point.z + other.point.z) / (
                                self.vector.z / self.vector.x - other.vector.z / other.vector.x)
                    return Point(x, self.point.y, self.z(x=x))
                else:
                    z = (self.vector.x / self.vector.z * self.point.z - other.vector.x / other.vector.z * other.point.z
                         - self.point.x + other.point.x) / (
                                    self.vector.x / self.vector.z - other.vector.x / other.vector.z)
                    return Point(self.x(z=z), self.point.y, z)
            if self.vector.z == 0 and other.vector.z == 0:
                if self.vector.x != 0 and other.vector.x != 0:
                    x = (self.vector.y / self.vector.x * self.point.x - other.vector.y / other.vector.x * other.point.x
                         - self.point.y + other.point.y) / (
                                self.vector.y / self.vector.x - other.vector.y / other.vector.x)
                    return Point(x, self.y(x=x), self.point.z)
                else:
                    y = (self.vector.x / self.vector.y * self.point.y - other.vector.x / other.vector.y * other.point.y
                         - self.point.x + other.point.x) / (
                                self.vector.x / self.vector.y - other.vector.x / other.vector.y)
                    return Point(self.x(y=y), y, self.point.z)
            if self.vector.x == 0:
                return Point(self.point.x, other.y(x=self.point.x), other.z(x=self.point.x))
            if self.vector.y == 0:
                return Point(other.x(y=self.point.y), self.point.y, other.z(y=self.point.y))
            if self.vector.z == 0:
                return Point(other.x(z=self.point.z), other.y(z=self.point.z), self.point.z)
            if other.vector.x == 0:
                return Point(other.point.x, self.y(x=other.point.x), self.z(x=other.point.x))
            if other.vector.y == 0:
                return Point(self.x(y=other.point.y), other.point.y, self.z(y=other.point.y))
            if other.vector.z == 0:
                return Point(self.x(z=other.point.z), self.y(z=other.point.z), other.point.z)
            y = (self.vector.x / self.vector.y * self.point.y - other.vector.x / other.vector.y * other.point.y -
                 self.point.x + other.point.x) / (self.vector.x / self.vector.y - other.vector.x / other.vector.y)
            return Point(self.x(y=y), y, self.z(y=y))
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    def is_on(self, other):
        if isinstance(other, Plane):
            return self.point.is_on(other) and abs(angle(self, other)) < 1e-10
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    def x(self, y=None, z=None):
        if y is not None:
            return self.vector.x * (y - self.point.y) / self.vector.y + self.point.x
        if z is not None:
            return self.vector.x * (z - self.point.z) / self.vector.z + self.point.x
        raise ValueError('no operand')

    def y(self, x=None, z=None):
        if x is not None:
            return self.vector.y * (x - self.point.x) / self.vector.x + self.point.y
        if z is not None:
            return self.vector.y * (z - self.point.z) / self.vector.z + self.point.y
        raise ValueError('no operand')

    def z(self, x=None, y=None):
        if x is not None:
            return self.vector.z * (x - self.point.x) / self.vector.x + self.point.z
        if y is not None:
            return self.vector.z * (y - self.point.y) / self.vector.y + self.point.z
        raise ValueError('no operand')

    def projection_xy(self):
        if self.vector.x == 0 and self.vector.y == 0:
            return Point(self.point.x, self.point.y, 0)
        return Line(Point(self.point.x, self.point.y, 0), Vector(self.vector.x, self.vector.y, 0))

    def projection_xz(self):
        if self.vector.x == 0 and self.vector.z == 0:
            return Point(self.point.x, 0, self.point.z)
        return Line(Point(self.point.x, 0, self.point.z), Vector(self.vector.x, 0, self.vector.z))

    def cut_by_x(self, min_x, max_x):
        return Segment(Point(min_x, self.y(x=min_x), self.z(x=min_x)), Point(max_x, self.y(x=max_x), self.z(x=max_x)))

    def cut_by_y(self, min_y, max_y):
        return Segment(Point(self.x(y=min_y), min_y, self.z(y=min_y)), Point(self.x(y=max_y), max_y, self.z(y=max_y)))

    def cut_by_z(self, min_z, max_z):
        return Segment(Point(self.x(z=min_z), self.y(z=min_z), min_z), Point(self.x(z=max_z), self.y(z=max_z), max_z))


class Plane:
    def __init__(self, object1, object2=None, object3=None):
        if isinstance(object1, Line) and isinstance(object2, Line):
            self.point = object1.point
            self.vector1 = object1.vector
            self.vector2 = object2.vector
            self.normal = self.vector1 & self.vector2
            self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z
            return
        if isinstance(object1, Line) and isinstance(object2, Point):
            self.point = object1.point
            self.vector1 = object1.vector
            self.vector2 = Vector(self.point, object2)
            self.normal = self.vector1 & self.vector2
            self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z
            return
        if isinstance(object1, Point) and isinstance(object2, Line):
            self.point = object2.point
            self.vector1 = object2.vector
            self.vector2 = Vector(self.point, object1)
            self.normal = self.vector2 & self.vector1
            self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z
            return
        if isinstance(object1, Vector) and object2 is not None:
            self.normal = object1
            if isinstance(object2, Point):
                self.point = object2
                self.d = -object1.x * object2.x - object1.y * object2.y - object1.z * object2.z
            else:
                self.d = object2
                if self.normal * Vector(0, 0, 1) != 0:
                    self.point = Point(0, 0, -self.d / self.normal.z)
                elif self.normal * Vector(0, 1, 0) != 0:
                    self.point = Point(0, -self.d / self.normal.y, 0)
                elif self.normal * Vector(1, 0, 0) != 0:
                    self.point = Point(-self.d / self.normal.x, 0, 0)
            return
        if isinstance(object1, str):
            p = Plane.from_str(object1)
            self.normal = p.normal
            self.d = p.d
            if self.normal * Vector(0, 0, 1) != 0:
                self.point = Point(0, 0, -self.d / self.normal.z)
            elif self.normal * Vector(0, 1, 0) != 0:
                self.point = Point(0, -self.d / self.normal.y, 0)
            elif self.normal * Vector(1, 0, 0) != 0:
                self.point = Point(-self.d / self.normal.x, 0, 0)
            return
        self.point = object1
        if isinstance(object2, Point):
            self.vector1 = Vector(object1, object2)
        else:
            self.vector1 = object2
        if isinstance(object3, Point):
            self.vector2 = Vector(object1, object3)
        else:
            self.vector2 = object3
        self.normal = self.vector1 & self.vector2
        self.d = -self.point.x * self.normal.x - self.point.y * self.normal.y - self.point.z * self.normal.z

    def __str__(self):
        return f'{self.normal.x}x + {self.normal.y}y + {self.normal.z}z + {self.d} = 0'

    def __or__(self, other):
        if isinstance(other, Plane):
            return self.normal | other.normal
        if isinstance(other, Line):
            return abs(angle(self, other)) < 1e-10
        raise ValueError(f'unsupported operand type(s) for |:  "Plane" and "{other.__class__.__name__}"')

    def intersection(self, other):
        if isinstance(other, Plane):
            # self.normal.x * x + self.normal.y * y + self.d = 0
            # other.normal.x * x + other.normal.y * y + other.d = 0
            # x = -(self.normal.y * y + self.d) / self.normal.x
            # other.normal.x * -(self.normal.y * y + self.d) / self.normal.x + other.normal.y * y + other.d = 0
            if self | other:
                return None
            try:
                y = (-other.d + other.normal.x * self.d / self.normal.x) / (other.normal.y - other.normal.x *
                                                                            self.normal.y / self.normal.x)
                x = -(self.normal.y * y + self.d) / self.normal.x
                return Line(Point(x, y, 0), self.normal & other.normal)
            except Exception:
                try:
                    z = (-other.d + other.normal.y * self.d / self.normal.y) / (other.normal.z - other.normal.y *
                                                                                self.normal.z / self.normal.y)
                    y = -(self.normal.z * z + self.d) / self.normal.y
                    return Line(Point(0, y, z), self.normal & other.normal)
                except Exception:
                    x = (-other.d + other.normal.z * self.d / self.normal.z) / (other.normal.x - other.normal.z *
                                                                                self.normal.x / self.normal.z)
                    z = -(self.normal.x * x + self.d) / self.normal.z
                    return Line(Point(x, 0, z), self.normal & other.normal)
        if isinstance(other, Line):
            k = -(self.normal.x * other.point.x + self.normal.y * other.point.y + self.normal.z * other.point.z +
                  self.d) / \
                (self.normal.x * other.vector.x + self.normal.y * other.vector.y + self.normal.z * other.vector.z)
            x = other.point.x + other.vector.x * k
            y = other.point.y + other.vector.y * k
            z = other.point.z + other.vector.z * k
            return Point(x, y, z)
        raise ValueError(f'unsupported operand type: "{other.__class__.__name__}"')

    @staticmethod
    def from_str(s, function=int):
        lst = s.split()
        for i in range(len(lst) - 1):
            lst[i] = lst[i].strip()
            if lst[i] == '-':
                lst[i] = ''
                lst[i + 1] = '-' + lst[i + 1].strip()
            elif lst[i] == '+':
                lst[i] = ''
        while '' in lst:
            lst.remove('')
        if lst[-2] != '=' or lst[-1] != '0':
            raise ValueError('invalid equation')
        a, b, c, d = 0, 0, 0, 0
        for i in range(len(lst) - 2):
            if 'x' in lst[i]:
                lst[i] = lst[i].replace('x', '')
                if lst[i] == '-' or lst[i] == '':
                    lst[i] += '1'
                a = function(lst[i])
            elif 'y' in lst[i]:
                lst[i] = lst[i].replace('y', '')
                if lst[i] == '-' or lst[i] == '':
                    lst[i] += '1'
                b = function(lst[i])
            elif 'z' in lst[i]:
                lst[i] = lst[i].replace('z', '')
                if lst[i] == '-' or lst[i] == '':
                    lst[i] += '1'
                c = function(lst[i])
            elif lst[i] != '+' and lst[i] != '-':
                d = function(lst[i])
            if a == 0 and b == 0 and c == 0:
                raise ValueError('invalid equation')
        return Plane(Vector(a, b, c), d)

    def x(self, y, z):
        return (-self.normal.y * y - self.normal.z * z - self.d) / self.normal.x

    def y(self, x, z):
        return (-self.normal.x * x - self.normal.z * z - self.d) / self.normal.y

    def z(self, x, y):
        return (-self.normal.x * x - self.normal.y * y - self.d) / self.normal.z

    def trace_xy(self):
        return self.intersection(Plane(Vector(0, 0, 1), Point(0, 0, 0)))

    def trace_xz(self):
        return self.intersection(Plane(Vector(0, 1, 0), Point(0, 0, 0)))

    def trace_yz(self):
        return self.intersection(Plane(Vector(1, 0, 0), Point(0, 0, 0)))

    def projection_xy(self):
        return self.trace_xy()

    def projection_xz(self):
        return self.trace_xz()

    def horizontal(self, point):
        return Line(point, self.normal & Vector(0, 0, 1))

    def frontal(self, point):
        return Line(point, self.normal & Vector(0, 1, 0))


def distance(object1, object2):
    """
    Вычисляет расстояние между двумя объектами
    :param object1: точка, прямая или плоскость
    :param object2: точка, прямая или плоскость
    :return: float
    """
    if isinstance(object1, Point) and isinstance(object2, Point):
        return abs(Vector(object1, object2))
    if isinstance(object1, Point) and isinstance(object2, Plane):
        return abs(object1.x * object2.normal.x + object1.y * object2.normal.y + object1.z * object2.normal.z +
                   object2.d) / abs(object2.normal)
    if isinstance(object1, Plane) and isinstance(object2, Point):
        return abs(object2.x * object1.normal.x + object2.y * object1.normal.y + object2.z * object1.normal.z +
                   object1.d) / abs(object1.normal)
    if isinstance(object1, Point) and isinstance(object2, Line):
        return (((object1.y - object2.point.y) * object2.vector.z - (
                    object1.z - object2.point.z) * object2.vector.y) ** 2
                + ((object1.x - object2.point.x) * object2.vector.z - (object1.z - object2.point.z) *
                   object2.vector.x) ** 2
                + ((object1.x - object2.point.x) * object2.vector.y - (object1.y - object2.point.y) *
                   object2.vector.x) ** 2) \
               ** 0.5 / abs(object2.vector)
    if isinstance(object1, Line) and isinstance(object2, Point):
        return (((object2.y - object1.point.y) * object1.vector.z - (object2.z - object1.point.z) * object1.vector.y) +
                ((object2.x - object1.point.x) * object1.vector.z - (object2.z - object1.point.z) * object1.vector.x) +
                ((object2.x - object1.point.x) * object1.vector.y - (object2.y - object1.point.y) * object1.vector.x)) \
               ** 0.5 / abs(object1.vector)
    if isinstance(object1, Line) and isinstance(object2, Line):
        return abs(Matrix([[object2.point.x - object1.point.x, object2.point.y - object1.point.y,
                            object2.point.z - object1.point.z],
                          [object1.vector.x, object1.vector.y, object1.vector.z],
                          [object2.vector.x, object2.vector.y, object2.vector.z]]).determinant()) / (
                       (object2.vector.y * object1.vector.z - object2.vector.z * object1.vector.y) ** 2 +
                       (object2.vector.x * object1.vector.z - object2.vector.z * object1.vector.x) ** 2 +
                       (object2.vector.x * object1.vector.y - object2.vector.y * object1.vector.x) ** 2) ** 0.5
    raise ValueError(f'unsupported operand types:  "{object1.__class__.__name__}" and "{object2.__class__.__name__}"')


def angle(object1, object2):
    """
    Вычисляет угол между двумя объектами (в радианах)
    :param object1: вектор, прямая или плоскость
    :param object2: вектор, прямая или плоскость
    :return: float
    """
    flag = False
    if isinstance(object1, Vector):
        vector1 = object1
    elif isinstance(object1, Line):
        vector1 = object1.vector
    elif isinstance(object1, Plane):
        vector1 = object1.normal
        flag = True
    else:
        raise ValueError
    if isinstance(object2, Vector):
        vector2 = object2
    elif isinstance(object2, Line):
        vector2 = object2.vector
    elif isinstance(object2, Plane):
        vector2 = object2.normal
        flag = True
    else:
        raise ValueError(f'unsupported operand types:  "{object1.__class__.__name__}"'
                         f'and "{object2.__class__.__name__}"')
    if flag:
        return math.asin(vector1 * vector2 / (abs(vector1) * abs(vector2)))
    return math.acos(vector1 * vector2 / (abs(vector1) * abs(vector2)))


class Segment:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return 'Segment({0}, {1})'.format(self.p1, self.p2)

    def projection_xy(self):
        if self.p1.x == self.p2.x and self.p1.y == self.p2.y:
            return Point(self.p1.x, self.p1.y, 0)
        return Segment(self.p1.projection_xy(), self.p2.projection_xy())

    def projection_xz(self):
        if self.p1.x == self.p2.x and self.p1.z == self.p2.z:
            return Point(self.p1.x, 0, self.p1.y)
        return Segment(self.p1.projection_xz(), self.p2.projection_xz())


class Circle:
    def __init__(self, center, radius, normal=Vector(0, 0, 1)):
        self.center = center
        self.radius = radius
        self.normal = normal
        self.plane = Plane(self.normal, self.center)

    def __str__(self):
        if self.normal | Vector(0, 0, 1):
            return f'Circle: {self.center}, R = {self.radius}'
        return f'Circle: {self.center}, R = {self.radius}, normal {self.normal}'

    def intersection(self, other):
        if isinstance(other, Line):
            if other.is_on(Plane(self.normal, self.center)):
                if abs((d := distance(self.center, other)) - self.radius) < 1e-12:
                    return Line(self.center, self.normal & other.vector).intersection(other)
                if d > self.radius:
                    return None
                s = math.sqrt(self.radius ** 2 - d ** 2)
                v1 = other.vector * (s / abs(other.vector))
                v2 = self.normal & other.vector * (d / abs(self.normal & other.vector))
                return self.center + v1 + v2, self.center + -v1 + v2
        if isinstance(other, Plane):
            return self.intersection(self.plane.intersection(other))
        if isinstance(other, Circle):
            if self.normal | other.normal and other.center.is_on(self.plane):
                dist = distance(self.center, other.center)
                if self.radius + other.radius < dist or \
                        min(self.radius, other.radius) + dist < max(self.radius, other.radius):
                    return
                x = (self.radius ** 2 - other.radius ** 2 + dist ** 2) / 2 / dist
                if x > self.radius:
                    return None
                r = (self.radius ** 2 - x ** 2) ** 0.5
                p = self.center + Vector(self.center, other.center) * (x / dist)
                v = Vector(self.center, other.center) & self.normal * \
                    (r / abs(Vector(self.center, other.center) & self.normal))
                return p + v, p + -v

    def area(self):
        return math.pi * self.radius ** 2

    def projection_xy(self):
        if self.normal.x == 0 and self.normal.y == 0:
            return Circle(self.center.projection_xy(), self.radius, Vector(0, 0, 1))
        if self.normal * Vector(0, 0, 1) == 0:
            point1, point2 = self.intersection(Line(self.center, self.normal & Vector(0, 0, 1)))
            return Segment(point1, point2).projection_xy()

    def projection_xz(self):
        if self.normal.x == 0 and self.normal.z == 0:
            return Circle(self.center.projection_xz(), self.radius, Vector(0, 1, 0))
        if self.normal * Vector(0, 1, 0) == 0:
            point1, point2 = self.intersection(Line(self.center, self.normal & Vector(0, 1, 0)))
            return Segment(point1, point2).projection_xz()


class Arc:
    def __init__(self, p1, p2, center, big_arc=False):
        if abs((r := distance(p1, center)) - distance(p2, center)) > 1e-10:
            raise ValueError
        self.center = center
        self.radius = r
        self.plane = Plane(p1, p2, center)
        self.normal = self.plane.normal
        self.vector_cos = Vector(center, p1)
        self.vector_sin = (self.vector_cos & self.normal) * (self.radius / abs(self.vector_cos & self.normal))
        self.angle = -angle(self.vector_cos, Vector(center, p2))
        if big_arc:
            self.angle = 2 * math.pi + self.angle


class Ellipse:
    def __init__(self, obj1, obj2, obj3):
        self.center = obj1
        self.point_a1 = obj2 if abs(Vector(obj1, obj2)) > abs(Vector(obj1, obj3)) else obj3
        self.point_a2 = self.center + -Vector(self.center, self.point_a1)
        self.point_b1 = obj3 if abs(Vector(obj1, obj2)) > abs(Vector(obj1, obj3)) else obj2
        self.point_b2 = self.center + -Vector(self.center, self.point_b1)
        self.a = abs(Vector(self.center, self.point_a1))
        self.b = abs(Vector(self.center, self.point_b1))
        self.c = (self.a ** 2 - self.b**2) ** 0.5
        self.f1 = self.center + Vector(self.center, self.point_a1) * (self.c / abs(Vector(self.center, self.point_a1)))
        self.f2 = self.center + Vector(self.center, self.point_a1) * -(self.c / abs(Vector(self.center, self.point_a1)))
        self.plane = Plane(self.center, self.point_a1, self.point_b1)


class Sphere:
    def __init__(self, center, radius):
        if not isinstance(center, Point):
            raise ValueError('Center is not a point')
        self.center = center
        self.radius = radius

    def __str__(self):
        return f'Sphere: {self.center}, R = {self.radius}'

    def intersection(self, other):
        if isinstance(other, Line):
            if distance(self.center, other) > self.radius:
                return None
            if distance(self.center, other) == self.radius:
                p = Plane(other, self.center)
                return Line(self.center, p.normal & other.vector).intersection(other)
            s = math.sqrt(self.radius ** 2 - distance(self.center, other) ** 2)
            v = other.vector * s / abs(other.vector)
            return other.point + v, other.point + -v
        if isinstance(other, Plane):
            if distance(self.center, other) > self.radius:
                return None
            if distance(self.center, other) == self.radius:
                return Line(self.center, other.normal).intersection(other)
            return Circle(Line(self.center, other.normal).intersection(other),
                          math.sqrt(self.radius ** 2 - distance(self.center, other)), other.normal)
        if isinstance(other, Sphere):
            dist = abs(Vector(self.center, other.center))
            if self.radius + other.radius < dist or \
                    min(self.radius, other.radius) + dist < max(self.radius, other.radius):
                return
            x = (self.radius ** 2 - other.radius ** 2 + dist ** 2) / 2 / dist
            if x > self.radius:
                return None
            r = (self.radius ** 2 - x ** 2) ** 0.5
            return Circle(self.center + Vector(self.center, other.center) * (x / dist), r,
                          Vector(self.center, other.center))


class Cylinder:
    def __init__(self, point, point2_or_height, radius, vector=Vector(0, 0, 1)):
        self.center1 = point
        self.radius = radius
        if isinstance(point2_or_height, Point):
            self.center2 = point2_or_height
            self.vector = Vector(self.center1, self.center2)
            self.height = abs(self.vector)
        else:
            self.height = point2_or_height
            self.vector = vector
            self.center2 = self.center1 + vector * self.height / abs(vector)

    def intersection(self, other):
        if isinstance(other, Plane) and other.normal | self.vector:
            return Circle(Line(self.center1, self.center2).intersection(other), self.radius, self.vector)
        if isinstance(other, Cone) or isinstance(other, Cylinder):
            if self.vector | other.vector:
                p1, p2 = self.center1, self.center2
                if self.vector * other.vector > 0:
                    if distance(self.center1, other.center2) < distance(p1, p2):
                        p1, p2 = self.center1, other.center2
                    if distance(other.center1, self.center2) < distance(p1, p2):
                        p1, p2 = other.center1, self.center2
                    if distance(other.center1, other.center2) < distance(p1, p2):
                        p1, p2 = other.center1, other.center2
                else:
                    if distance(self.center1, other.center1) < distance(p1, p2):
                        p1, p2 = self.center1, other.center1
                    if distance(other.center2, self.center2) < distance(p1, p2):
                        p1, p2 = other.center2, self.center2
                    if distance(other.center2, other.center1) < distance(p1, p2):
                        p1, p2 = other.center2, other.center1
                v = Vector(p1, p2) * 0.01
                if isinstance(other, Cylinder):
                    return Segment(self.intersection(Plane(v, p1)).intersection(other.intersection(Plane(v, p1)))[0],
                                   self.intersection(Plane(v, p2)).intersection(other.intersection(Plane(v, p2)))[0]), \
                           Segment(self.intersection(Plane(v, p2)).intersection(other.intersection(Plane(v, p2)))[0],
                                   self.intersection(Plane(v, p2)).intersection(other.intersection(Plane(v, p2)))[1]), \
                           Segment(self.intersection(Plane(v, p2)).intersection(other.intersection(Plane(v, p2)))[1],
                                   self.intersection(Plane(v, p1)).intersection(other.intersection(Plane(v, p1)))[1]), \
                           Segment(self.intersection(Plane(v, p1)).intersection(other.intersection(Plane(v, p1)))[1],
                                   self.intersection(Plane(v, p1)).intersection(other.intersection(Plane(v, p1)))[0])
                lst1, lst2 = [], []
                for i in range(101):
                    try:
                        p = self.intersection(Plane(v, p1 + v * i)).intersection(other.intersection(Plane(v, p1 + v * i)))
                    except Exception:
                        continue
                    if isinstance(p, tuple):
                        lst1.append(p[0])
                        lst2.append(p[1])
                    elif p is not None:
                        lst1.append(p)
                return Spline3D(*lst1, *reversed(lst2))


class Cone:
    def __init__(self, point, point2_or_height, radius1, radius2=0, vector=Vector(0, 0, 1)):
        self.center1 = point
        self.radius1 = radius1
        self.radius2 = radius2
        if isinstance(point2_or_height, Point):
            self.center2 = point2_or_height
            self.vector = Vector(self.center1, self.center2)
            self.height = abs(self.vector)
        else:
            self.height = point2_or_height
            self.vector = vector
            self.center2 = self.center1 + vector * self.height / abs(vector)

    def intersection(self, other):
        if isinstance(other, Plane) and other.normal | self.vector:
            p = Line(self.center1, self.center2).intersection(other)
            return Circle(p, self.radius1 - (self.radius1 - self.radius2) * distance(self.center1, p) / distance(
                self.center1, self.center2), self.vector)
        if isinstance(other, Cylinder) or isinstance(other, Cone):
            if self.vector | other.vector:
                p1, p2 = self.center1, self.center2
                if self.vector * other.vector > 0:
                    if distance(self.center1, other.center2) < distance(p1, p2):
                        p1, p2 = self.center1, other.center2
                    if distance(other.center1, self.center2) < distance(p1, p2):
                        p1, p2 = other.center1, self.center2
                    if distance(other.center1, other.center2) < distance(p1, p2):
                        p1, p2 = other.center1, other.center2
                else:
                    if distance(self.center1, other.center1) < distance(p1, p2):
                        p1, p2 = self.center1, other.center1
                    if distance(other.center2, self.center2) < distance(p1, p2):
                        p1, p2 = other.center2, self.center2
                    if distance(other.center2, other.center1) < distance(p1, p2):
                        p1, p2 = other.center2, other.center1
                v = Vector(p1, p2) * 0.01
                lst1, lst2 = [], []
                for i in range(101):
                    p = self.intersection(Plane(v, p1 + v * i)).intersection(other.intersection(Plane(v, p1 + v * i)))
                    if isinstance(p, tuple):
                        lst1.append(p[0])
                        lst2.append(p[1])
                    elif p is not None:
                        lst1.append(p)
                return Spline3D(*lst1, *reversed(lst2))


class Spline2:
    def __init__(self, plane, *points):
        self.plane = plane
        self.points = list(points)
        self.horizontal = Line(Point(plane.x(0, 0), 0, 0), plane.normal & Vector(0, 0, 1))
        self.vector_2d = self.horizontal.vector & Vector(0, 0, 1)
        self.vector_3d = self.horizontal.vector & plane.normal
        self.vector_2d *= 1 / abs(self.vector_2d)
        self.vector_3d *= 1 / abs(self.vector_3d)
        points = []
        for point in self.points:
            points.append(self.convert_3d_point_to_2d(point))

        self.array = [(points[0],)]
        i = 1
        mtrx = Matrix([[points[i - 1].x ** 2, points[i - 1].x, 1],
                       [points[i].x ** 2, points[i].x, 1],
                       [points[i + 1].x ** 2, points[i + 1].x, 1]]) ** -1 * \
               Matrix([[points[i - 1].y], [points[i].y], [points[i + 1].y]])
        a, b, c, d = 0, mtrx.mtrx[0][0], mtrx.mtrx[1][0], mtrx.mtrx[2][0]
        der = 3 * a * points[i].x ** 2 + 2 * b * points[i].x + c
        self.array.append((points[i], a, b, c, d))

        for i in range(2, len(points) - 1):
            mtrx = Matrix([[points[i - 1].x**3, points[i - 1].x**2, points[i - 1].x, 1],
                           [points[i].x**3, points[i].x**2, points[i].x, 1],
                           [points[i + 1].x ** 3, points[i + 1].x ** 2, points[i + 1].x, 1],
                           [3 * points[i - 1].x ** 2, 2 * points[i - 1].x, 1, 0]]) ** -1 * \
                   Matrix([[points[i - 1].y], [points[i].y], [points[i + 1].y], [der]])
            a, b, c, d = mtrx.mtrx[0][0], mtrx.mtrx[1][0], mtrx.mtrx[2][0], mtrx.mtrx[3][0]
            der = 3 * a * points[i].x ** 2 + 2 * b * points[i].x + c

            self.array.append((self.points[i], a, b, c, d))
        self.array.append((self.points[-1], a, b, c, d))

    def convert_3d_point_to_2d(self, point):
        d = distance(point, self.horizontal)
        return (point + self.vector_3d * -d) + self.vector_2d * d

    def convert_2d_point_to_3d(self, point):
        d = distance(point, self.horizontal)
        return (point + self.vector_2d * -d) + self.vector_3d * d


class Spline:
    def __init__(self, plane, *points):
        self.plane = plane
        p1, p2, p3 = points[0], points[1], points[2]
        l1 = Line(p1 + Vector(p1, p2) * 0.5, Vector(p1, p2) & self.plane.normal)
        l2 = Line(p2 + Vector(p2, p3) * 0.5, Vector(p2, p3) & self.plane.normal)
        c = l1.intersection(l2, 1e20)
        self.array = [(points[0],), (points[1], Arc(p1, p2, c)), (points[2], Arc(p2, p3, c))]
        for i in range(1, len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            l1 = Line(p1 + Vector(p1, p2) * 0.5, Vector(p1, p2) & self.plane.normal)
            l2 = Line(c, p1)
            c = l1.intersection(l2, 1e20)

            self.array.append((p2, Arc(p1, p2, c)))


class Spline3D:
    def __init__(self, *points):
        p1, p2, p3 = points[0], points[1], points[2]
        pl = Plane(p1, p2, p3)
        l1 = Line(p1 + Vector(p1, p2) * 0.5, Vector(p1, p2) & pl.normal)
        l2 = Line(p2 + Vector(p2, p3) * 0.5, Vector(p2, p3) & pl.normal)
        c = l1.intersection(l2, 1e20)
        pl3 = Plane(p2, Vector(c, p2), pl.normal)
        v = pl.normal & Vector(c, p2)
        self.array = [(points[0],), (points[1], Arc(p1, p2, c))]
        for i in range(2, len(points)):
            p1, p2 = points[i - 1], points[i]
            if distance(p1, p2) == 0:
                continue
            pl1 = Plane(Vector(p1, p2), p1 + Vector(p1, p2) * 0.5)
            pl2 = Plane(p1, p2, v)
            c = pl1.intersection(pl2).intersection(pl3)
            pl3 = Plane(p2, Vector(c, p2), Plane(p1, p2, c).normal)
            v = pl.normal & Vector(c, p2)

            self.array.append((p2, Arc(p1, p2, c)))
