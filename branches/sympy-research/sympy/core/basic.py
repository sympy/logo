"""Base class for all objects in sympy"""

class Basic(object):
    """
    Base class for all objects in sympy
    
    possible assumptions are: 
        
        - is_real
        
        - is_commutative
        
        - is_number
        
        - is_bounded
        
    Assumptions can have 3 possible values: 
    
        - True, when we are sure about a property. For example, when we are
        working only with real numbers:
        >>> from sympy import *
        >>> Symbol('x', real = True)
        x
        
        - False
        
        - None (if you don't know if the property is True or false)

    """

    interactive = False        # defines the output of repr()
    singleton_classes = {}     # singleton class mapping

    _default_assumption_names = ['is_real',
                                 'is_integer',
                                 'is_commutative',
                                 'is_bounded',
                                 'is_dummy']

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        assumptions = kwargs.copy()
        for a in assumptions.keys():
            if a not in cls._default_assumption_names:
                raise NotImplementedError('Assumption %r' % (a))
        for a in cls._default_assumption_names:
            if not assumptions.has_key(a):
                assumptions[a] = None
        obj._mhash = None
        obj._args = []
        return obj

    def __hash__(self):
        h = self._mhash
        if h is None:
            self._mhash = h = hash((self.__class__.__name__,) + self._hashable_content())
        return h

    def _hashable_content(self):
        # If class defines additional attributes, like name in Symbol,
        # then this method should be updated accordingly.
        return tuple(self._args)

    def tostr(self, level=0):
        return self.torepr()

    def torepr(self):
        l = []
        for o in self:
            try:
                l.append(o.torepr())
            except AttributeError:
                l.append(repr(o))
        return self.__class__.__name__ + '(' + ', '.join(l) + ')'

    def __str__(self):
        return self.tostr()

    def __repr__(self):
        if Basic.interactive:
            return self.tostr()
        return self.torepr()

    def __getitem__(self, iter):
        return self._args[iter]

    def __getattr__(self, name):
        if self._assumptions.has_key(name):
            return self._assumptions[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s'"%
                                 (self.__class__.__name__, name))

    @staticmethod
    def sympify(a):
        """
        Usage
        =====
            Converts an arbitrary expression to a type that can be used
            inside sympy. For example, it will convert python int's into
            instance of sympy.Rational, floats into intances of sympy.Real, etc.
            
        Notes
        =====
            It currently accepts as arguments: 
                - any object defined in sympy (except maybe matrices [TODO])
                - standard numeric python types: int, long, float, Decimal
                - strings (like "0.09" or "2e-19")
            
            If the argument is already a type that sympy understands, it will do
            nothing but return that value - this can be used at the begining of a
            method to ensure you are workint with the corerct type. 
            
        Examples
        ========
            >>> def is_real(a):
            ...     a = Basic.sympify(a)
            ...     return a.is_real
            >>> is_real(2.0)
            True
            >>> is_real(2)
            True
            >>> is_real("2.0")
            True
            >>> is_real("2e-45")
            True
        """
        if isinstance(a, Basic):
            return a
        if isinstance(a, bool):
            raise NotImplementedError("bool support")
        if isinstance(a, (int, long)):
            return Basic.Integer(a)
        if isinstance(a, (float, decimal.Decimal)):
            return Basic.Real(a)
        if isinstance(a, complex):
            real, imag = Basic.sympify(a.real), Basic.sympify(a.imag)
            return real + Basic.I * imag
        if isinstance(a, str):
            raise NotImplementedError("parsing string")
        raise ValueError("%r must be a subclass of Basic" % (a))


class Singleton(Basic):
    """ Singleton object.
    """

    def __new__(cls,*args,**kws):
        obj = Singleton.__dict__.get(cls.__name__)
        if obj is None:
            obj = Basic.__new__(cls,*args,**kws)
            setattr(Singleton, cls.__name__, obj)
        return obj

Basic.Singleton = Singleton
