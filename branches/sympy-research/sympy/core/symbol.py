
from basic import Basic, Atom
from methods import RelMeths, ArithMeths

class Symbol(Atom, RelMeths, ArithMeths):
    """
    Assumptions::
       is_real = True
       is_commutative = True

    You can override the default assumptions in the constructor::
       >>> A = Symbol('A', is_commutative = False)
       >>> B = Symbol('B', is_commutative = False)
       >>> A*B != B*A
       True
       >>> (A*B*2 == 2*A*B) == True # multiplication by scalars is commutative
       True
    """

    dummycount = 0

    def __new__(cls, name, commutative=True, dummy=False, real=False, 
                **assumptions):
        """if dummy == True, then this Symbol is totally unique, i.e.::
        
        >>> (Symbol("x") == Symbol("x")) == True
        True
        
        but with the dummy variable ::
        
        >>> (Symbol("x", dummy = True) == Symbol("x", dummy = True)) == True
        False

        """
        obj = Basic.singleton.get(name)
        if obj is not None:
            return obj()
        obj = Basic.__new__(cls,
                            commutative=commutative,
                            dummy=dummy,
                            real=real,
                            **assumptions)
        if dummy:
            Symbol.dummycount += 1
            obj.dummy_index = Symbol.dummycount

        obj.name = name
        return obj

    def _hashable_content(self):
        if self.is_dummy:
            return (self.name, self.dummy_index)
        return (self.name,)

    def tostr(self, level=0):
        if self.is_dummy:
            return '_' + self.name
        return self.name

    def torepr(self):
        if self.is_dummy:
            return '%s(%r, dummy=True)' % (self.__class__.__name__, self.name)
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def as_dummy(self):
        assumptions = self._assumptions.copy()
        assumptions['dummy'] = True
        return self.__class__(self.name, **assumptions)

    def __call__(self, *args, **assumptions):
        return Basic.Function(self.name, nofargs=len(args))(*args, **assumptions)

    #def __mathml__(self): ..
    #def __latex__(self): ..
    #def __pretty__(self): ..

class Wild(Symbol):
    """
    Wild() matches any expression but another Wild().
    """

    def __new__(cls, name = None, **assumptions):
        assumptions['dummy'] = True
        if name is None:
            name = 'W%s' % (Symbol.dummycount+1)
        return Symbol.__new__(cls, name, **assumptions)

    def matches(pattern, expr, repl_dict, evaluate=False):
        for p,v in repl_dict.items():
            if p==pattern:
                if v==expr: return repl_dict
                return None
        repl_dict = repl_dict.copy()
        repl_dict[pattern] = expr
        return repl_dict

    def __call__(self, *args, **assumptions):
        return Basic.WildFunction(self.name, nofargs=len(args))(*args, **assumptions)

    def tostr(self, level=0):
        return self.name + '_'
