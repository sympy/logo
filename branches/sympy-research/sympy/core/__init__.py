"""Core module. Provides the basic operations needed in sympy.
"""
# merging symbolic and sympy.core
# Author: Pearu Peterson <pearu.peterson@gmail.com>
# Created: May 2007

from basic import Basic
from symbol import Symbol
from numbers import Real, Rational, Integer
from power import Pow
from mul import Mul
from add import Add
from relational import Equality, Inequality, Unequality, StrictInequality
from function import Lambda

# set repr output to pretty output:
Basic.interactive = True

# expose singletons like exp, log, oo, I, etc.
for _n,_cls in Basic.singleton.items():
    exec _n + ' = _cls()'
