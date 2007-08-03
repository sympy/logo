from sympy import *
from sympy.core.defined_functions import ApplyExp
from float_ import Float, ComplexFloat
import functions
import constants
from utils_ import bitcount


def polyfunc(expr):
    """
    Convert a SymPy expression representing a univariate polynomial
    into a function for numerical evaluation using Floats /
    ComplexFloats.

        >>> x = Symbol('x')
        >>> polyfunc(x**3 + 4)(2)
        Float('12')

    """
    poly = Polynomial(expr)
    degree = poly.coeffs[0][1]
    coeffs = [0] * int(degree + 1)
    for c, e in poly.coeffs:
        coeffs[int(e)] = evalf(c)
    def g(x):
        x = evalf(x)
        y = 0
        for c in reversed(coeffs):
            y = y*x+c
        return y
    return g


def evalf(expr):
    """
    evalf(expr) attempts to evaluate a SymPy expression to a Float or
    ComplexFloat with an error smaller than 10**(-Float.getdps())
    """

    if isinstance(expr, (Float, ComplexFloat)):
        return expr
    elif isinstance(expr, (int, float)):
        return Float(expr)
    elif isinstance(expr, complex):
        return ComplexFloat(expr)

    expr = Basic.sympify(expr)

    if isinstance(expr, (Rational)):
        y = Float(expr)
    elif isinstance(expr, Real):
        y = Float(str(expr))

    elif expr is I:
        y = ComplexFloat(0,1)

    elif expr is pi:
        y = constants.pi_float()

    elif expr is E:
        y = functions.exp(1)

    elif isinstance(expr, Mul):
        factors = expr[:]
        workprec = Float.getprec() + 1 + len(factors)
        Float.store()
        Float.setprec(workprec)
        y = Float(1)
        for f in factors:
            y *= evalf(f)
        Float.revert()

    elif isinstance(expr, Pow):
        base, expt = expr[:]
        workprec = Float.getprec() + 8 # may need more
        Float.store()
        Float.setprec(workprec)
        base = evalf(base)
        expt = evalf(expt)
        if expt == 0.5:
            y = functions.sqrt(base)
        else:
            y = functions.exp(functions.log(base) * expt)
        Float.revert()

    elif isinstance(expr, ApplyExp):
        Float.store()
        Float.setprec(Float.getprec() + 3)
        x = evalf(expr[1])
        y = functions.exp(x)
        Float.revert()

    elif isinstance(expr, Add):
        # TODO: this doesn't yet work as it should. 
        # We need some way to handle sums whose results are
        # very close to 0, and when necessary, repeat the
        # summation with higher precision
        reqprec = Float.getprec()
        Float.store()
        Float.setprec(10)
        terms = expr[:]
        approxterms = [abs(evalf(x)) for x in terms]
        min_mag = min(x.exp for x in approxterms)
        max_mag = max(x.exp+bitcount(x.man) for x in approxterms)
        Float.setprec(reqprec - 10 + max_mag - min_mag + 1 + len(terms))
        workprec = Float.getdps()
        y = 0
        for t in terms:
            y += evalf(t)
        Float.revert()

    else:
        # print expr, expr.__class__
        raise NotImplementedError

    # print expr, y

    return +y
