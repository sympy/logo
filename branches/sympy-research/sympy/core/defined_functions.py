
from basic import Basic
from function import DefinedFunction, Apply, Lambda

class ApplyExp(Apply):

    def as_base_exp(self):
        coeff, terms = self.args[0].as_coeff_terms()
        return self.func(Basic.Mul(*terms)), coeff

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        if self==old: return new
        if isinstance(old, ApplyExp):
            b,e = self.as_base_exp()
            bo,eo = old.as_base_exp()
            if b==bo:
                return new ** (e/eo) # exp(2/3*x*3).subs(exp(3*x),y) -> y**(2/3)
        return self.func(self.args[0].subs(old, new))

    def _eval_is_real(self):
        return self.args[0].is_real
    def _eval_is_positive(self):
        return self.args[0].is_real
    def _eval_is_bounded(self):
        arg = self.args[0]
        if arg.is_unbounded:
            if arg.is_negative: return True
            if arg.is_positive: return False
        if arg.is_bounded:
            return True
    def _calc_as_coeff_leadterm(self, x):
        arg = self.args[0]
        func = self.func
        if isinstance(arg, Basic.Add):
            return Basic.Mul._seq_as_coeff_leadterm([func(t).as_coeff_leadterm(x) for t in arg])
        c, e, f = arg.as_coeff_leadterm(x)
        # exp(c * x**e * log(x)**f)
        if e.is_positive:
            return Basic.One(), Basic.Zero(), Basic.Zero()
        if isinstance(e, Basic.Zero):
            # exp(c * log(x)**f) -> (exp(log(x)**f))**c
            if isinstance(f, Basic.Zero):
                return func(c), Basic.Zero(), Basic.Zero() # exp(c)
            if isinstance(f, Basic.One) and c.is_comparable:
                return Basic.One(),c,Basic.Zero()          # x ** c
        return func(c*x**e*Log()(x)**f), Basic.Zero(), Basic.Zero()
        if f<=0 and c.is_positive and e.is_negative: # essential singularity exp(1/x)
            return Basic.Infinity(),Basic.Zero(),Basic.Zero()
        if f>0 and c.is_positive and e.is_negative:
            if f.is_odd: # exp(ln(x)/x) -> 0
                return Basic.Zero(),Basic.Zero(),Basic.Zero()
            if f.is_even:
                return Basic.Infinity(),Basic.Zero(),Basic.Zero()
        print c._assumptions, x._assumptions, arg[1].args[0]._assumptions
        raise NotImplementedError("leading term of %s(%s) -> %s((%s) * (%s)**(%s) * log(%s)**(%s)) at %s=0" % (func,arg,func,c,x,e,x,f, x))


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
            if isinstance(arg, Basic.One):
                return Basic.Exp1()
            if isinstance(arg, Basic.Infinity):
                return arg
            if isinstance(arg, Basic.NegativeInfinity):
                return Basic.Zero()
            #return Basic.Exp1()**arg
        elif isinstance(arg, ApplyLog):
            return arg.args[0]
        elif isinstance(arg, (Basic.Add, Basic.Mul)):
            if isinstance(arg, Basic.Add):
                args = arg[:]
            else:
                args = [arg]
            l = []
            al = []
            for f in args:
                coeff, terms = f.as_coeff_terms()
                if len(terms)==1 and isinstance(terms[0], Basic.ApplyLog):
                    l.append(terms[0].args[0]**coeff)
                else:
                    al.append(f)
            if l:
                return Basic.Mul(*(l+[self(Basic.Add(*al))]))
        
    def _eval_apply_power(self, arg, exp):
        return self(arg * exp)
        
    def _eval_apply_evalf(self, arg):
        arg = arg.evalf()
        if isinstance(arg, Basic.Number):
            return arg.exp()

    def _calc_apply_positive(self, x):
        if x.is_real: return True

    def _calc_apply_real(self, x):
        if x.is_real: return True



