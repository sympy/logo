"""
This module contain solvers for all kinds of equations,
both algebraic (solve) and differential (dsolve).
"""

from sympy import Basic, Symbol, Number, Mul, log, Add, \
        sin, cos, integrate, sqrt, exp, Rational

from sympy.core.functions import Derivative, diff
from sympy.modules.simplify import collect, simplify
from sympy.modules.matrices import zeronm
from sympy.modules.utils import any

class Equation(Basic):

    def __init__(self, lhs, rhs):
        Basic.__init__(self)

        self._args = [Basic.sympify(lhs),
                      Basic.sympify(rhs)]

    @property
    def lhs(self):
        return self._args[0]

    @property
    def rhs(self):
        return self._args[1]

    @staticmethod
    def addeval(x, y):
        if isinstance(x, Equation) and isinstance(y, Equation):
            return Equation(x.lhs + y.lhs, x.rhs + y.rhs)
        elif isinstance(x, Equation):
            return Equation(x.lhs + y, x.rhs + y)
        elif isinstance(y, Equation):
            return Equation(x + y.lhs, x + y.rhs)
        else:
            return None

    @staticmethod
    def muleval(x, y):
        if isinstance(x, Equation) and isinstance(y, Equation):
            return Equation(x.lhs * y.lhs, x.rhs * y.rhs)
        elif isinstance(x, Equation):
            return Equation(x.lhs * y, x.rhs * y)
        elif isinstance(y, Equation):
            return Equation(x * y.lhs, x * y.rhs)
        else:
            return None

    def __eq__(self, other):
        if isinstance(other, bool):
            if other == True:
                return self.lhs.hash() == self.rhs.hash()
            else:
                return self.lhs.hash() != self.rhs.hash()
        elif isinstance(other, Equation):
            return self.lhs.hash() == other.lhs.hash() and \
                   self.rhs.hash() == other.rhs.hash()
        else:
            return self.lhs.hash() == other.hash() and \
                   self.rhs.hash() == other.hash()

    def __ne__(self, other):
        if isinstance(other, bool):
            if other == False:
                return self.lhs.hash() == self.rhs.hash()
            else:
                return self.lhs.hash() != self.rhs.hash()
        elif isinstance(other, Equation):
            return self.lhs.hash() != other.lhs.hash() or \
                   self.rhs.hash() != other.rhs.hash()
        else:
            return self.lhs.hash() != other.hash() or \
                   self.rhs.hash() != other.hash()

    def __nonzero__(self):
        return self.lhs.hash() == self.rhs.hash()

    def __latex__(self):
        return "%s = %s" % (self.lhs.__latex__(), self.rhs.__latex__())

class Inequality(Basic):

    def __init__(self, lhs, rhs):
        Basic.__init__(self)

        self._args = [Basic.sympify(lhs),
                      Basic.sympify(rhs)]

    @property
    def lhs(self):
        return self._args[0]

    @property
    def rhs(self):
        return self._args[1]

    @staticmethod
    def addeval(x, y):
        if isinstance(x, Inequality) and isinstance(y, Inequality):
            return Inequality(x.lhs + y.lhs, x.rhs + y.rhs)
        elif isinstance(x, Inequality):
            return Inequality(x.lhs + y, x.rhs + y)
        elif isinstance(y, Inequality):
            return Inequality(x + y.lhs, x + y.rhs)
        else:
            return None

    def __latex__(self):
        return "%s < %s" % (self.lhs.__latex__(), self.rhs.__latex__())

class StrictInequality(Inequality):

    @staticmethod
    def addeval(x, y):
        if isinstance(x, StrictInequality) and isinstance(y, StrictInequality):
            return StrictInequality(x.lhs + y.lhs, x.rhs + y.rhs)
        elif isinstance(x, StrictInequality):
            return StrictInequality(x.lhs + y, x.rhs + y)
        elif isinstance(y, StrictInequality):
            return StrictInequality(x + y.lhs, x + y.rhs)
        else:
            return None

    def __latex__(self):
        return "%s \le %s" % (self.lhs.__latex__(), self.rhs.__latex__())

