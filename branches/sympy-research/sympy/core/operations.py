
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
            assumptions['commutative'] = not nc_part
            obj = Basic.__new__(cls, *(c_part + nc_part), **assumptions)
        if order_symbols is not None:
            obj = Basic.Order(obj, *order_symbols)
        if lambda_args is not None:
            obj = Basic.Lambda(obj, *lambda_args)
        return obj

    @classmethod
    def identity(cls):
        if cls is Basic.Mul: return Basic.One()
        if cls is Basic.Add: return Basic.Zero()
        if cls is Basic.Composition:
            s = Basic.Symbol('x',dummy=True)
            return Basic.Lambda(s,s)
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
        return [], new_seq, None, None

    subs = Basic._seq_subs

    def _matches_commutative(pattern, expr, repl_dict):
        # cache pattern specific calculations
        if not hasattr(pattern, '_wilds'):
            pattern._wilds = wilds = []
            pattern._notwilds = rest = []
            for o in pattern[:]:
                if isinstance(o, Basic.Wild):
                    wilds.append(o)
                else:
                    rest.append(o)
        else:
            wilds = pattern._wilds
            rest = pattern._notwilds
        if len(wilds)==0:
            return Basic.matches(pattern, expr, repl_dict)

        # look for a free wild symbol
        d = repl_dict.copy()
        wild = None
        for w in wilds:
            if not d.has_key(w):
                if wild is None:
                    wild = w
                else:
                    d[w] = pattern.__class__.identity()
        if wild is None or len(wilds)>1:
            patexpr = pattern
            for w in wilds:
                if w is wild: continue
                patexpr = patexpr.subs(w, d[w])
            return patexpr.matches(expr, d)

        # pattern contains exactly one free wild symbol
        expr = Basic.sympify(expr)
        if isinstance(expr, pattern.__class__):
            expr_list = list(expr)
        else:
            expr_list = [expr]
        for o in rest:
            d1 = None
            for e in expr_list:
                d1 = o.matches(e,d)
                if d1 is not None:
                    break
            if d1 is None:
                return None
            expr_list.remove(e)
            d = d1

        # check if wild value matches with one in repl_dict
        wv = pattern.__class__(*expr_list)
        for k,v in d.items():
            if k==wild:
                if v!=wv:
                    return None
                return d
        d[wild] = wv
        return d
