
from basic import Basic, Atom, sympify
from symbol import BasicSymbol, BasicDummySymbol
from function import Function, FunctionSignature, FunctionClass
from qm import qm
from utils import memoizer_immutable_args

class BooleanMeths:

    def __nonzero__(self): return False

    # convenience methods:
    def __invert__(self): return Not(self)            # ~ operator
    def __or__(self, other): return Or(self, other)   # | operator
    def __xor__(self, other): return XOr(self, other) # ^ operator
    def __and__(self, other): return And(self, other) # & operator
    def __ror__(self, other): return Or(self, other)   # | operator
    def __rxor__(self, other): return XOr(self, other) # ^ operator
    def __rand__(self, other): return And(self, other) # & operator

    def is_subset_of(self, other):
        """ Returns True if from other follows self.
        """
        return False

    def is_opposite_to(self, other):
        """ Returns True if from not other follows self.
        """
        return False

    def truth_table(self, atoms=None):
        """ Compute truth table of boolean expression.

        Return (atoms, table) where table is a map
          {<tuple of boolean values>: <self truth value>}
        and atoms is a list conditions and boolean
        symbols.
        """
        if atoms is None:
            atoms = list(self.atoms(Boolean).union(self.conditions()))
        n = len(atoms)
        r = range(n-1, -1, -1)
        table = {}
        for i in range(2**n):
            # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/219300
            bvals =  tuple(map(lambda y:bool((i>>y)&1), r))
            table[bvals] = self.subs_list(atoms, bvals)
        return atoms, table


    @memoizer_immutable_args('BooleanMeths.compute_truth_table')
    def compute_truth_table(self):
        """ Compute full truth table.

        Return (atoms, table) where table is a map
          {<integer value>: <list of boolean values>}
        where integer value is obtained from binary representation
        of boolean values. The table contains only combinations
        of boolean values that evaluate self to True.
        """        
        conditions = sorted(self.conditions())
        atoms = sorted(self.atoms(Boolean))
        table = {}
        if conditions:
            bsyms = [DummyBoolean('b%s' % (i)) for i in range(len(conditions))]
            expr = self.subs_list(conditions, bsyms)
            syms = map(str, atoms + bsyms)
        else:
            expr = self
            syms = map(str, atoms)
        n = len(syms)
        r = range(n-1,-1,-1)
        string_expr = expr.tostr()
        for i in range(2**n):
            bvals =  map(lambda y:bool((i>>y)&1), r)
            dvals = {}
            for s,b in zip(syms, bvals):
                dvals[s] = b
            v = eval(string_expr, dvals, {'XOr':XOr})
            if v is True:
                table[i] = bvals
            else:
                assert isinstance(v, bool),`v`
        return atoms + conditions, table

    def test(self, test):
        """
        Return conditions when test holds assuming that self is True.
        """
        test = sympify(test)
        if isinstance(test, bool): return test
        atoms, table = self.compute_truth_table()
        if not table:
            raise ValueError('assumption expression %r is never True' % (str(self)))
        t_atoms = sorted(test.atoms(Boolean).union(test.conditions()))
        n = len(atoms)
        indices = []
        for i in range(n):
            a = atoms[i]
            if a in t_atoms:
                continue
            flag = True
            for t in t_atoms:
                if t.is_subset_of(a) or a.is_subset_of(t):
                    flag = False
                    break
            if flag:
                indices.append(i)
        r = range(n-1, -1, -1)
        l = []
        for bvals in table.values():
            t = test.subs_list(atoms, bvals)
            if t is False:
                continue
            if t is True and indices:
                bvals = bvals[:]
                for i in indices:
                    bvals[i] = atoms[i]
                t = self.subs_list(atoms, bvals)
            l.append(t)
        if not l:
            return False
        return And(*l)

    def conditions(self, type=None):
        """
        Return a set of Condition instances.
        """
        if type is None: type = Condition
        s = set()
        if isinstance(self, type):
            s.add(self)
        for obj in self:
            if obj.is_Predicate:
                s = s.union(obj.conditions(type=type))
        return s

    def minimize(self):
        """ Return minimal boolean expression using Quine-McCluskey algorithm.

        See
            http://en.wikipedia.org/wiki/Quine-McCluskey_algorithm

        Note:
          The algorithm does not know about XOR operator. So, expressions
          containing XOr instances may not be minimal.
        """
        atoms, table = self.compute_truth_table()
        n = len(atoms)
        l = []
        r = range(n)
        q = qm(ones=table.keys(), vars=n)
        for t in q:
            p = []
            for c,i in zip(t,r):
                if c=='0': p.append(Not(atoms[i]))
                elif c=='1': p.append(atoms[i])
            l.append(And(*p))
        return Or(*l)

