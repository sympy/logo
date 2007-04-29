import sys
sys.path.append(".")

import py

import sympy as g
from sympy import sin, Symbol, log, Order, Rational, exp

def testseries1():
    x=Symbol("x")
    e=sin(x)
    assert e.series(x,0) != 0
    assert e.series(x,0) == Order(1)
    assert e.series(x,1) == Order(x)
    assert e.series(x,2) == x + Order(x**2)
    assert e.series(x,3) == x + Order(x**3)
    assert e.series(x,4) == x-x**3/6 + Order(x**4)

    e=(exp(x)-1)/x
    assert e.series(x,2) == 1+Order(x)
    #this tests, that the Basic.series() cannot do it (but Mul.series can)
    py.test.raises(g.core.power.pole_error, g.core.basic.Basic.series, e,x,0)

    assert x.series(x,0) == Order(1)
    assert x.series(x,1) == Order(x)
    assert x.series(x,2) == x

def testseriesbug1():
    x=g.Symbol("x")
    assert (1/x).series(x,3)==1/x
    assert (x+1/x).series(x,3)==x+1/x

def testseries2():
    x=g.Symbol("x")
    assert ((x+1)**(-2)).series(x,4)==1-2*x+3*x**2-4*x**3+Order(x**4)
    assert ((x+1)**(-1)).series(x,4)==1-x+x**2-x**3+Order(x**4)
    assert ((x+1)**0).series(x,3)==1
    assert ((x+1)**1).series(x,3)==1+x
    assert ((x+1)**2).series(x,3)==1+2*x+x**2+Order(x**3)
    assert ((x+1)**3).series(x,3)==1+3*x+3*x**2+Order(x**3)

    assert (1/(1+x)).series(x,4)==1-x+x**2-x**3+Order(x**4)
    assert (x+3/(1+2*x)).series(x,4)==3-5*x+12*x**2-24*x**3+Order(x**4)

    assert ((1/x+1)**3).series(x,3)== x**(-3)+3*x**(-2)+Order(x**(-1))
    assert (1/(1+1/x)).series(x,3)==x-x**2+x**3
    assert (1/(1+1/x**2)).series(x,6)==x**2-x**4+x**6-x**8+x**10-x**12

def xtestfind(self):
    a=g.Symbol("a")
    b=g.Symbol("b")
    c=g.Symbol("c")
    p=g.Rational(5)
    e=a*b+b**p
    assert e.find(b)
    assert not e.find(c)

def xtest_log():
    "too difficult"
    x=g.Symbol("x")
    ec=g.exp(g.Rational(1))
    e=(g.log(1/x+ec)-ec)/(x*g.log(1/x+1))
    print
    print e.eval()
    d= e.diff(x)

def test_bug2():
    w=g.Symbol("w")
    log=g.log
    e=(w**(-1)+w**(-log(3)*log(2)**(-1)))**(-1)*(3*w**(-log(3)*log(2)**(-1))+2*w**(-1))
    e=e.eval().expand()
    #should be 3, but is 2
#    print e.series(w,4)

def test_exp():
    x=Symbol("x")
    e=(1+x)**(1/x)
    assert e.series(x,2) == exp(1)

def test_exp2():
    x=g.Symbol("x")
    w=g.Symbol("w")
    log=g.log
    e=w**(1-log(x)/(log(2)+log(x)))
    assert e.eval().series(w,1)!=0

def test_generalexponent():
    x=g.Symbol("x")
    log=g.log
    p=2
    e=(2/x+3/x**p)/(1/x+1/x**p)
    assert e.eval().series(x,1).leadterm(x)==(3,0)
    p=g.Rational(1,2)
    e=(2/x+3/x**p)/(1/x+1/x**p)
    assert e.eval().series(x,1).leadterm(x)==(2,0)
    p=g.Rational(3,2)
    e=(2/x+3/x**p)/(1/x+1/x**p)
    assert e.eval().series(x,1).leadterm(x)==(3,0)

    e=1+x**g.Rational(1,2)
    assert e.eval().series(x,4)==1+x**g.Rational(1,2)
    e=1/(1+x**g.Rational(1,2))
    assert e.eval().series(x,2)==1-x**g.Rational(1,2)

def test_subsbug1():
    x=g.Symbol("x")
    e=1+x**g.Rational(1,2)
    e=e.diff(x)
    py.test.raises(g.core.power.pole_error,e.subs,x,g.Rational(0))

def test_seriesbug2():
    w=Symbol("w")
    #simple case (1):
    e=((2*w)/w)**(1+w)
    assert e.series(w,1) == 2 + Order(w)
    assert e.series(w,1).subs(w,0)==2

    #test sin
    e=sin(2*w)/w
    assert e.series(w,2) == 2 + Order(w)

    #more complicated case, but sin(x)~x, so the result is the same as in (1)
    e=(sin(2*w)/w)**(1+w)
    #correct:
    #assert e.series(w,2) == 2 + Order(w)
    #this is wrong!!:
    assert e.series(w,2) == 2 + Order(w**2)
    assert e.series(w,2).subs(w,0)==2

def test_seriesbug3():
    x=Symbol("x")
    w=Symbol("w")

    #some limits need this series expansion to work:
    e=(w**(-log(5)/log(3))-1/w)**(1/x)
    assert  e.series(w,1).subs(log(w),-log(3)*x).subs(w,0) == 5

def test_order():
    #these tests basically define the Order's behavior. So be very careful
    #when changing them (as with every test in SymPy :)
    x = Symbol("x")
    assert Order(x) == Order(x)
    assert Order(x**2) == Order(x**2)
    assert Order(x) != Order(x**2)

    assert Order(x) + Order(x) == Order(x)
    assert Order(x) - Order(x) != 0
    assert Order(x) - Order(x) == Order(x)

    assert Order(2*x) == Order(x)
    assert 2*Order(x) == Order(x)
    assert Order(3*x) == Order(x)
    assert 3*Order(x) == Order(x)
    assert Order(x) == Order(x*8)
    assert Order(x) == Order(x)*8

    assert Order(x+1) == Order(x)
    assert Order(x)+0 == Order(x)
    assert Order(x)+0 == 0+Order(x)
    assert Order(x)+1 != Order(x)
    assert Order(x)+1 == 1+Order(x)
    assert Order(x)+x == Order(x)
    assert Order(x)+x**2 == Order(x)
    assert Order(x)+x**3 == Order(x)

    assert x*Order(x) != Order(x)
    assert x*Order(x) == Order(x**2)
    assert Order(x)*x == Order(x**2)
    assert Order(x**3)*x == Order(x**4)

    assert ((x+Order(x)) - (x+Order(x))) == Order(x)
    assert Order(x)/x == Order(1)

    assert Order(x)*Order(x) == Order(x**2)

    assert Order(1).diff(x) == Order(1)
    assert Order(x).diff(x) == Order(1)
    assert Order(x**2).diff(x) == Order(x)

    x = Symbol("w")
    assert Order(x)+1 != Order(x)

    assert (2+Order(x)) != 2
    assert (2+Order(x)).removeOrder() == 2
    assert (2+x+Order(x**2)).removeOrder() == x+2
