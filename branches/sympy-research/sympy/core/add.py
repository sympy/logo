
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
        while seq:
            o = seq.pop(0)
            if isinstance(o, Basic.Function):
                o, lambda_args = o.with_dummy_arguments(lambda_args)
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
