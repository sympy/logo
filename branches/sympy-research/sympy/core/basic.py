"""Base class for all objects in sympy"""

import decimal
from basic_methods import BasicMeths

class Basic(BasicMeths):
    """
    Base class for all objects in sympy.
    """

    # for backward compatibility, will be removed:
    @property
    def is_number(self): return False
    def hash(self): return self.__hash__()
    #

    def __new__(cls, *args, **assumptions):
        obj = object.__new__(cls)
        obj.assume(**assumptions)
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
        if isinstance(a, (list,tuple)) and len(a)==2:
            return Basic.Interval(*a)
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

    def as_numer_denom(self):
        # a/b -> a,b
        base, exp = self.as_base_exp()
        coeff, terms = exp.as_coeff_terms()
        if coeff.is_negative:
            # b**-e -> 1, b**e
            return Basic.One(), base ** (-exp)
        return self, Basic.One()

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

    def _eval_integral(self, s):
        return

    def _eval_defined_integral(self, s, a, b):
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

    def _eval_apply_subs(self, *args):
        return

    def _calc_apply_positive(self, *args):
        return

    def _calc_apply_real(self, *args):
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
                raise TypeError(".diff() argument must be Symbol|Integer instance (got %s)" % (s.__class__.__name__))
        ret = Basic.Derivative(self, *new_symbols, **assumptions)
        return ret

    def fdiff(self, *indices):
        return Basic.FApply(Basic.FDerivative(*indices), self)

    def integral(self, *symbols, **assumptions):
        new_symbols = []
        for s in symbols:
            s = Basic.sympify(s)
            if isinstance(s, Basic.Integer) and new_symbols:
                last_s = new_symbols[-1]
                i = int(s)
                new_symbols += [last_s] * (i-1)
            elif isinstance(s, (Basic.Symbol, Basic.Equality)):
                new_symbols.append(s)
            else:
                raise TypeError(".integral() argument must be Symbol|Integer|Equality instance (got %s)" % (s.__class__.__name__))
        return Basic.Integral(self, *new_symbols, **assumptions)

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

    def solve4linearsymbol(eqn, rhs, symbols = None):
        """ Solve equation
          eqn == rhs
        with respect to some linear symbol in eqn.
        Returns (symbol, solution). If eqn is nonlinear
        with respect to all symbols, then return
        trivial solution (eqn, rhs).
        """
        if isinstance(eqn, Basic.Symbol):
            return (eqn, rhs)
        if symbols is None:
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

    def ldegree(self, *symbols):
        s = Basic.Zero()
        c0 = self
        for x in symbols:
            c0,e0,f0 = c0.as_coeff_leadterm(x)
            assert f0==0,`c0,e0,f0`
            s += e0
        return s

    def leading_term(self, *symbols):
        l = []
        c0 = self
        for x in symbols:
            c0,e0,f0 = c0.as_coeff_leadterm(x)
            l.append(x ** e0)
            l.append(Basic.Log()(x)**f0)
        l.append(c0)
        return Basic.Mul(*l)

    def _calc_as_coeff_leadterm(self, x):
        raise NotImplementedError("%s._calc_as_coeff_leadterm(x)" % (self.__class__.__name__))

    def as_coeff_leadterm(self, x):
        """ Return (c, e, f) such that the leading term of an expression is c * x**e * ln(x)**f.
        Here e,f are arbitrary real numbers.

        In the limiting process x->0+ the leading terms are ordered as
        follows
        
          0 < x**n < x < x**(1/n) < 1 < |ln(x)| < |ln(x)|^m < x**(-1/n) < 1/x < x**(-n) < +oo

        for any positive integers n,m.
        """
        x = Basic.sympify(x)
        if not isinstance(x, Basic.Symbol):
            # f(x).leadterm(1+3*x) -> f((z-1)/3).leadterm(z)
            z = Basic.Symbol('z',dummy=True)
            x1, s1 = x.solve4linearsymbol(z)
            res = self.subs(x1, s1).as_coeff_leadterm(z)
            return res

        numer, denom = self.as_numer_denom()

        if denom.has(x):
            nc,ne,nf = numer.as_coeff_leadterm(x)
            dc,de,df = denom.as_coeff_leadterm(x)
            res = nc/dc, ne-de, nf-df
            return res

        dc,de,df = denom, Basic.Zero(), Basic.Zero()
        assert dc!=0,`denom,dc`
        
        if not numer.has(x):
            nc,ne,nf = numer, Basic.Zero(), Basic.Zero()
        elif numer==x:
            nc,ne,nf = Basic.One(), Basic.One(), Basic.Zero()
        else:
            nc,ne,nf = numer._calc_as_coeff_leadterm(x)

        if nc==0 and not isinstance(numer, Basic.Zero):
            assert nf==0 and ne>=0,`nc,ne,nf`
            ne = Basic.Zero()
            r = numer
            while isinstance(nc, Basic.Zero):
                ne += 1
                r = r.diff(x)
                nc = r.subs(x,0)
            nc /= Basic.Factorial()(ne)

        res = nc/dc, ne-de, nf-df
        return res

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
        s = Basic.Zero()
        j = 1
        for i in range(0,n):
            if i:
                j *= i
                f = f.diff(x)
            t = (f.subs(x,0)/j)*(x**i)
            if t.has(Basic.NaN()):
                raise TypeError("cannot expand %s into Taylor series around %s=0, got nan term." % (self, x))                
            s += t
        if s==self:
            return s
        return s + Basic.Order(x**(n))

    def power_series(self, x, n=6):
        expr = self
        s = Basic.Zero()
        j = 1
        for i in range(0,n):
            ldi = expr.leading_term(x)
            expr = expr - ldi
            s += ldi
        return s
        
    def series(self, *args, **parameters):
        kind = parameters.pop('kind','taylor')
        mth = getattr(self, kind+'_series', None)
        if mth is None:
            raise ValueError("%s does not define %s_series method" % (self.__class__,kind))
        return mth(*args, **parameters)

    def _calc_splitter(self, d):
        if d.has_key(self):
            return d[self]
        r = self.__class__(*[t._calc_splitter(d) for t in self])
        if d.has_key(r):
            return d[r]
        s = d[r] = Basic.Temporary()
        return s

    def splitter(self):
        d = {}
        r = self._calc_splitter(d)
        l = [(s.dummy_index,s,e) for e,s in d.items()]
        l.sort()
        return [(s,e) for i,s,e in l]

    def count_ops(self):
        """ Return the number of operations in expressions.

        Examples:
        >>> (1+a+b**2).count_ops()
        POW + 2 * ADD
        >>> (sin(x)*x+sin(x)**2).count_ops()
        ADD + MUL + POW + 2 * SIN
        """
        return Basic.Integer(len(self[:])-1) + sum([t.count_ops() for t in self])

    def limit(self, x, xlim, direction='<', **assumptions):
        return Basic.Limit(self, x, xlim, direction=direction, **assumptions)

class Atom(Basic):

    precedence = 1000

    def _eval_derivative(self, s):
        if self==s: return Basic.One()
        return Basic.Zero()

    def pattern_match(pattern, expr, repl_dict):
        if pattern==expr:
            return repl_dict
        return None

    def as_numer_denom(self):
        return self, Basic.One()

    def _calc_splitter(self, d):
        return self

    def count_ops(self):
        return Basic.Zero()

    def _eval_integral(self, s):
        if s==self:
            return self**2/2
        return self*s

    def _eval_defined_integral(self, s, a, b):
        if s==self:
            return (b**2-a**2)/2
        return self*(b-a)

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
