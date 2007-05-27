
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
            if q==0:
                if p==0: return NaN()
                if p<0: return NegativeInfinity()
                return Infinity()
            n = gcd(abs(p), q)
            if n>1:
                p /= n
                q /= n
            if q==1:
                return Integer(p)
            if p==1 and q==2:
                return Half()
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
            if isinstance(e, NaN):
                return NaN()
            if e.is_negative:
                # (3/4)**-2 -> (4/3)**2
                return Rational(b.q, b.p) ** (-e)
            if isinstance(e, Infinity):
                if b.p > b.q:
                    # (3/2)**oo -> oo
                    return Infinity()
                if b.p < -b.q:
                    # (-3/2)**oo -> oo + I*oo
                    return Infinity() + Infinity() * ImaginaryUnit()
                return Zero()
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
            if i==-1: return NegativeOne()
            obj = Basic.__new__(cls)
            obj.p = i
            return obj
        if isinstance(i, Integer):
            return i
        raise TypeError("Expected integer but got %r" % (i))

    @property
    def is_odd(self):
        return bool(self.p % 2)

    @property
    def is_even(self):
        return not (self.p % 2)

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

    def _eval_power(b, e):
        return b

class NegativeOne(Singleton, Integer):

    p = -1
    q = 1

    def _eval_power(b, e):
        if isinstance(e, Number):
            if isinstance(e, NaN):
                return NaN()
            if isinstance(e, (Infinity, NegativeInfinity)):
                return NaN()
            if isinstance(e, Integer):
                if e.is_odd: return NegativeOne()
                return One()
            if isinstance(e, Half):
                return ImaginaryUnit()
            if isinstance(e, Rational):
                if e.q == 2:
                    return ImaginaryUnit() ** Integer(e.p)
                q = int(e)
                if q:
                    q = Integer(q)
                    return b ** q * b ** (e - q)
        return

class Half(Singleton, Rational):

    p = 1
    q = 2

class Infinity(Singleton, Rational):

    p = 1
    q = 0

    is_commutative = True
    is_real = True
    is_positive = is_nonnegative = True
    is_nonpositive = is_negative = False

    def tostr(self, level=0):
        return 'oo'


class NegativeInfinity(Singleton, Rational):

    p = -1
    q = 0

    is_commutative = True
    is_real = True
    is_positive = is_nonnegative = False
    is_nonpositive = is_negative = True

    precedence = 40 # same as Add

    def tostr(self, level=0):
        return '-oo'


class NaN(Singleton, Rational):

    p = 0
    q = 0

    is_commutative = True
    is_real = False
    is_positive = is_nonnegative = False
    is_nonpositive = is_negative = False

    def tostr(self, level=0):
        return 'nan'


class NumberSymbol(Singleton, Atom, RelMeths, ArithMeths):

    is_commutative = True


class Exp1(NumberSymbol):

    is_real = True
    is_positive = is_nonnegative = True
    is_nonpositive = is_negative = False

    def tostr(self, level=0):
        return 'E'


class Pi(NumberSymbol):
    is_real = True
    is_positive = is_nonnegative = True
    is_nonpositive = is_negative = False    

    def tostr(self, level=0):
        return 'Pi'

class ImaginaryUnit(Singleton, Atom, RelMeths, ArithMeths):

    is_commutative = True
    is_real = False
    is_positive = is_nonnegative = False
    is_nonpositive = is_negative = False

    def tostr(self, level=0):
        return 'I'

    def _eval_power(b, e):
        """
        b is I = sqrt(-1)
        e is symbolic object but not equal to 0, 1

        I ** r -> (-1)**(r/2) -> exp(r/2 * Pi * I) -> sin(Pi*r/2) + cos(Pi*r/2) * I, r is decimal
        I ** 0 mod 4 -> 1
        I ** 1 mod 4 -> I
        I ** 2 mod 4 -> -1
        I ** 3 mod 4 -> -I
        """


        if isinstance(e, Number):
            #if isinstance(e, Decimal):
            #    a = decimal_math.pi() * exponent.num / 2
            #    return Decimal(decimal_math.sin(a) + decimal_math.cos(a) * ImaginaryUnit())
            if isinstance(e, Integer):
                e = e.p % 4
                if e==0: return One()
                if e==1: return ImaginaryUnit()
                if e==2: return -One()
                return -ImaginaryUnit()
            return -One() ** (e/2)
        return

    def as_base_exp(self):
        return -One(),Rational(1,2)

Basic.singleton['E'] = Exp1
Basic.singleton['Pi'] = Pi
Basic.singleton['I'] = ImaginaryUnit
Basic.singleton['oo'] = Infinity
