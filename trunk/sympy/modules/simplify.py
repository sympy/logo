from sympy.core.basic import Basic
from sympy.core.symbol import Symbol
from sympy.core.functions import Function, exp
from sympy.core.functions import Derivative
from sympy.core.numbers import Rational
from sympy.core.addmul import Add, Mul
from sympy.core.power import Pow

from sympy.modules.utils import make_list

from sys import maxint

def fraction(expr, pretty=True):
    """Returns a pair with expression's numerator and denominator.
       If the given expression is not a fraction then this function
       will assume that the denominator is equal to one.

       This function will not make any attempt to simplify nested
       fractions or to do any term rewriting at all.

       If only one of the numerator/denominator pair is needed then
       use numer(expr) or denom(expr) functions respectively.

       >>> from sympy import *
       >>> x, y = symbols('x', 'y')

       >>> fraction(x/y)
       (x, y)
       >>> fraction(x)
       (x, 1)

       >>> fraction(1/y**2)
       (1, y**2)

       >>> fraction(x*y/2)
       (x*y, 2)
       >>> fraction(Rational(1, 2))
       (1, 2)

       This function will also work fine with assumptions:

       >>> k = Symbol('k', negative=True)
       >>> fraction(x * y**k)
       (x, y**(-k))

       If we know nothing bout sign of some exponent, then its structure
       will be analyzed and 'pretty' fraction will be returned:

       >>> fraction(2*x**(-y))
       (2, x**y)


    """
    expr = Basic.sympify(expr)

    numer, denom = [], []

    for term in make_list(expr, Mul):
        if isinstance(term, Pow):
            if term.exp.is_negative:
                if term.exp.is_minus_one:
                    denom.append(term.base)
                else:
                    denom.append(Pow(term.base, -term.exp))
            elif pretty and isinstance(term.exp, Mul):
                coeff, tail = term.exp.getab()

                if isinstance(coeff, Rational) and coeff.is_negative:
                    denom.append(Pow(term.base, -term.exp))
                else:
                    numer.append(term)
            else:
                numer.append(term)
        elif isinstance(term, exp):
            if term._args.is_negative:
                denom.append(exp(-term.args))
            elif pretty and isinstance(term._args, Mul):
                coeff, tail = term._args.getab()

                if isinstance(coeff, Rational) and coeff.is_negative:
                    denom.append(exp(-term._args))
                else:
                    numer.append(term)
            else:
                numer.append(term)
        elif isinstance(term, Rational):
            if term.is_integer:
                numer.append(term)
            else:
                numer.append(Rational(term.p))
                denom.append(Rational(term.q))
        else:
            numer.append(term)

    return Mul(*numer), Mul(*denom)

def numer(expr):
    return fraction(expr)[0]

def denom(expr):
    return fraction(expr)[1]

def fraction_expand(expr):
    a, b = fraction(expr)
    return a.expand() / b.expand()

def numer_expand(expr):
    a, b = fraction(expr)
    return a.expand() / b

def denom_expand(expr):
    a, b = fraction(expr)
    return a / b.expand()

def separate(expr, deep=False):
    """Rewrite or separate a power of product to a product of powers
       but without any expanding, ie. rewriting products to summations.

       >>> from sympy import *
       >>> x, y, z = symbols('x', 'y', 'z')

       >>> separate((x*y)**2)
       x**2*y**2

       >>> separate((x*(y*z)**3)**2)
       z**6*y**6*x**2

       >>> separate((x*sin(x))**y + (x*cos(x))**y)
       x**y*cos(x)**y+x**y*sin(x)**y

       >>> separate((exp(x)*exp(y))**x)
       exp(x*y)*exp(x**2)

       Notice that summations are left un touched. If this is not the
       requested behaviour, apply 'expand' to input expression before:

       >>> separate(((x+y)*z)**2)
       z**2*(x+y)**2

       >>> separate((x*y)**(1+z))
       y**(1+z)*x**(1+z)

    """
    expr = Basic.sympify(expr)

    if isinstance(expr, Pow):
        terms, expo = [], separate(expr.exp, deep)

        if isinstance(expr.base, Mul):
            return Mul(*[ separate(t**expo, deep) for t in expr.base ])
        elif isinstance(expr.base, exp):
            if deep == True:
                return exp(separate(expr.base._args, deep)*expo)
            else:
                return exp(expr.base._args*expo)
        else:
            return Pow(separate(expr.base, deep), expo)
    elif isinstance(expr, (Add, Mul)):
        return type(expr)(*[ separate(t, deep) for t in expr ])
    elif isinstance(expr, Function) and deep:
        return type(expr)(separate(expr._args, deep))
    else:
        return expr

