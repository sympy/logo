"""Module providing the class Polynomial and low-level functions"""

from sympy import Add, Basic, Mul, Number, Pow, Rational, Real, Symbol
from sympy.modules.polynomials.common import *

coeff_rings = ['int', 'rat', 'real', 'cplx', 'sym']

class PolynomialException(Exception):
    pass

class Polynomial(Basic):
    """Polynomial representation in coefficient list form.

    Offers more efficient arithmetic and a unified way to handle
    polynomials and access their coefficient list as well as keep
    compatibility with other Basic objects.

    Examples:
    >>> x = Symbol('x')
    >>> y = Symbol('y')
    >>> f = Polynomial(x + 1)
    >>> g = Polynomial(y**2 - x*y)
    >>> s = f+g
    >>> s.var == [x, y]
    True
    >>> (s == y**2 - x*y + x + 1) == True
    True
    """
    def __init__(self, p, var=None, order=None, coeff=None):
        p = Basic.sympify(p)
        if not isinstance(p, Basic):
            raise PolynomialException(
                'Can not create Polynomial out of a %s!' % type(p))
        # TODO: Check if really a polynomial?
        # Is an instance of Basic, get per property basic
        self._basic = p
        # Get per property var
        self._var = var
        # Get per property order
        self._order = order
        # Get per property coeff
        self._coeff = coeff
        # Coefficient list, get per property cl
        self._cl = None

    def get_basic(self):
        if self._basic == None:
            self._basic = poly(self.cl, self.var)
        return self._basic
    def set_basic(self, p):
        p = Basic.sympify(p)
        if not isinstance(p, Basic):
            raise PolynomialException(
                'Can not create Polynomial out of a %s!' % type(p))
        # TODO: Check if really a polynomial?
        self._basic = p
        self._cl = None
    basic = property(get_basic, set_basic)

    def get_cl(self):
        if self._cl == None:
            self._cl = coeff_list(self.basic, self.var, self.order)
        # TODO: Take care that self._cl isn't changed by __setitem__
        #       or self._basic will remain incompatible!
        return self._cl
    def set_cl(self, cl):
        # TODO: Sanity check before overwriting list?
        self._basic = None
        self._cl = cl
    cl = property(get_cl, set_cl)

    def get_coeff(self):
        if self._coeff == None:
            # TODO: Determine coefficient ring.
            self._coeff = 'sym' # == worst case
        return self._coeff
    def set_coeff(self, coeff):
        if not coeff in coeff_rings:
            raise PolynomialException(
                "%s is not and implemented coefficiend ring." % coeff)
        self._coeff = coeff
    coeff = property(get_coeff, set_coeff)

    def get_order(self):
        if self._order == None:
            self._order = 'grevlex' # Global default, most efficient?
        return self._order
    def set_order(self, order):
        # TODO: Check if order is implemented?
        # TODO: Check if self.var is really changed?
        # TODO: Just re-sort, instead of delete?
        if self._cl != None: # The coefficient list is no longer good.
            self.basic
            self._cl = None
        self._order = order
    order = property(get_order, set_order)
    
    def get_var(self):
        if self._var == None:
            self._var = self.basic.atoms(type=Symbol)
            self._var.sort(key=str)
        return self._var
    def set_var(self, var):
        if isinstance(var, Symbol):
            var = [var]
        elif not (isinstance(var, list) and
                  all(map(lambda v: isinstance(v, Symbol), var))):
            raise PolynomialException('Variables are not of type Symbol.')
        # TODO: Check if self.var is really changed?
        if self._cl != None: # The coefficient list is no longer good.
            self.basic
            self._cl = None
        self._var = var
    var = property(get_var, set_var)

    def __str__(self):
        return str(self.basic)

    def __repr__(self):
        return "Polynomial(%s, %s, %s, %s)" % \
               (self.basic, self._var, repr(self.order), repr(self._coeff))

    def __eq__(self, other):
        if isinstance(other, Polynomial):
            other = other.basic
        return self.basic == other

    def __ne__(self, other):
        if isinstance(other, Polynomial):
            other = other.basic
        return self.basic != other

    def __pos__(self):
        return self

    def __neg__(self):
        if self._basic != None:
            self._basic = -self._basic
        if self._cl != None:
            for term in self._cl:
                term[0] *= Rational(-1)

    def __add__(self, other):
        # Uses Add class if one summand doesn't yet have coeff list ready.
        if not isinstance(other, Polynomial):
            # TODO: Which var to choose?
            return Polynomial(self.basic + other, order=self.order)

        var = merge_var(self.var, other.var)
        if self.order == other.order:
            order = self.order
        else:
            order = None
        if self.coeff == other.coeff:
            coeff = self.coeff
        else:
            coeff = None

        if self._cl == None or other._cl == None:
            return Polynomial(self.basic + other.basic, var, order, coeff)

        # Now we are going to do the addition on the coeff list.
        if self.var != other.var or self.order != other.order:
            ss = self.copy()
            ss.var = var
            ss.order = order
            oo = other.copy()
            oo.var = var
            oo.order = order
            s = ss.cl
            o = oo.cl
        else:
            s = self.cl
            o = other.cl

        # Finally, the actual addition can begin!
        r = Polynomial(Rational(0), var, order, coeff)
        cl = []
        # Merge the terms of self and other:
        i, j = 0, 0
        while i < len(s) and j < len(o):
            if (s[i][1:] == o[j][1:]):
                c = s[i][0]+o[j][0]
                if c != 0:
                    cl.append([c] + s[i][1:])
                i += 1
                j += 1
            elif term_cmp(s[i], o[j], r.order) > 0:
                cl.append(s[i])
                i += 1
            else:
                cl.append(o[j])
                j += 1
        cl += s[i:]
        cl += o[j:]
        # Check if something was appended to the (empty) result.
        if len(cl) == 0:
            return r # == 0
        # Check for remaining zero terms (coming directly from self or other?).
        if len(cl) > 1:
            cl = filter(lambda t:t[0] != 0, cl)
        r.cl = cl
        return r

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return other.__add__(-self)

    def __mul__(self, other):
        # Uses Mul class if one factor doesn't yet have coeff list ready.
        if not isinstance(other, Polynomial):
            # TODO: Which var to choose?
            return Polynomial(self.basic * other, order=self.order)

        var = merge_var(self.var, other.var)
        if self.order == other.order:
            order = self.order
        else:
            order = None
        if self.coeff == other.coeff:
            coeff = self.coeff
        else:
            coeff = None

        if self._cl == None or other._cl == None:
            return Polynomial(self.basic * other.basic, var, order, coeff)

        # Now we are going to do the multiplication on the coeff list.
        if self.var != other.var or self.order != other.order:
            ss = self.copy()
            ss.var = var
            ss.order = order
            oo = other.copy()
            oo.var = var
            oo.order = order
            s = ss.cl
            o = oo.cl
        else:
            s = self.cl
            o = other.cl

        # Finally, the actual multiplication can begin!
        r = Polynomial_old(0, var, order, coeff)
        cl = r.cl
        # Distribute the multiplication
        for self_term in s:
            co = copy_cl(o)
            for i in range(0, len(co)):
                co[i][0] = (co[i][0] * self_term[0]).expand()
                for j in range(1, len(self_term)):
                    co[i][j] += self_term[j]
            # Merge the terms in co into cl.
            i, j = 0, 0
            while i < len(cl) and j < len(co):
                if (cl[i][1:] == co[j][1:]):
                    c = cl[i][0] + co[j][0]
                    if c == 0:
                        cl[i:i+1] = () # remove cancelled term
                    else:
                        cl[i][0] = c
                        i += 1
                    j += 1
                elif term_cmp(cl[i], co[j], order) > 0:
                    i += 1
                else:
                    cl.insert(i, co[j])
                    i += 1
                    j += 1
            cl += co[j:]
        # Check if something is left.
        if len(cl) == 0:
            r._cl = None
            return r # == 0
        # Check for remaining zero terms (coming directly from self or other?).
        if len(cl) > 1:
            cl = filter(lambda t:t[0] != 0, cl)
        r.cl = cl
        return r

    def __rmul__(self, other):
        return self.__mul__(other)

    def copy(self):
        r = Polynomial(Rational(0), self.var, self.order, self.coeff)
        if self._basic != None:
            r._basic = self._basic
        if self._cl != None:
            r._cl = copy_cl(self._cl)
        return r

