
from basic import Basic
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
        return

    @property
    def precedence(self):
        coeff, rest = self.as_coeff_terms()
        if coeff.is_negative: return 40 # same as default Add
        return 50

    def tostr(self, level = 0):
        delim = ' * '
        precedence = self.precedence
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
        if precedence<=level:
            return '(%s)' % r
        return r

    def as_coeff_terms(self):
        coeff = self[0]
        if isinstance(coeff, Basic.Number):
            return coeff, self[1:]
        return Basic.One(), self[:]

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
