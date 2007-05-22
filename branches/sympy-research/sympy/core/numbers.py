
from basic import Basic, Singleton

def gcd(a, b):
    '''Returns the Greatest Common Divisor,
    implementing Euclid\'s algorithm.'''
    while a:
        a, b = b%a, a
    return b


class Number(Basic):    
    """Represents any kind of number in sympy.


    Floating point numbers are represented by the Real class.
    Integer numbers (of any size), together with rational numbers (again, there
    is no limit on their size) are represented by the Rational class. 

    If you want to represent for example 1+sqrt(2), then you need to do:

    Rational(1) + sqrt(Rational(2))
    """


class Rational(Number):
    """Represents integers and rational numbers (p/q) of any size.

    Thanks to support of long ints in Python. 

    Usage:

    Rational(3)      ... 3
    Rational(1,2)    ... 1/2
    """

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
            obj = Number.__new__(cls)
            obj.p = p
            obj.q = q
            return obj
        raise TypeError("Expected integers but got %r, %r" % (p,q))

    def _hashable_content(self):
        return (self.p, self.q)

    def tostr(self, level=0):
        precedence = self.get_precedence()
        if precedence<=level:
            return '(%s/%s)' % (self.p, self.q)
        return '%s/%s' % (self.p, self.q)

    def torepr(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.p, self.q)

class Integer(Rational):

    q = 1

    def __new__(cls, i):
        if isinstance(i, (int, long)):
            if i==0:
                return Zero()
            obj = Basic.__new__(cls)
            obj.p = i
            return obj
        if isinstance(i, Integer):
            return i
        raise TypeError("Expected integer but got %r" % (i))


class Zero(Singleton, Integer):
    p = 0
    q = 1


Basic.Number = Number
Basic.Rational = Rational
Basic.Integer = Integer
Basic.Zero = Zero
Basic.singleton_classes['Zero'] = Zero
