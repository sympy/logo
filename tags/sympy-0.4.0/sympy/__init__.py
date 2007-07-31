"""
Computer Algebra System (CAS) in Python
=======================================

Sympy is a symbolic manipulation package, written in pure Python. Its aim is to
become a full featured CAS in Python, while keeping the code as simple as
possible in order to be comprehensible and easily extensible.

Features
========

Currently, SymPy core has only around 1500 lines of code (including extensive
comments) and its capabilities include:

    - basic arithmetics *,/,+,-
    - basic simplification (like a*b*b + 2*b*a*b -> 3*a*b^2)
    - expansion (like (a+b)^2 -> a^2 + 2*a*b + b^2)
    - functions (exp, ln, sin, cos, tan, ...)
    - complex numbers (like exp(I*x).evalc() ->
    - cos(x)+I*sin(x))
    - differentiation
    - taylor series
    - basic substitution (like x-> ln(x))
    - arbitrary precision integers,
    - rationals and floats 

Then there are SymPy modules (1000 lines) for these tasks:

    - limits (like limit(x*log(x), x, 0) -> 0)
    - integration (currently it can only do very simple integrals)
    - polynomials (division, gcd, square free decomposition)
    - symbolic matrices 

To help you get started, here is a simple example in the python
interpreter:

    >>> from sympy import Symbol, cos
    >>> x = Symbol('x')
    >>> e = 1/cos(x)
    >>> print e.series(x,10)
    1+1/2*x**2+O(x**10)+5/24*x**4+61/720*x**6+277/8064*x**8

For full documentation, see the docs at our web page:
U{http://code.google.com/p/sympy/wiki/Documentation}

Structure
=========

Sympy is basically divided in two modules: the core module, which contains 
the classes needed for basic symbolic manipulations, like the definition of a
Symbol or a Rational number, and sympy.modules, a high-level module that 
contains algorithms for symbolic computations, like limit, integration, etc.


G{packagetree sympy}
"""

__version__ = "0.4.0"

from sympy.core.basic import Basic
from sympy.core.symbol import Symbol, O
from sympy.core.functions import Function, exp, log, ln, sqrt, sign, diff
from sympy.core.functions import Derivative
from sympy.core.numbers import Rational, Real, Number, oo, I, pi
from sympy.core.power import Pow, pole_error
from sympy.core.addmul import Add, Mul
from sympy.core.hashing import mhash

from sympy.modules.limits import limit
from sympy.modules.trigonometric import sin, cos, tan, sec, csc, cot, atan, asin
from sympy.modules.integrals import integrate
from sympy.modules.matrices import Matrix
from sympy.modules.solvers import solve, dsolve
from sympy.modules.simplify import ratsimp, simplify
from sympy.modules.polynomials import factor, roots, div, groebner

from sympy.modules.printing.pretty import pretty, pretty_print, pprint
from sympy.modules.printing.mathml import mathml
from sympy.modules.printing.latex import latex