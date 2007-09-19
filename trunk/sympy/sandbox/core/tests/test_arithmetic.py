from sympy.sandbox.core import *

def test_arithmetic():
    x = Symbol('x')
    y = Symbol('y')
    assert x+1 == 1+x
    assert x+y == y+x
    assert (x+y)+3 == x+(y+3)
    assert 2*x == x*2
    assert 0*x == 0
    assert 1*x == x
    assert 2*x - x == x

def test_mul_performance():
    from time import clock
    from random import randint
    from sympy.sandbox.core import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Mul(x,randint(0,1000000),y)
    t2 = clock()
    d1 = t2-t1

    from sympy.core import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Mul(x,randint(0,1000000),y)
    t2 = clock()
    d2 = t2-t1
    print '\ntiming Mul(x, <random int>, y): sandbox.core %s secs, sympy.core %s secs' % (d1,d2)

def test_add_performance():
    from time import clock
    from random import randint
    from sympy.sandbox.core import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Add(x,randint(0,1000000),y)
    t2 = clock()
    d1 = t2-t1

    from sympy.core import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Add(x,randint(0,1000000),y)
    t2 = clock()
    d2 = t2-t1
    print '\ntiming Add(x, <random int>, y): sandbox.core %s secs, sympy.core %s secs' % (d1,d2)

def test_sum_performance():
    from time import clock
    from sympy.sandbox.core import Symbol, MutableAdd, Integer
    x = Symbol('x')
    n = 200

    i = n
    s = Integer(0)    
    t1 = clock()
    while i:
        i -= 1
        s += x**i
    assert len(s)==n-1
    t2 = clock()
    d1 = t2-t1
    
    i = n
    s = MutableAdd()
    t1 = clock()
    while i:
        i -= 1
        s += x**i
    t2 = clock()
    s = s.canonical()
    assert len(s)==n-1
    d2 = t2-t1

    from sympy.core import Symbol, Add
    i = n
    x = Symbol('x')
    s = Add()
    t1 = clock()
    while i:
        i -= 1
        s += x**i
    t2 = clock()
    assert len(s)==n
    d3 = t2-t1
    print '\ntiming summation: sandbox.core(direct/MutableAdd) %s/%s secs, sympy.core %s secs' % (d1,d2,d3)