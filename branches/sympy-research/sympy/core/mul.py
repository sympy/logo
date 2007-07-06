
from basic import Basic
from basic import singleton as S
from operations import AssocOp
from methods import RelMeths, ArithMeths

class Mul(AssocOp, RelMeths, ArithMeths):

    @classmethod
    def flatten(cls, seq):
        # apply associativity, separate commutative part of seq
        c_part = []
        nc_part = []
        coeff = Basic.One()
        c_seq = []
        nc_seq = seq
        c_powers = {}
        lambda_args = None
        order_symbols = None
        while c_seq or nc_seq:
            if c_seq:
                # first process commutative objects
                o = c_seq.pop(0)
                if isinstance(o, Basic.Function):
                    o, lambda_args = o.with_dummy_arguments(lambda_args)
                if isinstance(o, Basic.Order):
                    o, order_symbols = o.as_expr_symbols(order_symbols)
                if o.__class__ is cls:
                    # associativity
                    c_seq = list(o._args) + c_seq
                    continue
                if isinstance(o, Basic.Number):
                    coeff *= o
                    continue
                if isinstance(o, Basic.ApplyExp):
                    # exp(x) / exp(y) -> exp(x-y)
                    b = Basic.Exp1()
                    e = o.args[0]
                else:
                    b, e = o.as_base_exp()
                if c_powers.has_key(b):
                    c_powers[b] += e
                else:
                    c_powers[b] = e
            else:
                o = nc_seq.pop(0)
                if isinstance(o, Basic.Function):
                    o, lambda_args = o.with_dummy_arguments(lambda_args)
                if isinstance(o, Basic.Order):
                    o, order_symbols = o.as_expr_symbols(order_symbols)
                if o.is_commutative:
                    # separate commutative symbols
                    c_seq.append(o)
                    continue
                if o.__class__ is cls:
                    # associativity
                    nc_seq = list(o._args) + nc_seq
                    continue
                if not nc_part:
                    nc_part.append(o)
                    continue
                # try to combine last terms: a**b * a ** c -> a ** (b+c)
                o1 = nc_part.pop()
                b1,e1 = o1.as_base_exp()
                b2,e2 = o.as_base_exp()
                if b1==b2:
                    nc_seq.insert(0, b1 ** (e1 + e2))
                else:
                    nc_part.append(o1)
                    nc_part.append(o)
        for b,e in c_powers.items():
            if isinstance(e, Basic.Zero):
                continue
            if isinstance(e, Basic.One):
                if isinstance(b, Basic.Number):
                    coeff *= b
                else:
                    c_part.append(b)
            else:
                c_part.append(Basic.Pow(b, e))
        if not isinstance(coeff, Basic.One):
            c_part.insert(0, coeff)
        if isinstance(coeff, Basic.Zero):
            c_part, nc_part = [coeff],[]
        c_part.sort(Basic.compare)
        if len(c_part)==2 and isinstance(c_part[0], Basic.Number) and isinstance(c_part[1], Basic.Add):
            # 2*(1+a) -> 2 + 2 * a
            coeff = c_part[0]
            c_part = [Basic.Add(*[coeff*f for f in c_part[1]])]
        return c_part, nc_part, lambda_args, order_symbols

    def _eval_power(b, e):
        if isinstance(e, Basic.Number):
            if b.is_commutative:
                if isinstance(e, Basic.Integer):
                    # (a*b)**2 -> a**2 * b**2
                    return Mul(*[s**e for s in b])
                coeff, rest = b.as_coeff_terms()
                if not isinstance(coeff, Basic.One):
                    # (2*a)**3 -> 2**3 * a**3
                    return coeff**e * Mul(*[s**e for s in rest])
            elif isinstance(e, Basic.Integer):
                coeff, rest = b.as_coeff_terms()
                l = [s**e for s in rest]
                if e.is_negative:
                    l.reverse()
                return coeff**e * Mul(*l)
        if e.atoms(Basic.Wild):
            return Mul(*[t**e for t in b])
        return

    @property
    def precedence(self):
        coeff, rest = self.as_coeff_terms()
        if coeff.is_negative: return Basic.Add_precedence
        return Basic.Mul_precedence

    def tostr(self, level = 0):
        precedence = self.precedence
        coeff, terms = self.as_coeff_terms()
        if coeff.is_negative:
            coeff = -coeff
            if not isinstance(coeff, Basic.One):
                terms.insert(0, coeff)
            r = '-' + ' * '.join([t.tostr(precedence) for t in terms])
        else:
            r = ' * '.join([t.tostr(precedence) for t in self])
        r = r.replace(' * 1 / ',' / ')
        if precedence<=level:
            return '(%s)' % r
        return r
    
        numer,denom = self.as_numer_denom()
        if isinstance(denom, Basic.One):
            delim = ' * '
            coeff, rest = self.as_coeff_terms()
            r = delim.join([s.tostr(precedence) for s in rest])
            if isinstance(coeff, Basic.One):
                pass
            elif isinstance(-coeff, Basic.One):
                r = '-' + r
            elif coeff.is_negative:
                r = '-' + (-coeff).tostr() + delim + r
            else:
                r = coeff.tostr() + delim + r
        else:
            if len(denom[:])>1:
                r = '(' + numer.tostr() + ') / (' + denom.tostr() + ')'
            else:
                r = '(' + numer.tostr() + ') / ' + denom.tostr()
        if precedence<=level:
            return '(%s)' % r
        return r

    def as_coeff_terms(self):
        coeff = self[0]
        if isinstance(coeff, Basic.Number):
            return coeff, list(self[1:])
        return Basic.One(), list(self[:])

    def expand(self):
        """
        (a + b + ..) * c -> a * c + b * c + ..
        """
        seq = []
        for t in self:
            t = t.expand()
            if not seq:
                if isinstance(t, Basic.Add):
                    seq = list(t)
                else:
                    seq.append(t)
            elif isinstance(t, Basic.Add):
                new_seq = []
                for f1 in seq:
                    for f2 in t:
                        new_seq.append(f1 * f2)
                seq = new_seq
            else:
                seq = [f*t for f in seq]
        return Basic.Add(*seq, **self._assumptions)

    def _eval_derivative(self, s):
        terms = list(self)
        factors = []
        for i in range(len(terms)):
            t = terms[i].diff(s)
            if isinstance(t, Basic.Zero):
                continue
            factors.append(Mul(*(terms[:i]+[t]+terms[i+1:])))
        return Basic.Add(*factors)

    def _matches_simple(pattern, expr, repl_dict):
        # handle (w*3).matches('x*5') -> {w: x*5/3}
        coeff, terms = pattern.as_coeff_terms()
        if len(terms)==1:
            return terms[0].matches(expr / coeff, repl_dict)
        return

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        if pattern.is_commutative and expr.is_commutative:
            return AssocOp._matches_commutative(pattern, expr, repl_dict, evaluate)
        # todo for commutative parts, until then use the default matches method for non-commutative products
        return Basic.matches(pattern, expr, repl_dict, evaluate)

    @staticmethod
    def _combine_inverse(lhs, rhs):
        return lhs / rhs

    def _calc_as_coeff_leadterm(self, x):
        return self._seq_as_coeff_leadterm([t.as_coeff_leadterm(x) for t in self])

    @staticmethod
    def _seq_as_coeff_leadterm(seq):
        c0,e0,f0 = Basic.One(), Basic.Zero(), Basic.Zero()
        for (c,e,f) in seq:
            c0 *= c
            e0 += e
            f0 += f
        return c0,e0,f0        

    def as_numer_denom(self):
        numers,denoms = [],[]
        for t in self:
            if isinstance(t, Basic.Number):
                numers.append(t)
                continue
            n,d = t.as_numer_denom()
            numers.append(n)
            denoms.append(d)
        return Mul(*numers), Mul(*denoms)

    def count_ops(self, symbolic=True):
        if symbolic:
            return Basic.Add(*[t.count_ops(symbolic) for t in self[:]]) + Basic.Symbol('MUL') * (len(self[:])-1)
        return Basic.Add(*[t.count_ops(symbolic) for t in self[:]]) + (len(self[:])-1)

    def _eval_integral(self, s):
        coeffs = []
        terms = []
        for t in self:
            if not t.has(s): coeffs.append(t)
            else: terms.append(t)
        if coeffs:
            return Mul(*coeffs) * Mul(*terms).integral(s)
        u = self[0].integral(s)
        v = Mul(*(self[1:]))
        uv = u * v
        return uv - (u*v.diff(s)).integral(s)
        
    def _eval_defined_integral(self, s, a, b):
        coeffs = []
        terms = []
        for t in self:
            if not t.has(s): coeffs.append(t)
            else: terms.append(t)
        if coeffs:
            return Mul(*coeffs) * Mul(*terms).integral(s==[a,b])
        # (u'v) -> (uv) - (uv')
        u = self[0].integral(s)
        v = Mul(*(self[1:]))
        uv = u * v
        return (uv.subs(s,b) - uv.subs(s,a)) - (u*v.diff(s)).integral(s==[a,b])

    _eval_is_real = lambda self: self._eval_template_is_attr('is_real')
    _eval_is_bounded = lambda self: self._eval_template_is_attr('is_bounded')
    _eval_is_commutative = lambda self: self._eval_template_is_attr('is_commutative')
    _eval_is_integer = lambda self: self._eval_template_is_attr('is_integer')
    _eval_is_comparable = lambda self: self._eval_template_is_attr('is_comparable')
    def _eval_is_irrational(self):
        for t in self:
            a = t.is_irrational
            if a: return True
            if a is None: return
        return False

    def _eval_is_positive(self):
        r = True
        for t in self:
            a = t.is_positive
            if a is None: return
            if a: continue
            r = not r
        return r
    def _eval_is_even(self):
        r = False
        for t in self:
            a = t.is_even
            if a is None: return
            if a: r = True
        return r

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        if self==old:
            return new
        coeff1,terms1 = self.as_coeff_terms()
        coeff2,terms2 = old.as_coeff_terms()
        if terms1==terms2: # (2*a).subs(3*a,y) -> 2/3*y
            return new * coeff1/coeff2
        l1,l2 = len(terms1),len(terms2)
        if l2<l1: # (a*b*c*d).subs(b*c,x) -> a*x*d 
            for i in range(l1-l2+1):
                if terms2==terms1[i:i+l2]:
                    m1 = Mul(*terms1[:i]).subs(old,new)
                    m2 = Mul(*terms1[i+l2:]).subs(old,new)
                    return Mul(*([coeff1/coeff2,m1,new,m2]))
        return self.__class__(*[s.subs(old, new) for s in self])

    def _eval_oseries(self, order):
        x = order.symbols[0]
        l = []
        r = []
        lt = []
        for t in self:
            if not t.has(x):
                l.append(t)
                continue
            r.append(t)
            lt.append(t.as_leading_term(x))
        if not r:
            if order.contains(1,x): return S.Zero
            return Mul(*l)
        if len(r)==1:
            return Mul(*(l + [r[0].oseries(order)]))
        for i in range(len(r)):
            m = Mul(*(lt[:i]+lt[i+1:]))
            o = order/m
            l.append(r[i].oseries(o))
        r = Mul(*l).expand()
        if isinstance(r, Basic.Add): # remove higher order terms
            r = r.oseries(order)
        return r

    def as_leading_term(self, x):
        return Mul(*[t.as_leading_term(x) for t in self])
