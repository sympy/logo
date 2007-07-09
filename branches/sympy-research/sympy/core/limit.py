
from basic import Basic, S
from methods import RelMeths, ArithMeths

class Limit(Basic, RelMeths, ArithMeths):
    """ Find the limit of the expression under process x->xlim.

    Limit(expr, x, xlim)
    Limit(expr, x==xlim)
    """

    def __new__(cls, expr, x, xlim, direction='<', **assumptions):
        raise 'aaa'
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
        r = self.expr.subs(self.var, Basic.Infinity())
        if r.is_bounded:
            return r
        if self.expr==self.var:
            return Basic.Infinity()
        raise 'aa'
        print self.expr
        m = MrvExpr(self.expr, self.var)
        #return MrvExpr(self.expr, self.var).get_limit()
        #if self.expr==self.var:
        #    return Basic.Infinity()
        #c0, e0 = MrvExpr(self.expr, self.var).leadterm()
        c0, e0 = mrv_leadterm(self.expr, self.var, task='limit')
        if isinstance(e0, Basic.Zero):
            assert not c0.has(self.var),`self,c0`
            return c0
        if e0.is_negative: return Basic.Sign()(c0) * Basic.Infinity()
        if e0.is_positive: return Basic.Zero()
        raise ValueError("Cannot determine sign of %s" % (e0))

def mrv_leadterm(expr, x, mrv_set=None, task=None, _cache={}, _catch_recursion={}):
    r = _cache.get((expr,x),None)
    if r is None:
        if 0: # use to catch recursion
            l = list(mrv_set or set())
            l.sort()
            l = tuple(l)
            c = _catch_recursion.get((expr,x,l),None)
            if c is None:
                _catch_recursion[(expr,x, l)] = 1
                r = _mrv_leadterm(expr, x, mrv_set, task)
                del _catch_recursion[(expr, x, l)]
            else:
                raise RuntimeError("recursion detected when evaluating mrv_leadterm(%s, %s, %s)" % (expr, x, mrv_set))
        elif 0:
            m = MrvExpr(expr, x)
            cache = m.expr,m.x, tuple(m.mrv_map.keys())
            c = _catch_recursion.get(cache,None)
            if c is None:
                _catch_recursion[cache] = 1
                r = m.leadterm()
                del _catch_recursion[cache]
            else:
                #print _catch_recursion,_cache
                raise RuntimeError("recursion detected when evaluating mrv_leadterm(%s, %s)" % (expr, x))
        else:
            #r = MrvExpr(expr, x).leadterm()
            r = _mrv_leadterm(expr, x, mrv_set)
        #print 'mrv_leadterm(%s, %s) -> %s ' % (expr, x, r)
        _cache[(expr,x)] = r
    else:
        pass
        #print 'CACHE'
    return r

def _mrv_leadterm(expr, x, mrv_set = None):
    """
    x -> (1,-1)
    """
    # x -> oo
    if not expr.has(x):
        return expr, Basic.Zero()

    if mrv_set is None:
        mrv_set = mrv(expr, x)
    log = Basic.Log()
    exp = Basic.Exp()
    if x in mrv_set:
        ex = exp(x)
        up_expr = expr.subs(x,ex)
        up_mrv_set = set([s.subs(x,ex) for s in mrv_set])
        c,e = mrv_leadterm(up_expr,x, up_mrv_set)
        assert isinstance(e, Basic.Number),`e`
        c = c.subs(x,log(x))
        return c,e
    for f in mrv_set:
        assert isinstance(f, Basic.ApplyExp),`f`
    w = Basic.Symbol('w',dummy=True,positive=True,infinitesimal=True)
    d, g = mrv_rewrite_dict(x, mrv_set, w)
    e = expr
    for f,f2 in d:
        e = e.subs(f,f2)
    #e = e.subs(g.args[0],-log(w))
    #print e
    if not e.has(w):
        c0,e0,f0 = e, Basic.Zero(), Basic.Zero()
    else:
        c0,e0,f0 = e.as_coeff_leadterm(w)
        assert not c0.has(w),`e,c0,e0,f0`
    #print 'EXPR=',expr
    #print '[%s->%s]' % (g,1/w)
    #print 'RESULT=',e
    #print 'LEADTERM=',c0,e0,f0
    if f0!=0:
        c1,e1,f0 = (log(g)**f0).as_coeff_leadterm(x)
        assert c1==1 and f0==0,`c1,e1,f0`
        e0 += e1
    if e0==0:
        return mrv_leadterm(c0, x)
    return c0, e0

