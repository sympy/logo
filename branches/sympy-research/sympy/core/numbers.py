
from basic import Basic, Atom, Singleton
from methods import RelMeths, ArithMeths

def gcd(a, b):
    '''Returns the Greatest Common Divisor,
    implementing Euclid\'s algorithm.'''
    while a:
        a, b = b%a, a
    return b


class Number(Atom, RelMeths, ArithMeths):
    """Represents any kind of number in sympy.


    Floating point numbers are represented by the Real class.
    Integer numbers (of any size), together with rational numbers (again, there
    is no limit on their size) are represented by the Rational class. 

    If you want to represent for example 1+sqrt(2), then you need to do:

    Rational(1) + sqrt(Rational(2))
    """
    is_commutative = True

class Rational(Number):
    """Represents integers and rational numbers (p/q) of any size.

    Thanks to support of long ints in Python. 

    Usage:

    Rational(3)      ... 3
    Rational(1,2)    ... 1/2
    """
    is_real = True
    is_integer = False

    def __new__(cls, p, q = None):
        if q is None:
            return Integer(p)
        if isinstance(p, (int, long)) and isinstance(q, (int, long)):
            assert q!=0
            n = gcd(abs(p), q)
            if n>1:
                p /= n
                q /= n
            if q==1:
                return Integer(p)
            obj = Basic.__new__(cls)
            obj.p = p
            obj.q = q
            return obj
        raise TypeError("Expected integers but got %r, %r" % (p,q))

    def _hashable_content(self):
        return (self.p, self.q)

    def tostr(self, level=0):
        if self.precedence<=level:
            return '(%s/%s)' % (self.p, self.q)
        return '%s/%s' % (self.p, self.q)

    def torepr(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.p, self.q)

    @property
    def precedence(self):
        if self.p < 0:
            return 40 # same as Add
        return 50 # same as Mul

    def _calc_positive(self): return self.p > 0
    def _calc_nonpositive(self): return self.p <= 0
    def _calc_negative(self): return self.p < 0
    def _calc_nonnegative(self): return self.p >= 0

    def __neg__(self): return Rational(-self.p, self.q)

    def __mul__(self, other):
        other = Basic.sympify(other)
        if isinstance(other, Rational):
            return Rational(self.p * other.p, self.q * other.q)
        return Number.__mul__(self, other)

    def __add__(self, other):
        other = Basic.sympify(other)
        if isinstance(other, Rational):
            return Rational(self.p * other.q + self.q * other.p, self.q * other.q)
        return Number.__add__(self, other)

    def _eval_power(b, e):
        if isinstance(e, Number):
            if e.is_negative:
                if isinstance(-e, One):
                    # (3/4)**-1 -> 4/3
                    return Rational(b.q, b.p)
                # (3/4)**-2 -> (4/3)**2
                return Rational(b.q, b.p) ** (-e)
            if isinstance(e, Integer):
                # (4/3)**2 -> 4**2 / 3**2
                return Rational(b.p ** e.p, b.q ** e.p)
            if isinstance(e, Rational):
                # (4/3)**(5/6) -> 4**(5/6) * 3**(-5/6)
                return Integer(b.p) ** e * Integer(b.q) ** (-e)
        return

class Integer(Rational):

    q = 1
    is_integer = True

    def __new__(cls, i):
        if isinstance(i, (int, long)):
            if i==0: return Zero()
            if i==1: return One()
            obj = Basic.__new__(cls)
            obj.p = i
            return obj
        if isinstance(i, Integer):
            return i
        raise TypeError("Expected integer but got %r" % (i))

    @property
    def precedence(self):
        if self.p < 0:
            return 40 # same as Add
        return Atom.precedence

    def tostr(self, level=0):
        if self.precedence<=level:
            return '(%s)' % (self.p)
        return str(self.p)

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, self.p)

class Zero(Singleton, Integer):

    p = 0
    q = 1

class One(Singleton, Integer):

    p = 1
    q = 1

