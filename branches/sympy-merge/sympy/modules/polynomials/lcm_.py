"""Least common multiple for the Polynomial class"""

from sympy.modules.polynomials.base import *

def uv(f, g):
    """Uses euclidean algorithm for univariate polynomials for the gcd/

    Coefficients assumed to be in a field.
    """
    from sympy.modules.polynomials import div_
    from sympy.modules.polynomials import gcd_

    gcd = gcd_.uv(f, g)
    q, r = div_.mv(f*g, gcd)
    assert r == S.Zero
    q = q[0] # q is a list!
    q.cl = map(lambda t:[t[0]/q.cl[0][0]] + t[1:], q.cl)
    return q

# TODO: implement uv_int?

def mv(f, g):
    """Computes the lcm of two polynomials.

    This is a special case of the intersection of two ideals using Groebner
    bases and the elimination theorem.
    """
    from sympy.modules.polynomials import groebner_

    # Compute a lexicographic Groebner base of the sum of the
    # two principal ideals generated by t*f and (t-1)*g.
    t = Symbol('t', dummy=True)
    var = [t] + f.var
    G = groebner_.groebner([Polynomial(t*f.basic, var, '1-el', f.coeff),
                            Polynomial((t-1)*g.basic, var, '1-el', g.coeff)],
                           reduced=True)

    # Now intersect this result with the polynomial ring in the
    # variables in `var', that is, eliminate t.
    I = filter(lambda p: not t in list(p.basic.atoms(type=Symbol)), G)

    # The intersection should be a principal ideal, that is generated
    # by a single polynomial.
    if not len(I) == 1:
        raise PolynomialException("No single generator.")
    return Polynomial(I[0].basic, f.var, f.order, f.coeff)