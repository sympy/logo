"""Base class for all objects in sympy"""

import decimal
from basic_methods import BasicMeths

class Basic(BasicMeths):
    """
    Base class for all objects in sympy.
    """

    def __new__(cls, *args, **assumptions):
        obj = object.__new__(cls)
        obj._assumptions = assumptions.copy()
        obj._mhash = None # will be set by BasicMeths.__hash__ method.
        obj._args = args  # all items in args must be Basic objects
        return obj

    @staticmethod
    def sympify(a):
        """
        Usage
        =====
            Converts an arbitrary expression to a type that can be used
            inside sympy. For example, it will convert python int's into
            instance of sympy.Rational, floats into intances of sympy.Real, etc.
            
        Notes
        =====
            It currently accepts as arguments: 
                - any object defined in sympy (except maybe matrices [TODO])
                - standard numeric python types: int, long, float, Decimal
                - strings (like "0.09" or "2e-19")
            
            If the argument is already a type that sympy understands, it will do
            nothing but return that value - this can be used at the begining of a
            method to ensure you are workint with the corerct type. 
            
        Examples
        ========
            >>> def is_real(a):
            ...     a = Basic.sympify(a)
            ...     return a.is_real
            >>> is_real(2.0)
            True
            >>> is_real(2)
            True
            >>> is_real("2.0")
            True
            >>> is_real("2e-45")
            True
        """
        if isinstance(a, Basic):
            return a
        if isinstance(a, bool):
            raise NotImplementedError("bool support")
        if isinstance(a, (int, long)):
            return Basic.Integer(a)
        if isinstance(a, (float, decimal.Decimal)):
            return Basic.Real(a)
        if isinstance(a, complex):
            real, imag = Basic.sympify(a.real), Basic.sympify(a.imag)
            return real + Basic.I * imag
        if isinstance(a, str):
            return parser.Expr(a).tosymbolic()
        raise ValueError("%s must be a subclass of Basic" % (`a`))

    def atoms(self, type=None):
        """Returns the atoms that form current object. 
        
        Example: 
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> y = Symbol('y')
        >>> (x+y**2+ 2*x*y).atoms()
        set([2, x, y])
        
        You can also filter the results by a given type of object
        >>> (x+y+2+y**2*sin(x)).atoms(type=Symbol)
        set([x, y])
        
        >>> (x+y+2+y**2*sin(x)).atoms(type=Number)
        set([2])
        """
        result = set()
        if isinstance(self, Atom):
            if type is None or isinstance(self, type):
                result.add(self)
        else:
            for obj in self:
                result = result.union(obj.atoms(type=type))
        return result

    def subs(self, old, new):
        """Substitutes an expression old -> new."""
        if self==old:
            return Basic.sympify(new)
        return self

    def _seq_subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        r = self.__class__(*[s.subs(old, new) for s in self])
        if r==self:
            r = self
        return r

    def _seq_evalf(self):
        return self.__class__(*[s.evalf() for s in self])

    def expand(self):
        if isinstance(self, Atom):
            return self
        return self.__class__(*[t.expand() for t in self], **self._assumptions)

    def as_base_exp(self):
        # a -> b ** e
        return self, Basic.One()

    def as_coeff_terms(self):
        # a -> c * t
        return Basic.One(), [self]

    def as_coeff_factors(self):
        # a -> c + f
        return Basic.Zero(), [self]

    def has(self, *symbols):
        if len(symbols)>1:
            for s in symbols:
                if self.has(s):
                    return True
            return False
        elif not symbols:
            raise TypeError("has() requires at least 1 argument (got none)")
        s = Basic.sympify(symbols[0])
        return not self.subs(s,s.as_dummy())==self

    def _eval_derivative(self, s):
        return

    def _eval_apply(self, *args, **assumptions):
        return

    def _eval_fapply(self, *args, **assumptions):
        return

    def _eval_fpower(b, e):
        return

    def _eval_apply_power(self,b,e):
        return

    def _eval_apply_evalf(self,*args):
        return

    def diff(self, *symbols):
        return Basic.Derivative(self, *symbols)

    def fdiff(self, *indices):
        return Basic.FApply(Basic.FDerivative(*indices), self)

    def __call__(self, *args):
        return Basic.Apply(self, *args)

    def order(self, s):
        if isinstance(self, Atom):
            if self==s:
                return Basic.Order(s,s)
            return Basic.Order(1,s)
        expr = self
        r = expr.subs(s, 0)
        n = 0
        while not isinstance(r, Basic.Zero):
            expr = expr.diff(s)
            r = expr.subs(s, 0)
            n += 1
        return Basic.Order(s**n, s)

class Atom(Basic):

    precedence = 1000

    def _eval_derivative(self, s):
        if self==s: return Basic.One()
        return Basic.Zero()


class Singleton(Basic):
    """ Singleton object.
    """

    def __new__(cls, *args, **assumptions):
        # if you need to overload __new__, then
        # use the same code as below to ensure
        # that only one instance of Singleton
        # class is created.
        obj = Singleton.__dict__.get(cls.__name__)
        if obj is None:
            obj = Basic.__new__(cls,*args,**assumptions)
            setattr(Singleton, cls.__name__, obj)
        return obj

import parser