class Boolean(BooleanMeths, BasicSymbol):

    def as_dummy(self):
        return DummyBoolean(self.name)

    def compute_truth_table(self):
        return [self],{1:[True]}

    def conditions(self, type=None):
        return set()

    def minimize(self):
        return self

class DummyBoolean(BasicDummySymbol, Boolean):

    pass



class Predicate(BooleanMeths, Function):
    """ Base class for predicate functions.
    """
    return_canonize_types = (Basic, bool)

    @memoizer_immutable_args('Predicate.__new__')
    def __new__(cls, *args):
        return Function.__new__(cls, *args)


boolean_classes = (Predicate, Boolean, bool, FunctionClass)
Predicate.signature = FunctionSignature(None, boolean_classes)

class And(Predicate):
    """ And(..) predicate.

    a & TRUE -> a
    a & FALSE -> FALSE
    a & (b & c) -> a & b & c
    a & a -> a
    a & ~a -> FALSE
    """

    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        new_operants = set()
        flag = False
        for o in operants:
            if isinstance(o, And):
                new_operants = new_operants.union(set(o.args))
                flag = True
            elif isinstance(o, bool):
                if not o: return False
                flag = True
            else:
                n = len(new_operants)
                new_operants.add(o)
                if n==len(new_operants):
                    flag = True
        for o in list(new_operants):
            if Not(o) in new_operants:
                return False
        if not new_operants:
            return True
        if len(new_operants)==1:
            return new_operants.pop()
        if flag:
            return cls(*new_operants)
        operants.sort(Basic.compare)
        return        

    def tostr(self, level=0):
        r = ' and '. join([c.tostr(self.precedence) for c in self])
        if self.precedence <= level:
            r = '(%s)' % r
        return r


class Or(Predicate):
    """
    a | TRUE -> TRUE
    a | FALSE -> a
    a | (b | c) -> a | b | c
    a | a -> a
    a | ~a -> TRUE
    """
    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        new_operants = set()
        flag = False
        for o in operants:
            if isinstance(o, Or):
                new_operants = new_operants.union(set(o.args))
                flag = True
            elif isinstance(o, bool):
                if o: return True
                flag = True
            else:
                n=len(new_operants)
                new_operants.add(o)
                if n==len(new_operants):
                    flag = True
        for o in list(new_operants):
            if Not(o) in new_operants:
                return True
        if not new_operants:
            return False
        if len(new_operants)==1:
            return new_operants.pop()
        if flag:
            return cls(*new_operants)
        operants.sort(Basic.compare)
        return

    def tostr(self, level=0):
        r = ' or '. join([c.tostr(self.precedence) for c in self])
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class XOr(Predicate):
    """
    a ^ TRUE -> ~a
    a ^ FALSE -> a
    a ^ (b ^ c) -> a ^ b ^ c
    a ^ a -> FALSE
    a ^ ~a -> TRUE
    """


    signature = FunctionSignature(list(boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, operants):
        if not operants:
            return False
        if len(operants)==1:
            arg = operants[0]
            return arg
        if False in operants:
            return cls(*[o for o in operants if o is not False])
        new_operants = []        
        flag = False
        truth_index = 0
        for o in operants:
            if isinstance(o, bool):
                flag = True
                if o: truth_index += 1
            elif o.is_XOr:
                flag = True
                new_operants.extend(o.args)
            else:
                new_operants.append(o)
        operants = new_operants
        new_operants = []
        for o in operants:
            if o not in new_operants:
                po = Not(o)
                if po in new_operants:
                    flag = True
                    truth_index += 1
                    new_operants.remove(po)
                else:
                    new_operants.append(o)
            else:
                new_operants.remove(o)
                flag = True
        if flag:
            if truth_index % 2:
                if new_operants:
                    new_operants[-1] = Not(new_operants[-1])
                else:
                    return True
            return cls(*new_operants)
        operants.sort(Basic.compare)
        return
    
    def tostr(self, level=0):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join([c.tostr(self.precedence) for c in self]))
        r = ' xor '. join([c.tostr(self.precedence) for c in self])
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class Not(Predicate):

    signature = FunctionSignature((boolean_classes,), boolean_classes)

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, bool):
            return not arg
        if arg.is_Not:
            return arg[0]

    def tostr(self, level=0):
        r = ' not %s' % (self.args[0].tostr(self.precedence))
        if self.precedence <= level:
            r = '(%s)' % r
        return r


