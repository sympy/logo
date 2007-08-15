
from sympy.core import *

from sympy.simplify import *

def test_ratsimp():
    x = Symbol("x")
    y = Symbol("y")
    e = 1/x+1/y
    assert e != (x+y)/(x*y)
    assert ratsimp(e) == (x+y)/(x*y)

    #e = -x-y-(x+y)**(-1)*y**2+(x+y)**(-1)*x**2
    #assert e != -2*y
    #assert ratsimp(e) == -2*y

    #e = x/(x+y)+y/(x+y)
    #assert e != 1
    #assert ratsimp(e) == 1

    e = 1/(1+1/x)
    assert ratsimp(e) == x/(x+1)
    assert (x+1)*ratsimp(e)/x == 1
    assert ratsimp(exp(e)) == exp(x/(x+1))

#def test_trigsimp():
#    x = Symbol('x')
#    y = Symbol('y')
#    assert trigsimp(5*cos(x)**2 + 5*sin(x)**2) == 5
#    assert trigsimp(5*cos(x/2)**2 + 2*sin(x/2)**2) == 2 + 3*cos(x/2)**2
#    assert trigsimp(1 + tan(x)**2) == sec(x)**2
#    assert trigsimp(1 + cot(x)**2) == csc(x)**2

#def test_factorial_simplify():
    # There are more tests in test_factorials.py. These are just to
    # ensure that simplify() calls factorial_simplify correctly
#    from sympy.specfun.factorials import factorial
#    x = Symbol('x')
#    assert simplify(factorial(x)/x) == factorial(x-1)
#    assert simplify(factorial(factorial(x))) == factorial(factorial(x))

def test_simplify():
    x = Symbol('x')
    y = Symbol('y')
    e = 1/x + 1/y
    assert e != (x+y)/(x*y)
    assert simplify(e) == (x+y)/(x*y)

    e = (4+4*x-2*(2+2*x))/(2+2*x)
    assert simplify(e) == 0

def test_fraction():
    x, y, z = map(Symbol, 'xyz')

    assert fraction(Rational(1, 2)) == (1, 2)

    assert fraction(x) == (x, 1)
    assert fraction(1/x) == (1, x)
    assert fraction(x/y) == (x, y)
    assert fraction(x/2) == (x, 2)

    assert fraction(x*y/z) == (x*y, z)
    assert fraction(x/(y*z)) == (x, y*z)

    assert fraction(1/y**2) == (1, y**2)
    assert fraction(x/y**2) == (x, y**2)

    assert fraction((x**2+1)/y) == (x**2+1, y)
    assert fraction(x*(y+1)/y**7) == (x*(y+1), y**7)

def test_together():
    x, y, z = map(Symbol, 'xyz')

    assert together(1/x) == 1/x

    assert together(1/x + 1) == (x+1)/x
    assert together(1/x + x) == (x**2+1)/x

    assert together(1/x + Rational(1, 2)) == (x+2)/(2*x)

    assert together(1/x + 2/y) == (2*x+y)/(y*x)
    assert together(1/(1 + 1/x)) == x/(1+x)
    assert together(x/(1 + 1/x)) == x**2/(1+x)

    assert together(1/x + 1/y + 1/z) == (x*y + x*z + y*z)/(x*y*z)

    assert together(1/(x*y) + 1/(x*y)**2) == y**(-2)*x**(-2)*(1+x*y)
    assert together(1/(x*y) + 1/(x*y)**4) == y**(-4)*x**(-4)*(1+x**3*y**3)
    assert together(1/(x**7*y) + 1/(x*y)**4) == y**(-4)*x**(-7)*(x**3+y**3)

    assert together(sin(1/x+1/y)) == sin(1/x+1/y)
    assert together(sin(1/x+1/y), deep=True) == sin((x+y)/(x*y))

def test_separate():
    x, y, z = map(Symbol, 'xyz')

    assert separate((x*y*z)**4) == x**4*y**4*z**4
    assert separate((x*y*z)**x) == x**x*y**x*z**x
    assert separate((x*(y*z)**2)**3) == x**3*y**6*z**6

    assert separate((sin((x*y)**2)*y)**z) == sin((x*y)**2)**z*y**z
    assert separate((sin((x*y)**2)*y)**z, deep=True) == sin(x**2*y**2)**z*y**z

    assert separate(exp(x)**2) == exp(2*x)
    assert separate((exp(x)*exp(y))**2) == exp(2*x)*exp(2*y)
    #assert separate((exp(x)*exp(y))**z) == exp(x*z)*exp(y*z)

    assert separate((exp((x*y)**z)*exp(y))**2) == exp(2*(x*y)**z)*exp(2*y)
    assert separate((exp((x*y)**z)*exp(y))**2, deep=True) == exp(2*x**z*y**z)*exp(2*y)

def test_collect():
    pass