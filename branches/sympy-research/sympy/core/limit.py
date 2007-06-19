
from basic import Basic
from methods import RelMeths, ArithMeths

class Limit(Basic, RelMeths, ArithMeths):
    """ Find the limit of the expression under process x->xlim.

    Limit(expr, x, xlim)
    Limit(expr, x==xlim)
    """

    def __new__(cls, expr, x, xlim, direction='<', **assumptions):
        expr = Basic.sympify(expr)
        x = Basic.sympify(x)
        xlim = Basic.sympify(xlim)
        if not isinstance(x, Basic.Symbol):
            raise ValueError("Limit 2nd argument must be Symbol instance (got %s)" % (x))
        assert isinstance(x, Basic.Symbol),`x`
        if not expr.has(x): return expr
        if isinstance(xlim, Basic.NegativeInfinity):
            return expr.subs(x,-x).limit(x,-xlim)
        if isinstance(xlim, Basic.Infinity):
            if x.is_positive and x.is_unbounded:
                result = MrvLimitInfProcess(expr,x).doit()
            else:
                dx = Basic.Symbol('xoo',dummy=True,positive=True,unbounded=True)
                new_expr = expr.subs(x,dx)
                result = MrvLimitInfProcess(new_expr,dx).doit()
        else:
            dx = Basic.Symbol('xoo',dummy=True,positive=True,unbounded=True)
            if direction=='<':
                result = MrvLimitInfProcess(expr.subs(x, xlim+1/dx),dx).doit()
            elif direction=='>':
                result = MrvLimitInfProcess(expr.subs(x, xlim-1/dx),dx).doit()
            else:
                raise ValueError("Limit direction must be < or > (got %s)" % (direction))
        if result is not None:
            return result

        obj = Basic.__new__(cls, expr, x, xlim, **assumptions)
        obj.direction = direction
        return obj

    def _hashable_content(self):
        return self._args + (self.direction,)

    @property
    def expr(self):
        return self._args[0]

    @property
    def var(self):
        return self._args[1]

    @property
    def varlim(self):
        return self._args[2]

    def tostr(self, level=0):
        if isinstance(self.varlim,(Basic.Infinity, Basic.NegativeInfinity)): s = ''
        elif self.direction=='<': s = '+'
        else: s = '-'    
        r = 'lim[%s->%s%s](%s)' % (self.var.tostr(), self.varlim.tostr(),s,self.expr.tostr())
        if self.precedence <= level: r = '(%s)' % (r)
        return r

class MrvLimitInfProcess(Basic):

    @property
    def expr(self):
        return self._args[0]

    @property
    def var(self):
        return self._args[1]

    def doit(self):
        c0, e0 = mrv_leadterm(self.expr, self.var)
        if isinstance(e0, Basic.Zero):
            assert not c0.has(self.var),`self,c0`
            return c0
        if e0.is_negative: return Basic.Sign()(c0) * Basic.Infinity()
        if e0.is_positive: return Basic.Zero()
        raise ValueError("Cannot determine sign of %s" % (e0))

mrv_moveup = lambda expr,x: expr.subs(x, Basic.Exp()(x))
mrv_set_moveup = lambda s,x: set([expr.subs(x, Basic.Exp()(x)) for expr in s])
mrv_movedown = lambda t,x: tuple([expr.subs(x, Basic.Log()(x)) for expr in t])


def mrv_leadterm(expr, x, mrv_set = None):
    """
    x -> (1,-1)
    """
    # x -> oo
    if not expr.has(x):
        return (expr, Basic.Zero())
    if mrv_set is None:
        mrv_set = mrv(expr, x)
    log = Basic.Log()
    if x in mrv_set:
        up_expr = mrv_moveup(expr,x)
        up_mrv_set = mrv_set_moveup(mrv_set,x)
        c,e = mrv_leadterm(up_expr,x,up_mrv_set)
        return c,e
    for f in mrv_set:
        assert isinstance(f, Basic.ApplyExp),`f`
    w = Basic.Symbol('w',dummy=True,positive=True,real=True)
    d, g = mrv_rewrite_dict(x, mrv_set, w)
    e = expr
    for f,f2 in d.items():
        e = e.subs(f,f2)
    c0,e0,f0 = e.as_coeff_leadterm(w)
    if f0!=0:
        c1,e1,f0 = (log(g)**f0).as_coeff_leadterm(x)
        assert c1==1 and f0==0,`c1,e1,f0`
        e0 += e1
    assert not c0.has(w),`c0,e0,f0`
    assert f0==0, `c0,e0,f0,e,expr`
    if e0==0:
        return mrv_leadterm(c0, x)
    return c0, e0

