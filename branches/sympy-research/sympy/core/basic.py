"""Base class for all objects in sympy"""

import decimal
from basic_methods import BasicMeths

class Basic(BasicMeths):
    """
    Base class for all objects in sympy.
    """

    # for backward compatibility, will be removed:
    is_number = False
    def hash(self): return self.__hash__()
    #

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
            return real + Basic.ImaginaryUnit() * imag
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
        if self==old:
            return new
        return self.__class__(*[s.subs(old, new) for s in self])

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

    def has(self, *patterns):
        """
        Return True if self has any of the patterns.
        """
        if len(patterns)>1:
            for p in patterns:
                if self.has(p):
                    return True
            return False
        elif not patterns:
            raise TypeError("has() requires at least 1 argument (got none)")
        p = Basic.sympify(patterns[0])
        if p.matches(self) is not None:
            return True
        for e in self:
            if e.has(p):
                return True
        return False

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

    def _eval_eq_nonzero(self, other):
        return

    def diff(self, *symbols, **assumptions):
        new_symbols = []
        for s in symbols:
            s = Basic.sympify(s)
            if isinstance(s, Basic.Integer) and new_symbols:
                last_s = new_symbols[-1]
                i = int(s)
                new_symbols += [last_s] * (i-1)
            elif isinstance(s, Basic.Symbol):
                new_symbols.append(s)
            else:
                raise TypeError("diff argument must be Symbol|Integer instance (got %s)" % (s.__class__.__name__))
        return Basic.Derivative(self, *new_symbols, **assumptions)

    def fdiff(self, *indices):
        return Basic.FApply(Basic.FDerivative(*indices), self)

    def __call__(self, *args):
        return Basic.Apply(self, *args)

    def subs_dict(self, old_new_dict):
        r = self
        for old,new in old_new_dict.items():
            r = r.subs(old,new)
        return r

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        """
        Helper method for match() - switches the pattern and expr.

        Can be used to solve linear equations:

          >>> x=Wild('x')
          >>> (a+b*x).matches(0)
          {x_: -a * b ** (-1)}

        """
        if evaluate:
            pat = pattern
            for old,new in repl_dict.items():
                pat = pat.subs(old, new)
            if pat!=pattern:
                return pat.matches(expr, repl_dict)
        expr = Basic.sympify(expr)
        if not isinstance(expr, pattern.__class__):
            return None
        if len(expr[:]) != len(pattern[:]):
            return None
        if len(pattern[:])==0:
            if pattern==expr:
                return repl_dict
            return None
        d = repl_dict.copy()
        i = 0
        for p,e in zip(pattern, expr):
            d = p.matches(e, d, evaluate=not i)
            i += 1
            if d is None:
                return None
        return d

    def match(self, pattern, syms = None):
        """
        Pattern matching.

        Wild symbols match all.

        Return None when expression (self) does not match
        with pattern. Otherwise return a dictionary such that

          pattern.subs_dict(self.match(pattern)) == self

        """
        # syms argument is used for backward compatibility, will be removed
        if syms is not None:
            pat = pattern
            wilds = []
            for s in syms:
                w = Basic.Wild(s.name)
                pat = pat.subs(s,w)
                wilds.append(w)
            result = self.match(pat)
            if result is not None:
                for w,s in zip(wilds, syms):
                    result[s] = result[w]
                    del result[w]
            return result
        #
        return Basic.sympify(pattern).matches(self, {})

    def _calc_leadterm(self, x):
        raise NotImplementedError("%s._calc_leadterm()" % (self.__class__.__name__))

    def solve4linearsymbol(eqn, rhs):
        """ Solve equation
          eqn == rhs
        with respect to some linear symbol in eqn.
        Returns (symbol, solution). If eqn is nonlinear
        with respect to all symbols, then return
        trivial solution (eqn, rhs).
        """
        if isinstance(eqn, Basic.Symbol):
            return (eqn, rhs)
        symbols = eqn.atoms(type=Basic.Symbol)
        if symbols:
            # find  symbol
            for s in symbols:
                deqn = eqn.diff(s)
                if isinstance(deqn.diff(s), Basic.Zero):
                    # eqn = a + b*c, a=eqn(c=0),b=deqn(c=0)
                    return s, (rhs - eqn.subs(s,0))/deqn.subs(s,0)
        # no linear symbol, return trivial solution
        return eqn, rhs

    def leadterm(self, x):
        """Returns the leading term c0*x^e0 of the power series 'self' in x
        with the lowest power of x in a form (c0,e0).
        """
        x = Basic.sympify(x)
        if not isinstance(x, Basic.Symbol):
            # f(x).leadterm(1+3*x) -> f((z-1)/3).leadterm(z)
            z = Basic.Symbol('z',dummy=True)
            x1, s1 = x.solve4linearsymbol(z)
            return self.subs(x1, s1).leadterm(z)
        if not self.has(x):
            return (self,Basic.Zero())
        if self==x:
            return Basic.One(),Basic.One()
        result = self._calc_leadterm(x)
        if result is not None:
            return result
        raise ValueError("unable to compute leading term of %s at %s=0" % (self, x))

    def ldegree(self, *symbols):
        s = Basic.Zero()
        c0 = self
        for x in symbols:
            c0,e0 = c0.leadterm(x)
            s += e0
        return s

    def leading_term(self, *symbols):
        l = []
        c0 = self
        for x in symbols:
            c0,e0 = c0.leadterm(x)
            l.append(x ** e0)
        l.append(c0)
        return Basic.Mul(*l)

    def taylor_series(self, x, n=6):
        """
        Usage
        =====
            Return the Taylor series around 0 of self with respect to x until
            the n-th term (default n is 6).
        
        Examples
        ========

        """
        f = self
        s = f.subs(x,0)
        j = 1
        for i in range(1,n):
            j *= i
            f = f.diff(x)
            s += (f.subs(x,0)/j)*(x**i)
        if s==self:
            return s
        return s + Basic.Order(x**n)

    def series(self, *args, **parameters):
        kind = parameters.pop('kind','taylor')
        mth = getattr(self, kind+'_series', None)
        if mth is None:
            raise ValueError("%s does not define %s_series method" % (self.__class__,kind))
        return mth(*args, **parameters)


class Atom(Basic):

    precedence = 1000

    def _eval_derivative(self, s):
        if self==s: return Basic.One()
        return Basic.Zero()

    def pattern_match(pattern, expr, repl_dict):
        if pattern==expr:
            return repl_dict
        return None

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


