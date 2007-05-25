""" Implementation of Basic low-level methods.
"""

from assumptions import AssumeMeths

# used for canonical ordering of symbolic sequences
# via __cmp__ method:
ordering_of_classes = [
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
    ]

#

class MetaBasicMeths(type):

    classnamespace = {}
    interactive = False        # defines the output of repr()

    def __init__(cls,*args,**kws):
        print 'initializing',cls
        MetaBasicMeths.classnamespace[cls.__name__] = cls
        type.__init__(cls, *args, **kws)
        
    def __getattr__(cls, name):
        c = MetaBasicMeths.classnamespace.get(name)
        if c is not None:
            return c
        raise AttributeError("'%s' object has no attribute '%s'"%
                             (cls.__name__, name))

    def __cmp__(cls, other):
        n1 = cls.__name__
        n2 = other.__name__
        c = cmp(n1,n2)
        if not c: return 0
        try:
            i1 = ordering_of_classes.index(n1)
        except ValueError:
            print 'Add',n1,'to basic_methods.ordering_of_classes list'
            return c
        try:
            i2 = ordering_of_classes.index(n2)
        except ValueError:
            print 'Add',n2,'to basic_methods.ordering_of_classes list'
            return c
        return cmp(i1,i2)


class BasicMeths(AssumeMeths):

    __metaclass__ = MetaBasicMeths

    def __getattr__(self, name):
        if name.startswith('is_'):
            # default implementation for assumptions
            name = name[3:]
            assumptions = self._assumptions
            try: return assumptions[name]
            except KeyError: pass
            if hasattr(self, '_calc_'+name):
                a = assumptions[name] = getattr(self,'_calc_'+name)()
                return a
            return None
        elif BasicMeths.classnamespace.has_key(name):
            return BasicMeths.classnamespace[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s'"%
                                 (self.__class__.__name__, name))

    def __hash__(self):
        h = self._mhash
        if h is None:
            self._mhash = h = hash((self.__class__.__name__,) + self._hashable_content())
        return h

    def _hashable_content(self):
        # If class defines additional attributes, like name in Symbol,
        # then this method should be updated accordingly to return
        # relevant attributes as tuple.
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
        if self.__class__.interactive:
            return self.tostr()
        return self.torepr()

    def __getitem__(self, iter):
        return self._args[iter]

    def __nonzero__(self):
        # prevent using constructs like:
        #   a = Symbol('a')
        #   if a: ..
        raise AssertionError("only Equality|Unequality can define __nonzero__ method")

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
        c = cmp(self.__class__, other.__class__)
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

