
from sympy.core.basic import Basic, S, cache_it, cache_it_immutable
from sympy.core.function import DefinedFunction, Apply, Lambda

###############################################################################
############################# SQUARE ROOT FUNCTION ############################
###############################################################################

class Sqrt(DefinedFunction):

    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex == 1:
            s = Basic.Symbol('x',dummy=True)
            return Lambda(S.Half * s**(-S.Half),s)
        else:
            raise ArgumentIndexError(self, argindex)

    def inverse(self, argindex=1):
        s = Basic.Symbol('x', dummy=True)
        return Lambda(s**2, s)

    def _eval_apply(self, arg):
        arg = Basic.sympify(arg)

        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.NaN):
                return S.NaN
            if isinstance(arg, Basic.Infinity):
                return S.Infinity
            if isinstance(arg, Basic.NegativeInfinity):
                return S.ImaginaryUnit * S.Infinity
            if isinstance(arg, Basic.Rational):
                factors = arg.factors()
                sqrt_factors = {}
                eval_factors = {}
                n = 1
                for k,v in factors.items():
                    n *= Basic.Integer(k) ** (v//2)
                    if v % 2:
                        n *= Basic.Integer(k) ** S.Half
                return n
            return arg ** S.Half
        if arg.is_nonnegative:
            coeff, terms = arg.as_coeff_terms()
            if not isinstance(coeff, Basic.One):
                return self(coeff) * self(Basic.Mul(*terms))
        base, exp = arg.as_base_exp()
        if isinstance(exp, Basic.Number):
            if exp == 2:
                return S.Abs(base)
            return base ** (exp/2)

    def _eval_apply_power(self, arg, exp):
        if isinstance(exp, Basic.Number):
            return arg ** (exp/2)

    def _eval_apply_evalf(self, arg):
        arg = arg.evalf()
        if isinstance(arg, Basic.Number):
            return arg.sqrt()

    def _eval_apply_subs(self, x, old, new):
        base, exp = old.as_base_exp()
        if base==x:
            return new ** (exp/2)

class ApplySqrt(Apply):
    def _eval_is_zero(self):
        return isinstance(self.args, Basic.Zero)

    def as_base_exp(self):
        return self.args[0], S.Half

Basic.singleton['sqrt'] = Sqrt

###############################################################################
############################# MINIMUM and MAXIMUM #############################
###############################################################################

class Max(DefinedFunction):

    nofargs = 2

    def _eval_apply(self, x, y):
        if isinstance(x, Basic.Number) and isinstance(y, Basic.Number):
            return max(x, y)
        if x.is_positive:
            if y.is_negative:
                return x
            if y.is_positive:
                if x.is_unbounded:
                    if y.is_unbounded:
                        return
                    return x
        elif x.is_negative:
            if y.is_negative:
                if y.is_unbounded:
                    if x.is_unbounded:
                        return
                    return x

class Min(DefinedFunction):

    nofargs = 2

    def _eval_apply(self, x, y):
        if isinstance(x, Basic.Number) and isinstance(y, Basic.Number):
            return min(x, y)

Basic.singleton['max_'] = Max
Basic.singleton['min_'] = Min