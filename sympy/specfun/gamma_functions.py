
from sympy.core import *

from zeta_functions import polygamma

class Gamma(DefinedFunction):

    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex == 1:
            x = Basic.Symbol('x', dummy=True)
            return Lambda(S.Gamma(x)*S.PolyGamma(0, x), x)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_apply(self, arg):
        arg = Basic.sympify(arg)

        if arg.is_integer:
            if arg.is_positive:
                return S.Factorial(arg-1)
            else:
                return #S.ComplexInfinity
        elif isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.NaN):
                return S.NaN
            elif isinstance(arg, Basic.Infinity):
                return S.Infinity
            elif isinstance(arg, Basic.Rational):
                if arg.q == 2:
                    n = abs(arg.p) // arg.q

                    if arg.is_positive:
                        coeff = S.One
                    else:
                        n = n - 1

                        if n & 1 == 0:
                            coeff = S.One
                        else:
                            coeff = S.NegativeOne

                    for i in range(3, 2*n, 2):
                        coeff *= i

                    if arg.is_positive:
                        return coeff*S.Sqrt(S.Pi)/2**n
                    else:
                        return 2**n*S.Sqrt(S.Pi)/coeff
            elif isinstance(arg, Basic.Real):
                return

class ApplyGamma(Apply):

    def _eval_rewrite_as_rf(self, arg):
        arg = arg.expand(basic=True)

        if isinstance(arg, Basic.Add):
            coeff, factors = arg.as_coeff_factors()

            if isinstance(coeff, Basic.Zero):
                return
            elif isinstance(coeff, Basic.Integer):
                expo = coeff
            elif isinstance(coeff, Basic.Rational):
                expo = coeff.p / coeff.q
                factors.append(S.Half)
            else:
                return

            base = Add(*factors)

            return S.RisingFactorial(base, expo)*S.Gamma(base)

    def _eval_is_real(self):
        return self.args[0].is_real

class LowerGamma(DefinedFunction):
    """Lower incomplete gamma function"""

    nofargs = 2

    def _eval_apply(self, a, x):
        if isinstance(a, Basic.Number):
            if isinstance(a, Basic.One):
                return S.One - S.Exp(-x)
            elif isinstance(a, Basic.Integer):
                b = a - 1

                if b.is_positive:
                    return b*LowerGamma()(b, x) - x**b * S.Exp(-x)

class ApplyLowerGamma(Apply):
    pass

    #def _eval_expand_func(self):
    #    b = self.args[0] - 1
    #
    #    if isinstance(a, Basic.Integer) and b.is_positive:
    #        return (b*LowerGamma(b, x) - x**b * exp(-x)).expand(func=True)

class UpperGamma(DefinedFunction):
    """Upper incomplete gamma function"""

    nofargs = 2

    def _eval_apply(self, a, x):
        if isinstance(x, Basic.Number):
            if isinstance(x, Basic.NaN):
                return S.NaN
            elif isinstance(x, Basic.Infinity):
                return S.Zero
            elif isinstance(x, Basic.Zero):
                return Gamma()(a)

        if isinstance(a, Basic.Number):
            if isinstance(a, Basic.One):
                return S.Exp(-x)
            elif isinstance(a, Basic.Integer):
                b = a - 1

                if b.is_positive:
                    return b*UpperGamma()(b, x) + x**b * S.Exp(-x)

class ApplyUpperGamma(Apply):
    pass

    #def _eval_expand_func(self):
    #    b = self.args[0] - 1
    #
    #    if isinstance(a, Basic.Integer) and b.is_positive:
    #        return (b*UpperGamma(b, x) + x**b * exp(-x)).expand(func=True)

gamma = Gamma()

lowergamma = LowerGamma()
uppergamma = UpperGamma()
