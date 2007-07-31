import sys
sys.path.append(".")

from sympy.modules.matrices import sigma, gamma, zero, one, I, Matrix,minkowski_tensor
from sympy import Symbol

def test_multiplication():
    a=Matrix((
        (1, 2),
        (3, 1),
        (0, 6),
        ))

    b = Matrix ((
        (1, 2),
        (3, 0),
        ))

    c= a*b
    assert c[0,0]==7
    assert c[0,1]==2
    assert c[1,0]==6
    assert c[1,1]==6
    assert c[2,0]==18
    assert c[2,1]==0

    x = Symbol("x")

    c = b * Symbol("x")
    assert isinstance(c,Matrix)
    assert c[0,0] == x
    assert c[0,1] == 2*x
    assert c[1,0] == 3*x
    assert c[1,1] == 0

    c = 5 * b
    assert isinstance(c,Matrix)
    assert c[0,0] == 5
    assert c[0,1] == 2*5
    assert c[1,0] == 3*5
    assert c[1,1] == 0

def test_power():
    A = Matrix([[2,3],[4,5]])
    assert (A**5)[:] == [6140, 8097, 10796, 14237]
    A = Matrix([[2, 1, 3],[4,2, 4], [6,12, 1]])
    assert (A**3)[:] == [290, 262, 251, 448, 440, 368, 702, 954, 433]

def test_Pauli():
    #this and the following test are testing both Pauli and Dirac matrices
    #and also that the general Matrix class works correctly in a real world
    #situation
    sigma1=sigma(1)
    sigma2=sigma(2)
    sigma3=sigma(3)

    assert sigma1 == sigma1
    assert sigma1 != sigma2

    assert sigma1*sigma2 == I*sigma3
    assert sigma3*sigma1 == I*sigma2
    assert sigma2*sigma3 == I*sigma1

    assert sigma1*sigma1 == one(2)
    assert sigma2*sigma2 == one(2)
    assert sigma3*sigma3 == one(2)

    assert sigma1*2*sigma1 == 2*one(2)
    assert sigma1*sigma3*sigma1 == -sigma3

def test_Dirac():
    gamma0=gamma(0)
    gamma1=gamma(1)
    gamma2=gamma(2)
    gamma3=gamma(3)
    gamma5=gamma(5)

    assert gamma5 == I * gamma0 * gamma1 * gamma2 * gamma3
    assert gamma1 * gamma2 + gamma2 * gamma1 == zero(4)
    assert gamma0 * gamma0 == one(4) * minkowski_tensor[0,0]
    assert gamma2 * gamma2 != one(4) * minkowski_tensor[0,0]
    assert gamma2 * gamma2 == one(4) * minkowski_tensor[2,2]

    assert gamma(5,True) == \
        I*gamma(0,True)*gamma(1,True)*gamma(2,True)*gamma(3,True)

def test_creation():
    x = Symbol("x")
    a = Matrix([x, 0], [0, 0])
    m = a
    assert m.cols == m.lines
    assert m.cols == 2
    assert m[:] == [x,0,0,0]
    b = Matrix(2,2, [x, 0, 0, 0])
    m = b
    assert m.cols == m.lines
    assert m.cols == 2
    assert m[:] == [x,0,0,0]

    assert a == b