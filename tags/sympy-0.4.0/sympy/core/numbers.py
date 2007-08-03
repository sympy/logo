
from sympy.core.basic import Basic
import decimal
from stringPict import prettyForm, stringPict


dummycount = 0

class Number(Basic):
    """Represents any kind of number in sympy.


    Floating point numbers are represented by the Real class.
    Integer numbers (of any size), together with rational numbers (again, there
    is no limit on their size) are represented by the Rational class. 

    If you want to represent for example 1+sqrt(2), then you need to do:

    Rational(1) + sqrt(Rational(2))
    """
    
    mathml_tag = "cn"
    
    def __init__(self):
        Basic.__init__(self, is_commutative = True)
        
    def __int__(self):
        raise NotImplementedError
    
    def __float__(self):
        return float(self.evalf())
    
    def __abs__(self):
        from functions import abs_
        return abs_(self)
    
    def __mathml__(self):
        import xml.dom.minidom
        if self._mathml:
            return self._mathml
        dom = xml.dom.minidom.Document()
        x = dom.createElement(self.mathml_tag)
        x.appendChild(dom.createTextNode(str(self)))
        self._mathml = x
        
        return self._mathml
    
    
    def diff(self,sym):
        return Rational(0)
    
    def evalf(self):
        raise NotImplementedError("cannot evaluate %s" % self.__class__.__name__)

    def evalc(self):
        return self

    def doit(self):
        return self
    
class Infinity(Number):
    """
    Usage
    =====
        Represents mathematical infinity. 
        
    Notes
    =====
        Can be used in expressions that are meaningful, so for example oo-oo,
        or oo/oo raise exception, but 1+oo, 2*oo, oo+oo are legal (and produce
        oo). Can be used in comparisons, like oo!=1, or oo!=x**3 and as results
        of limits, integration limits etc.
          
    Examples
    ========
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> limit(x, x, oo)
        oo
    """
    
    def __init__(self, sign=1):
        Basic.__init__(self, 
                       is_real = False, 
                       is_commutative = False, 
                       )
    
    def __latex__(self):
        return "\infty"
    
    def __pretty__(self):
        return "oo"

    def __str__(self):
        return "oo"
    
    def sign(self):
        return self._sign
    
    def __lt__(self, num):
        if self.sympify(num).is_number:
            if self._sign == -1:
                return True
            else:
                return False
    
    def __gt__(self, num):
        return not self.__lt__(num)
    
    def evalf(self):
        return self

    @staticmethod
    def muleval(a, b):
        if isinstance(a, Infinity) and b.is_number:
            if b > 0:
                return oo
            elif b < 0 and b != -1:
                return -oo
            elif b == 0:
                raise ArithmeticError("Cannot compute oo*0")
        a, b = b, a
        if isinstance(a, Infinity) and b.is_number:
            if b > 0:
                return oo
            elif b < 0 and b != -1:
                return -oo
            elif b == 0:
                raise ArithmeticError("Cannot compute 0*oo")

    @staticmethod
    def addeval(a, b):
        #print a,b
        if isinstance(a, Infinity) and b.is_number:
            return oo
        if isinstance(b, Infinity) and a.is_number:
            return oo

oo = Infinity()

class Real(Number):
    """Represents a floating point number. It is capable of representing
    arbitrary-precision floating-point numbers

    Usage:

    Real(3.5)   .... 3.5 (the 3.5 was converted from a python float)
    Real("3.0000000000000005")
    
    """
    
    
    def __init__(self,num):
        Basic.__init__(self, 
                        is_real = True, 
                        is_commutative = True, 
                        )
        if isinstance(num,str):
            num = decimal.Decimal(num)
        if isinstance(num, decimal.Decimal):
            self.num = num
        elif isinstance(num, Real):
            self.num = num.evalf()
        else:
            self.num = decimal.Decimal(str(float(num)))
        self._args = [self.num]
        
    def __str__(self):
        if self.num < 0:
            f = "(%s)"
        else:
            f = "%s"
        return f % (str(self.num))

    def __float__(self):
        return float(self.num)
        
    def __int__(self):
        return int(self.evalf())
    
    def __add__(self,a):
        from addmul import Add
        a = Basic.sympify(a)
        if a.is_number:
            if isinstance(a, Real):
                return Real(self.num + a.num)
            elif not a.is_real:
                return Add(self, a)
            else:
                return Real(self.num + decimal.Decimal(str(float(a))))
        else:
            assert isinstance(a, Basic)
            return Add(self, a)
        
    def __mul__(self,a):
        from addmul import Mul
        a = Basic.sympify(a)
        if a.is_number:
            if a.is_real:
                return Real(self.num * decimal.Decimal(str(float(a))))
                #FIXME: too many boxing-unboxing
            else:
                return Mul(self, a)
        else:
            assert isinstance(a, Basic)
            return Mul(self, a)
        
    def __pow__(self,a):
        from power import Pow
        return Pow(self, a)
        
    def __rpow__(self, a):
        from power import Pow
        return Pow(a, self)
        
    def isone(self):
        if self.num == 1:
            return True
        else:
            return False
        
    @property
    def is_integer(self):
        return int(self) - self.evalf() == 0
        
    def evalf(self):
        #evalf() should return either a float or an exception
        return self.num
    
    def __pretty__(self):
        if self.num < 0:
            f = "(%s)"
        else:
            f = "%s"
        return f % (str(self.num))
    
    def __eq__(self, a):
        """this is overriden because by default, a python int get's converted
        to a Rational, so things like Real(1) == 1, would return false
        """
        try:
            return decimal.Decimal(str(a)) == self.num
        except:
            return False

