
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

    Properties:

      g(x) = O(f(x)) as x->0  <->  |g(x)|<=M|f(x)| near x=0  <->  lim_{x->0}  |g(x)/f(x)|  < oo

      g(x,y) = O(f(x,y))  <->  lim_{x,y->0}  |g(x,y)/f(x,y)|  < oo, will assume that limits commute.

       r = sqrt(x**2+y**2), lim_{r->0}  |g(x,y)/f(x,y)| < oo.
       x = a * r, y = b * r, a**2+b**2=1
       g(x,y) = O(f(a*r,b*r))
       
    
      f1(x)=O(g1(x)), f2(x)=O(g2(x))  -> f1(x)*f2(x)=O(g1(x)*g2(x))
      h(x)=f(x)O(g(x)) -> h(x)=O(f(x)*g(x))
      O(g1(x))+O(g2(x)) = O(max(|g1(x)|,|g2(x)|))
      h(x)=f(x)+O(g(x)) -> h(x)=O(f(x)+g(x))
      f1(x), f2(x) in O(g(x)) -> f1(x)+f2(x) in O(g(x))
      O(k*g(x)) = O(g(x)), k!=0

      O = Order
      Order(f(x),x) == O(f(x)), x->0
      Order(f(x),x) * g(x) -> Order(f(x)*g(x))
      Order(f(x),x) ** g -> Order(f(x)**g)
      Order(f(x),x) + g(x) -> Order(f(x),x) if leading order of g(x) is Order(f(x),x)
      Order(k*f(x),x) -> Order(f(x),x), k!=0
      Order(k) -> Order(1)
      Order(0) -> raise ValueError

      
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

    @staticmethod
    def _eval_add(expr, other):
        assert isinstance(other, Order),`other`
        if isinstance(expr, Basic.Add):
            return expr + other
        if isinstance(expr, Order):
            l = list(expr.symbols)
            l = l + [s for s in other.symbols if s not in l]
            e = expr.expr / other.expr
            for s in l:
                r = e.subs(s,0)

    def add_orders(self, other):
        if isinstance(other, Order):
            common_symbols = [s for s in self.symbols if s in other.symbols]
            if not common_symbols:
                return False
            s1 = Order(self.expr, *common_symbols)
            s2 = Order(other.expr, *common_symbols)
            