def coeff_list(p, var=None, order='grevlex'):
    """Return the list of coeffs and exponents.

    Currently, lexicographic ('lex'), graded lex ('grlex'), graded
    reverse lex ('grevlex') and 1-elimination ('1-el')orders are implemented.
    The list of variables determines the order of the variables.
    The coefficients are assumed to be non-zero real numbers, that is,
    you can divide by them.

    Examples:
    >>> x = Symbol('x')
    >>> y = Symbol('y')
    >>> from sympy.modules.trigonometric import sin
    >>> coeff_list(x+sin(y)*x**2, [x])
    [[sin(y), 2], [1, 1]]

    >>> coeff_list(6*y**3+7*y*x**2)
    [[7, 2, 1], [6, 0, 3]]

    >>> coeff_list(6*y**3+7*y*x**2, [y,x])
    [[6, 3, 0], [7, 1, 2]]

    """

    p = Basic.sympify(p)
    p = p.expand()

    if isinstance(var, Symbol):
        var = [var]
    if var == None:
        var = p.atoms(type=Symbol)
        var.sort(Basic.cmphash)

    res = []

    if isinstance(p, Add):
        for a in p._args:
            res.append(*coeff_list(a, var, order))
    else:
        if not isinstance(p, Mul):
            p = Mul(Rational(1), p, evaluate=False)
        item = [Rational(1)] + len(var)*[Rational(0)]
        for factor in p._args:
            # check if any of the var appear
            if filter(lambda x:x in var, factor.atoms(type=Symbol)):
                if isinstance(factor, Pow) \
                   and (factor.base in var) \
                   and isinstance(factor.exp, Number) \
                   and factor.exp.is_integer \
                   and factor.exp > 0:
                    item[var.index(factor.base)+1] += factor.exp
                elif isinstance(factor, Symbol):
                    item[var.index(factor)+1] += 1
                else:
                    raise PolynomialException('Not a polynomial!')
            else: # the factor is relativly constant
                item[0] *= factor
        res = [item]

    # sort list according to monomial ordering
    if order == 'lex':
        res.sort(key=lambda x: x[1:], reverse=True)
    elif order == 'grlex':
        res.sort(key=lambda x: [sum(x[1:])] + x[1:], reverse=True)
    elif order == 'grevlex':
        res.sort(key=lambda x: [sum(x[1:])]
                 + reverse(map(lambda l:-l, x[1:])), reverse=True)
    elif order == '1-el':
        res.sort(key=lambda x: [x[1]] + [sum(x[2:])]
                 + reverse(map(lambda l:-l, x[2:])), reverse=True)
    else:
        raise PolynomialException(str(order) + 'is not an implemented order.')

    # unify monomials
    result = []
    for item in res:
        filt = filter(lambda x: x[1:] == item[1:], result)
        if filt:
            result[ result.index(filt[0]) ][0] += item[0]
        else:
            result.append(item)

    return result


