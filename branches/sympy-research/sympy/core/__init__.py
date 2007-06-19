"""Core module. Provides the basic operations needed in sympy.
"""
# merging symbolic and sympy.core
# Author: Pearu Peterson <pearu.peterson@gmail.com>
# Created: May 2007

from basic import Basic
from symbol import Symbol, Wild
from numbers import Number, Real, Rational, Integer
from power import Pow
from mul import Mul
from add import Add
from relational import Equality, Inequality, Unequality, StrictInequality
from function import Lambda, Function, Apply, FApply, Composition, FPow, WildFunction, Integral, Derivative
from interval import Interval

import defined_functions

from order import Order
from limit import Limit

# set repr output to pretty output:
Basic.interactive = True

# expose singletons like exp, log, oo, I, etc.
for _n,_cls in Basic.singleton.items():
    exec _n + ' = _cls()'

sympify = Basic.sympify

# this is for backward compatibilty, to be removed:
mhash = lambda obj: hash(obj)
hashing = lambda obj: hash(obj)
#