def _parse_rational(s):
    """Parse rational number from string representation"""
    # Simple fraction
    if "/" in s:
        p, q = s.split("/")
        return int(p), int(q)
    # Recurring decimal
    elif "[" in s:
        sign = 1
        if s[0] == "-":
            sign = -1
            s = s[1:]
        s, periodic = s.split("[")
        periodic = periodic.rstrip("]")
        offset = len(s) - s.index(".") - 1
        n1 = int(periodic)
        n2 = int("9" * len(periodic))
        r = Rational(*_parse_rational(s)) + Rational(n1, n2*10**offset)
        return sign*r.p, r.q
    # Ordinary decimal string. Use the Decimal class's built-in parser
    else:
        sign, digits, expt = decimal.Decimal(s).as_tuple()
        p = (1, -1)[sign] * int("".join(str(x) for x in digits))
        if expt >= 0:
            return p*(10**expt), 1
        else:
            return p, 10**-expt

def _load_decimal(d):
    """Create Rational from a Decimal instance"""

class Rational(Number):
    """Represents integers and rational numbers (p/q) of any size.

    Thanks to support of long ints in Python. 

    Examples
    ========

    >>> Rational(3)
    3
    >>> Rational(1,2)
    1/2

    You can create a rational from a string:
    >>> Rational("3/5")
    3/5
    >>> Rational("1.23")
    123/100

    Use square brackets to indicate a recurring decimal:
    >>> Rational("0.[333]")
    1/3
    >>> Rational("1.2[05]")
    1193/990
    >>> float(Rational(1193,990))
    1.2050505050505051

    """
    
    def __init__(self,*args):
        Basic.__init__(self, 
                       is_real = True, 
                       is_commutative = True, 
                       )
        if len(args)==1:
            if isinstance(args[0], str):
                p, q = _parse_rational(args[0])
            else:
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
        s = sign(p)*sign(q)
        p = abs(p)
        q = abs(q)
        c = self.gcd(p,q)
        self.p = p/c*s
        self.q = q/c
        self._args = [self.p,self.q] # needed by .hash and others. we should move [p,q] to _args
                        # and then create properties p and q
        
    def sign(self):
        return sign(self.p)*sign(self.q)
        
    def gcd(self,a,b):
        """Primitive algorithm for a greatest common divisor of "a" and "b"."""
        while b:
            a, b = b, a % b
        return a
        
    def __str__(self):
        if self.q == 1:
            f = "%d"
            return f % (self.p)
        else:
            f = "%d/%d"
            return f % (self.p,self.q)

    def __mul__(self,a):
        a = self.sympify(a)
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
        #TODO: move to Mul.eval
        if isinstance(a, int):
            return Rational(self.p, self.q *a)
        return self * (a**Rational(-1))
        
    def __rdiv__(self, a):
        #TODO: move to Mul.eval
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
        from power import Pow
        return Pow(self, a)
    
    def __rpow__(self, a):  
        """Returns "a" to the power of self
        """
        from power import Pow
        return Pow(a, self)
    

    def __int__(self):
        assert self.is_integer
        return self.p
    
    def iszero(self):
        return self.p == 0 
        
    def isone(self):
        return self.p == 1 and self.q == 1
        
    def isminusone(self):
        return self.p == -1 and self.q == 1
        
    @property
    def is_integer(self):
        """Returns True if the current number is an integer
        and False otherwise. 
        
        Examples
        ========
            >>> Rational(1).is_integer
            True
            >>> Rational(1,2).is_integer
            False
            
        """
        return self.q == 1
        
    def evalf(self):
        return decimal.Decimal(self.p)/self.q
        
    def diff(self,sym):
        return Rational(0)

    def match(self, pattern, syms):
        from symbol import Symbol
        if isinstance(pattern, Symbol):
            try:
                return {syms[syms.index(pattern)]: self}
            except ValueError:
                pass
        if isinstance(pattern, Rational):
            if self==pattern:
                return {}
        from addmul import Mul
        if isinstance(pattern, Mul):
            return Mul(Rational(1),self,evaluate = False).match(pattern,syms)
 
        return None
    
    def __pretty__(self):
        if self.q == 1:
            return prettyForm(str(self.p), prettyForm.ATOM)
        elif self.p < 0:
            pform = prettyForm(str(-self.p))/prettyForm(str(self.q))
            return prettyForm(*pform.left('- '))
        else:
            return prettyForm(str(self.p))/prettyForm(str(self.q))
 
   

