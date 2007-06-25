
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
    ===========

      g(x) = O(f(x)) as x->0  <->  |g(x)|<=M|f(x)| near x=0  <->  lim_{x->0}  |g(x)/f(x)|  < oo

      g(x,y) = O(f(x,y))  <->  lim_{x,y->0}  |g(x,y)/f(x,y)|  < oo, will assume that limits commute.

    Notes:
    ======
    
      In O(f(x),x) the expression f(x) is assumed to have a leading term.
      O(f(x),x) is automatically transformed to O(f(x).leading_term(x),x).
      O(expr*f(x),x) is O(f(x),x)
      O(expr,x) is O(1,e)
      O(0, x) is 0.

      Multivariate O is also supported:
        O(f(x,y),x,y) is transformed to O(f(x,y).leading_term(x,y).leading_term(y), x, y)

      If O is used with only expression argument then the symbols are
      all symbols in the expression.
    """

    precedence = 70

    _cache = {}

    def __new__(cls, expr, *symbols, **assumptions):
        expr = Basic.sympify(expr)
        if symbols:
            symbols = map(Basic.sympify, symbols)
        else:
            symbols = list(expr.atoms(Basic.Symbol))
        symbols.sort(Basic.compare)
        if isinstance(expr, Order):
            new_symbols = list(expr.symbols)
            for s in symbols:
                if s not in new_symbols:
                    new_symbols.append(s)
            if len(new_symbols)==len(expr.symbols):
                return expr
            symbols = new_symbols
        elif symbols:
            symbol_map = {}
            new_symbols = []
            for s in symbols:
                if isinstance(s, Basic.Symbol):
                    new_symbols.append(s)
                    continue
                z = Basic.Symbol('z',dummy=True)
                x1,s1 = s.solve4linearsymbol(z)
                expr = expr.subs(x1,s1)
                symbol_map[z] = s
                new_symbols.append(z)
            if symbol_map:
                r = Order(expr, *new_symbols, **assumptions)
                expr = r.expr.subs_dict(symbol_map)
                symbols = []
                for s in r.symbols:
                    if symbol_map.has_key(s):
                        symbols.append(symbol_map[s])
                    else:
                        symbols.append(s)
            else:
                if isinstance(expr, Basic.Add):
                    expr = Basic.Add(*[Order(f,*symbols, **assumptions).expr for f in expr])
                else:
                    expr = expr.leading_term(*symbols)
                    coeff, terms = expr.as_coeff_terms()
                    if isinstance(coeff, Basic.Zero):
                        return coeff
                    expr = Basic.Mul(*[t for t in terms if t.has(*symbols)])
        elif not isinstance(expr, Basic.Zero):
            expr = Basic.One()
        if isinstance(expr, Basic.Zero):
            return expr
        symbols = tuple([s for s in symbols if expr.has(s)])

        cache = Order._cache.get(symbols,[])
        for o in cache:
            if o.expr==expr:
                return o
        obj = Basic.__new__(cls, expr, *symbols, **assumptions)
        Order._update_cache(obj, symbols)
        return obj

    @staticmethod
    def _update_cache(obj, symbols):
        cache = Order._cache.get(symbols,[])
        try: return cache.index(obj)
        except ValueError: pass
        assert isinstance(obj, Order),`obj`        
        i = -1
        for o in cache:
            i += 1
            l = obj.expr/o.expr
            for s in symbols:
                l = l.limit(s,0,direction='<')
            if l.is_unbounded:
                cache.insert(i,obj)
                break
            if l.is_bounded:
                continue
            raise NotImplementedError("failed to determine the inclusion relation between %s and %s" % (o, obj))
        else:
            cache.append(obj)
        Order._cache[symbols] = cache
        return cache.index(obj)

    @property
    def expr(self):
        return self._args[0]

    @property
    def symbols(self):
        return self._args[1:]

    def tostr(self, level = 0):
        r = 'O(%s)' % (', '.join([s.tostr() for s in self]))
        if self.precedence <= level:
            r = '(%s)' % (r)
        return r

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

    def contains(self, expr):
        if isinstance(expr, Order):
            symbols = self.symbols
            for s in expr.symbols:
                if s not in symbols:
                    symbols = symbols + (s,)
            Order._update_cache(self, symbols) # make sure that expr is in proper cache
            i2 = Order._update_cache(expr, symbols)
            i1 = Order._update_cache(self, symbols)
            return i1<=i2
        obj = Order(expr, *expr.atoms(Basic.Symbol))
        return self.contains(obj)

    def subs(self, old, new):
        old = Basic.sympify(old)
        if self==old:
            return Basic.sympify(new)
        return Order(self.expr.subs(old, new), *self.symbols)

    def _calc_leadterm(self, x):
        return self.expr.leadterm(x)

    def _calc_splitter(self, d):
        return Basic.Zero()

    def _calc_as_coeff_leadterm(self, x):
        return self.expr.as_coeff_leadterm(x)
            
Basic.singleton['O'] = lambda : Order
