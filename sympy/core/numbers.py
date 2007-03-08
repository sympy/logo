import hashing
from basic import Basic
import utils 
import decimal

class Number(Basic):
    """Represents any kind of number in sympy.


    Floating point numbers are represented by the Real class.
    Integer numbers (of any size), together with rational numbers (again, there
    is no limit on their size) are represented by the Rational class. 

    If you want to represent for example 1+sqrt(2), then you need to do:

    Rational(1) + Rational(2)**( Rational(1)/2 )
    """
    
    def __init__(self):
        Basic.__init__(self)
        
    def __int__(self):
        raise NotImplementedError
        
    def __float__(self):
        return self.evalf()
    
    def __abs__(self):
        from functions import abs_
        return abs_(self)
    
    def diff(self,sym):
        return Rational(0)
    
    def evalf(self):
        return self
    
class Infinity(Number):
    """Infinity. Cannot be used in expressions like 1+infty.  
    Only as a Symbol, for example results of limits, integration limits etc.
    Can however be used in comparisons, like infty!=1, or infty!=x**3
    
    this class represents all kinds of infinity, i.e. both +-infty.
    """
    
    def __init__(self):
        Number.__init__(self)
        self._sign=1
        
    def print_sympy(self):
        return "Inf"
    
    def hash(self):
        if self.mhash: 
            return self.mhash.value
        self.mhash = hashing.mhash()
        self.mhash.addstr(str(type(self)))
        return self.mhash.value
    
    def sign(self):
        return self._sign

infty=Infinity()

class Real(Number):
    """Represents a floating point number.

    Currently, it supports python floats only.

    Usage:

    Real(3.5)   .... 3.5 (the 3.5 was converted from a python float)
    Real("3.5") .... 3.5 (currently, the 3.5 is also a python float,
            but in the future, we could use some other library)
    """
    
    
    def __init__(self,num):
        Number.__init__(self)
        if isinstance(num,str):
            num = decimal.Decimal(num)
#        assert utils.isnumber(num)
        if isinstance(num, decimal.Decimal):
            self.num = num
        elif isinstance(num, Real):
            self.num = num.evalf()
        else:
            self.num = decimal.Decimal(str(float(num)))
        
    def hash(self):
        if self.mhash: 
            return self.mhash.value
        self.mhash=hashing.mhash()
        self.mhash.addstr(str(type(self)))
        self.mhash.addfloat(self.num)
        return self.mhash.value
        
    def print_sympy(self):
        if self.num < 0:
            f = "(%r)"
        else:
            f = "%r"
        return f % (str(self.num))
    
    def __float__(self):
        return float(self.num)
        
    def __int__(self):
        return int(self.evalf())
    
    def __add__(self,a):
        if utils.isnumber(a):
            if isinstance(a, Real):
                return Real(self.num + a.num)
            else:
                return Real(self.num + decimal.Decimal(str(float(a))))
        else:
            assert isinstance(a, Basic)
            from addmul import Add
            return Add(self, a)
        
    def __mul__(self,a):
        if utils.isnumber(a):
            return Real(self.num * decimal.Decimal(str(float(a))))
            #FIXME: too many boxing-unboxing
        else:
            assert isinstance(a, Basic)
            from addmul import Mul
            return Mul(self, a)
        
    def __pow__(self,a):
        if utils.isnumber(a):
            if isinstance(a, int):
                return Real(self.num ** a)
            elif isinstance(a, Rational) and a.q == 1:
                return Real(self.num ** decimal.Decimal(a.p))
            # can't do decimal ** decimal, the module doesen't handle it
        else:
            assert isinstance(a, Basic)
            from power import Pow
            return Pow(self, a)
        
    def __rpow__(self, a):
#        if utils.isnumber(a):
#            return float(a) ** self.num
#        else:
#            assert isinstance(a, Basic)
            from power import Pow
            return Pow(a, self)
        
    def __lt__(self, a):
        return self.num < a
    
    def __gt__(self, a):
        return self.num > a
        
    def iszero(self):
        if self.num == 0:
            return True
        else: 
            return False
        
    def isone(self):
        if self.num == 1:
            return True
        else:
            return False
        
    def isinteger(self):
        return False
        
    def evalf(self):
        #evalf() should return either a float or an exception
        return self.num

