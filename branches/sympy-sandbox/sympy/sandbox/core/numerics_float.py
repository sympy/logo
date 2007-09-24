"""
This module implements a multiprecision binary floating-point type in
Python. It is typically 10-100 times fasterthan Python's standard
Decimals. For details on usage, refer to the docstrings in the Float
class.
"""

from utils import memoizer_immutable_args, memoizer_Float_new
from basic import Basic, sympify
from number import Real



import math
import decimal

LOG2_10 = math.log(10,2)  # 3.3219..., used for binary--decimal conversion

def binary_to_decimal(man, exp, n):
    """Represent as a decimal string with at most n digits"""
    import decimal
    prec_ = decimal.getcontext().prec
    decimal.getcontext().prec = n
    if exp >= 0: d = decimal.Decimal(man) * (1<<exp)
    else:        d = decimal.Decimal(man) / (1<<-exp)
    a = str(d)
    decimal.getcontext().prec = prec_
    return a


# All supported rounding modes. We define them as integer constants for easy
# management, but change __repr__ to 

class _RoundingMode(int):
    def __new__(cls, level, name):
        a = int.__new__(cls, level)
        a.name = name
        return a
    def __repr__(self): return self.name

ROUND_DOWN    = _RoundingMode(1, 'ROUND_DOWN')
ROUND_UP      = _RoundingMode(2, 'ROUND_UP')
ROUND_FLOOR   = _RoundingMode(3, 'ROUND_FLOOR')
ROUND_CEILING = _RoundingMode(4, 'ROUND_CEILING')
ROUND_HALF_UP = _RoundingMode(5, 'ROUND_HALF_UP')
ROUND_HALF_DOWN = _RoundingMode(6, 'ROUND_HALF_DOWN')
ROUND_HALF_EVEN = _RoundingMode(7, 'ROUND_HALF_EVEN')



#----------------------------------------------------------------------------#
#                                                                            #
#                     Low-level arithmetic functions                         #
#                                                                            #
#                          Bit manipulation, etc                             #
#                                                                            #
#----------------------------------------------------------------------------#

def bitcount(n, log=math.log, table=(0,1,2,2,3,3,3,3,4,4,4,4,4,4,4,4)):
    """Give size of n in bits; i.e. the position of the highest set bit
    in n. If n is negative, the absolute value is used. The bitcount of
    zero is taken to be 0."""

    if not n: return 0
    if n < 0: n = -n

    # math.log gives a good estimate, and never overflows, but
    # is not always exact. Subtract 2 to underestimate, then
    # count remaining bits by table lookup
    bc = int(log(n, 2)) - 2
    if bc < 0:
        bc = 0
    return bc + table[n >> bc]

def trailing_zeros(n):
    """Count trailing zero bits in an integer. If n is negative, it is
    replaced by its absolute value."""
    if n & 1: return 0
    if not n: return 0
    if n < 0: n = -n
    t = 0
    while not n & 0xffffffffffffffff: n >>= 64; t += 64
    while not n & 0xff: n >>= 8; t += 8
    while not n & 1: n >>= 1; t += 1
    return t

def rshift(x, n, mode):
    """Shift x n bits to the right (i.e., calculate x/(2**n)), and
    round to the nearest integer in accordance with the specified
    rounding mode. The exponent n may be negative, in which case x is
    shifted to the left (and no rounding is necessary)."""

    if not n or not x:
        return x
    # Support left-shifting (no rounding needed)
    if n < 0:
        return x << -n

    # To get away easily, we exploit the fact that Python rounds positive
    # integers toward zero and negative integers away from zero when dividing
    # or shifting. The simplest rounding modes can be handled entirely through
    # shifts:
    if mode < ROUND_HALF_UP:
        if mode == ROUND_DOWN:
            if x > 0: return x >> n
            else:     return -((-x) >> n)
        if mode == ROUND_UP:
            if x > 0: return -((-x) >> n)
            else:     return x >> n
        if mode == ROUND_FLOOR:
            return x >> n
        if mode == ROUND_CEILING:
            return -((-x) >> n)

    # Here we need to inspect the bits around the cutoff point
    if x > 0: t = x >> (n-1)
    else:     t = (-x) >> (n-1)
    if t & 1:
        if mode == ROUND_HALF_UP or \
           (mode == ROUND_HALF_DOWN and x & ((1<<(n-1))-1)) or \
           (mode == ROUND_HALF_EVEN and (t&2 or x & ((1<<(n-1))-1))):
            if x > 0:  return (t>>1)+1
            else:      return -((t>>1)+1)
    if x > 0: return t>>1
    else:     return -(t>>1)