def solve(eq, syms):
    """
    Solves any (supported) kind of equation (not differential).

    Examples
    ========
      >>> from sympy import Symbol
      >>> x, y = Symbol('x'), Symbol('y')
      >>> solve(2*x-3, [x])
      3/2

    """

    if isinstance(syms, Basic):
        syms = [syms]

    if isinstance(syms, Symbol) or len(syms) == 1: # change this
        x = syms[0]
        a,b,c = [Symbol(s, dummy = True) for s in ["a","b","c"]]

        r = eq.match(a*x + b, [a,b]) # linear equation
        if r and _wo(r,x): return solve_linear(r[a], r[b])

        r = eq.match(a*x**2 + c, [a,c]) # quadratic equation
        if r and _wo(r,x): return solve_quadratic(r[a], 0, r[c])

        r = eq.match(a*x**2 + b*x + c, [a,b,c]) # quadratic equation
        if r and _wo(r,x): return solve_quadratic(r[a], r[b], r[c])

        d = Symbol('d', dummy=True)
        r = eq.match(a*x**3 + b*x**2 + c*x + d, [a,b,c,d])
        if r and _wo(r, x): return solve_cubic(r[a], r[b], r[c], r[d])

        r = eq.match(a*x**3 - b*x + c)
        if r and _wo(r, x): return solve_cubic(r[a], 0, r[b], r[c])
    else:
        # augmented matrix
        n, m = len(eq), len(syms)
        matrix = zeronm(n, m+1)

        index = {}

        for i in range(0, len(syms)):
            index[syms[i]] = i

        for i in range(0, n):
            if isinstance(eq[i], Equation):
                # got equation, so move all the
                # terms to the left hand side
                equ = eq[i].lhs - eq[i].rhs
            else:
                equ = Basic.sympify(eq[i])

            content = collect(equ.expand(), syms, pretty=False)

            for sym, expr in content.iteritems():
                if isinstance(sym, Symbol) and not expr.has_any(syms):
                    matrix[i, index[sym]] = expr
                elif sym == Rational(1) and not expr.has_any(syms):
                    matrix[i, m] = -expr
                else:
                    raise "Not a linear system."
        else:
            return solve_linear_system(matrix, syms)

    # at this point we will need Groebner basis
    # and multivariate polynomial factorization

    raise "Sorry, can't solve it (yet)."

