"""Core module. Provides the basic operations needed in sympy.
"""
# make output from recursion errors more pleasant
#import sys
#sys.setrecursionlimit(30)

from basic import Basic, sympify #, S
from symbol import Symbol #, Wild, symbols
from number import Number, Real, Rational, Integer, Fraction, Float
#from power import Pow
#from mul import Mul
from add import Add, MutableAdd
from mul import Mul, MutableMul, Pow, sqrt
#from relational import Equality, Inequality, Unequality, StrictInequality
#from new_function import NewFunction, sin_
#from function import Lambda, Function, Apply, FApply, Composition, FPow, WildFunction, Derivative, DefinedFunction, diff
from function import Function, Lambda
from interval import Interval
from singleton import pi, I, oo, zoo, E, nan

import assume
from predicate import And, Or, XOr, Not, Implies, Equiv, \
     Equal, Less, IsReal, IsInteger, IsRational, IsPositive,\
     IsNegative, Boolean, IsNonPositive, IsNonNegative, \
     IsPrime, IsComposite, IsFraction, IsComplex, LessEqual, \
     GreaterEqual, Greater, IsImaginary, IsEven, IsOdd, IsZero, \
     IsIrrational, IsNonZero


# set repr output to pretty output:
#Basic.set_repr_level(1)

# expose singletons like exp, log, oo, I, etc.
#for _n, _cls in Basic.singleton.items():
#    exec '%s = _cls()' % (_n)

#sympify = Basic.sympify
