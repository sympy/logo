
from sympy.core.basic import Basic, S, cache_it, cache_it_immutable
from sympy.core.function import DefinedFunction, Apply, Lambda

###############################################################################
######################### REAL and IMAGINARY PARTS ############################
###############################################################################

class Re(DefinedFunction):
    """Returns real part of expression. This function performs only
       elementary analysis and so it will fail to decompose properly
       more complicated expressions. If completely simplified result
       is needed then use Basic.as_real_imag() or perform complex
       expansion on instance of this function.

       >>> from sympy import *

       >>> x, y = symbols('x', 'y')

       >>> re(2*E)
       2*E

       >>> re(2*I + 17)
       17

       >>> re(2*I)
       0

       >>> re(im(x) + x*I + 2)
       2

    """

    nofargs = 1

    is_real = True

    def _eval_apply(self, arg):
        arg = Basic.sympify(arg)

        if isinstance(arg, Basic.NaN):
            return S.NaN
        elif arg.is_real:
            return arg
        else:
            if not isinstance(arg, Basic.Add):
                arg = [arg]

            included, reverted, excluded = [], [], []

            for term in arg:
                coeff = term.as_coefficient(S.ImaginaryUnit)

                if coeff is not None:
                    if not coeff.is_real:
                        reverted.append(coeff)
                elif not term.has(S.ImaginaryUnit) and term.is_real:
                    excluded.append(term)
                else:
                    included.append(term)

            if len(arg[:]) != len(included):
                a, b, c = map(lambda xs: Basic.Add(*xs),
                    [included, reverted, excluded])

                return self(a) - S.Im(b) + c

class ApplyRe(Apply):

    def _eval_conjugate(self):
        return self

    def _eval_is_real(self):
        return True

    def _eval_expand_complex(self, *args):
        return self.func(self[0].as_real_imag()[0])

class Im(DefinedFunction):
    """Returns imaginary part of expression. This function performs
       only elementary analysis and so it will fail to decompose
       properly more complicated expressions. If completely simplified
       result is needed then use Basic.as_real_imag() or perform complex
       expansion on instance of this function.

       >>> from sympy import *

       >>> x, y = symbols('x', 'y')

       >>> im(2*E)
       0

       >>> re(2*I + 17)
       17

       >>> im(x*I)
       re(x)

       >>> im(re(x) + y)
       im(y)

    """

    nofargs = 1

    is_real = True

    def _eval_apply(self, arg):
        arg = Basic.sympify(arg)

        if isinstance(arg, Basic.NaN):
            return S.NaN
        elif arg.is_real:
            return S.Zero
        else:
            if not isinstance(arg, Basic.Add):
                arg = [arg]

            included, reverted, excluded = [], [], []

            for term in arg:
                coeff = term.as_coefficient(S.ImaginaryUnit)

                if coeff is not None:
                    if not coeff.is_real:
                        reverted.append(coeff)
                    else:
                        excluded.append(coeff)
                elif term.has(S.ImaginaryUnit) or not term.is_real:
                    included.append(term)

            if len(arg[:]) != len(included):
                a, b, c = map(lambda xs: Basic.Add(*xs),
                    [included, reverted, excluded])

                return self(a) + S.Re(b) + c

class ApplyIm(Apply):

    def _eval_conjugate(self):
        return self

    def _eval_is_real(self):
        return True

    def _eval_expand_complex(self, *args):
        return self.func(self[0].as_real_imag()[1])

Basic.singleton['re'] = Re
Basic.singleton['im'] = Im

###############################################################################
############### SIGN, ABSOLUTE VALUE, ARGUMENT and CONJUGATION ################
###############################################################################

class Sign(DefinedFunction):

    nofargs = 1

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.NaN):
            return S.NaN
        if isinstance(arg, Basic.Zero): return S.One
        if arg.is_positive: return S.One
        if arg.is_negative: return S.NegativeOne
        if isinstance(arg, Basic.Mul):
            coeff, terms = arg.as_coeff_terms()
            if not isinstance(coeff, Basic.One):
                return self(coeff) * self(Basic.Mul(*terms))

class ApplySign(Apply):

    is_bounded = True

    def _eval_conjugate(self):
        return self

    def _eval_is_zero(self):
        return isinstance(self[0], Basic.Zero)

class Abs(DefinedFunction):

    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex == 1:
            raise NotImplementedError("Abs.fdiff()")
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.NaN):
            return S.NaN
        if arg.is_positive: return arg
        if arg.is_negative: return -arg
        coeff, terms = arg.as_coeff_terms()
        if not isinstance(coeff, Basic.One):
            return self(coeff) * self(Basic.Mul(*terms))
        if arg.is_real is False:
            return S.Sqrt( (arg * arg.conjugate()).expand() )
        return

    def _eval_is_zero(self):
        return isinstance(self[0], Basic.Zero)

class ApplyAbs(Apply):

    def _eval_conjugate(self):
        return self

class Arg(DefinedFunction):

    nofargs = 1

    is_real = True

    def _eval_apply(self, arg):
        return

class ApplyArg(Apply):

    def _eval_conjugate(self):
        return self

    def _eval_is_real(self):
        return True

class Conjugate(DefinedFunction):

    nofargs = 1

    def _eval_apply(self, arg):
        obj = arg._eval_conjugate()
        if obj is not None:
            return obj

class ApplyConjugate(Apply):

    def _eval_conjugate(self):
        return self[0]

Basic.singleton['sign'] = Sign
Basic.singleton['abs_'] = Abs
Basic.singleton['arg'] = Arg
Basic.singleton['conjugate'] = Conjugate