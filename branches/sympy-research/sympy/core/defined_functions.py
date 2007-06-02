
from basic import Basic
from function import DefinedFunction, Apply, Lambda

class Exp(DefinedFunction):
    """ Exp() -> exp
    """

    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex==1:
            return self
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        return Log()

    def _eval_apply(self, arg):
        arg = Basic.sympify(arg)
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return Basic.One()
        elif isinstance(arg, Apply) and isinstance(arg.func, Log):
            return arg.args[0]

    def _eval_apply_power(self, arg, exp):
        return self(arg * exp)
        
    def _eval_apply_evalf(self, arg):
        arg = arg.evalf()
        if isinstance(arg, Basic.Number):
            return arg.exp()

class Log(DefinedFunction):
    """ Log() -> log
    """

    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex==1:
            s = Basic.Symbol('x',dummy=True)
            return Lambda(s**(-1),s)
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        return Exp()

    def _eval_apply(self, arg, base=None):
        if base is not None:
            base = Basic.sympify(base)
            if not isinstance(base, Basic.Exp1):
                return self(arg)/self(base)
        arg = Basic.sympify(arg)
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Exp1):
                return Basic.One()
            if isinstance(arg, Basic.One):
                return Basic.Zero()
            if arg.is_negative:
                return Basic.Pi() * Basic.ImaginaryUnit() + self(-arg)
        elif isinstance(arg, Basic.Pow) and isinstance(arg.exp, Basic.Number):
            return arg.exp * self(arg.base)
        elif isinstance(arg, Apply) and isinstance(arg.func, Exp):
            return arg.args[0]

    def as_base_exp(self):
        return Exp(),Basic.Integer(-1)

    def _eval_apply_evalf(self, arg):
        arg = arg.evalf()
        if isinstance(arg, Basic.Number):
            return arg.log()

class Sqrt(DefinedFunction):

    nofargs = 1
    
    def fdiff(self, argindex=1):
        if argindex==1:
            s = Basic.Symbol('x',dummy=True)
            return Lambda(Basic.Half() * s**(-Basic.Half()),s)
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        s = Basic.Symbol('x',dummy=True)
        return Lambda(s**2, s)

    def _eval_apply(self, arg):
        return

    def _eval_apply_power(self, arg, exp):
        if isinstance(exp, Basic.Number):
            return arg ** (exp/2)

class Abs(DefinedFunction):

    nofargs = 1
    
    def fdiff(self, argindex=1):
        if argindex==1:
            raise NotImplementedError("Abs.fdiff()")
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def _eval_apply(self, arg):
        if arg.is_positive:
            return arg
        if arg.is_negative:
            return -arg
        return

class Sin(DefinedFunction):
    
    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex==1:
            return Cos()
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        return ASin()

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return arg
        return

class Cos(DefinedFunction):
    
    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex==1:
            return -Sin()
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        return ACos()

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return Basic.One()
        return

class Tan(DefinedFunction):
    
    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex==1:
            raise NotImplementedError('tan derivative')
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        return ATan()

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return arg
        return

Basic.singleton['exp'] = Exp
Basic.singleton['log'] = Log
Basic.singleton['ln'] = Log
Basic.singleton['sin'] = Sin
Basic.singleton['cos'] = Cos
Basic.singleton['tan'] = Tan
Basic.singleton['sqrt'] = Sqrt
Basic.singleton['abs_'] = Abs