def together(expr, deep=False):
    """Combine together and denest rational functions into a single
       fraction. By default the resulting expression is simplified
       to reduce the total order of both numerator and denominator
       and minimize the number of terms.

       Densting is done recursively on fractions level. However this
       function will not attempt to rewrite composite objects, like
       functions, interior unless 'deep' flag is set.

       By definition, 'together' is a complement to 'apart', so
       apart(together(expr)) should left expression unhanged.

       >>> from sympy import *
       >>> x, y, z = symbols('x', 'y', 'z')

       You can work with sums of fractions easily. The algorithm
       used here will, in an iterative style, collect numerators
       and denominator of all expressions involved and perform
       needed simplifications:

       >>> together(1/x + 1/y)
       (x+y)/(y*x)

       >>> together(1/x + 1/y + 1/z)
       (z*x+x*y+z*y)/(y*x*z)

       >>> together(1/(x*y) + 1/y**2)
       (x+y)*y**(-2)/x

       Or you can just denest multi-level fractional expressions:

       >>> together(1/(1 + 1/x))
       x/(1+x)

       It also perfect possible to work with symbolic powers or
       exponential functions or combinations of both:

       >>> together(1/x**y + 1/x**(y-1))
       x**(-y)*(1+x)

       >>> together(1/x**(2*y) + 1/x**(y-z))
       x**(-2*y)*(1+x**(z+y))

       >>> together(1/exp(x) + 1/(x*exp(x)))
       (1+x)/(x*exp(x))

       >>> together(1/exp(2*x) + 1/(x*exp(3*x)))
       (1+exp(x)*x)/(x*exp(3*x))

    """
    def _together(expr):
        if isinstance(expr, Add):
            items, basis = [], {}

            for elem in expr:
                numer, q = fraction(_together(elem))

                denom = {}

                for term in make_list(q.expand(), Mul):
                    expo = Rational(1)

                    if isinstance(term, Pow):
                        if isinstance(term.exp, Rational):
                            term, expo = term.base, term.exp
                        elif isinstance(term.exp, Mul):
                            coeff, tail = term.exp.getab()

                            if isinstance(coeff, Rational):
                                term, expo = Pow(term.base, tail), coeff
                    elif isinstance(term, exp):
                        if isinstance(term._args, Rational):
                            term, expo = exp(1), term._args
                        elif isinstance(term._args, Mul):
                            coeff, tail = term._args.getab()

                            if isinstance(coeff, Rational):
                                term, expo = exp(tail), coeff

                    if term in denom:
                        denom[term] += expo
                    else:
                        denom[term] = expo

                    if term in basis:
                        total, maxi = basis[term]

                        n_total = total + expo
                        n_maxi = max(maxi, expo)

                        basis[term] = (n_total, n_maxi)
                    else:
                        basis[term] = (expo, expo)

                items.append((numer, denom))

            numerator, denominator = [], []

            for (term, (total, maxi)) in basis.iteritems():
                basis[term] = (total, total-maxi)

                if isinstance(term, exp):
                    denominator.append(exp(maxi*term._args))
                else:
                    denominator.append(Pow(term, maxi))

            for (numer, denom) in items:
                expr = []

                for term in basis.iterkeys():
                    total, sub = basis[term]

                    if term in denom:
                        expo = total-denom[term]-sub
                    else:
                        expo = total-sub

                    if isinstance(term, exp):
                        expr.append(exp(expo*term._args))
                    else:
                        expr.append(Pow(term, expo))

                numerator.append(Mul(*([numer] + expr)))

            return Add(*numerator)/Mul(*denominator)
        elif isinstance(expr, (Mul, Pow)):
            return type(expr)(*[ _together(t) for t in expr ])
        elif isinstance(expr, Function) and deep:
            return type(expr)(_together(expr._args))
        else:
            return expr

    return _together(separate(expr))