def mrv_rewrite_dict(x, mrv_set, w):
    l = list(mrv_set)
    l.sort(Basic.compare)
    g = l[0]
    t = g.args[0]
    # g=exp(t) -> oo as x->oo is ensured by mrv() function
    d = {}
    for f in l:
        s = f.args[0]
        c = (s/t).limit(x,Basic.Infinity())
        #c = mrv_leadterm(s/t, x)[0]
        A = Basic.Exp()(s-c*t)
        f2 = A * w ** -c  # w**-c is due to g->oo as x->oo.
        d[f] = f2
    return d, g

def mrv_max(s1, s2, x):
    assert isinstance(x, Basic.Symbol),`x`
    if not s1: return s2
    if not s2: return s1
    if s1.intersection(s2): return s1.union(s2)
    if x in s2: return s1
    if x in s1: return s2
    c = mrv_compare(list(s1)[0],list(s2)[0], x)
    if c=='>': return s1
    if c=='<': return s2
    return s1.union(s2)

def mrv_compare(f, g, x):
    log = Basic.Log()
    f = log(f)
    g = log(g)
    if 1:
        c = (f/g).limit(x,Basic.Infinity())
        if c==0: return '<'
        if isinstance(abs(c), Basic.Infinity): return '>'
        if not c.is_comparable:
            raise ValueError("non-comparable result: %s" % (c))
        return '='
    c0,e0 = mrv_leadterm(f/g,x)
    se = Basic.Sign()(e0)
    if se==0: return '='
    if se==-1: return '>'
    if se==1: return '<'
    raise ValueError("failed to determine the sign of %s (got %s)" % (e0, se))

def mrv(expr, x):
    """
    Return a set of most rapidly varying subexpressions of expr with respect to x.
    Since f and 1/f have the same level of rapid variation then for all
      f in Mrv(expr,x)
    the property
      f -> oo as x->oo
    holds.
    """
    if not expr.has(x): return set()
    if expr==x: return set([x])
    if isinstance(expr, (Basic.Add, Basic.Mul)):
        s = set()
        for t in expr:
            s = mrv_max(s, mrv(t,x), x)
        return s
    if isinstance(expr, Basic.Pow) and not expr.exp.has(x):
        return mrv(expr.base, x)
    log = Basic.Log()
    exp = Basic.Exp()
    if isinstance(expr, Basic.Pow):
        return mrv(exp(expr.exp * log(expr.base)), x)
    if isinstance(expr, Basic.Apply):
        func = expr.func
        if isinstance(func, Basic.Exp):
            e = expr.args[0]
            l = e.limit(x,Basic.Infinity())
            m = mrv(e,x)
            if isinstance(l, Basic.Infinity):
                # arg -> oo as x->oo
                pass
            elif isinstance(l, Basic.NegativeInfinity):
                # arg -> -oo as x->oo
                # rewrite to ensure that exp(arg) -> oo
                e = -e
            else:
                # |arg| < oo as x->oo
                return m
            coeff, terms = e.as_coeff_terms()
            if abs(coeff)!=1:
                coeff = Basic.Sign()(coeff)
                if not isinstance(coeff, Basic.One):
                    terms.insert(0,coeff)
                e = Basic.Mul(*terms)
            return mrv_max(set([expr.func(e)]), m, x)
        # assume that func is trackable
        s = set()
        for arg in expr.args:
            s = mrv_max(s, mrv(arg, x), x)
        return s
    raise NotImplementedError("don't know how to find mrv(%s,%s)" % (expr,x))
