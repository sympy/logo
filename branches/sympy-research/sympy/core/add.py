
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

    def _calc_leadterm(self, x):
        c0,e0 = self[0].leadterm(x)
        if not isinstance(e0, Basic.Number):
            raise TypeError("cannot determine lead term with respect to %r of a sum with symbolic exponents: %r" % (x,self))
        for f in self[1:]:
            c,e = f.leadterm(x)
            if not e.is_comparable:
                raise TypeError("cannot determine lead term with respect to %r of a sum with symbolic exponents: %r" % (x,self))
            if e < e0:
                c0,e0 = c,e
            elif e==e0:
                c0,e0 = c0+c,e
        return c0,e0