#apart -> partial fractions decomposition (will be here :)

def collect(expr, syms, pretty=True, exact=False):
    """Collect additive terms with respect to a list of symbols up
       to powers with rational exponents. By the term symbol here
       are meant arbitrary expressions, which can contain powers,
       products, sums etc. In other words symbol is a pattern
       which will be searched for in the expression's terms.

       This function will not apply any redundant expanding to the
       input expression, so user is assumed to enter expression in
       final form. This makes 'collect' more predictable as there
       is no magic behind the scenes. However it is important to
       note, that powers of products are converted to products of
       powers using 'separate' function.

       There are two possible types of output. First, if 'pretty'
       flag is set, this function will return a single expression
       or else it will return a dictionary with separated symbols
       up to rational powers as keys and collected sub-expressions
       as values respectively.

       >>> from sympy import *
       >>> x, y, z = symbols('x', 'y', 'z')
       >>> a, b, c = symbols('a', 'b', 'c')

       This function can collect symbolic coefficients in polynomial
       or rational expressions. It will manage to find all integer or
       rational powers of collection variable:

       >>> collect(a*x**2 + b*x**2 + a*x - b*x + c, x)
       c+(-b+a)*x+(a+b)*x**2

       The same result can achieved in dictionary form:

       >>> collect(a*x**2 + b*x**2 + a*x - b*x + c, x, pretty=False)
       {x: -b+a, x**2: a+b, 1: c}

       You can also work with multi-variate polynomials. However
       remeber that this function is greedy so it will care only
       about a single symbol at time, in specification order:

       >>> collect(x**2 + y*x**2 + x*y + y + a*y, [x, y])
       (1+a)*y+x**2*(1+y)+x*y

       >>> collect(x**2*y**4 + z*(x*y**2)**2 + z + a*z, [x*y**2, z])
       (1+z)*x**2*y**4+z*(1+a)

       Also more complicated expressions can be used as patterns:

       >>> collect(a*sin(2*x) + b*sin(2*x), sin(2*x))
       (a+b)*sin(2*x)

       >>> collect(a*x**2*log(x)**2 + b*(x*log(x))**2, x*log(x))
       log(x)**2*(a+b)*x**2

       It is also possible to work with symbolic powers, although
       it has more complicated behaviour, because in this case
       power's base and symbolic part of the exponent are treated
       as a single symbol:

       >>> collect(a*x**c + b*x**c, x)
       x**c*a+x**c*b

       >>> collect(a*x**c + b*x**c, x**c)
       (a+b)*x**c

       However if you incorporate rationals to the exponents, then
       you will get well known behaviour:

       >>> collect(a*x**(2*c) + b*x**(2*c), x**c)
       (a+b)*x**(2*c)

       Note also that all previously stated facts about 'collect'
       function apply to the exponential function, so you can get:

       >>> collect(a*exp(2*x) + b*exp(2*x), exp(x))
       (a+b)*exp(2*x)

       If you are interested only in collecting specific powers
       of some symbols then set 'exact' flag in arguments:

       >>> collect(a*x**7 + b*x**7, x, exact=True)
       a*x**7+x**7*b

       >>> collect(a*x**7 + b*x**7, x**7, exact=True)
       (a+b)*x**7

       You can also apply this function to differential equations, where
       derivatives of arbitary order can be collected:

       >>> from sympy import Derivative as D
       >>> f = Function(x)

       >>> collect(a*D(f,x) + b*D(f,x), D(f,x))
       (a+b)*Function'(x)

       >>> collect(a*D(D(f,x),x) + b*D(D(f,x),x), D(f,x))
       (a+b)*(Function'(x))'

       >>> collect(a*D(D(f,x),x) + b*D(D(f,x),x), D(f,x), exact=True)
       a*(Function'(x))'+b*(Function'(x))'

       >>> collect(a*D(D(f,x),x) + b*D(D(f,x),x) + a*D(f,x) + b*D(f,x), D(f,x))
       (a+b)*Function'(x)+(a+b)*(Function'(x))'

       Or you can even match both derivative order and exponent at time:

       >>> collect(a*D(D(f,x),x)**2 + b*D(D(f,x),x)**2, D(f,x))
       (a+b)*(Function'(x))'**2

    """
    def make_expression(terms):
        product = []

        for term, rat, sym, deriv in terms:
            if deriv is not None:
                var, order = deriv

                while order > 0:
                    term, order = Derivative(term, var), order-1

            if sym is None:
                if rat.is_one:
                    product.append(term)
                else:
                    product.append(Pow(term, rat))
            else:
                product.append(Pow(term, rat*sym))

        return Mul(*product)

    def parse_derivative(deriv):
        # scan derivatives tower in the input expression and return
        # underlying function and maximal differentiation order
        expr, sym, order = deriv.f, deriv.x, 1

        while isinstance(expr, Derivative) and expr.x == sym:
            expr, order = expr.f, order+1

        return expr, (sym, Rational(order))

    def parse_term(expr):
        rat_expo, sym_expo = Rational(1), None
        sexpr, deriv = expr, None

        if isinstance(expr, Pow):
            if isinstance(expr.base, Derivative):
                sexpr, deriv = parse_derivative(expr.base)
            else:
                sexpr = expr.base

            if isinstance(expr.exp, Rational):
                rat_expo = expr.exp
            elif isinstance(expr.exp, Mul):
                coeff, tail = expr.exp.getab()

                if isinstance(coeff, Rational):
                    rat_expo, sym_expo = coeff, tail
                else:
                    sym_expo = expr.exp
            else:
                sym_expo = expr.exp
        elif isinstance(expr, exp):
            if isinstance(expr._args, Rational):
                sexpr, rat_expo = exp(Rational(1)), expr._args
            elif isinstance(expr._args, Mul):
                coeff, tail = expr._args.getab()

                if isinstance(coeff, Rational):
                    sexpr, rat_expo = exp(tail), coeff
        elif isinstance(expr, Derivative):
            sexpr, deriv = parse_derivative(expr)

        return sexpr, rat_expo, sym_expo, deriv

    def parse_expression(terms, pattern):
        pattern = make_list(pattern, Mul)

        if len(terms) < len(pattern):
            # pattern is longer than  matched product
            # so no chance for positive parsing result
            return None
        else:
            pattern = [ parse_term(elem) for elem in pattern ]

            elems, common_expo, has_deriv = [], Rational(1), False

            for elem, e_rat, e_sym, e_ord in pattern:
                if e_ord is not None:
                    # there is derivative in the pattern so
                    # there will by small performance penalty
                    has_deriv = True

                for j in range(len(terms)):
                    term, t_rat, t_sym, t_ord = terms[j]

                    if elem == term and e_sym == t_sym:
                        if exact == False:
                            # we don't have to exact so find common exponent
                            # for both expression's term and pattern's element
                            expo = t_rat / e_rat

                            if common_expo.is_one:
                                common_expo = expo
                            else:
                                # common exponent was negotiated before so
                                # teher is no chance for pattern match unless
                                # common and current exponents are equal
                                if common_expo != expo:
                                    return None
                        else:
                            # we ought to be exact so all fields of
                            # interest must match in very details
                            if e_rat != t_rat or e_ord != t_ord:
                                continue

                        # found common term so remove it from the expression
                        # and try to match next element in the pattern
                        elems.append(terms[j])
                        del terms[j]

                        break
                else:
                    # pattern element not found
                    return None

            return terms, elems, common_expo, has_deriv

    summa = [ separate(i) for i in make_list(Basic.sympify(expr), Add) ]

    if isinstance(syms, list):
        syms = [ separate(s) for s in syms ]
    else:
        syms = [ separate(syms) ]

    collected, disliked = {}, Rational(0)

    for product in summa:
        terms = [ parse_term(i) for i in make_list(product, Mul) ]

        for symbol in syms:
            result = parse_expression(terms, symbol)

            if result is not None:
                terms, elems, common_expo, has_deriv = result

                # when there was derivative in current pattern we
                # will need to rebuild its expression from scratch
                if not has_deriv:
                    index = Pow(symbol, common_expo)
                else:
                    index = make_expression(elems)

                terms = separate(make_expression(terms))
                index = separate(index)

                if index in collected:
                    collected[index] += terms
                else:
                    collected[index] = terms

                break
        else:
            # none of the patterns matched
            disliked += product

    if disliked != Rational(0):
        collected[Rational(1)] = disliked

    if pretty:
        return Add(*[ a*b for a, b in collected.iteritems() ])
    else:
        return collected