def solve_linear_system(system, syms):
    """Solve system of N linear equations with M variables, which means
       both Cramer and over defined systems are supported. The possible
       number of solutions is zero, one or infinite. Respectively this
       functions will return empty dictionary or dictionary containing
       the same or less number of items as the number of variables. If
       there is infinite number of solutions, it will skip variables
       with can be assigned with arbitrary values.

       Input to this functions is a Nx(M+1) matrix, which means it has
       to be in augmented form. If you are unhappy with such setting
       use 'solve' method instead, where you can input equations
       explicitely. And don't worry aboute the matrix, this function
       is persistent and will make a local copy of it.

       The algorithm used here is fraction free Gaussian elimination,
       which results, after elimination, in upper-triangular matrix.
       Then solutions are found using back-substitution. This approach
       is more efficient and compact than the Gauss-Jordan method.

       >>> from sympy import *
       >>> x, y = symbols('x', 'y')

       Solve the following system:

              x + 4 y ==  2
           -2 x +   y == 14

       >>> system = Matrix(( (1, 4, 2), (-2, 1, 14)))
       >>> solve_linear_system(system, [x, y])
       {x: -6, y: 2}

    """
    #matrix = system.copy()  # we would like to be persistent
    matrix = system          # where is copy() ???
    i, m = 0, matrix.cols-1  # don't count augmentation

    while i < matrix.lines:
        if matrix [i, i] == 0:
            # there is no pivot in current column
            # so try to find one in other colums
            for k in range(i+1, m):
                if matrix[i, k] != 0:
                    break
            else:
                if matrix[i, m] != 0:
                    return {}   # no solutions
                else:
                    # zero row or was a linear combination of
                    # other rows so now we can safely skip it
                    matrix.row_del(i)
                    continue

            # we want to change the order of colums so
            # the order of variables must also change
            syms[i], syms[k] = syms[k], syms[i]
            matrix.col_swap(i, k)

        pivot = matrix [i, i]

        # divide all elements in the current row by the pivot
        matrix.row(i, lambda x, _: x / pivot)

        for k in range(i+1, matrix.lines):
            if matrix[k, i] != 0:
                coeff = matrix[k, i]

                # subtract from the current row the row containing
                # pivot and multiplied by extracted coefficient
                matrix.row(k, lambda x, j: x - matrix[i, j]*coeff)

        i += 1

    # if there weren't any problmes, augmented matrix is now
    # in row-echelon form so we can check how many solutions
    # there are and extract them using back substitution

    if len(syms) == matrix.lines:
        # this system is Cramer equivalent so there is
        # exactly one solution to this system of equations
        k, solutions = i-1, {}

        while k >= 0:
            content = matrix[k, m]

            # run back-substitution for variables
            for j in range(k+1, m):
                content -= matrix[k, j]*solutions[syms[j]]

            solutions[syms[k]] = simplify(content)

            k -= 1

        return solutions
    elif len(syms) > matrix.lines:
        # this system will have infinite number of solutions
        # dependent on exactly len(syms) - i parameters
        k, solutions = i-1, {}

        while k >= 0:
            content = matrix[k, m]

            # run back-substitution for variables
            for j in range(k+1, i):
                content -= matrix[k, j]*solutions[syms[j]]

            # run back-substitution for parameters
            for j in range(i, m):
                content -= matrix[k, j]*syms[j]

            # NOTE: I'm not sure if 'simplify' should be applied
            # here. It would have been better if there was keyword
            # simplify=True for this.
            solutions[syms[k]] = simplify(content)

            k -= 1

        return solutions
    else:
        return {}   # no solutions

def solve_undetermined_coeffs(equ, coeffs, sym):
    """Solve equation of a type p(x; a_1, ..., a_k) == q(x) where both
       p, q are univariate polynomials and f depends on k parameters.
       The result of this functions is a dictionary with symbolic
       values of those parameters with respect to coefficiens in q.

       This functions accepts both Equations class instances and ordinary
       SymPy expressions. Specification of parameters and variable is
       obligatory for efficiency and simplicity reason.

       >>> from sympy import *
       >>> a, b, c, x = symbols('a', 'b', 'c', 'x')

       >>> solve_undetermined_coeffs(2*a*x + a+b == x, [a, b], x)
       {a: 1/2, b: -1/2}

       >>> solve_undetermined_coeffs(a*c*x + a+b == x, [a, b], x)
       {a: (1/c), b: -1/c}

    """
    if isinstance(equ, Equation):
        # got equation, so move all the
        # terms to the left hand side
        equ = equ.lhs - equ.rhs

    system = collect(equ, sym, pretty=False).values()

    if not any([ equ.has(sym) for equ in system ]):
        # consecutive powers in the input expressions have
        # been successfully collected, so solve remaining
        # system using Gaussian ellimination algorithm
        return solve(system, coeffs)
    else:
        return {} # no solutions

def solve_linear_system_LU(matrix, syms):
    """ LU function works for invertible only """
    assert matrix.lines == matrix.cols-1
    A = matrix[:matrix.lines,:matrix.lines]
    b = matrix[:,matrix.cols-1:]
    soln = A.LUsolve(b)
    solutions = {}
    for i in range(soln.lines):
        solutions[syms[i]] = soln[i,0]
    return solutions

def solve_linear(a, b):
    """Solve a*x + b == 0"""
    return -b/a

def solve_quadratic(a, b, c):
    """Solve the cuadratic a*x**2 + b*x + c == 0"""
    D = b**2-4*a*c
    if D == 0:
        return [-b/(2*a)]
    else:
        return [
                (-b+sqrt(D))/(2*a),
                (-b-sqrt(D))/(2*a)
               ]
