
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

