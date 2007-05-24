
from basic import Basic

class AssocOp(Basic):
    """ Associative operations, checks for commutativity.
    
    (a op b) op c == a op (b op c) == a op b op c.
    
    Base class for Add and Mul.
    """

    is_commutative = None
    
    def __new__(cls, *args):
        if len(args)==0:
            return cls.identity
        if len(args)==1:
            return args[0]
        c_part, nc_part = cls.flatten(map(Basic.sympify, args))
        if len(c_part) + len(nc_part) <= 1:
            if c_part: return c_part[0]
            if nc_part: return nc_part[0]
            return cls.identity
        obj = Basic.__new__(cls, commutative=not nc_part, *(c_part + nc_part))
        return obj

    @classmethod
    def identity(cls):
        if cls is Basic.Mul: return Basic.One()
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