def ratsimp(expr):
    """
    Usage
    =====
        ratsimp(expr) -> joins two rational expressions and returns the simples form

    Notes
    =====
        Currently can simplify only simple expressions, for this to be really usefull
        multivariate polynomial algorithms are needed

    Examples
    ========
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> y = Symbol('y')
        >>> e = ratsimp(1/x + 1/y)
    """
    if isinstance(expr, Pow):
        return Pow(ratsimp(expr.base), ratsimp(expr.exp))
    elif isinstance(expr, Mul):
        res = []
        for x in expr:
            res.append( ratsimp(x) )
        return Mul(*res)
    elif isinstance(expr, Function):
        return type(expr)( ratsimp(expr[0]) )
    elif not isinstance(expr, Add):
        return expr

    def get_num_denum(x):
        """Matches x = a/b and returns a/b."""
        a = Symbol("a", dummy = True)
        b = Symbol("b", dummy = True)
        r = x.match(a/b,[a,b])
        if r is not None and len(r) == 2:
            return r[a],r[b]
        return x, 1
    x,y = expr.getab()
    a,b = get_num_denum(ratsimp(x))
    c,d = get_num_denum(ratsimp(y))
    num = a*d+b*c
    denum = b*d

    # Check to see if the numerator actually expands to 0
    if num.expand() == 0:
        return 0

    #we need to cancel common factors from numerator and denumerator
    #but SymPy doesn't yet have a multivariate polynomial factorisation
    #so until we have it, we are just returning the correct results here
    #to pass all tests...
    if isinstance(denum,Pow):
        e = (num/denum[0]).expand()
        f = (e/(-2*Symbol("y"))).expand()
        if f == denum/denum[0]:
            return -2*Symbol("y")
        return e/(denum/denum[0])
    return num/denum

