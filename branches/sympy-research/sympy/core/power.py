
from basic import Basic
from methods import ArithMeths, RelMeths, NoRelMeths

class Pow(Basic, ArithMeths, RelMeths):

    precedence = 60

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
        return

    def _calc_commutative(self):
        return self.base.is_commutative and self.exp.is_commutative

    def tostr(self, level=0):
        precedence = self.precedence
        r = '%s ** %s' % (self.base.tostr(precedence),
                          self.exp.tostr(precedence))
        if precedence<=level:
            return '(%s)' % (r)
        return r

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        if self==old: return new
        #elif exp(self.exp * log(self.base)) == old: return new
        return self.base.subs(old, new) ** self.exp.subs(old, new)

    def as_base_exp(self):
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
                    p = base[:]
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