class LogicalIdentity(Predicate):
    signature = FunctionSignature((boolean_classes,), boolean_classes)
    @classmethod
    def canonize(cls, (arg,)):
        return arg

# Implies = Or(Not, LogicalIdentity)
class Implies(Predicate):

    signature = FunctionSignature((boolean_classes,boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Or(Not(lhs), rhs)

# Equiv = Not(XOr)
class Equiv(Predicate):

    signature = FunctionSignature((boolean_classes, boolean_classes), boolean_classes)

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Not(XOr(lhs, rhs))

#
#
#

class Condition(Predicate):
    """ Base class for conditions.

    Number of conditions can be expressed in terms of
    other conditions. The following classes are
    fundamental conditions:
      Equal, Less
      IsComplex, IsReal, IsRational, IsInteger, IsPrime
    """

    def subs(self, old, new):
        old = sympify(old)
        new = sympify(new)
        if self==old: return new
        if new is True:
            if old.is_subset_of(self):
                # IsInteger(x).subs(IsOdd(x), True) -> True
                return True
            if old.is_opposite_to(self):
                # IsInteger(x).subs(IsFraction(x), True) -> False
                return False
        if new is False:
            if self.is_subset_of(old):
                # IsInteger(x).subs(IsReal(x), False) -> False
                return False
        return self        


#
# Relational conditions
#

class Relational(Condition):

    signature = FunctionSignature((Basic, Basic), boolean_classes)

    @property
    def lhs(self): return self[0]
    @property
    def rhs(self): return self[1]

    def minimize(self):
        return self

    def decompose(self, conditional=False):
        return self

class Equal(Relational):

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return IsZero(lhs-rhs)
        if lhs==rhs:
            return True
        if lhs.is_Number and rhs.is_Number:
            return False
        if not rhs.is_zero:
            return Equal(lhs-rhs, 0)

    def tostr(self, level=0):
        r = '%s == %s' % (self.lhs.tostr(self.precedence),
                          self.rhs.tostr(self.precedence))
        if self.precedence <= level:
            r = '(%s)' % r
        return r

class Less(Relational):

    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs.is_Number and rhs.is_Number:
            return lhs < rhs
        if lhs==rhs:
            return False
        return IsPositive(rhs-lhs)
        if not rhs.is_zero:
            return Less(lhs-rhs, 0)

    def tostr(self, level=0):
        r = '%s < %s' % (self.lhs.tostr(self.precedence),
                         self.rhs.tostr(self.precedence))
        if self.precedence <= level:
            r = '(%s)' % r
        return r    

class LessEqual(Relational):
    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Or(Less(lhs, rhs), Equal(lhs, rhs))

class GreaterEqual(Relational):
    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Or(Less(rhs, lhs), Equal(lhs, rhs))

class Greater(Relational):

    @classmethod
    def canonize(cls, (lhs, rhs)):
        return Less(rhs, lhs)

## class IsNonNegative(Predicate):
##     signature = FunctionSignature((Basic,), boolean_classes)
##     @classmethod
##     def canonize(cls, (arg,)):
##         if arg.is_ImaginaryUnit: return False
##         return Not(Less(arg, 0))

## class IsPositive(Predicate):

##     signature = FunctionSignature((Basic,), boolean_classes)
    
##     @classmethod
##     def canonize(cls, (arg,)):
##         if arg.is_ImaginaryUnit: return False
##         return Less(0, arg)

## class IsNonPositive(Predicate):

##     signature = FunctionSignature((Basic,), boolean_classes)
    
##     @classmethod
##     def canonize(cls, (arg,)):
##         if arg.is_ImaginaryUnit: return False
##         return Not(Less(0, arg))

## class IsNegative(Predicate):

##     signature = FunctionSignature((Basic,), boolean_classes)
    
##     @classmethod
##     def canonize(cls, (arg,)):
##         if arg.is_ImaginaryUnit: return False
##         return Less(arg, 0)

#
# Inclusion conditions:
#

@memoizer_immutable_args('get_opposite_classes_map')
def get_opposite_classes_map():
    return dict(IsComplex=(),
                IsReal=(IsImaginary,),
                IsImaginary=(IsReal,),
                IsRational=(IsIrrational, IsImaginary,),
                IsIrrational=(IsRational, IsImaginary,),
                IsInteger=(IsFraction, IsIrrational, IsImaginary,),
                IsFraction=(IsInteger, IsIrrational, IsImaginary,),
                IsOdd=(IsZero, IsEven, IsFraction, IsIrrational, IsImaginary,),
                IsEven=(IsOdd,IsFraction, IsIrrational, IsImaginary,),
                IsPrime=(IsZero, IsComposite, IsFraction, IsIrrational, IsImaginary,),
                IsComposite=(IsPrime, IsFraction, IsIrrational, IsImaginary,),
                IsPositive=(IsNonPositive, IsNegative, IsZero, IsImaginary,),
                IsNegative=(IsNonNegative, IsPositive, IsZero, IsImaginary,),
                IsNonPositive=(IsPositive, IsImaginary, ),
                IsNonNegative=(IsNegative, IsImaginary, ),
                IsZero=(IsPositive,IsNegative, IsPrime, IsOdd)
                )

class Inclusion(Condition):

    signature = FunctionSignature((Basic,), boolean_classes)

    @property
    def expr(self):
        return self[0]

    def is_subset_of(self, other):
        if other.is_Inclusion:
            if self.expr==other.expr:
                if isinstance(self, other.__class__):
                    return True
        return False

    def is_opposite_to(self, other):
        if other.is_Inclusion:
            if self.expr==other.expr:
                clses = get_opposite_classes_map().get(self.__class__.__name__)
                if clses is not None and isinstance(other,clses):
                    return True
            elif self.is_Signed and other.is_Signed:
                if self.__class__ is other.__class__ and self.expr==-other.expr:
                    return True
        return False

class IsComplex(Inclusion):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Real: return True
        if arg.is_ImaginaryUnit: return True

class IsZero(IsComplex):
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Number:
            return arg==0
        if arg.is_Add and len(arg)==1:
            return IsZero(arg.items()[0][0])

class IsReal(IsComplex):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Real: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsImaginary(IsComplex):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return True

class IsRational(IsReal):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Rational: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsIrrational(IsReal):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Rational: return False
        if arg.is_ImaginaryUnit: return False

class IsInteger(IsRational):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsFraction(IsRational):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Fraction: return True
        if arg.is_Number: return False
        if arg.is_ImaginaryUnit: return False

class IsPrime(IsInteger):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer:
            if arg<=0: return False
            from ntheory.primetest import isprime
            return isprime(arg)
        if arg.is_Number:
            return False

class IsComposite(IsInteger):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer:
            if arg<=0: return True
            from ntheory.primetest import isprime
            return not isprime(arg)
        if arg.is_Number:
            return False

class IsEven(IsInteger):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer:
            return arg % 2==0
        if arg.is_Number:
            return False

class IsOdd(IsInteger):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Integer:
            return arg % 2==1
        if arg.is_Number:
            return False


class Signed(IsReal):

    signature = FunctionSignature((Basic,), boolean_classes)

class IsNonPositive(Signed):
    """ Represents condition x <= 0.
    """
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Number:
            return arg <= 0
        #return Or(IsPositive(-arg), IsZero(arg))

class IsNonNegative(Signed):
    
    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Number:
            return arg >= 0


class IsPositive(IsNonNegative):
    """ Represents condition x > 0.
    """

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Number:
            return arg > 0


class IsNegative(IsNonPositive):

    @classmethod
    def canonize(cls, (arg,)):
        if arg.is_Number:
            return arg < 0

