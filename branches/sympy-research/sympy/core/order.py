
from basic import Basic
from methods import ArithMeths, RelMeths

class Order(Basic, ArithMeths, RelMeths):
    """
    Represents O(f(x)) at the point x = 0.

    Definition
    ==========

    g(x) = O(f(x)) as x->a  if and only if
    |g(x)|<=M|f(x)| near x=a                     (1)

    In our case Order is for a=0. An equivalent way of saying (1) is:

    lim_{x->a}  |g(x)/f(x)|  < oo
    
    Let's illustrate it on the following example:

    sin x = x - x**3/3! + O(x**5)

    where in this case O(x**5) = x**5/5! - x**7/7! + .... and the definition
    of O means:

    |x**5/5! - x**7/7! + ....| <= M|x**5|      near x=0

    or equivalently:

    lim_{x->0} |x**5/5! - x**7/7! + .... / x**5| < oo

    which surely is true, because 
    
    lim_{x->0} |x**5/5! - x**7/7! + .... / x**5| = 1/5!


    So intuitively O(x**3) means (in our case): all terms x**3, x**4 and
    higher. But not x**2, x or 1.

    Examples:
    =========
    >>> from sympy import *
    >>> x = Symbol("x")
    >>> Order(x)
    O(x)
    >>> Order(x)*x
    O(x**2)
    >>> Order(x)-Order(x)
    O(x)

       External links
       --------------

         U{Big O notation<http://en.wikipedia.org/wiki/Big_O_notation>}
    """

    precedence = 70

    def __new__(cls, expr, *symbols, **assumptions):
        expr = Basic.sympify(expr)
        if symbols:
            symbols = map(Basic.sympify, symbols)
        else:
            symbols = list(expr.atoms(Basic.Symbol))
        symbols.sort(Basic.compare)
        obj = cls._evaluate(expr.expand(), *symbols)
        if obj is None:
            obj = Basic.__new__(cls, expr, *symbols, **assumptions)
        return obj

    @property
    def expr(self):
        return self._args[0]

    @property
    def symbols(self):
        return self._args[1:]

    def tostr(self, level = 0):
        r = 'O(%s)' % (self.expr.tostr())
        if self.precedence <= level:
            r = '(%s)' % (r)
        return r

    def torepr(self):
        return '%s%r' % (self.__class__.__name__, self[:])

    @staticmethod
    def _evaluate(expr, *symbols):
        if isinstance(expr, Order):
            return expr
        if isinstance(expr, Basic.Number) and not isinstance(expr, (Basic.One, Basic.Zero)):
            return Order(expr, *symbols)
        if isinstance(expr, Basic.Add):
            coeff, factors = expr.as_coeff_factors()
            return Basic.Add(*[Order(t,*symbols) for t in factors])
        if isinstance(expr, Basic.Mul):
            coeff, terms = expr.as_coeff_terms()
            l = []
            for t in terms:
                if t.has(*symbols):
                    l.append(t)
            if len(l)!=len(terms) or not isinstance(coeff, Basic.One):
                return Order(Basic.Mul(*l), *symbols)
        return

    def _eval_power(b, e):
        if isinstance(e, Basic.Number):
            return Order(b.expr ** e, *b.symbols)
        return

    def as_expr_symbols(self, order_symbols):
        if order_symbols is None:
            order_symbols = self.symbols
        else:
            for s in self.symbols:
                if s not in order_symbols:
                    order_symbols = order_symbols + (s,)
        return self.expr, order_symbols
