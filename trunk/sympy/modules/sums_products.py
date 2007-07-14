from sympy import Basic, Symbol, Add, Mul, Pow, Rational, oo, simplify

class Sum(Basic):
    """
    Symbolic summation with a variable number of terms

    Sum(f, (i, a, b)) represents \sum_{i=a}^b f(i)
    """
    def __init__(self, f, (i, a, b)):
        Basic.__init__(self)
        assert isinstance(i, Symbol)
        self.i = i
        self.f = self.sympify(f)
        self.a = self.sympify(a)
        self.b = self.sympify(b)

    def __str__(self):
        return "sum_{%s=%s}^{%s} %s" % (self.i, self.a, self.b, self.f)

    def eval(self):
        f, i, a, b = self.f, self.i, self.a, self.b

        # Exploit the linearity of the sum
        if not f.has(i):
            return f*(b-a+1)
        if isinstance(f, Mul):
            L, R = f.getab()
            if not L.has(i): return L*Sum(R, (i,a,b))
            if not R.has(i): return R*Sum(L, (i,a,b))
        if isinstance(f, Add):
            L, R = f.getab()
            lsum = Sum(L, (i,a,b))
            rsum = Sum(R, (i,a,b))
            if not (isinstance(lsum, Sum) and isinstance(rsum, Sum)):
                return lsum + rsum

        # Polynomial terms with Faulhaber's formula
        if f == i:
            f = Pow(i, 1, evaluate=False) # TODO: match should handle this
        p = Symbol('p', dummy=True)
        e = f.match(i**p, [p])
        if e != None and not p.has(i):
            c = p.subs_dict(e)
            if c.is_integer and c >= 0:
                from sympy.modules.specfun import bernoulli_poly as B
                return ((B(c+1, b+1)-B(c+1, a))/(c+1)).expand()

        # Geometric terms
        if isinstance(f, Pow):
            r, k = f[:]
            if not r.has(i) and k == i:
                # TODO: Pow should be able to simplify x**oo depending
                # on whether |x| < 1 or |x| > 1 for non-rational x
                if b == oo and isinstance(r, Rational) and abs(r) < 1:
                    return r**a / (1-r)
                else:
                    return (r**a - r**(b+1)) / (1-r)

        # Should nothing else works, use brute force if possible
        if isinstance(a, Rational) and a.is_integer and \
           isinstance(b, Rational) and b.is_integer:
            s = 0
            for j in range(a, b+1):
                s += f.subs(i, j)
            return s

        return self

# TODO: implement me
class Product(Basic):
    """
    Symbolic product with a variable number of factors

    Product(f, (i, a, b)) represents \prod_{i=a}^b f(i)
    """

    def __init__(self, f, (i, a, b)):
        Basic.__init__(self)
        assert isinstance(i, Symbol)
        self.i = i
        self.f = self.sympify(f)
        self.a = self.sympify(a)
        self.b = self.sympify(b)