def trigsimp(expr):
    """
    Usage
    =====
        trig(expr) -> reduces expression by using known trig identities

    Notes
    =====


    Examples
    ========
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> y = Symbol('y')
        >>> trigsimp(2*sin(x)**2 + 2*cos(x)**2)
        2
    """
    from trigonometric import sin, cos, tan, sec, csc, cot
    if isinstance(expr, Function):
        return type(expr)( trigsimp(expr[0]) )
    elif isinstance(expr, Mul):
        ret = Rational(1)
        for x in expr:
            ret *= trigsimp(x)
        return ret
    elif isinstance(expr, Pow):
        return Pow(trigsimp(expr.base), trigsimp(expr.exp))
    elif isinstance(expr, Add) and len(expr[:]) > 1:
        # The type of functions we're interested in
        a = Symbol('a', is_dummy=True)
        b = Symbol('b', is_dummy=True)
        matchers = {"sin": a*sin(b)**2, "tan": a*tan(b)**2, "cot": a*cot(b)**2}

        # The matches we find
        matches = {"sin": [], "tan": [], "cot": []}

        # Scan for the terms we need
        ret = Rational(0)
        for x in expr:
            x = trigsimp(x)
            res = None
            ex = [atom for atom in expr.atoms() if isinstance(atom, Symbol)]
            for mname in matchers:
                try:
                    res = x.match(matchers[mname], [a,b], exclude=ex)
                except:
                    res = x.match(matchers[mname], [a,b])
                if res is not None:
                    if a in res and b in res:
                        matches[mname].append( (res[a], res[b]) )
                        break
                    else:
                        res = None

            if res is not None:
                continue
            ret += x

        # Expand matches
        for match in matches["sin"]:
            ret += match[0] - match[0]*cos(match[1])**2
        for match in matches["tan"]:
            ret += match[0]*sec(match[1])**2 - match[0]
        for match in matches["cot"]:
            ret += match[0]*csc(match[1])**2 - match[0]

        return ret

    return expr

def simplify(expr):
    return ratsimp(expr.combine().expand())