class Rational(Number):
    """Represents integers and rational numbers (p/q) of any size.

    Thanks to support of long ints in Python. 

    Usage:

    Rational(3)      ... 3
    Rational(1,2)    ... 1/2
    """
    
    def __init__(self,*args):
        Number.__init__(self)
        if len(args)==1:
            p = args[0]
            q = 1 
        elif len(args)==2:
            p = args[0]
            q = args[1]
        else:
            raise "invalid number of arguments"
        assert (isinstance(p, int) or isinstance(p, long)) and \
               (isinstance(q, int) or isinstance(q, long))
        assert q != 0
        s = utils.sign(p)*utils.sign(q)
        p = abs(p)
        q = abs(q)
        c = self.gcd(p,q)
        self.p = p/c*s
        self.q = q/c
        
    def __lt__(self,a):
        """Compares two Rational numbers."""
        return self.evalf() < float(a)
        
    def sign(self):
        return utils.sign(self.p)*utils.sign(self.q)
        
    def hash(self):
        if self.mhash: 
            return self.mhash.value
        self.mhash = hashing.mhash()
        self.mhash.addstr(str(type(self)))
        self.mhash.addint(self.p)
        self.mhash.addint(self.q)
        return self.mhash.value
        
    def gcd(self,a,b):
        """Primitive algorithm for a greatest common divisor of "a" and "b"."""
        while b!=0:
            c = a % b
            a,b=b,c
        return a
        
    def print_sympy(self):
        if self.q == 1:
            f = "%d"
            return f % (self.p)
        else:
            f = "%d/%d"
            return f % (self.p,self.q)
            
    def __mul__(self,a):
        a=self.sympify(a)
        if isinstance(a, Rational):
            return Rational(self.p * a.p, self.q * a.q)
        elif isinstance(a, int) or isinstance(a, long):
            return Rational(self.p * a, self.q)
        elif isinstance(a, Real):
            return a.__mul__(self)
        else:
            from addmul import Mul
            return Mul(self, a)
    
    def __rmul__(self, a):
        return self.__mul__(a)
    
    def __div__(self, a):
        if isinstance(a, int):
            return Rational(self.p, self.q *a)
        return self * (a**Rational(-1))
        
    def __rdiv__(self, a):
        if isinstance(a, int):
            return Rational(self.q * a, self.p )
        return self * (a**Rational(-1))
    
    def __add__(self,a):
        a=self.sympify(a)
        if isinstance(a, Rational):
            return Rational(self.p*a.q+self.q*a.p,self.q*a.q)
        elif isinstance(a, int) or isinstance(a, long):
            return Rational(self.p + a*self.q, self.q)
        elif isinstance(a, Real):
            return a.__add__(self)
        else:
            from addmul import Add
            return Add(self, a)
        
    def __pow__(self,a):
        """Returns the self to the power of "a"
        """
        from power import Pow, pole_error
    
        if utils.isnumber(a):
            if self.p == 0:
                if a < 0:
                    # 0 ** a = undefined, where a <= 0 
                    raise pole_error("pow::eval(): Division by 0.")
                elif a == 0:
                    #FIXME : mathematically wrong but needed for limits.py
                    #raise pole_error("pow::eval(): Division by 0.")
                    return Rational(1)
                else:
                    # 0 ** a = 0, where a > 0
                    return Rational(0)
            elif isinstance(a, Rational):
                if a.q == 1:
                    if a.p > 0:
                        return Rational(self.p ** a.p, self.q ** a.p)
                    else:
                        return Rational(self.q**(-a.p),self.p**(-a.p))
        return Pow(self, self.sympify(a))
            
    def __rpow__(self, a):  
        """Returns "a" to the power of self
        """
        from power import Pow
        if self.p == 0:
            return Rational(1)
        elif a == 0:
            return Rational(0)
        if self.q != 1:
            #if self is an integer
            if hasattr(a, 'evalf'):
                return Pow(a.evalf(), self)
            else:
                return Pow(self.sympify(a), self)
        elif isinstance(a, Rational):
            if self.p > 0:
                return Rational(a.p ** self.p, a.q ** self.p)
            else:
                return Rational(a.q ** (-self.p), a.p ** (-self.p))
        elif isinstance(a, int):
            if self.p > 0:
                return Rational(a ** self.p)
            else:
                return Rational(1, a ** -(self.p))
        return Pow(a, self )

    def __int__(self):
        return self.getinteger()
    
    def iszero(self):
        return self.p == 0 
        
    def isone(self):
        return self.p == 1 and self.q == 1
        
    def isminusone(self):
        return self.p == -1 and self.q == 1
        
    def isinteger(self):
        return self.q == 1
        
    def getinteger(self):
        assert self.isinteger()
        return self.p
        
    def evalf(self):
        return float(self.p)/self.q
        
    def diff(self,sym):
        return Rational(0)
    

class ImaginaryUnit(Basic):
    """Imaginary unit "i"."""

    def print_sympy(self):
        return "i"

    def hash(self):
        if self.mhash: 
            return self.mhash.value
        self.mhash = hashing.mhash()
        self.mhash.addstr(str(type(self)))
        return self.mhash.value

I=ImaginaryUnit()

class Constant(Basic):
    """Mathematical constant abstract class."""
    
    def __call__(self, precision=28):
            return self.evalf(precision)
        
    def hash(self):
        if self.mhash: 
            return self.mhash.value
        self.mhash = hashing.mhash()
        self.mhash.addstr(str(type(self)))
        return self.mhash.value

    def diff(self,sym):
        return Rational(0)

class ConstPi(Constant):
    """
    
    Usage: pi -> Returns the mathematical constant pi 
           pi() -> Returns a numerical aproximation for pi
           
    Notes:
        Can have an option precision (integer) for the number of digits 
        that will be returned. Default is set to 28
       
        pi() is a shortcut for pi.evalf()
    
    Examples: 
        In [1]: pi
        Out[1]: pi

        In [2]: pi()
        Out[2]: '3.141592653589793238462643383'

        In [3]: pi(precision=200)
        Out[3]: '3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303820'

    """
    
    def evalf(self, precision=28):
        """Compute Pi to the current precision.

        >>> print pi.eval()
        3.141592653589793238462643383
        
        """
        decimal.getcontext().prec = precision + 2  # extra digits for intermediate steps
        three = decimal.Decimal(3)      # substitute "three=3.0" for regular floats
        lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        while s != lasts:
            lasts = s
            n, na = n+na, na+8
            d, da = d+da, da+32
            t = (t * n) / d
            s += t
        decimal.getcontext().prec -= 2
        return Real(+s)               # unary plus applies the new precision
        # this was a recipe taken from http://docs.python.org/lib/decimal-recipes.html
        # don't know how fiable it is


    def print_sympy(self):
        return "pi"

pi=ConstPi()