class Log(DefinedFunction):
    """ Log() -> log
    """
    is_comparable = True
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
        if isinstance(arg, Basic.Exp1):
            return Basic.One()
        elif isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.One):
                return Basic.Zero()
            if isinstance(arg, Basic.Infinity):
                return arg
            if arg.is_negative:
                return Basic.Pi() * Basic.ImaginaryUnit() + self(-arg)
        elif isinstance(arg, Basic.Pow) and isinstance(arg.exp, Basic.Number):
            return arg.exp * self(arg.base)
        elif isinstance(arg, ApplyExp) and arg.args[0].is_real:
            return arg.args[0]
        elif isinstance(arg, Basic.Mul) and arg.is_real:
            return Basic.Add(*[self(a) for a in arg])

    def as_base_exp(self):
        return Exp(),Basic.Integer(-1)

    def _eval_apply_evalf(self, arg):
        arg = arg.evalf()
        if isinstance(arg, Basic.Number):
            return arg.log()


    
    def _calc_apply_positive(self, x):
        if x.is_positive and x.is_unbounded: return True

    def _calc_apply_unbounded(self, x):
        return x.is_unbounded


class ApplyLog(Apply):

    def _eval_is_real(self):
        return self.args[0].is_positive
    def _eval_is_bounded(self):
        return self.args[0].is_bounded
    def _eval_is_positive(self):
        arg = self.args[0]
        if arg.is_positive:
            if arg.is_unbounded: return True
            if isinstance(arg, Basic.Number):
                return arg>1
    def _calc_as_coeff_leadterm(self, x):
        arg = self.args[0]
        func = self.func
        if arg==x: return Basic.One(), Basic.Zero(),Basic.One()
        if isinstance(arg, Basic.Mul):
            return Basic.Add._seq_as_coeff_leadterm([func(t).as_coeff_leadterm(x) for t in arg])
        c, e, f = arg.as_coeff_leadterm(x)
        # log(c * x**e * log(x)**f) -> log(c) + e*log(x) + f * log(log(x))
        if f==0:
            if e==0:
                if isinstance(c, Basic.One):
                    return (arg-1).as_coeff_leadterm(x)
                return func(c),Basic.Zero(),Basic.Zero()
            return Basic.Add._seq_as_coeff_leadterm([(func(c),Basic.Zero(), Basic.Zero()),
                                                     (e,Basic.Zero(),Basic.One()),
                                                     #(f*self(self(x)),Basic.Zero(),Basic.Zero())
                                                     ])
        raise NotImplementedError("leading term of %s at %s=0" % (self(c*x**e*Log()(x)**f), x))

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
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Rational):
                factors = arg.factors()
                sqrt_factors = {}
                eval_factors = {}
                n = Basic.One()
                for k,v in factors.items():
                    n *= Basic.Integer(k) ** (v//2)
                    if v % 2:
                        n *= Basic.Integer(k) ** Basic.Half()
                return n
            return arg ** Basic.Half()
        coeff, terms = arg.as_coeff_terms()
        if not isinstance(coeff, Basic.One):
            return self(coeff) * self(Basic.Mul(*terms))
        base, exp = arg.as_base_exp()
        if isinstance(exp, Basic.Number):
            return base ** (exp/2)
        
    def _eval_apply_power(self, arg, exp):
        if isinstance(exp, Basic.Number):
            return arg ** (exp/2)

    def _eval_apply_leadterm(self, x, arg):
        raise
        c0, e0 = arg.leadterm(x)
        if isinstance(e0, Basic.Zero):
            return self(c0), e0
        return self(c0), e0/2

    def _eval_apply_evalf(self, arg):
        arg = arg.evalf()
        if isinstance(arg, Basic.Number):
            return arg.sqrt()

    def _eval_apply_subs(self, x, old, new):
        base, exp = old.as_base_exp()
        if base==x:
            return new ** (exp/2)

class ApplySqrt(Apply):

    def as_base_exp(self):
        return self.args[0], Basic.Half()

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        if self==old: return new
        arg = self.args[0]
        func = self.func
        return func(arg.subs(old, new))

    def ___calc_as_coeff_leadterm(self, x):
        arg = self.args[0]
        func = self.func

class Abs(DefinedFunction):

    nofargs = 1
    
    def fdiff(self, argindex=1):
        if argindex==1:
            raise NotImplementedError("Abs.fdiff()")
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def _eval_apply(self, arg):
        if arg.is_positive: return arg
        if arg.is_negative: return -arg
        coeff, terms = arg.as_coeff_terms()
        if not isinstance(coeff, Basic.One):
            return self(coeff) * self(Basic.Mul(*terms))
        return

    def _eval_apply_leadterm(self, x, arg):
        raise
        c0, e0 = arg.leadterm(x)
        if isinstance(e0, Basic.Zero):
            return self(c0), Basic.Zero()
        raise ValueError("unable to compute leading term %s(%s) at %s=0" % (self, arg, x))

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


class ApplySin(Apply):

    def _calc_as_coeff_leadterm(self, x):
        arg = self.args[0]
        func = self.func
        c0, e0, f0 = arg.as_coeff_leadterm(x)
        if e0==0 and f0==0:
            # sin(5+x) -> sin(5)
            if isinstance(c0, Basic.Zero):
                return c0,e0,f0
            c = func(c0)
            if not isinstance(c, Basic.Zero):
                return c,e0,f0
            return func(arg - c).as_coeff_leadterm(x)
        if e0>0:
            return c0,e0,f0
        raise ValueError("unable to compute leading term %s(%s) at %s=0" % (func, arg, x))

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


class ApplyCos(Apply):

    def _calc_as_coeff_leadterm(self, x):
        arg = self.args[0]
        func = self.func
        c0, e0, f0 = arg.as_coeff_leadterm(x)
        if e0==0 and f0==0:
            # cos(5+x) -> cos(5)
            if isinstance(c0, Basic.Zero):
                return c0,e0,f0
            c = func(c0)
            if not isinstance(c, Basic.Zero):
                return c,e0,f0
            return func(arg - c).as_coeff_leadterm(x)
        if e0>0:
            return Basic.One(),Basic.Zero(),Basic.Zero()
        raise ValueError("unable to compute leading term %s(%s) at %s=0" % (func, arg, x))

class Tan(DefinedFunction):
    
    nofargs = 1

    def fdiff(self, argindex=1):
        if argindex==1:
            return 1+self**2
        raise TypeError("argindex=%s is out of range [1,1] for %s" % (argindex,self))

    def inverse(self, argindex=1):
        return ATan()

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.Number):
            if isinstance(arg, Basic.Zero):
                return arg
        return

    def _eval_apply_leadterm(self, x, arg):
        raise
        c0, e0 = arg.leadterm(x)
        if isinstance(e0, Basic.Zero):
            # tan(5+x) -> tan(5)
            c0 = self(c0)
            if not isinstance(c0, Basic.Zero):
                return c0, e0
            # tan(Pi+x) -> tan(-x)
            raise NotImplementedError("compute leading term %s(%s) at %s=0" % (self, arg, x))
        if e0.is_positive:
            # tan(2*x) -> 2 * x
            return c0, e0
        # tan(1/x)
        raise ValueError("unable to compute leading term %s(%s) at %s=0" % (self, arg, x))

class Sign(DefinedFunction):

    nofargs = 1

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.Zero): return arg
        if arg.is_positive: return Basic.One()
        if arg.is_negative: return -Basic.One()
        if isinstance(arg, Basic.Mul):
            coeff, terms = arg.as_coeff_terms()
            if not isinstance(coeff, Basic.One):
                return self(coeff) * self(Basic.Mul(*terms))

class Factorial(DefinedFunction):

    nofargs = 1

    def _eval_apply(self, arg):
        if isinstance(arg, Basic.Zero): return Basic.One()
        if isinstance(arg, Basic.Integer) and arg.is_positive:
            r = arg.p
            m = 1
            while r:
                m *= r
                r -= 1
            return Basic.Integer(m)

Basic.singleton['exp'] = Exp
Basic.singleton['log'] = Log
Basic.singleton['ln'] = Log
Basic.singleton['sin'] = Sin
Basic.singleton['cos'] = Cos
Basic.singleton['tan'] = Tan
Basic.singleton['sqrt'] = Sqrt
Basic.singleton['abs_'] = Abs
Basic.singleton['sign'] = Sign
Basic.singleton['factorial'] = Factorial