def solve_cubic(a, b, c, d):
    """Solve the cubic a*x**3 + b*x**2 + c*x + d == 0

    arguments are supposed to be sympy objects (so no python float's, int's, etc.)

    Cardano's method: http://en.wikipedia.org/wiki/Cubic_equation#Cardano.27s_method
    """
    # we calculate the depressed cubic t**3 + p*t + q

    #normalize
    a_1 = b / a
    b_1 = c / a
    c_1 = c / a

    del a, b, c

    p = b_1 - (a_1**2)/3
    q = c_1 + (2*a_1**3 - 9*a_1*b_1)/27

    u_1 = ( (q/2) + sqrt((q**2)/4 + (p**3)/27) )**Rational(1,3)
    u_2 = ( (q/2) - sqrt((q**2)/4 + (p**3)/27) )**Rational(1,3)
    # todo: this irnores

    x_1 = p/(3*u_1) - u_1 - a_1/3
    x_2 = p/(3*u_2) - u_2 - a_1/3

    return (x_1, x_2)


def dsolve(eq, funcs):
    """
    Solves any (supported) kind of differential equation.

    Usage
    =====
        dsolve(f, y(x)) -> Solve a differential equation f for the function y


    Details
    =======
        @param f: ordinary differential equation

        @param y: indeterminate function of one variable

        - you can declare the derivative of an unknown function this way:
        >>> from sympy import *
        >>> x = Symbol('x') # x is the independent variable
        >>> f = Function(x) # f is a function of f
        >>> f_ = Derivative(f, x) # f_ will be the derivative of f with respect to x

        - This function just parses the equation "eq" and determines the type of
        differential equation, then it determines all the coefficients and then
        calls the particular solver, which just accepts the coefficients.

    Examples
    ========
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> f = Function(x)
        >>> dsolve(Derivative(Derivative(f,x),x)+9*f, f)
        C1*sin(3*x)+C2*cos(3*x)

        #this is probably returned on amd64
        sin(3*x)*C1+cos(3*x)*C2

    """

    #currently only solve for one function
    if isinstance(funcs, Basic) or len(funcs) == 1:
        if isinstance(funcs, (list, tuple)): # normalize args
            f = funcs[0]
        else:
            f = funcs

        x = f[0]
        a,b,c = [Symbol(s, dummy = True) for s in ["a","b","c"]]

        r = eq.match(a*Derivative(f,x) + b, [a,b])
        if r and _wo(r,f): return solve_ODE_first_order(r[a], r[b], f, x)

        r = eq.match(a*Derivative(Derivative(f,x),x) + b*f, [a,b])
        if r and _wo(r,f): return solve_ODE_second_order(r[a], 0, r[b], f, x)

        #special equations, that we know how to solve
        t = x*exp(-f)
        tt = (a*diff(t, x, 2)/t).expand()
        r = eq.match(tt, [a])
        if r:
            #check, that we've rewritten the equation correctly:
            #assert ( r[a]*diff(t, x,2)/t ) == eq.subs(f, t)
            return solve_ODE_1(f, x)
        eq = (eq*exp(f)/exp(-f)).expand()
        r = eq.match(tt, [a])
        if r:
            #check, that we've rewritten the equation correctly:
            #assert ( diff(t, x,2)*r[a]/t ).expand() == eq
            return solve_ODE_1(f, x)

    raise NotImplementedError("Sorry, can't solve it (yet)")

def solve_ODE_first_order(a, b, f, x):
    """ a*f'(x)+b = 0 """
    return integrate(-b/a, x) + Symbol("C1")

def solve_ODE_second_order(a, b, c, f, x):
    """ a*f''(x) + b*f'(x) + c = 0 """
    #a very special case, for b=0 and a,c not depending on x:
    return Symbol("C1")*sin(sqrt(c/a)*x)+Symbol("C2")*cos(sqrt(c/a)*x)

def solve_ODE_1(f, x):
    """ (x*exp(-f(x)))'' = 0 """
    C1 = Symbol("C1")
    C2 = Symbol("C2")
    return -log(C1+C2/x)


def _wo(di, x):
    """Are all items in the dictionary "di" without "x"?"""
    for d in di:
        if di[d].has(x):
            return False
    return True