def mrv_rewrite_dict(x, mrv_set, w):
    l = list(mrv_set)
    l.sort(cmp_ops_count)
    g = l[0]
    t = g.args[0]
    # g=exp(t) -> oo as x->oo is ensured by mrv() function
    d = []
    for f in l:
        s = f.args[0]
        #c = (s/t).limit(x,Basic.Infinity())
        c = mrv_leadterm(s/t, x, task='mrv_rewrite_dict')[0]
        assert not c.has(x),`c`
        Aarg = s -c*t
        Aarg = Aarg.subs(g, 1/w)
        A = Basic.Exp()(Aarg)
        #A = Basic.Exp()(s-c*t)#.subs(t,-Basic.Log()(w))
        f2 = A * w ** -c  # w**-c is due to g->oo as x->oo.
        #print 5*'*','g=',g
        #print 5*'*','f=',f
        #print 5*'*','c=',c
        ##print 5*'*','compare(A,f)='
        #cr = mrv_compare(A,f,x)
        #assert cr=='<',`cr,A,f`
        d.insert(0, (f,f2))
    return d, g

def cmp_ops_count(e1,e2):
    return cmp(e1.count_ops(symbolic=False), e2.count_ops(symbolic=False))

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
    if isinstance(f, Basic.ApplyExp): f = f.args[0]
    else: f = log(f)
    if isinstance(g, Basic.ApplyExp): g = g.args[0]
    else: g = log(g)
    if 1:
        c = (f/g).inflimit(x)
        #print c,f,g
        if c==0:
            return '<'
        if isinstance(abs(c), Basic.Infinity):
            return '>'
        if not c.is_comparable:
            raise ValueError("non-comparable result: %s" % (c))
        return '='
    c0,e0 = mrv_leadterm(f/g,x, task='mrv_compare')
    se = Basic.Sign()(e0)
    if se==0:
        if c0==0: return '<'
        if isinstance(abs(c0), Basic.Infinity): return '>'
        return '='
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

def mrv2(expr, x, d, md):
    """
    Compute a set of most rapidly varying subexpressions of expr with respect to x.

    d = {}
    md = {}
    mrv2(x + exp(x),x,d) -> x+se, d={x:x, exp(x):se}, md={exp(x):se}
    """
    if d.has_key(expr): return d[expr]
    if not expr.has(x):
        return expr
    if expr==x:
        if not md: md[x] = x
        return x
    if isinstance(expr, (Basic.Add, Basic.Mul)):
        r = expr.__class__(*[mrv2(t, x, d, md) for t in expr])
        d[expr] = r
        return r
    log = Basic.Log()
    exp = Basic.Exp()
    if isinstance(expr, Basic.Pow):
        if not expr.exp.has(x):
            r = mrv2(expr.base, x, d, md)**expr.exp
        else:
            r = mrv2(exp(expr.exp * log(expr.base)), x, d, md)
        d[expr] = r
        return r
    if isinstance(expr, Basic.ApplyExp):
        e = expr.args[0]
        #l = e.limit(x,Basic.Infinity())
        l = e.inflimit(x)
        r = exp(mrv2(e, x, d, md))
        if isinstance(l, Basic.Infinity):
            # e -> oo as x->oo
            en = e
        elif isinstance(l, Basic.NegativeInfinity):
            # e -> -oo as x->oo
            # rewrite to ensure that exp(e) -> oo
            en = -e
        else:
            # |e| < oo as x->oo
            d[expr] = r
            return r
        # normalize exp(2*e) -> exp(e)
        coeff, terms = en.as_coeff_terms()
        new_terms = []
        for t in terms:
            if t.has(x):
                pass
            elif t.is_positive:
                continue
            elif t.is_negative:
                coeff *= -1
                continue
            new_terms.append(t)
        terms = new_terms
        coeff = Basic.Sign()(coeff)
        if not isinstance(coeff, Basic.One):
            terms.insert(0,coeff)
        en = Basic.Mul(*terms)
        nexpr = exp(en)
        #print coeff,terms,nexpr
        if md.has_key(x):
            c = '>'
        else:
            lst = md.keys()
            lst.sort(cmp_ops_count)
            c = mrv_compare(nexpr, lst[0], x)
        if c !='<':
            if c=='>':
                md.clear()
            if md.has_key(nexpr):
                tmp = md[nexpr]
            else:
                tmp = Basic.Temporary()
                md[nexpr] = tmp
            r = expr.subs(nexpr, tmp)
        d[expr] = r
        return r
    if isinstance(expr, Basic.Apply):
        r = expr.func(*[mrv2(a, x, d, md) for a in expr.args])
        d[expr] = r
        return r
    raise NotImplementedError("don't know how to find mrv2(%s,%s)" % (expr,x))

