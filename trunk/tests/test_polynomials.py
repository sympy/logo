
import sys
sys.path.append(".")

import py

from sympy import Symbol
from sympy.modules.polynomials import *

def test_ispoly():
    x = Symbol("x")
    y = Symbol("y")
    assert not ispoly( x.sqrt(), x )
    assert ispoly( Rational(2), x)
    assert ispoly( x, x)
    assert ispoly( x**2, x)
    assert ispoly( x**2 + 3*x - 8, x)
    assert ispoly( x**2 + 3*x*y.sqrt() - 8, x)
    assert not ispoly( x**2 + 3*x*y.sqrt() - 8 , y)

    #assert Rational(1).ispoly(sin(x))
    #assert not exp(x).ispoly(sin(x))

def test_coeff():
    x = Symbol("x")
    assert coeff(x**2, x, 1) == 0
    assert coeff(x**2, x, 2) == 1
    assert coeff(x**2, x, 2) != 0

    assert coeff(2*x+18*x**8, x, 1) == 2
    assert coeff(2*x+18*x**8, x, 4) == 0
    assert coeff(2*x+18*x**8, x, 8) == 18

def test_get_poly():
    x = Symbol("x")
    y = Symbol("y")
    assert get_poly(3*x**2,x) == [(3,2)]
    assert get_poly(2*x+3*x**2 - 5,x) == [(-5, 0), (2, 1), (3,2)]
    assert get_poly(2*x**100+3*x**2 - 5,x) == [(-5, 0), (3,2), (2, 100)]

    assert get_poly(y.sqrt()*x,x) == [(y.sqrt(),1)]
    py.test.raises(PolynomialException, "get_poly(x.sqrt(),x)")
