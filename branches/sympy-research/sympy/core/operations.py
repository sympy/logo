
from basic import Basic

class AssocOp(Basic):
    """ Associative operations, checks for commutativity.
    
    (a op b) op c == a op (b op c) == a op b op c.
    
    Base class for Add and Mul.
    """

    commutative = None
    
    def __new__(cls, *args):
        if len(args)==0:
            return Basic.sympify(cls.identity)
        if len(args)==1:
            return args[0]
        c_part, nc_part = cls.flatten(map(Basic.sympify, args))
        obj = Basic.__new__(cls, *(c_part + nc_part))
        return obj

    @property
    @staticmethod
    def identity():
        raise NotImplementedError,"%s.identity not defined" % (self.__class__.__name__)

    @classcmethod
    def flatten(cls, seq):
        # apply associativity and separate commutative and noncommutative parts
        new_seq = []
        commutative_part = []
        noncommutative_part = []
        while seq:
            o = seq.pop(0)
            if o.__class__ is cls: # classes must match exactly
                seq = o[:] + seq
                continue
            if o.is_commutative:
                commutative_part.append(o)
            else:
                non_commutative_part.append(o)
        return commutative_part, noncommutative_part