class MrvExpr(object):

    def __new__(cls, expr, x, func = lambda o:o, mrv_map=None, newexpr=None):
        expr = Basic.sympify(expr)
        if isinstance(expr, Basic.Apply) and expr.func.nofargs==1 and expr.args[0] != x:
            return MrvExpr(expr.args[0], x, expr.func)
        expr_map = {}
        if mrv_map is None:
            mrv_map = {}
            newexpr = mrv2(expr, x, expr_map, mrv_map)
        if mrv_map.has_key(x):
            up_expr = expr.subs(x, Basic.Exp()(x))
            up_newexpr = newexpr.subs(x, Basic.Exp()(x))
            up_mrv_map = {}
            for k,v in mrv_map.items():
                tmp = Basic.Temporary()
                up_k = k.subs(x, Basic.Exp()(x))
                up_mrv_map[k.subs(x, Basic.Exp()(x))] = tmp
                up_newexpr = up_newexpr.subs(up_k, tmp).subs(x, Basic.Log()(tmp))
            return MrvExpr(up_expr, x, lambda obj: func(obj.subs(x, Basic.Log()(x))),
                           mrv_map=up_mrv_map, newexpr=up_newexpr)
        obj = object.__new__(cls)
        obj.func = func # applied to leading coefficient
        obj.x = x
        obj.expr = expr
        obj.newexpr = newexpr
        obj.expr_map = expr_map
        obj.mrv_map = mrv_map
        obj.w = Basic.Symbol('w',dummy=True,positive=True,infinitesimal=True)
        obj.rewrite_mrv_map()
        obj.rewrite_expr()
        obj.leadterm_w = None #,obj.newexpr_rw.as_coeff_leadterm(obj.w)
        obj.leadterm_w2 = obj.newexpr_rw.as_leading_term(obj.w)
        #obj.leadterm_w0 = obj.leadterm_w2.limit(obj.w, 0)
        return obj

    def __str__(self):
        l = ['EXPR:%s' % (self.expr),
             'VAR:%s' % (self.x),
             'EXPR_MAP:'
             ]
        for k,v in self.expr_map.items():
            l.append('  %s:%s' % (k,v))
        l.append('NEWEXPR:%s' % (self.newexpr))
        l.append('MRV_MAP:')
        for k,v in self.mrv_map.items():
            l.append('  %s:%s' % (k,v))
        l.append('MRV_MAP_RW:')
        for k,v in self.mrv_map_rw.items():
            l.append('  %s:%s' % (k,v))
        l.append('REFGERM:%s' % (self.refgerm))
        l.append('FUNC(x):%s' % (self.func(self.x)))
        l.append('NEWEXPR_RW:%s' % (self.newexpr_rw))
        l.append('LEADTERM(%s):%s' % (self.w, `self.leadterm_w`))
        l.append('LEADTERM2(%s):%s' % (self.w, `self.leadterm_w2`))
        l.append('LEADTERM(%s->0):%s' % (self.w, `self.leadterm_w0`))
        return '\n'.join(l)

    def get_leadterm(self):
        c,e,f = self.leadterm_w
        if f!=0:
            # c * w**e * log(w)**f
            # w = 1/g
            # g = exp(s)
            # c * exp(-e*s) * s**f
            c *= (-self.refgerm.args[0])**f
            print c,self.refgerm,f
            assert e==0,`e`
            f = Basic.Zero()
        assert f==0,`c,e,f`
        if e==0 and c.has(self.x):
            m = MrvExpr(c, self.x, func=self.func)
            return m.get_leadterm()
        return c,e

    def get_limit(self):
        r = self.leadterm_w0
        #if r.has(self.x):
        #    r = r.limit(self.x, Basic.Infinity())
        return self.func(r)

        if self.leadterm_w0==0:
            return self.func(Basic.Zero())
        
        c, e = self.get_leadterm()
        if e==0:
            return self.func(c)
        if e.is_positive:
            return self.func(Basic.Zero())
        if e.is_negative:
            return self.func(Basic.Sign()(c) * Basic.Infinity())
        raise ValueError("Cannot determine sign of %s" % (e))

    def rewrite_expr(self):
        tmps = self.newexpr.atoms(Basic.Temporary)
        e = self.newexpr
        for t in tmps:
            germ = self.mrv_map_rw.get(t, None)
            if t is None: continue
            e = e.subs(t, germ)
        self.newexpr_rw = e

    def rewrite_mrv_map(self):
        x = self.x
        w = self.w
        germs = self.mrv_map.keys()
        germs.sort(cmp_ops_count)
        if germs:
            g = germs[0]
            gname = self.mrv_map[g]
            garg = g.args[0]
        else:
            g = None
        d = {}
        log = Basic.Log()
        for germ in germs:
            name = self.mrv_map[germ]
            if name==gname:
                d[name] = 1/w
                continue
            arg = germ.args[0]
            c = (arg/garg).limit(x, Basic.Infinity())
            Aarg = arg-c*garg
            Aarg = Aarg.subs(g, 1/w)
            c0,e0,f0 = Aarg.as_coeff_leadterm(w)
            if e0==0:
                c0, e0, f0 = c0.subs(g, 1/w).as_coeff_leadterm(w)
            Aarg = c0 * w**e0    
            A = Basic.Exp()(Aarg)
            new_germ = A * w ** -c
            d[name] = new_germ
        self.mrv_map_rw = d
        self.refgerm = g

    def leadterm(self):
        x = self.x
        c, e = self._leadterm()
        func = self.func
        if func is not None:
            c = func(c)
        return c,e

    def _leadterm(self):
        x = self.x
        expr = self.expr
        if not expr.has(x):
            return expr, Basic.Zero()
        #print expr, self.mrv_map
        up = self
        while up.mrv_map.has_key(x):
            up = MrvExpr(expr, x, up)
        if self is not up:
            return up.leadterm()
        w = self.w
        mrv_map_rw,refgerm = self.mrv_map_rw, self.refgerm
        e = self.newexpr
        for name, germ in mrv_map_rw.items():
            e = e.subs(name, germ)
        if not e.has(w):
            c0,e0,f0 = e, Basic.Zero(), Basic.Zero()
        else:
            c0,e0,f0 = e.as_coeff_leadterm(w)
            print c0,e0,f0,e,self.expr,self.newexpr
            assert not c0.has(w)
            #if c0.has(w):
            #    c0 = c0.subs(1/w,refgerm)

        if f0!=0:
            c1,e1,f0 = (Basic.Log()(refgerm)**f0).as_coeff_leadterm(x)
            assert c1==1 and f0==0,`c1,e1,f0,expr,e,refgerm`
            e0 += e1
        if e0==0:
            return MrvExpr(c0, x).leadterm()
        return c0,e0

