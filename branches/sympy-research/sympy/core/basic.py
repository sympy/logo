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
        #if self.subs(p, Basic.Symbol('x',dummy=True))!=self:
        #    return True
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

    def count_ops(self, symbolic=True):
        """ Return the number of operations in expressions.

        Examples:
        >>> (1+a+b**2).count_ops()
        POW + 2 * ADD
        >>> (sin(x)*x+sin(x)**2).count_ops()
        ADD + MUL + POW + 2 * SIN
        """
        return Basic.Integer(len(self[:])-1) + sum([t.count_ops(symbolic=symbolic) for t in self])

    ###################################################################################
    ##################### EXPRESSION REPRESENTATION METHODS ###########################
    ###################################################################################

    def expand(self):
        if isinstance(self, Atom):
            return self
        return self.__class__(*[t.expand() for t in self], **self._assumptions)

    def normal(self):
        n, d = self.as_numer_denom()
        if isinstance(d, Basic.One):
            return n
        return n/d

    def as_base_exp(self):
        # a -> b ** e
        return self, Basic.One()

    def as_coeff_terms(self, x=None):
        # a -> c * t
        if x is not None:
            if not self.has(x):
                return self, []
        return Basic.One(), [self]

    def as_indep_terms(self, x):
        coeff, terms = self.as_coeff_terms()
        indeps = [coeff]
        new_terms = []
        for t in terms:
            if t.has(x):
                new_terms.append(x)
            else:
                indeps.append(x)
        return Mul(*indeps), Mul(*new_terms)

    def as_coeff_factors(self, x=None):
        # a -> c + f
        if x is not None:
            if not self.has(x):
                return self, []
        return Basic.Zero(), [self]

    def as_numer_denom(self):
        # a/b -> a,b
        base, exp = self.as_base_exp()
        coeff, terms = exp.as_coeff_terms()
        if coeff.is_negative:
            # b**-e -> 1, b**e
            return Basic.One(), base ** (-exp)
        return self, Basic.One()

    def as_expr_orders(self):
        """ Split expr + Order(..) to (expr, Order(..)).
        """
        l1 = []
        l2 = []
        if isinstance(self, Basic.Add):
            for f in self:
                if isinstance(f, Basic.Order):
                    l2.append(f)
                else:
                    l1.append(f)
        elif isinstance(self, Basic.Order):
            l2.append(self)
        else:
            l1.append(self)
        return Basic.Add(*l1), Basic.Add(*l2)

    ###################################################################################
    ##################### DERIVATIVE, INTEGRAL, FUNCTIONAL METHODS ####################
    ###################################################################################

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

    ###################################################################################
    ##################### SERIES, LEADING TERM, LIMIT, ORDER METHODS ##################
    ###################################################################################

    def series(self, x, n = 6):
        """
        Usage
        =====
            Return the Taylor series around 0 of self with respect to x until
            the n-th term (default n is 6).

        Notes
        =====
            For computing power series, use oseries() method.
        """
        x = Basic.sympify(x)
        return self.oseries(Basic.Order(x**n,x))

    def oseries(self, order):
        """
        Return the series of an expression upto given Order symbol.
        """
        order = Basic.Order(order)
        if isinstance(order, Basic.Zero):
            return self
        o = self.is_order
        if o is not None:
            if o.contains(order):
                return self
        if order.contains(self):
            return Basic.Zero()
        if len(order.symbols)>1:
            r = self
            for s in order.symbols:
                o = Basic.Order(order.expr, s)
                r = r.oseries(o)
            return r
        x = order.symbols[0]
        if not self.has(x):
            return self
        obj = self._eval_oseries(order)
        if obj is not None:
            obj2 = obj.expand()
            if obj2 != obj:
                return obj2.oseries(order)
            return obj2
        raise NotImplementedError('(%s).oseries(%s)' % (self, order))    

    def _eval_oseries(self, order):
        return

    def _compute_oseries(self, arg, order, taylor_term, unevaluated_func, correction = 0):
        """
        compute series sum(taylor_term(i, arg), i=0..n-1) such
        that order.contains(taylor_term(n, arg)). Assumes that arg->0 as x->0.
        """
        x = order.symbols[0]
        ln = Basic.Log()
        o = Basic.Order(arg*x, x)
        if isinstance(o, Basic.Zero):
            return unevaluated_func(arg)
        e = ln(order.expr)/ln(o.expr)
        n = e.limit(x,0) + 1 + correction
        if n.is_unbounded:
            # requested accuracy gives infinite series,
            # order is probably nonpolynomial e.g. O(exp(-1/x), x).
            return unevaluated_func(arg)
        n = int(n)
        assert n>=0,`n`
        l = []
        g = None
        for i in range(n+2):
            g = taylor_term(i, arg, g)
            g = g.oseries(order)
            l.append(g)
        return Basic.Add(*l)

    def limit(self, x, xlim, direction='<'):
        """ Compute limit x->xlim.
        """
        x = Basic.sympify(x)
        xlim = Basic.sympify(xlim)
        if not self.has(x): return self
        if isinstance(xlim, Basic.Infinity):
            return self.inflimit(x)
        var = Basic.Symbol(x.name+'_oo',dummy=True,positive=True,unbounded=True)
        if isinstance(xlim, Basic.NegativeInfinity): 
            return self.subs(x,-var).inflimit(var)
        if direction=='<':
            return self.subs(x, xlim+1/var).inflimit(var)
        if direction=='>':
            return self.subs(x, xlim-1/var).inflimit(var)
        raise ValueError("Limit direction must be < or > (got %s)" % (direction))

    def inflimit(self, x, _xoo_cache={}, _inflimit_cache={}):
        x = Basic.sympify(x)
        assert isinstance(x,Basic.Symbol),`x`
        if not self.has(x):
            return self
        try:
            xoo = _xoo_cache['xoo']
        except KeyError:
            xoo = _xoo_cache['xoo'] = Basic.Symbol('_oo', dummy=True, unbounded=True, positive=True)
        use_cache = True
        if not self.has(xoo):
            expr = self.subs(x, xoo)
        elif x==xoo:
            expr = self
        else:
            xoo = Basic.Symbol(x.name + '_oo', dummy=True, unbounded=True, positive=True)
            expr = self.subs(x, xoo)
            use_cache = False

        cache = _inflimit_cache
        if use_cache:
            try:
                return cache[expr]
            except KeyError:
                pass

        obj = expr._eval_inflimit(xoo)

        if obj is not None and not isinstance(obj, Basic.NaN):
            if use_cache:
                cache[expr] = obj
            return obj

        obj = expr._eval_mrv_inflimit(xoo)

        if use_cache:
            cache[expr] = obj
        return obj

    def _eval_mrv_inflimit(self, x):
        from limit import mrv2, rewrite_mrv_map, rewrite_expr, MrvSet
        expr_map = {}
        mrv_map = {}
        newexpr = mrv2(self, x, expr_map, mrv_map)
        if mrv_map.has_key(x):
            t = Basic.Temporary(unbounded=True, positive=True)
            return self.subs(S.Log(x),t).subs(x, S.Exp(t)).subs(t, x)._eval_mrv_inflimit(x)
        w = Basic.Symbol('w_0',dummy=True, positive=True, infinitesimal=True)
        germ, new_mrv_map = rewrite_mrv_map(mrv_map, x, w)
        new_expr = rewrite_expr(newexpr, germ, new_mrv_map, w)
        lt = new_expr.as_leading_term(w)
        if germ is not None:
            lt = lt.subs(S.Log(w), -germ.args[0])
        c,e = lt.as_coeff_exponent(w)
        assert not c.has(w),`c`
        if e==0:
            return c.inflimit(x)
        if e.is_positive:
            return S.Zero
        if e.is_negative:
            return S.Sign(c) * S.Infinity
        raise RuntimeError('Failed to compute as_mrv_leading_term(%s, %s), got lt=%s' % (self, x, lt))

    def as_leading_term(self, *symbols, **_cache):
        if len(symbols)>1:
            c = self
            for x in symbols:
                c = c.as_leading_term(x)
            return c
        elif not symbols:
            return self
        x = Basic.sympify(symbols[0])
        assert isinstance(x, Basic.Symbol),`x`
        r = _cache.get((self,x),None)
        if r is not None:
            return r
        if not self.has(x):
            _cache[(self,x)] = self
            return self
        expr = self.expand()
        obj = expr._eval_as_leading_term(x)
        if obj is not None:
            _cache[(self,x)] = obj
            return obj
        raise NotImplementedError('as_leading_term(%s, %s)' % (self, x))

    def as_coeff_exponent(self, x):
        """ c*x**e -> c,e where x can be any symbolic expression.
        """
        x = Basic.sympify(x)
        wc = Basic.Wild()
        we = Basic.Wild()
        c, terms = self.as_coeff_terms()
        p  = wc*x**we
        d = self.match(p)
        if d is not None:
            return d[wc], d[we]
        return self, Basic.Zero()

    def ldegree(self, x):
        x = Basic.sympify(x)
        c,e = self.as_leading_term(x).as_coeff_exponent(x)
        if not c.has(x):
            return e
        raise ValueError("cannot compute ldegree(%s, %s), got c=%s" % (self, x, c))

    ##########################################################################
    ##################### END OF BASIC CLASS #################################
    ##########################################################################

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

    def count_ops(self, symbolic=True):
        return Basic.Zero()

    def _eval_integral(self, s):
        if s==self:
            return self**2/2
        return self*s

    def _eval_defined_integral(self, s, a, b):
        if s==self:
            return (b**2-a**2)/2
        return self*(b-a)

    def _eval_oseries(self, order):
        # .oseries() method checks for order.contains(self)
        return self

    def _eval_inflimit(self, x):
        if self==x: return S.Infinity
        return self

    def _eval_as_leading_term(self, x):
        return self

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

class SingletonFactory:
    """
    A map between singleton classes and the corresponding instances.
    """
    def __getattr__(self, clsname):
        obj = Singleton.__dict__.get(clsname)
        if obj is None:
            cls = getattr(Basic, clsname)
            assert issubclass(cls, Singleton),`cls`
            obj = cls()
            setattr(self, clsname, obj)
        return obj

S = singleton = SingletonFactory()

import parser
