
from basic import Basic
from methods import ArithMeths, RelMeths, NoRelMeths

class Pow(Basic, ArithMeths, RelMeths):

    precedence = Basic.Pow_precedence

    def __new__(cls, a, b, **assumptions):
        a = Basic.sympify(a)
        b = Basic.sympify(b)
        if isinstance(b, Basic.Zero):
            return Basic.One()
        if isinstance(b, Basic.One):
            return a
        obj = a._eval_power(b)
        if obj is None:
            obj = Basic.__new__(cls, a, b, **assumptions)
        return obj

    @property
    def base(self):
        return self._args[0]

    @property
    def exp(self):
        return self._args[1]

    def _eval_power(self, other):
        if isinstance(other, Basic.Number):
            if isinstance(self.exp, Basic.Number):
                # (a ** 2) ** 3 -> a ** (2 * 3)
                return Pow(self.base, self.exp * other)
            if isinstance(other, Basic.Integer):
                # (a ** b) ** 3 -> a ** (3 * b)
                return Pow(self.base, self.exp * other)
        if other.atoms(Basic.Wild):
            return Pow(self.base, self.exp * other)
        return

    def _eval_is_commutative(self):
        c1 = self.base.is_commutative
        if c1 is None: return
        c2 = self.base.is_commutative
        if c2 is None: return
        return c1 and c2

    def _eval_is_comparable(self):
        c1 = self.base.is_comparable
        if c1 is None: return
        c2 = self.base.is_comparable
        if c2 is None: return
        return c1 and c2

    def _eval_is_positive(self):
        if self.base.is_positive:
            if self.exp.is_real:
                return True
        elif self.base.is_real:
            if self.exp.is_even:
                return True
            if self.exp.is_odd:
                return False

    def _eval_is_integer(self):
        c1 = self.base.is_integer
        if c1 is None: return
        c2 = self.exp.is_integer
        if c2 is None: return
        if c1 and c2 and self.exp.is_positive:
            return True

    def _eval_is_real(self):
        c1 = self.base.is_real
        if c1 is None: return
        c2 = self.exp.is_real
        if c2 is None: return
        if c1 and c2:
            if self.base.is_positive:
                return True
            if self.base.is_negative:
                if self.exp.is_integer:
                    return True
    def _eval_is_even(self):
        if not (self.is_integer and self.exp.is_positive): return
        return self.base.is_even

    def _eval_is_bounded(self):
        if self.exp.is_negative:
            if self.is_infinitesimal:
                return False
            return True
        c1 = self.base.is_bounded
        if c1 is None: return
        c2 = self.exp.is_bounded
        if c2 is None: return
        if c1 and c2: return True

    def tostr(self, level=0):
        precedence = self.precedence
        b = self.base.tostr(precedence)
        if isinstance(self.exp, Basic.NegativeOne):
            r = '1 / %s' % (b)
        else:
            r = '%s ** %s' % (b,self.exp.tostr(precedence))
        if precedence<=level:
            return '(%s)' % (r)
        return r

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        if self==old: return new
        if isinstance(old, self.__class__) and self.base==old.base:
            coeff1,terms1 = self.exp.as_coeff_terms()
            coeff2,terms2 = old.exp.as_coeff_terms()
            if terms1==terms2: return new ** (coeff1/coeff2) # (x**(2*y)).subs(x**(3*y),z) -> z**(2/3*y)
        if isinstance(old, Basic.ApplyExp):
            coeff1,terms1 = old.args[0].as_coeff_terms()
            coeff2,terms2 = (self.exp * Basic.Log()(self.base)).as_coeff_terms()
            if terms1==terms2: return new ** (coeff1/coeff2) # (x**(2*y)).subs(exp(3*y*log(x)),z) -> z**(2/3*y)
        return self.base.subs(old, new) ** self.exp.subs(old, new)

    def as_base_exp(self):
        if isinstance(self.base, Basic.Rational) and self.base.p==1:
            return 1/self.base, -self.exp
        return self.base, self.exp

    def expand(self):
        """
        (a*b)**n -> a**n * b**n
        (a+b+..) ** n -> a**n + n*a**(n-1)*b + .., n is positive integer
        """
        base = self.base.expand()
        exponent = self.exp.expand()
        result = base ** exponent
        if isinstance(result, Pow):
            base = result.base
            exponent = result.exp
        else:
            return result
        if isinstance(exponent, Basic.Integer):
            if isinstance(base, Basic.Mul):
                return Basic.Mul(*[t**exponent for t in base])
            if exponent.is_positive and isinstance(base, Basic.Add):
                m = int(exponent)
                if base.is_commutative:
                    p = []
                    order_terms = []
                    for o in base:
                        if isinstance(o, Basic.Order):
                            order_terms.append(o)
                        else:
                            p.append(o)
                    if order_terms:
                        # (f(x) + O(x^n))^m -> f(x)^m + m*f(x)^{m-1} *O(x^n)
                        f = Basic.Add(*p)
                        fm1 = (f**(m-1)).expand()
                        return (f*fm1).expand() + m*fm1*Basic.Add(*order_terms)
                ## Consider polynomial
                ##   P(x) = sum_{i=0}^n p_i x^k
                ## and its m-th exponent
                ##   P(x)^m = sum_{k=0}^{m n} a(m,k) x^k
                ## The coefficients a(m,k) can be computed using the
                ## J.C.P. Miller Pure Recurrence [see D.E.Knuth,
                ## Seminumerical Algorithms, The art of Computer                
                ## Programming v.2, Addison Wesley, Reading, 1981;]:
                ##  a(m,k) = 1/(k p_0) sum_{i=1}^n p_i ((m+1)i-k) a(m,k-i),
                ## where a(m,0) = p_0^m.
                    n = len(p)-1
                    cache = {0: p[0] ** m}
                    p0 = [t/p[0] for t in p]
                    for k in range(1, m * n + 1):
                        a = []
                        for i in range(1,n+1):
                            if i<=k:
                                a.append(Basic.Mul(Basic.Rational((m+1)*i-k, k),
                                                   p0[i], cache[k-i]).expand())
                        cache[k] = Basic.Add(*a)
                    return Basic.Add(*cache.values())
                else:
                    if m==2:
                        p = base[:]
                        return Basic.Add(*[t1*t2 for t1 in p for t2 in p])
                    return Basic.Mul(base, Pow(base, m-1).expand()).expand()                        
        return result

    def _eval_derivative(self, s):
        dbase = self.base.diff(s)
        dexp = self.exp.diff(s)
        return self * (dexp * Basic.Log()(self.base) + dbase * self.exp/self.base)

    def _calc_as_coeff_leadterm(self, x):
        if not self.exp.has(x):
            c,e,f = self.base.as_coeff_leadterm(x)
            return c**self.exp, e*self.exp, f*self.exp
        if isinstance(self.exp, Basic.Add):
            return Basic.Mul._seq_as_coeff_leadterm([(self.base**f).as_coeff_leadterm(x) for f in self.exp])
        raise NotImplementedError("leading term of %s at %s=0" % (self, x))

    evalf = Basic._seq_evalf

    def _calc_splitter(self, d):
        if d.has_key(self):
            return d[self]
        base = self.base._calc_splitter(d)
        exp = self.exp._calc_splitter(d)
        if isinstance(exp, Basic.Integer):
            if abs(exp.p)>2:
                n = exp.p//2
                r = exp.p - n
                if n!=r:
                    p1 = (base ** n)._calc_splitter(d)
                    p2 = (base ** r)._calc_splitter(d)
                    r = p1*p2
                else:
                    r = (base ** n)._calc_splitter(d) ** 2
            elif exp.p==-2:
                r = (1/base)._calc_splitter(d) ** 2
            else:
                r = base ** exp
        else:
            r = base ** exp
        if d.has_key(r):
            return d[r]
        s = d[r] = Basic.Temporary()
        return s

    def count_ops(self, symbolic=True):
        if symbolic:
            return Basic.Add(*[t.count_ops(symbolic) for t in self[:]]) + Basic.Symbol('POW')
        return Basic.Add(*[t.count_ops(symbolic) for t in self[:]]) + 1

    def _eval_integral(self, s):
        if not self.exp.has(s):
            if self.base==s:
                n = self.exp+1
                return self.base ** n/n
            y = Basic.Symbol('y',dummy=True)
            x,ix = self.base.solve4linearsymbol(y,symbols=set([s]))
            if isinstance(x, Basic.Symbol):
                dx = 1/self.base.diff(x)
                if not dx.has(s):
                    return (y**self.exp*dx).integral(y).subs(y, self.base)
        
    def _eval_defined_integral(self, s, a, b):
        if not self.exp.has(s):
            if self.base==s:
                n = self.exp+1
                return (b**n-a**n)/n
            x,ix = self.base.solve4linearsymbol(s)
            if isinstance(x, Basic.Symbol):
                dx = ix.diff(x)
                if isinstance(dx, Basic.Number):
                    y = Basic.Symbol('y',dummy=True)
                    return (y**self.exp*dx).integral(y==[self.base.subs(s,a), self.base.subs(s,b)])

    def as_numer_denom(self):
        base, exp = self.as_base_exp()
        c,t = exp.as_coeff_terms()
        n,d = base.as_numer_denom()
        if c.is_negative:
            exp = -exp
            n,d = d,n
        return n ** exp, d ** exp

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        Basic.matches.__doc__
        if evaluate:
            pat = pattern
            for old,new in repl_dict.items():
                pat = pat.subs(old, new)
            if pat!=pattern:
                return pat.matches(expr, repl_dict)
        expr = Basic.sympify(expr)
        b, e = expr.as_base_exp()
        d = repl_dict.copy()
        d = pattern.base.matches(b, d, evaluate=False)
        if d is None:
            return None
        d = pattern.exp.matches(e, d, evaluate=True)
        if d is None:
            return Basic.matches(pattern, expr, repl_dict, evaluate)
        return d

    def _eval_oseries(self, order):
        """
        f**g + O(h) == (f+O(k))**g -> .. -> f**g + O(f**(g-1)*k), hence O(k)==O(h*f**(1-g)).
        If f->0 as x->0 then
        """
        x = order.symbols[0]
        e = self.exp
        b = self.base
        ln = Basic.Log()
        exp = Basic.Exp()
        if e.has(x):
            return exp(e * ln(b)).oseries(order)
        if b==x: return self
        b0 = b.limit(x,0)
        if isinstance(b0, Basic.Zero) or b0.is_unbounded:
            lt = b.as_leading_term(x)
            o = order * lt**(1-e)
            bs = b.oseries(o)
            r = (bs**e).expand()
            if isinstance(r, Basic.Add):
                r = r.oseries(order)
            return r
        o = order * (b0**-e)
        # b -> b0 + (b-b0) -> b0 * (1 + (b/b0-1))
        z = (b/b0-1)
        return self._compute_oseries(z, o, self.taylor_term, lambda z: 1+z) * b0**e
        
    def as_leading_term(self, x):
        if not self.exp.has(x):
            return self.base.as_leading_term(x) ** self.exp
        return Basic.Exp()(self.exp * Basic.Log()(self.base)).as_leading_term(x)

    def taylor_term(self, n, x, *previous_terms): # of (1+x)**e
        if n<0: return Basic.Zero()
        x = Basic.sympify(x)
        return Basic.Binomial()(self.exp, n) * x**n
