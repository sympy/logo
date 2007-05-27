
from basic import Basic

class AssocOp(Basic):
    """ Associative operations, can separate noncommutative and
    commutative parts.
    
    (a op b) op c == a op (b op c) == a op b op c.
    
    Base class for Add and Mul.
    """
    
    def __new__(cls, *args, **assumptions):
        if len(args)==0:
            return cls.identity
        if len(args)==1:
            return args[0]
        c_part, nc_part, lambda_args, order_symbols = cls.flatten(map(Basic.sympify, args))
        if len(c_part) + len(nc_part) <= 1:
            if c_part: obj = c_part[0]
            elif nc_part: obj = nc_part[0]
            else: obj = cls.identity()
        else:
            c_part.sort(Basic.compare)
            obj = Basic.__new__(cls, commutative=not nc_part, *(c_part + nc_part),
                                **assumptions)
        if order_symbols is not None:
            obj = Basic.Order(obj, *order_symbols)
        if lambda_args is not None:
            obj = Basic.Lambda(obj, *lambda_args)
        return obj

    @classmethod
    def identity(cls):
        if cls is Basic.Mul: return Basic.One()
        if cls is Basic.Add: return Basic.Zero()
        raise NotImplementedError,"identity not defined for class %r" % (cls.__name__)

    @classmethod
    def flatten(cls, seq):
        # apply associativity, no commutativity property is used
        new_seq = []
        while seq:
            o = seq.pop(0)
            if o.__class__ is cls: # classes must match exactly
                seq = list(o[:]) + seq
                continue
            new_seq.append(o)
        return [], new_seq

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        return self.__class__(*[s.subs(old, new) for s in self])
