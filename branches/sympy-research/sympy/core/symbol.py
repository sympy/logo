
from basic import Basic

class Symbol(Basic):
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
                *args, **kwargs):
        """if dummy == True, then this Symbol is totally unique, i.e.::
        
        >>> (Symbol("x") == Symbol("x")) == True
        True
        
        but with the dummy variable ::
        
        >>> (Symbol("x", dummy = True) == Symbol("x", dummy = True)) == True
        False

        """
        assert not args,`args`
        obj = Basic.__new__(cls, name, is_commutative=commutative, is_dummy=dummy, is_real=dummy,
                            **kwargs)
        if dummy:
            Symbol.dummycount += 1
            name + '__' + str(Symbol.dummycount)
        obj.name = name
        return obj

    def _hashable_content(self):
        return (self.name,)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

Basic.Symbol = Symbol