def normalize(man, exp, prec, mode):
    """Normalize the binary floating-point number represented by
    man * 2**exp to the specified precision level, rounding according
    to the specified rounding mode if necessary. The mantissa is also
    stripped of trailing zero bits, and its bits are counted. The
    returned value is a tuple (man, exp, bc)."""

    if not man:
        return 0, 0, 0
    bc = bitcount(man)
    if bc > prec:
        man = rshift(man, bc-prec, mode)
        exp += (bc - prec)
        bc = prec

    # Strip trailing zeros
    if not man & 1:
        tr = trailing_zeros(man)
        if tr:
            man >>= tr
            exp += tr
            bc -= tr

    if not man:
        return (0, 0, 0)
    return man, exp, bc


def fadd(s, t, prec=53, rounding=ROUND_HALF_EVEN):
    """Floating-point addition. Given two tuples s and t containing the
    components of floating-point numbers, return their sum rounded to 'prec'
    bits using the 'rounding' mode, represented as a tuple of components."""

    #  General algorithm: we set min(s.exp, t.exp) = 0, perform exact integer
    #  addition, and then round the result.
    #                   exp = 0
    #                       |
    #                       v
    #          11111111100000   <-- s.man (padded with zeros from shifting)
    #      +        222222222   <-- t.man (no shifting necessary)
    #          --------------
    #      =   11111333333333

    # We assume that s has the higher exponent. If not, just switch them:
    if t[1] > s[1]:
        s, t = t, s

    sman, sexp, sbc = s
    tman, texp, tbc = t

    # Check if one operand is zero. Float(0) always has exp = 0; if the
    # other operand has a large exponent, its mantissa will unnecessarily
    # be shifted a huge number of bits if we don't check for this case.
    if not tman:
        return normalize(sman, sexp, prec, rounding)
    if not sman:
        return normalize(tman, texp, prec, rounding)

    # More generally, if one number is huge and the other is small,
    # and in particular, if their mantissas don't overlap at all at
    # the current precision level, we can avoid work.

    #       precision
    #    |            |
    #     111111111
    #  +                 222222222
    #     ------------------------
    #  #  1111111110000...

    # However, if the rounding isn't to nearest, correct rounding mandates
    # the result should be adjusted up or down. This is not yet implemented.

    if sexp - texp > 100:
        bitdelta = (sbc+sexp)-(tbc+texp)
        if bitdelta > prec + 5:
            # TODO: handle rounding here
            return normalize(sman, sexp, prec, rounding)

    # General case
    return normalize(tman+(sman<<(sexp-texp)), texp, prec, rounding)




# Construct Float from raw man and exp
def makefloat(man, exp, newtuple=tuple.__new__):
    return newtuple(Float, normalize(man, exp, Float._prec, Float._mode))

