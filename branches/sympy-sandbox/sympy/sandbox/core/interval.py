"""
Interval arithmetic with correct rounding.

"""

from utils import memoizer_Interval_new
from basic import sympify
from number import Number
from numerics_float import *



class _Rounding:
    def begin(self): self.stored = Float.getmode()
    def end(self): Float.setmode(self.stored)
    def down(self): Float.setmode(ROUND_FLOOR)
    def up(self): Float.setmode(ROUND_CEILING)

rounding = _Rounding()

makeinterval = lambda a, b: tuple.__new__(Interval, (a,b))

class Interval(Number, tuple):
    """
    An Interval represents the set of all real numbers between two
    endpoints a and b. If the interval is closed (which is what is
    implemented here), the endpoints are themselves considered part
    of the interval. That is, the interval between a and b, denoted
    by [a, b], is the set of points x satisfying a <= x <= b.
    """

    @memoizer_Interval_new
    def __new__(cls, a, b=None):
        """
        Interval(a) creates an exact interval (width 0)
        Interval(a, b) creates the interval [a, b]
        """
        a = sympify(a)
        if b is None:
            if isinstance(a, Interval):
                return a
            b = a
        else:
            b = sympify(b)
            assert a <= b, "endpoints must be properly ordered"
        return tuple.__new__(Interval, (a,b))

    make = staticmethod(makeinterval)

    @property
    def a(self):
        return self[0]
    @property
    def b(self):
        return self[1]

    def __repr__(self):
        return "Interval(%r, %r)" % (self.a, self.b)

    def __str__(self):
        return '[%s, %s]' % (self.a, self.b)

    def compare(self, other):
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        return tuple.__cmp__(self, other)

    def __hash__(self):
        return tuple.__hash__(self)

    def __eq__(self, other):
        """Two intervals are considered equal if all endpoints are equal"""
        other = sympify(other)
        if other.is_Real:
            other = Interval(other)
        if self is other: return True
        if other.is_Interval:
            return tuple.__eq__(self, other)
        return super(Number, self).__eq__(other)

    def __contains__(self, x):
        """Return True if x is contained in the interval, otherwise False."""
        return (self.a <= x) and (x <= self.b)

    def __neg__(self):
        return Interval(-self.b, -self.a)

    def __add__(l, r):
        r = sympify(r)
        if r.is_Real:
            r = r.as_Interval
        if r.is_Interval:
            rounding.begin()
            rounding.down()
            a = l.a + r.a
            rounding.up()
            b = l.b + r.b
            rounding.end()
            return Interval(a, b)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            if other.is_Real:
                other = other.as_Interval
            if other.is_Interval:
                return other + self
            return Basic.Add(other, self)
        return sympify(other) + self

    def __sub__(l, r):
        r = sympify(r)
        if r.is_Real:
            r = r.as_Interval
        if r.is_Interval:
            r = -r
            rounding.begin()
            rounding.down()
            a = l.a + r.a
            rounding.up()
            b = l.b + r.b
            rounding.end()
            return Interval(a, b)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Basic):
            if other.is_Real:
                other = other.as_Interval
            if other.is_Interval:
                return other - self
            return Basic.Add(other, -self)
        return sympify(other) - self

    def __mul__(l, r):
        r = sympify(r)
        if r.is_Real:
            r = r.as_Interval
        if r.is_Interval:
            rounding.begin()
            rounding.down()
            xd, yd, zd, wd = l.a*r.a, l.a*r.b, l.b*r.a, l.b*r.b
            a = min(xd,yd,zd,wd)
            rounding.up()
            xu, yu, zu, wu = l.a*r.a, l.a*r.b, l.b*r.a, l.b*r.b
            b = max(xu,yu,zu,wu)
            rounding.end()
            return Interval(a,b)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Basic):
            if other.is_Real:
                other = other.as_Interval
            if other.is_Interval:
                return other * self
            return Basic.Mul(other, self)
        return sympify(other) * self

    def __div__(l, r):
        r = sympify(r)
        if r.is_Real:
            r = r.as_Interval
        if r.is_Interval:
            if 0 in r:
                raise ZeroDivisionError, "cannot divide by interval containing 0"
            rounding.begin()
            rounding.down()
            xd, yd, zd, wd = l.a/r.a, l.a/r.b, l.b/r.a, l.b/r.b
            a = min(xd,yd,zd,wd)
            rounding.up()
            xu, yu, zu, wu = l.a/r.a, l.a/r.b, l.b/r.a, l.b/r.b
            b = max(xu,yu,zu,wu)
            rounding.end()
            return Interval(a,b)
        return NotImplemented

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            if other.is_Real:
                other = other.as_Interval
            if other.is_Interval:
                return other / self
            return Basic.Mul(other, 1/self)
        return sympify(other) / self

    __truediv__ = __div__
    __rtruediv__ = __rdiv__
    __floordiv__ = __div__
    __rfloordiv__ = __rdiv__

    def mid(self):
        return (self.a+self.b)/2

    @staticmethod
    def from_absolute_error(x, error=0):
        return Interval(x-error, x+error)

    @staticmethod
    def from_relative_error(x, error=0):
        # XXX: round
        return Interval(x*(1-error), x*(1+error))

    def absolute_error(self):
        rounding.begin()
        rounding.up()
        p = abs((self.b-self.a)/2)
        rounding.end()
        return p

    def relative_error(self):
        return self.absolute_error() / self.mid()

