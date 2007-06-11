
from basic import Basic
from operations import AssocOp
from methods import RelMeths, ArithMeths

class Add(AssocOp, RelMeths, ArithMeths):

    precedence = 40

    @classmethod
    def flatten(cls, seq):
        # apply associativity, all terms are commutable with respect to addition
        terms = {}
        coeff = Basic.Zero()
        lambda_args = None
        order_terms = {}
        while seq:
            o = seq.pop(0)
            if isinstance(o, Basic.Function):
                o, lambda_args = o.with_dummy_arguments(lambda_args)
            if isinstance(o, Basic.Order):
                if order_terms.has_key(o.symbols):
                    order_terms[o.symbols] += o.expr
                else:
                    order_terms[o.symbols] = o.expr
                continue
            if isinstance(o, Basic.Number):
                coeff += o
                continue
            if o.__class__ is cls:
                seq = list(o._args) + seq
                continue
            if isinstance(o, Basic.Mul):
                c = o[0]
                if isinstance(c, Basic.Number):
                    if isinstance(c, Basic.One):
                        s = o
                    else:
                        s = Basic.Mul(*o[1:])
                else:
                    c = Basic.One()
                    s = o
            else:
                c = Basic.One()
                s = o
            if terms.has_key(s):
                terms[s] += c
            else:
                terms[s] = c
        newseq = []
        noncommutative = False
        orders = []
        for s,c in terms.items():
            if isinstance(c, Basic.Zero):
                continue
            if isinstance(s, Basic.Order):
                orders.append(s)
            elif isinstance(c, Basic.One):
                newseq.append(s)
            else:
                newseq.append(Basic.Mul(c,s))
            noncommutative = noncommutative or not s.is_commutative
        if not isinstance(coeff, Basic.Zero):
            newseq.insert(0, coeff)

        if order_terms:
            lowest_degree = None        
            lorder_terms = {}
            for symbols, expr in order_terms.items():
                ld = expr.ldegree(*symbols)
                if lowest_degree is None:
                    lowest_degree = ld
                    lorder_terms = {symbols: expr}
                elif ld == lowest_degree: # O(x**2) + O(x*y) -> O(x**2+x*y)
                    if lorder_terms.has_key(symbols):
                        lorder_terms[symbols] += expr
                    else:
                        lorder_terms[symbols] = expr
                elif ld < lowest_degree: # O(x**2) + O(x) -> O(x)
                    lowest_degree = ld
                    lorder_terms = {symbols: expr}
            order_list = [Basic.Order(expr.leading_term(*symbols), *symbols) for symbols, expr in lorder_terms.items()]
            newseq2 = []
            for t in newseq:
                for oterm in order_list:
                    if oterm.contains(t): # x + x**2 + O(x**2) -> x + O(x**2)
                        t = None
                        break
                if t is not None:
                    newseq2.append(t)
            newseq = newseq2 + order_list

        newseq.sort(Basic.compare)
        if noncommutative:
            return [],newseq,lambda_args,None
        return newseq,[],lambda_args,None

    def tostr(self, level=0):
        coeff, rest = self.as_coeff_factors()
        l = []
        precedence = self.precedence
        if not isinstance(coeff, Basic.Zero):
            l.append(coeff.tostr(precedence))
        for factor in rest:
            f = factor.tostr(precedence)
            if f.startswith('-'):
                l.extend(['-',f[1:]])
            else:
                l.extend(['+',f])
        if l[0]=='+': l.pop(0)
        r = ' '.join(l)
        if precedence<=level:
            return '(%s)' % r
        return r

    def as_coeff_factors(self):
        coeff = self[0]
        if isinstance(coeff, Basic.Number):
            return coeff, self[1:]
        return Basic.Zero(), self[:]

    def _eval_derivative(self, s):
        return Add(*[f.diff(s) for f in self])

    def _matches_simple(pattern, expr, repl_dict):
        # handle (w+3).matches('x+5') -> {w: x+2}
        coeff, factors = pattern.as_coeff_factors()
        if len(factors)==1:
            return factors[0].matches(expr - coeff, repl_dict)
        return

    matches = AssocOp._matches_commutative

    @staticmethod
    def _combine_inverse(lhs, rhs):
        return lhs - rhs

    @staticmethod
    def _calc_leadterm_simple(expr, x):
        if not isinstance(expr, Add):
            return expr.leadterm(x)
        d = {}
        for f in expr:
            c,e = f.leadterm(x)
            if not e.is_comparable:
                raise TypeError("cannot determine lead term with respect to %r of a sum with symbolic exponents: %r" % (x,expr))
            if d.has_key(e):
                d[e] += c
            else:
                d[e] = c
        l = d.items()
        l.sort()
        e0,c0 = l.pop(0)
        return c0,e0

    def _calc_leadterm(self, x):
        numer, denom = self.as_numer_denom()
        nc0,ne0 = Add._calc_leadterm_simple(numer,x)
        dc0,de0 = Add._calc_leadterm_simple(denom,x)
        if isinstance(nc0, Basic.Zero):
            raise `numer,denom`
        return nc0/dc0, ne0-de0

    def as_numer_denom(self):
        numers, denoms = [],[]
        for n,d in [f.as_numer_denom() for f in self]:
            numers.append(n)
            denoms.append(d)
        r = range(len(numers))
        return Add(*[Basic.Mul(*(denoms[:i]+[numers[i]]+denoms[i+1:])) for i in r]),Basic.Mul(*denoms)

    def _calc_splitter(self, d):
        if d.has_key(self):
            return d[self]
        coeff, factors = self.as_coeff_factors()
        r = self.__class__(*[t._calc_splitter(d) for t in factors])
        if isinstance(r,Add) and 0:
            for e,t in d.items():
                w = Basic.Wild()
                d1 = r.match(e+w)
                if d1 is not None:
                    r1 = t + d1[w]
                    break
        if d.has_key(r):
            return coeff + d[r]
        s = d[r] = Basic.Temporary()
        return s + coeff

    def count_ops(self):
        return Add(*[t.count_ops() for t in self[:]]) + Basic.Symbol('ADD') * (len(self[:])-1)