def makefloat_from_fraction(p, q):
    prec = Float._prec
    mode = Float._mode
    n = prec + bitcount(q) + 2
    return tuple.__new__(Float, normalize((p<<n)//q, -n, prec, mode))



#----------------------------------------------------------------------
# Float class
#

class Float(Real, tuple):
    """
    A Float is a rational number of the form

        man * 2**exp

    ("man" and "exp" are short for "mantissa" and "exponent"). Both man
    and exp are integers, possibly negative, and may be arbitrarily large.
    Essentially, a larger mantissa corresponds to a higher precision
    and a larger exponent corresponds to larger magnitude.

    A Float instance is represented by a tuple

        (man, exp, bc)

    where bc is the bitcount of the mantissa. The elements can be
    accessed as named properties:

        >>> x = Float(3)
        >>> x.man
        3
        >>> x.exp
        0
        >>> x.bc
        2

    When performing an arithmetic operation on two Floats, or creating a
    new Float from an existing numerical value, the result gets rounded
    to a fixed precision level, just like with ordinary Python floats.
    Unlike regular Python floats, however, the precision level can be
    set arbitrarily high. You can also change the rounding mode (all
    modes supported by Decimal are also supported by Float).

    The precision level and rounding mode are stored as properties of
    the Float class. (An individual Float instances does not have any
    precision or rounding data associated with it.) The precision level
    and rounding mode make up the current working context. You can
    change the working context through static methods of the Float
    class:

        Float.setprec(n)    -- set precision to n bits
        Float.extraprec(n)  -- increase precision by n bits
        Float.setdps(n)     -- set precision equivalent to n decimals
        Float.setmode(mode) -- set rounding mode

    Corresponding methods are available for inspection:

        Float.getprec()
        Float.getdps()
        Float.getmode()

    There are also two methods Float.store() and Float.revert(). If
    you call Float.store() before changing precision or mode, the
    old context can be restored with Float.revert(). (If Float.revert()
    is called one time too much, the default settings are restored.)
    You can nest multiple uses of store() and revert().

    (In the future, it will also be possible to use the 'with'
    statement to change contexts.)

    Note that precision is measured in bits. Since the ratio between
    binary and decimal precision levels is irrational, setprec and
    setdps work slightly differently. When you set the precision with
    setdps, the bit precision is set slightly higher than the exact
    corresponding precision to account for the fact that decimal
    numbers cannot generally be represented exactly in binary (the
    classical example is 0.1). The exact number given to setdps
    is however used by __str__ to determine number of digits to
    display. Likewise, when you set a bit precision, the decimal
    printing precision used for __str__ is set slightly lower.

    The following rounding modes are available:

        ROUND_DOWN       -- toward zero
        ROUND_UP         -- away from zero
        ROUND_FLOOR      -- towards -oo
        ROUND_CEILING    -- towards +oo
        ROUND_HALF_UP    -- to nearest; 0.5 to 1
        ROUND_HALF_DOWN  -- to nearest; 0.5 to 0
        ROUND_HALF_EVEN  -- to nearest; 0.5 to 0 and 1.5 to 2

    The rounding modes are available both as global constants defined
    in this module and as properties of the Float class, e.g.
    Float.ROUND_CEILING.

    The default precision level is 53 bits and the default rounding
    mode is ROUND_HALF_EVEN. In this mode, Floats should round exactly
    like regular Python floats (in the absence of bugs!).
    """

    #------------------------------------------------------------------
    # Static methods for context management
    #

    # Also make these constants available from the class
    ROUND_DOWN = ROUND_DOWN
    ROUND_UP = ROUND_UP
    ROUND_FLOOR = ROUND_FLOOR
    ROUND_CEILING = ROUND_CEILING
    ROUND_HALF_UP = ROUND_HALF_UP
    ROUND_HALF_DOWN = ROUND_HALF_DOWN
    ROUND_HALF_EVEN = ROUND_HALF_EVEN

    _prec = 53
    _dps = 15
    _mode = ROUND_HALF_EVEN
    _stack = []

    make = staticmethod(makefloat)
    make_from_fraction = staticmethod(makefloat_from_fraction)

    @staticmethod
    def store():
        """Store the current precision/rounding context. It can
        be restored by calling Float.revert()"""
        Float._stack.append((Float._prec, Float._dps, Float._mode))

    @staticmethod
    def revert():
        """Revert to last precision/rounding context stored with
        Float.store()"""
        if Float._stack:
            Float._prec, Float._dps, Float._mode = Float._stack.pop()
        else:
            Float._prec, Float._dps, Float._mode = 53, 15, ROUND_HALF_EVEN

    @staticmethod
    def setprec(n):
        """Set precision to n bits"""
        n = int(n)
        Float._prec = n
        Float._dps = int(round(n/LOG2_10)-1)

    @staticmethod
    def setdps(n):
        """Set the precision high enough to allow representing numbers
        with at least n decimal places without loss."""
        n = int(n)
        Float._prec = int(round((n+1)*LOG2_10))
        Float._dps = n

    @staticmethod
    def extraprec(n):
        Float.setprec(Float._prec + n)

    @staticmethod
    def setmode(mode):
        assert isinstance(mode, _RoundingMode)
        Float._mode = mode

    @staticmethod
    def getprec(): return Float._prec

    @staticmethod
    def getdps(): return Float._dps

    @staticmethod
    def getmode(): return Float._mode


    #------------------------------------------------------------------
    # Core object functionality
    #

    man = property(lambda self: self[0])
    exp = property(lambda self: self[1])
    bc = property(lambda self: self[2])

    @classmethod
    def makefloat(cls, man, exp, newtuple=tuple.__new__):
        return newtuple(cls, normalize(man, exp, cls._prec, cls._mode))

    @memoizer_Float_new
    def __new__(cls, x=0, prec=None, mode=None):
        # when changing __new__ signature, update memoizer_Float_new accordingly
        """
        Float(x) creates a new Float instance with value x. The usual
        types are supported for x:

            >>> Float(3)
            Float('3')
            >>> Float(3.5)
            Float('3.5')
            >>> Float('3.5')
            Float('3.5')
            >>> Float(Rational(7,2))
            Float('3.5')

        You can also create a Float from a tuple specifying its
        mantissa and exponent:

            >>> Float((5, -3))
            Float('0.625')

        Use the prec and mode arguments to specify a custom precision
        level (in bits) and rounding mode. If these arguments are
        omitted, the current working precision is used instead.

            >>> Float('0.500001', prec=3, mode=ROUND_DOWN)
            Float('0.5')
            >>> Float('0.500001', prec=3, mode=ROUND_UP)
            Float('0.625')

        """
        prec = prec or cls._prec
        mode = mode or cls._mode
        if x.__class__ is tuple:
            return tuple.__new__(cls, normalize(x[0], x[1], prec, mode))
        if isinstance(x, (int, long)):
            return tuple.__new__(cls, normalize(x, 0, prec, mode))
        if isinstance(x, float):
            # We assume that a float mantissa has 53 bits
            m, e = math.frexp(x)
            return tuple.__new__(cls, normalize(int(m*(1<<53)), e-53, prec, mode))

        if isinstance(x, (str, Basic.Rational)):
            # Basic.Rational should support parsing
            if isinstance(x, str):
                # XXX: fix this code
                import sympy
                x = sympy.Rational(x)
                x = Basic.Rational(x.p, x.q)

            n = prec + bitcount(x.q) + 2
            return tuple.__new__(cls, normalize((x.p<<n)//x.q, -n, prec, mode))

        if isinstance(x, Basic):
            return x.evalf()
        raise TypeError(`x`)

    def __hash__(s):
        try:
            # Try to be compatible with hash values for floats and ints
            return hash(float(s))
        except OverflowError:
            # We must unfortunately sacrifice compatibility with ints here. We
            # could do hash(man << exp) when the exponent is positive, but
            # this would cause unreasonable inefficiency for large numbers.
            return tuple.__hash__(s)

    def __pos__(s):
        """Normalize s to the current working precision, rounding
        according to the current rounding mode."""
        return makefloat(s[0], s[1])

    def __float__(s):
        """Convert to a Python float. May raise OverflowError."""
        try:
            return math.ldexp(s.man, s.exp)
        except OverflowError:
            # Try resizing the mantissa. Overflow may still happen here.
            n = s.bc - 53
            m = s.man >> n
            return math.ldexp(m, s.exp + n)

    def __int__(s):
        """Convert to a Python int, using floor rounding"""
        return rshift(s.man, -s.exp, 0)

    def rational(s): # XXX: use s.as_Fraction instead
        """Convert to a SymPy Rational"""
        if s.exp > 0:
            return Basic.Rational(s.man * 2**s.exp, 1)
        else:
            return Basic.Rational(s.man, 2**(-s.exp))

    def __repr__(s):
        """Represent s as a decimal string, with sufficiently many
        digits included to ensure that Float(repr(s)) == s at the
        current working precision."""
        st = "Float('%s')"
        return st % binary_to_decimal(s.man, s.exp, Float._dps + 2)

    def __str__(s):
        """Print slightly more prettily than __repr__"""
        return binary_to_decimal(s.man, s.exp, Float._dps)


    #------------------------------------------------------------------
    # Comparisons
    #

    def compare(self, other):
        """
        Warning: in extreme cases, the truncation error resulting from
        calling Float(t) will result in an erroneous comparison: for
        example, Float(2**80) will compare as equal to 2**80+1. This
        problem can be circumvented by manually increasing the working
        precision or by converting numbers into Rationals for
        comparisons.
        """
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c        
        # An inequality between two numbers s and t is determined by looking
        # at the value of s-t. A full floating-point subtraction is relatively
        # slow, so we first try to look at the exponents and signs of s and t.
        sm, se, sbc = self # = s
        tm, te, tbc = other # = t

        # Very easy cases: check for 0's and opposite signs
        if not tm: return cmp(sm, 0)
        if not sm: return cmp(0, tm)
        if sm > 0 and tm < 0: return 1
        if sm < 0 and tm > 0: return -1

        # In this case, the numbers likely have the same magnitude
        if se == te: return cmp(sm, tm)

        # The numbers have the same sign but different exponents. In this
        # case we try to determine if they are of different magnitude by
        # checking the position of the highest set bit in each number.
        a = sbc + se
        b = tbc + te
        if sm > 0:
            if a < b: return -1
            if a > b: return 1
        else:
            if a < b: return 1
            if a < b: return -1

        # The numbers have similar magnitude but different exponents.
        # So we subtract and check the sign of resulting mantissa.
        return cmp((self-other)[0], 0)

    def __eq__(self, other):
        """s.__eq__(t) <==> s == Float(t)

        Determine whether s and Float(t) are equal (see warning for
        __cmp__ about conversion between different types.)"""
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return tuple.__eq__(self, other)
        return NotImplemented

    def __ne__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return tuple.__ne__(self, other)
        return NotImplemented

    def __lt__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)==-1
        return NotImplemented

    def __le__(self, other):
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)<=0
        return NotImplemented

    def __gt__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)==1
        return NotImplemented

    def __ge__(self, other):
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)>=0
        return NotImplemented

    def ae(s, t, rel_eps=None, abs_eps=None):
        """
        Determine whether the difference between s and t is smaller
        than a given epsilon ("ae" is short for "almost equal").

        Both a maximum relative difference and a maximum difference
        ('epsilons') may be specified. The absolute difference is
        defined as |s-t| and the relative difference is defined
        as |s-t|/max(|s|, |t|).

        If only one epsilon is given, both are set to the same value.
        If none is given, both epsilons are set to 2**(-prec+m) where
        prec is the current working precision and m is a small integer.
        """
        if not isinstance(t, Float):
            t = Float(t)
        if abs_eps is None and rel_eps is None:
            rel_eps = tuple.__new__(Float, (1, -s._prec+4, 1))
            rel_eps = Float((1, -s._prec+4))
        if abs_eps is None:
            abs_eps = rel_eps
        elif rel_eps is None:
            rel_eps = abs_eps
        diff = abs(s-t)
        if diff <= abs_eps:
            return True
        abss = abs(s)
        abst = abs(t)
        if abss < abst:
            err = diff/abst
        else:
            err = diff/abss
        return err <= rel_eps

    def almost_zero(s, prec):
        """Quick check if |s| < 2**-prec. May return a false negative
        if s is very close to the threshold."""
        return s.bc + s.exp < prec

    def __nonzero__(s):
        return not not s[0]

    #------------------------------------------------------------------
    # Arithmetic
    #

    def __abs__(s):
        if s[0] < 0:
            return -s
        return s

    def __neg__(s):
        return makefloat(-s[0], s[1])

    def __add__(s, t):
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            return Float(fadd(s, t, Float._prec, Float._mode))
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other + self
            return Basic.Add(other, self)
        return sympify(other) + self

    def __sub__(s, t):
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            return s + tuple.__new__(Float, (-t[0],) + t[1:])
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other - self
            return Basic.Add(other, -self)
        return sympify(other) - self

    def __mul__(s, t):
        if isinstance(t, (int, long, Basic.Integer)):
            return makefloat(s[0]*int(t), s[1])
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            sman, sexp, sbc = s
            tman, texp, tbc = t
            return makefloat(sman*tman, sexp+texp)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other * self
            return Basic.Mul(other, self)
        return sympify(other) * self

    def __div__(s, t):
        if isinstance(t, (int, long, Basic.Integer)):
            t = int(t)
            sman, sexp, sbc = s
            extra = s._prec - sbc + bitcount(t) + 4
            return makefloat((sman<<extra)//t, sexp-extra)
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            sman, sexp, sbc = s
            tman, texp, tbc = t
            extra = s._prec - sbc + tbc + 4
            if extra < 0:
                extra = 0
            return makefloat((sman<<extra)//tman, sexp-texp-extra)
        return NotImplemented

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other / self                
            return Basic.Mul(other, makefloat_from_fraction(1,1) / self)
        return sympify(other) / self

    def __pow__(s, n):
        if isinstance(n, (int, long, Basic.Integer)):
            n = int(n)
            if n == 0: return makefloat_from_fraction(1,1)
            if n == 1: return +s
            if n == 2: return s * s
            if n == -1: return makefloat_from_fraction(1,1) / s
            if n < 0:
                Float._prec += 2
                r = Float(1) / (s ** -n)
                Float._prec -= 2
                return +r
            else:
                prec2 = Float._prec + int(4*math.log(n, 2) + 4)
                man, exp, bc = normalize(s.man, s.exp, prec2, ROUND_FLOOR)
                pm, pe, bc = 1, 0, 1
                while n:
                    if n & 1:
                        pm, pe, bc = normalize(pm*man, pe+exp, prec2, ROUND_FLOOR)
                        n -= 1
                    man, exp, _ = normalize(man*man, exp+exp, prec2, ROUND_FLOOR)
                    n = n // 2
                return makefloat(pm, pe)
        n = sympify(n)
        if n.is_Rational:
            n = n.as_Float
        if n.is_Float:
            if n == 0.5:
                from numerics.functions import sqrt
                return sqrt(s)
            from numerics.functions import exp, log
            return exp(n * log(s))
        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, Basic):
            if other.is_Float:
                other = other.as_Float
            if other.is_Float:
                return other ** self
            return Basic.Pow(other, self)
        return sympify(other) ** self