def rewrite_mrv_map(mrv_map, x, w):
    germs = mrv_map.keys()
    germs.sort(cmp_ops_count)
    if germs:
        g = germs[0]
        gname = mrv_map[g]
        garg = g.args[0]
    else:
        g = None
    d = {}
    log = Basic.Log()
    for germ in germs:
        name = mrv_map[germ]
        if name==gname:
            d[name] = 1/w
            continue
        arg = germ.args[0]
        c = (arg/garg).inflimit(x)
        Aarg = arg-c*garg
        Aarg = Aarg.subs(g, 1/w)
        A = Basic.Exp()(Aarg)
        new_germ = A * w ** -c
        d[name] = new_germ
    return g, d

def rewrite_expr(expr, germ, mrv_map, w):
    tmps = expr.atoms(Basic.Temporary)
    e = expr
    for t in tmps:
        g = mrv_map.get(t, None)
        if g is None: continue
        e = e.subs(t, g)
    if germ is not None:
        mrvlog = S.MrvLog
        log = S.Log
        e = e.subs(log, mrvlog).subs(germ.args[0], -S.Log(w)).subs(mrvlog, log)
    return e

class MrvSet:

    def __init__(self, expr, x, level=0):
        self.expr = expr
        self.x = x
        self.expr_map, self.mrv_map = {}, {}
        self.level = level
        self.newexpr = None
        self.new_expr = None

    def mrvmap(self):
        self.newexpr = mrv2(self.expr, self.x, self.expr_map, self.mrv_map)
        if self.mrv_map.has_key(self.x):
            m = MrvSet(self.expr.subs(self.x, S.Exp(self.x)), self.x, self.level+1)
            em = m.mrv_map
            for k,v in self.mrv_map.items():
                em[k.subs(self.x, S.Exp(self.x))] = v.subs(self.x, S.Exp(self.x))
            exm = m.expr_map
            for k,v in self.expr_map.items():
                exm[k.subs(self.x, S.Exp(self.x))] = v.subs(self.x, S.Exp(self.x))
            m.newexpr = self.newexpr.subs(self.x, S.Exp(self.x))
        else:
            m = self
        m.w = Basic.Symbol('w_0',dummy=True, positive=True, infinitesimal=True)
        germ, new_mrv_map = rewrite_mrv_map(m.mrv_map, m.x, m.w)
        m.new_expr = rewrite_expr(m.newexpr, germ, new_mrv_map, m.w)
        return m

    def __str__(self):
        l = ['----------']
        l.append('level=%s' % (self.level))
        l.append('expr=%s' % (self.expr))
        l.append('newexpr=%s' % (self.newexpr))
        l.append('new_expr=%s' % (self.new_expr))
        l.append('x=%s' % (self.x))
        l.append('expr_map=%s' % (self.expr_map))
        l.append('mrv_map=%s' % (self.mrv_map))
        return '\n'.join(l)
