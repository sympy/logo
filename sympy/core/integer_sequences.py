
from basic import Basic, S, Memoizer
from numbers import Integer, Rational
from function import DefinedFunction, Lambda, Function, Apply

class IntegerSequence(DefinedFunction):
    """
    http://en.wikipedia.org/wiki/Category:Integer_sequences
    """

    pass

###############################################################################
########################### FACTORIALS and BINOMIAL ###########################
###############################################################################

class Factorial(IntegerSequence):

    nofargs = 1

    def _eval_apply(self, arg):
        arg = Basic.sympify(arg)

        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return S.One
            elif isinstance(arg, Basic.Integer):
                if arg.is_negative:
                    return S.Zero
                else:
                    k, n = arg.p, 1

                    while k:
                        n *= k
                        k -= 1

                    return Integer(n)

class Binomial(IntegerSequence):

    nofargs = 2

    def _eval_apply(self, r, k):
        r, k = map(Basic.sympify, (r, k))

        if isinstance(k, Basic.Integer):
            if k.is_negative:
                return S.Zero
            else:
                rk, result = r - k, []

                for i in xrange(1, k.p+1):
                    result.append(rk+i)

                numer = Basic.Mul(*result)
                denom = Factorial()(k)

                return (numer/denom).expand()

Basic.singleton['factorial'] = Factorial
Basic.singleton['binomial'] = Binomial

###############################################################################
###################### BERNOULLI NUMBERS and POLYNOMIALS ######################
###############################################################################

def _bernoulli_sum(m, M):
    s = 0

    for j in range(M, 0, -1):
        b = Binomial()(m+3, m-6*j)
        s += b * Bernoulli()(m-6*j)

    return s

@Memoizer((int, long))
def _b0mod6(m):
    return (Rational(m+3, 3) - _bernoulli_sum(m, m//6)) / Binomial()(m+3, m)

@Memoizer((int, long))
def _b2mod6(m):
    return (Rational(m+3, 3) - _bernoulli_sum(m, (m-2)//6)) / Binomial()(m+3, m)

@Memoizer((int, long))
def _b4mod6(m):
    return (-Rational(m+3, 6) - _bernoulli_sum(m, (m-4)//6)) / Binomial()(m+3, m)

class Bernoulli(DefinedFunction):

    def _eval_apply(self, arg, sym=None):
        arg = Basic.sympify(arg)

        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return S.One
            elif isinstance(arg, Basic.One):
                if sym is None:
                    return -S.Half
                else:
                    return sym - S.Half
            elif isinstance(arg, Basic.Integer):
                if arg.is_nonnegative:
                    if sym is None:
                        m = int(arg)

                        val_table = {
                            0 : _b0mod6,
                            2 : _b2mod6,
                            4 : _b4mod6
                        }

                        try:
                            return val_table[m % 6](m)
                        except KeyError:
                            return S.Zero
                    else:
                        n, result = int(arg), []

                        for k in xrange(n + 1):
                            result.append(Binomial()(n, k)*self(k)*sym**(n-k))

                        return Basic.Add(*result)
                else:
                    raise ValueError("Bernoulli numbers are defined only"
                                     " for nonnegative integer indices.")

Basic.singleton['bernoulli'] = Bernoulli