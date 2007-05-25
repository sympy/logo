
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
        while c_seq or nc_seq:
            if c_seq:
                # first process commutative objects
                o = c_seq.pop(0)
                if o.__class__ is cls:
                    # associativity
                    c_seq = list(o._args) + c_seq
                    continue
                if isinstance(o, Basic.Number):
                    coeff *= o
                    continue
                if isinstance(o, Basic.Pow):
                    b = o.base
                    e = o.exp
                else:
                    b = o
                    e = Basic.One()
                if c_powers.has_key(b):
                    c_powers[b] += e
                else:
                    c_powers[b] = e
            else:
                o = nc_seq.pop(0)
                if o.is_commutative:
                    # separate commutative symbols
                    c_seq.append(o)
                    continue
                if o.__class__ is cls:
                    # associativity
                    nc_seq = list(o._args) + nc_seq
                    continue
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
        return c_part, nc_part

    def _eval_power(b, e):
        if isinstance(e, Basic.Number):
            if isinstance(e, Basic.Integer):
                # (a*b)**2 -> a**2 * b**2
                return Mul(*[s**e for s in b])
            coeff, rest = b._coeff_rest()
            if not isinstance(coeff, Basic.One):
                # (2*a)**3 -> 2**3 * a**3
                return coeff**e * Mul(*[s**e for s in rest])
        return

    @property
    def precedence(self):
        coeff, rest = self._coeff_rest()
        if coeff.is_negative: return 40 # same as default Add
        return 50

    def tostr(self, level = 0):
        delim = ' * '
        precedence = self.precedence
        coeff, rest = self._coeff_rest()
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
