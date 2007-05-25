"""Base class for all objects in sympy"""

import decimal
from assumptions import AssumeMeths

# used for canonical ordering of symbolic sequences
# via __cmp__ method:
ordering_of_classes = (
    # singleton numbers
    'Zero', 'One',
    # numbers
    'Integer','Rational',
    # singleton symbols
    # symbols
    'Symbol',
    # arithmetic operations
    'Power', 'Mul', 'Add',
    # singleton functions
    # functions
    # relational operations
    'Equality', 'Unequality', 'StrictInequality', 'Inequality', 
    )

#
atom_class_names = ('Symbol', 'Number')

class Basic(AssumeMeths):
    """
    Base class for all objects in sympy

    """

    interactive = False        # defines the output of repr()
    singleton_classes = {}     # singleton class mapping

    @staticmethod
    def _initialize():
        # initialize Basic attributes, call after all modules
        # are imported.
        Basic.atom_classes = tuple([getattr(Basic, n) for n in atom_class_names])

        return

    def __new__(cls, *args, **assumptions):
        obj = object.__new__(cls)
        obj._assumptions = assumptions.copy()
        obj._mhash = None
        obj._args = args
        return obj

    def __hash__(self):
        h = self._mhash
        if h is None:
            self._mhash = h = hash((self.__class__.__name__,) + self._hashable_content())
        return h

    def _hashable_content(self):
        # If class defines additional attributes, like name in Symbol,
        # then this method should be updated accordingly.
        return self._args

    @property
    def precedence(self):
        return 0

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

    def __nonzero__(self):
        # avoid using constructs like:
        #   a = Symbol('a')
        #   if a: ..
        raise AssertionError("only Equality|Unequality can define __nonzero__ method")

    def _compare_classes(self, other):
        n1 = self.__class__.__name__
        n2 = other.__class__.__name__
        c = cmp(n1,n2)
        if not c: return 0
        try:
            i1 = ordering_of_classes.index(n1)
        except ValueError:
            print 'Add',n1,'to basic.ordering_of_classes list'
            return c
        try:
            i2 = ordering_of_classes.index(n2)
        except ValueError:
            print 'Add',n2,'to basic.ordering_of_classes list'
            return c
        return cmp(i1,i2)

    def __cmp__(self, other):
        """
        Return -1,0,1 if the object is smaller, equal, or greater than other
        (not always in mathematical sense).
        If the object is of different type from other then their classes
        are ordered according to sorted_classes list.
        """
        # all redefinitions of __cmp__ method should start with the
        # following three lines:
        if self is other: return 0
        c = self._compare_classes(other)
        if c: return c
        #
        st = self._hashable_content()
        ot = other._hashable_content()
        c = cmp(len(st),len(ot))
        if c: return c
        for l,r in zip(st,ot)[1:]:
            c = cmp(l, r)
            if c: return c
        return 0

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

    def atoms(self, type=None):
        """Returns the atoms that form current object. 
        
        Example: 
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> y = Symbol('y')
        >>> (x+y**2+ 2*x*y).atoms()
        set([2, x, y])
        
        You can also filter the results by a given type of object
        >>> (x+y+2+y**2*sin(x)).atoms(type=Symbol)
        set([x, y])
        
        >>> (x+y+2+y**2*sin(x)).atoms(type=Number)
        set([2])
        """
        atom_classes = Basic.atom_classes
        result = set()
        if isinstance(self, atom_classes):
            if type is None or isinstance(self, type):
                result.add(self)
        else:
            for obj in self:
                result = result.union(obj.atoms(type=type))
        return result

    def subs(self, old, new):
        """Substitutes an expression old -> new."""
        if self==old:
            return Basic.sympify(new)
        return self

class Singleton(Basic):
    """ Singleton object.
    """

    def __new__(cls,*args,**kws):
        # if you need to overload __new__, then
        # use the same code as below to ensure
        # that only one instance of Singleton
        # class is created.
        obj = Singleton.__dict__.get(cls.__name__)
        if obj is None:
            obj = Basic.__new__(cls,*args,**kws)
            setattr(Singleton, cls.__name__, obj)
        return obj

Basic.Singleton = Singleton