def ispoly(p, var=None):
    """
    Usage:
      ispoly(p, var) -> Returns True if p is a polynomial in variable var.
                        Returns False otherwise.

    Notes:
        You can check wether it's a polynomial in several variables at
        once giving a tuple of symbols second argument
        (like ispoly(x**2 + y + 1, (x,y)) ).

    Examples:
        >>> from sympy import *
        >>> from sympy.modules.polynomials import *
        >>> x = Symbol('x')
        >>> ispoly(x**2+x+1, x)
        True
        >>> y = Symbol('y')
        >>> ispoly(x**2 + y + 1, (x,y)) #polynomial in variables x and y
        True
        >>> ispoly(x**2 + exp(y) + 1, (x,y))
        False

    See also:
       L{coeff_list}, L{coeff}

    """
    p = Basic.sympify(p)

    if var == None:
        var = p.atoms(type=Symbol)
    elif isinstance(var, Basic):
        # if the var argument is not a tuple or list
        var = [var] # so we can iterate over it

    if len(var) == 0:
        return True # constant is polynomial.
    elif len(var) > 1:
        return ispoly(p, var[0]) and ispoly(p, var[1:])

    if not var[0] in p.atoms(type=Symbol):
        return True # constant is polynomial.

    # Now we look for one variable, that is in the expression.
    if isinstance(p, Pow):
        if isinstance(p.exp, Number) \
           and p.exp.is_integer \
           and p.exp > 0:
            return ispoly(p.base, var[0])
        else:
            return False
    elif isinstance(p, (Add, Mul)):
        a, b = p.getab()
        return ispoly(a, var[0]) and ispoly(b, var[0])
    elif isinstance(p, Number):
        return True
    elif isinstance(p, Symbol):
        return True
    else:
        return False


def poly(p, var):
    """Returns a sympy polynomial from the representation p returned by
    coeff_list().
    """

    if isinstance(var, Symbol):
        var = [var]

    if len(p) == 0:
        return Rational(0)
    elif len(p[0]) != len(var) + 1:
        raise PolynomialException('Wrong number of variables given.')

    r = 0
    for item in p:
        c = item[0]
        for v in var:
            c *= v**item[var.index(v)+1]
        r += c
    return r