class Constant(Number):
    """Mathematical constant abstract class.
    
    Is the base class for constatns such as pi or e
    """
    
    def __init__(self):
        Basic.__init__(self, is_commutative = True)
    
    def __call__(self, precision=28):
        return self.evalf(precision)
       
    def eval(self):
        return self

    def diff(self,sym):
        return Rational(0)

    def __mod__(self, a):
        raise NotImplementedError

    def __rmod__(self, a):
            raise NotImplementedError
        
    def match(self, pattern, syms):
        if self == pattern:
            return {}
        if len(syms) == 1:
            if pattern == syms[0]:
                return {syms[0]: self}
            if self == pattern:
                return {}
        if isinstance(pattern, Constant):
            try:
                return {syms[syms.index(pattern)]: self}
            except ValueError:
                pass
        from addmul import Mul
        if isinstance(pattern, Mul):
            return Mul(Rational(1),self,evaluate = False).match(pattern,syms)
        return None

class ImaginaryUnit(Constant):
    """Imaginary unit "i"."""

    def __init__(self):
        Basic.__init__(self, 
                       is_real = False, 
                       is_commutative = True, 
                       )

    def __str__(self):
        return "I"

    def __latex__(self):
        return "\mathrm{i}"

    def evalf(self):
        """Evaluate to a float. By convention, will return 0, 
        which means that evalf() of a complex number will mean 
        the projection of the complex plane to the real line. 
        For example:
        >>> (1-2*I).evalf()
        1.00
        >>> (-2+1*I).evalf()
        (-2.0)
        """
        return Rational(0)

    def evalc(self):
        return self

I = ImaginaryUnit()

class ConstPi(Constant):
    """
    
    Usage
    ===== 
           pi -> Returns the mathematical constant pi 
           pi() -> Returns a numerical aproximation for pi
           
    Notes
    =====
        Can have an option precision (integer) for the number of digits 
        that will be returned. Default is set to 28
       
        pi() is a shortcut for pi.evalf()
    
    Further examples
    ================
        >>> pi
        pi

        >>> pi()
        3.141592653589793238462643383

        >>> pi(precision=109)
        3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148087

    """
    
    def __init__(self):
        Basic.__init__(self,
                       is_commutative = True, 
                       is_real = True, 
                       )

    def evalf(self, precision=28):
        """
        Compute PI to artibtrary precision using series developed by
        Chudnovsky brothers. This series converges extraordinarily
        rapidly, giving 14 decimal places per single iteration. 
        
        """
        
        A, B, C = 13591409, 545140134, 262537412640768000
        D = 68925893036108889235415629824000000
        
        decimal.getcontext().prec = precision + 14
        
        r = A / decimal.Decimal(C).sqrt()

        if (precision > 14):
            n = precision / 15 + 1
        
            b, c = B, C**3
            i, u, v, s = 1, 7, 4, -1
            f_6, f_3, f_1 = 720, 6, 1

            while i <= n:
                r += (s * f_6 * (A + b)) / (f_1**3 * f_3 * decimal.Decimal(c).sqrt())

                for k in range(u, u+6):
                    f_6 *= k
                
                for k in range(v, v+3):
                    f_3 *= k

                u, v = u+6, v+3
                b, i = b+B, i+1
                
                c, s, f_1 = c*D, s*(-1), f_1*i
                
        r = 1 / (12 * r)
                
        decimal.getcontext().prec -= 14

        return Real(+r) 

    def __str__(self):
        return "pi"
    
    def __latex__(self):
        return "\pi"
    
    def __pretty__(self):
        return prettyForm("pi", unicode=u"\u03C0", binding=prettyForm.ATOM)

pi=ConstPi()

def sign(x):
    """Return the sign of x, that is, 
    1 if x is positive, 0 if x == 0 and -1 if x is negative
    """
    if x < 0: return -1
    elif x==0: return 0
    else: return 1