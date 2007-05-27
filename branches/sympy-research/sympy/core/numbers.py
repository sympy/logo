
import math
import decimal
import decimal_math
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

    def __new__(cls, *obj):
        if len(obj)==1: obj=obj[0]
        if isinstance(obj, (int, long)):
            return Integer(obj)
        if isinstance(obj,tuple) and len(obj)==2:
            return Rational(*obj)
        if isinstance(obj, (str,float,decimal.Decimal)):
            return Real(obj)
        if isinstance(obj, Number):
            return obj
        raise TypeError("expected str|int|long|float|Decimal|Number object but got %r" % (obj))

    def eval(self):
        return self

    def evalf(self):
        return Real(self._as_decimal())

    def __float__(self):
        return float(self._as_decimal())

    def _as_decimal(self):
        raise NotImplementedError('%s needs ._as_decimal() method' % (self.__class__.__name__))

decimal_to_Number_cls = {
    decimal.Decimal('0').as_tuple():'Zero',
    decimal.Decimal('1').as_tuple():'One',
    decimal.Decimal('-1').as_tuple():'NegativeOne',
    decimal.Decimal('Infinity').as_tuple():'Infinity',
    decimal.Decimal('-Infinity').as_tuple():'NegativeInfinity',
    decimal.Decimal('NaN').as_tuple():'NaN',
    }


class Real(Number):
    """Represents a floating point number. It is capable of representing
    arbitrary-precision floating-point numbers

    Usage:

    Real(3.5)   .... 3.5 (the 3.5 was converted from a python float)
    Real("3.0000000000000005")
    
    """
    is_real = True
    is_commutative = True
    
    def __new__(cls, num):
        if isinstance(num, (str, int, long)):
            num = decimal.Decimal(num)
        elif isinstance(num, float):
            num = Real.float_to_decimal(num)
        if isinstance(num, decimal.Decimal):
            singleton_cls_name = decimal_to_Number_cls.get(num.as_tuple(), None)
            if singleton_cls_name is not None:
                return getattr(Basic, singleton_cls_name)()
            obj = Basic.__new__(cls)
            obj.num = num
            return obj
        raise TypeError("expected str|int|long|float|Decimal but got %r" % (num))

    @staticmethod
    def float_to_decimal(f):
        "Convert a floating point number to a Decimal with no loss of information"
        # Transform (exactly) a float to a mantissa (0.5 <= abs(m) < 1.0) and an
        # exponent.  Double the mantissa until it is an integer.  Use the integer
        # mantissa and exponent to compute an equivalent Decimal.  If this cannot
        # be done exactly, then retry with more precision.

        mantissa, exponent = math.frexp(f)
        while mantissa != int(mantissa):
            mantissa *= 2.0
            exponent -= 1
        mantissa = int(mantissa)

        oldcontext = decimal.getcontext()
        decimal.setcontext(decimal.Context(traps=[decimal.Inexact]))
        try:
            while True:
                try:
                    return mantissa * decimal.Decimal(2) ** exponent
                except decimal.Inexact:
                    decimal.getcontext().prec += 1
        finally:
            decimal.setcontext(oldcontext)

    def _hashable_content(self):
        return (self.num,)

    def tostr(self, level=0):
        r = str(self.num.normalize())
        if self.precedence<=level:
            return '(%s)' % (r)
        return r

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, str(self.num))

    def _calc_positive(self): return self.num.as_tuple()[0] == 0
    def _calc_nonpositive(self): return self.num.as_tuple()[0] == 1
    def _calc_negative(self): return self.num.as_tuple()[0] == 1
    def _calc_nonnegative(self): return self.num.as_tuple()[0] == 0

    def evalf(self):
        return self

    def _as_decimal(self):
        return self.num

    def __neg__(self):
        return Real(-self.num)

    def __mul__(self, other):
        other = Basic.sympify(other)
        if isinstance(other, Number):
            return Real(self.num * other._as_decimal())
        return Number.__mul__(self, other)

    def __add__(self, other):
        other = Basic.sympify(other)
        if isinstance(other, Number):
            return Real(self.num + other._as_decimal())
        return Number.__add__(self, other)

    def _eval_power(b, e):
        """
        b is Real but not equal to rationals, integers, 0.5, oo, -oo, nan
        e is symbolic object but not equal to 0, 1

        (-p) ** r -> exp(r * log(-p)) -> exp(r * (log(p) + I*Pi)) ->
                  -> p ** r * (sin(Pi*r) + cos(Pi*r) * I)
        """
        if isinstance(e, Number):
            if isinstance(e, Integer):
                e = e.p
            else:
                e = e._as_decimal()
            if b.is_negative:
                m = decimal_math.pow(-b.num, e)
                a = decimal_math.pi() * e
                s = m * decimal_math.sin(a)
                c = m * decimal_math.cos(a)
                return Real(s) + Real(c) * ImaginaryUnit()
            return Real(decimal_math.pow(b.num, e))
        return

    def __abs__(self):
        return Real(abs(self.num))

    def __int__(self):
        return int(self.num)

    def __float__(self):
        return float(self.num)


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

    def _as_decimal(self):
        return decimal.Decimal(self.p) / decimal.Decimal(self.q)

    def __abs__(self):
        return Rational(abs(self.p), self.q)

    def __int__(self):
        return int(self.p//self.q)

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

    def evalf(self):
        return Real(decimal_math.e())

class Pi(NumberSymbol):
    is_real = True
    is_positive = is_nonnegative = True
    is_nonpositive = is_negative = False    

    def tostr(self, level=0):
        return 'Pi'

    def evalf(self):
        return Real(decimal_math.pi())

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
            return -One() ** (e * Half())
        return

    def as_base_exp(self):
        return -One(),Rational(1,2)

Basic.singleton['E'] = Exp1
Basic.singleton['pi'] = Pi
Basic.singleton['I'] = ImaginaryUnit
Basic.singleton['oo'] = Infinity
Basic.singleton['nan'] = NaN
