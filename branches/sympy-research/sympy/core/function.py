"""
There are different types of functions:
1) defined function like exp or sin that has a name and body
   (in the sense that function can be evaluated).
    e = exp
2) undefined function with a name but no body. Undefined
  functions can be defined using Symbol class as follows:
    f = Symbol('f', function=True)
  (the result will be Function instance)
  or
    f = Function('f')
3) anonymous function or lambda function that has no name
   but has body with dummy variables. An anonymous function
   object creation examples:
    f = Lambda(x, exp(x)*x)
    f = Lambda(exp(x)*x)  # free symbols in the expression define the number of arguments
    f = exp * Lambda(x,x)
4) composition of functions, inverse functions

One can perform certain operations with functions, the
result will be a lambda function. Allowed operations are
addition and multiplication. Function multiplication is
elementise ie (f*g)(x) is equivalent to f(x) * g(x).
Multiplication by a number is equivalent to multiplication
by a constant function.
Composition of functions is achived via Composition class@
Eg

  f+Composition(2,exp,sin) -> lambda _x: f(x)+2*exp(sin(x))

In the above functions did not have arguments, then
it is said that functions are in unevaluated form.
When calling a function with arguments, then we get
an instance of the function value. Eg

  exp(1) -> 1
  (2*f)(x)  -> 2 * f(x)
  Lambda(x, exp(x)*x)(y) -> exp(y)*y

One can construct undefined function values from Symbol
object:
  f = Symbol('f')
  fx = f(x)
  fx.func -> Function('f')
  fx.args -> (Symbol('x'),)
As seen above, function values are Apply instances and
have attributes .func and .args.
"""

from basic import Basic, Singleton, Atom
from methods import ArithMeths, NoRelMeths, RelMeths
from operations import AssocOp

class Apply(Basic, ArithMeths, RelMeths):
    """ Represents unevaluated function value.

    Apply(func, arg1, arg2, ..., **assumptions) <-> func(arg1, arg2, .., **assumptions)
    """

    precedence = 70

    def __new__(cls, *args, **assumptions):
        args = map(Basic.sympify,args)
        obj = args[0]._eval_apply(*args[1:])
        if obj is None:
            obj = Basic.__new__(cls, *args,**assumptions)
        return obj

    @property
    def func(self):
        return self._args[0]

    @property
    def args(self):
        return self._args[1:]

    def tostr(self, level=0):
        p = self.precedence
        r = '%s(%s)' % (self.func.tostr(p), ', '.join([a.tostr() for a in self.args]))
        if p <= level:
            return '(%s)' % (r)
        return r

    subs = Basic._seq_subs

    def evalf(self):
        return self.func._eval_apply_evalf(*self.args)

    @property
    def is_comparable(self):
        for s in self:
            if not s.is_comparable:
                return
        return True

    def _eval_derivative(self, s):
        # Apply(f(x), x).diff(s) -> x.diff(s) * f.fdiff(1)(s)
        i = 0
        l = []
        r = Basic.Zero()
        for a in self.args:
            i += 1
            da = a.diff(s)
            if isinstance(da, Basic.Zero):
                continue
            df = self.func.fdiff(i)
            l.append(Apply(df,*self.args) * da)
        return Basic.Add(*l)

    def _eval_power(b, e):
        if len(b.args)==1:
            return b.func._eval_apply_power(b.args[0], e)
        return

    def _calc_commutative(self):
        for a in self._args:
            if not a.is_commutative: return a.is_commutative
        return True

    def _calc_leadterm(self, x):
        if hasattr(self.func,'_eval_apply_leadterm'):
            return self.func._eval_apply_leadterm(x, *self.args)

class Function(Basic, ArithMeths, NoRelMeths):
    """ Base class for function objects, represents also undefined functions.

    Undefined functions:
      f = Function('f', nofargs=1)
      f.fdiff(1) -> FApply(DF(1), f)
      f(x).diff(x) -> Apply(f,x).diff(x) -> Apply(FApply(DF(1),f),x)
      
    Defined functions:
      exp = Exp()
      f.fdiff(1) -> exp
      log = Log()
      log.fdiff(1) -> Lambda(1/_x, _x)

    Anonymous/lambda functions:
      f = Lambda(_x**2 + 1, _x)
      f.fdiff(1) -> Lambda((_x**2+1).diff(_x), _x) -> Lambda(2*_x, _x)
      f = Lambda(g(_x), _x) -> Lambda(Apply(g,_x),_x) -> g
      f = Lambda(g(2*_x), _x) -> Lambda(Apply(g,2*_x),_x)
      f.fdiff(1) -> Lambda(Apply(FApply(DF(1), g), 2*_x) * (2*_x).diff(_x), _x)

    Function derivatives (applying operators to functions):
      df = DF(1)(f) == FApply(DF(1), f)
      df.fdiff(1) -> FApply(DF(1), FApply(DF(1), f)) -> FApply(DF(1,1), f)

    Composition of functions:
      e2 = Composition(exp, sin)
      e2(x) -> exp(sin(x)) -> Apply(exp, Apply(sin, x))
      e2.fdiff(1) -> Lambda(exp(sin(_x)).diff(_x), _x) -> Lambda(Apply(exp, Apply(sin, _x)).diff(_x), _x)
                  -> Lambda(Apply(Compostion(exp, sin), _x).diff(_x), _x)
                  -> Lambda(Apply(FApply(DF(1),exp), Apply(sin, _x)) * Apply(FApply(DF(1), sin),_x), _x)
      
    """

    nofargs = None
    args = None
    body = None
    has_derivative = False

    def __new__(cls, name, nofargs = None, **assumptions):
        obj = Basic.singleton.get(name)
        if obj is not None:
            return obj()
        obj = Basic.__new__(cls, **assumptions)
        obj.name = name
        obj.nofargs = nofargs
        return obj

    def _hashable_content(self):
        return (self.name, self.nofargs)

    def tostr(self, level=0):
        return self.name

    def torepr(self):
        return '%s(%r, nofargs = %r)' % (self.__class__.__name__, self.name, self.nofargs)

    def _eval_apply(self, *args):
        return

    def __call__(self, *args, **assumptions):
        n = self.nofargs
        if n is not None and n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)'\
                            % (self, n, len(args)))
        return Apply(self, *args, **assumptions)

    def with_dummy_arguments(self, args = None):
        """ Return a function value with dummy arguments.
        """
        if args is None:
            if self.nofargs is None:
                raise TypeError('unknown number of arguments for undefined function %r' % (self))
            else:
                args = tuple([Basic.Symbol('x%s'%(i+1),dummy=True) for i in range(self.nofargs)])
        else:
            if self.nofargs is None:
                self.nofargs = len(args)
        return self(*args), args

    def expand(self):
        return self

    def fdiff(self, argindex=1):
        if self.nofargs is not None:
            if not (1<=argindex<=self.nofargs):
                raise TypeError("argument index %r is out of range [1,%s]" % (i,self.nofargs))
        return FDerivative(argindex)(self)

    def diff(self,*args,**assumptions):
        raise TypeError('%s.diff not usable for functions, use .fdiff() method instead.' % (self.__class__.__name__))

    def _eval_power(b, e):
        body, args = b.with_dummy_arguments()
        return Lambda(body**e, *args)

    def inverse(self):
        return FPow(self, -1)

    # functions can define leadterm0() and leadterm1() methods

class WildFunction(Function):

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        for p,v in repl_dict.items():
            if p==pattern:
                if v==expr: return repl_dict
                return None
        repl_dict = repl_dict.copy()
        repl_dict[pattern] = expr
        return repl_dict

    def tostr(self, level=0):
        return self.name + '_'

class FApply(Function):
    """ Defines n-ary operator that acts on symbolic functions.

    DF(1)(f) -> FApply(DF(1), f)
    DF(2)(FApply(DF(1), f)) -> FApply(DF(2), FApply(DF(1),f)) -> FApply(DF(1,2), f)
    """
    
    def __new__(cls, operator, *funcs, **assumptions):
        operator = Basic.sympify(operator)
        funcs = map(Basic.sympify, funcs)
        obj = operator._eval_fapply(*funcs, **assumptions)
        if obj is not None:
            return obj
        return Basic.__new__(cls, operator, *funcs, **assumptions)

    def _hashable_content(self):
        return self._args

    @property
    def operator(self):
        return self._args[0]

    @property
    def funcs(self):
        return self._args[1:]

    def tostr(self, level=0):
        p = self.precedence
        r = '%s(%s)' % (self.operator.tostr(p), ', '.join([a.tostr() for a in self.funcs]))
        if p <= level:
            return '(%s)' % (r)
        return r

    subs = Basic._seq_subs



class Lambda(Function):
    """
    Lambda(expr, arg1, arg2, ...) -> lambda arg1, arg2,... : expr

    Lambda instance has the same assumptions as its body.

    Lambda(Apply(g,x),x) -> g
    """
    precedence = 1
    name = None
    has_derivative = True

    def __new__(cls, expr, *args):
        expr = Basic.sympify(expr)
        args = tuple(map(Basic.sympify, args))
        if isinstance(expr, Apply):
            if expr.args==args:
                return expr.func
        dummy_args = []
        for a in args:
            if not isinstance(a, Basic.Symbol):
                raise TypeError("%s %s-th argument must be Symbol instance (got %r)" \
                                % (cls.__name__, len(dummy_args)+1,a))
            d = a.as_dummy()
            expr = expr.subs(a, d)
            dummy_args.append(d)
        obj = Basic.__new__(cls, expr, *dummy_args, **expr._assumptions)
        return obj

    def _hashable_content(self):
        return self._args

    @property
    def nofargs(self):
        return len(self._args)-1

    @property
    def args(self):
        return self._args[1:]

    @property
    def body(self):
        return self._args[0]

    def tostr(self, level=0):
        precedence = self.precedence
        r = 'lambda %s: %s' % (', '.join([a.tostr() for a in self.args]),
                               self.body.tostr(precedence))
        if precedence <= level:
            return '(%s)' % r
        return r

    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join([a.torepr() for a in self]))

    def as_coeff_terms(self):
        c,t = self.body.as_coeff_terms()
        return c, [Lambda(Basic.Mul(*t),*self.args)]

    def _eval_power(b, e):
        """
        (lambda x:f(x))**e -> (lambda x:f(x)**e)
        """
        return Lambda(b.body**e, *b.args)

    def _eval_fpower(b, e):
        """
        FPow(lambda x:f(x), 2) -> lambda x:f(f(x)))
        """
        if isinstance(e, Basic.Integer) and e.is_positive and e.p < 10 and len(b.args)==1:
            r = b.body
            for i in range(e.p-1):
                r = b(r)
            return Lambda(r, *b.args)

    def with_dummy_arguments(self, args = None):
        if args is None:
            args = tuple([a.as_dummy() for a in self.args])
        if len(args) != len(self.args):
            raise TypeError("different number of arguments in Lambda functions: %s, %s"\
                            (len(args), len(self.args)))
        expr = self.body
        for a,na in zip(self.args, args):
            expr = expr.subs(a, na)
        return expr, args

    def expand(self):
        return Lambda(self.body.expand(), *self.args)

    def diff(self,*symbols):
        return Lambda(self.body.diff(*symbols), *self.args)

    def fdiff(self, argindex=1):
        if not (1<=argindex<=len(self.args)):
            raise TypeError("%s.fderivative() argindex %r not in the range [1,%s]"\
                            % (self.__class__, argindex, len(self.args)))
        s = self.args[argindex-1]
        expr = self.body.diff(s)
        return Lambda(expr, *self.args)

    subs = Basic._seq_subs

    def _eval_apply(self, *args):
        n = self.nofargs
        if n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)'\
                            % (self, n, len(args)))
        expr = self.body
        for da,a in zip(self.args, args):
            expr = expr.subs(da,a)
        return expr


class FPow(Function):

    precedence = 70

    def __new__(cls, a, b, **assumptions):
        a = Basic.sympify(a)
        b = Basic.sympify(b)
        if isinstance(b, Basic.Zero):
            return Basic.One()
        if isinstance(b, Basic.One):
            return a
        obj = a._eval_fpower(b)
        if obj is None:
            obj = Basic.__new__(cls, a, b, **assumptions)
        return obj

    def _hashable_content(self):
        return self._args

    @property
    def base(self):
        return self._args[0]

    @property
    def exp(self):
        return self._args[1]

    def _eval_fpower(self, other):
        if isinstance(other, Basic.Number):
            if isinstance(self.exp, Basic.Number):
                # (a ** 2) ** 3 -> a ** (2 * 3)
                return FPow(self.base, self.exp * other)
        return

    def _eval_apply(self, *args):
        if isinstance(self.exp, Basic.Integer) and self.exp.is_positive and self.exp.p < 10:
            r = self.base(*args)
            for i in range(self.exp.p-1):
                r = self.base(r)
            return r

    def tostr(self, level=0):
        r = '%s(%s, %s)' % (self.__class__.__name__, self.base.tostr(), self.exp.tostr())
        if self.precedence<=level:
            return '(%s)' % (r)
        return r

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        if self==old: return new
        #elif exp(self.exp * log(self.base)) == old: return new
        return self.base.subs(old, new) ** self.exp.subs(old, new)

    def as_base_exp(self):
        return self.base, self.exp


class Composition(AssocOp, Function):
    """ Composition of functions.
    
    Composition(f1,f2,f3)(x) -> f1(f2(f3(x)))

    >>> l1 = Lambda('x**2','x')
    >>> l2 = Lambda('x+1','x')
    >>> Composition(l1,l2)('y')
    (1 + y) ** 2
    >>> Composition(l2,l1)('y')
    1 + y ** 2
    >>> Composition(exp,log,exp,exp)('x')
    exp(exp(x))
    """
    
    @classmethod
    def flatten(cls, seq):
        c_part = []
        nc_part = []
        while seq:
            o = seq.pop(0)
            if isinstance(o, Basic.One):
                continue
            if o.__class__ is cls:
                # associativity
                seq = list(o._args) + seq
                continue
            if not nc_part:
                nc_part.append(o)
                continue
            # try to combine last terms: a**b * a ** c -> a ** (b+c)
            o1 = nc_part.pop()
            b1,e1 = o1.as_base_exp()
            b2,e2 = o.as_base_exp()
            if b1==b2:
                seq.insert(0, Basic.FPow(b1,e1 + e2))
            elif o1.is_homogeneous and isinstance(o, Basic.Number):
                seq.insert(0,o1)
                seq.insert(0,o)
            elif isinstance(o1, Basic.Number) and isinstance(o, Basic.Number):
                nc_part.append(o1 * o)
            elif isinstance(o1, Basic.Lambda) and isinstance(o, Basic.Lambda):
                nc_part.append(Lambda(o1(o.body),*o.args))
            else:
                nc_part.append(o1)
                nc_part.append(o)
        return [], nc_part, None, None

    def tostr(self, level=0):
        return '%s(%s)' % (self.__class__.__name__,', '.join([f.tostr() for f in self]))

    def _eval_apply(self, *args):
        l = list(self)
        r = l.pop()(*args)
        while l:
            r = l.pop()(r)
        return r

    def _hashable_content(self):
        return self._args

    def _matches_simple(pattern, expr, repl_dict):        
        return


class FDerivative(Function):

    is_homogeneous = True

    def __new__(cls, *indices, **assumptions):
        indices = map(Basic.sympify, indices)
        indices.sort(Basic.compare)
        return Basic.__new__(cls, *indices, **assumptions)


    def _hashable_content(self):
        return self._args

    @property
    def indices(self):
        return self._args

    def tostr(self, level=0):
        return 'FD%s' % (repr(tuple(self.indices)))

    def _eval_fapply(self, *funcs):
        if len(funcs)==1:
            func = funcs[0]
            if isinstance(func, FApply) and isinstance(func.operator, FDerivative):
                # FApply(FD(1),FApply(FD(2),f)) -> FApply(FD(1,2), f)
                return FApply(FDerivative(*(self.indices+func.operator.indices)), *func.funcs)
            if isinstance(func, Lambda):
                # FApply(FD(1),Lambda _x: f(_x)) -> FApply(Lambda _x: f(_x).diff(_x))
                expr = func.body
                unevaluated_indices = []
                for i in self.indices:
                    if isinstance(i, Basic.Integer):
                        a = func.args[int(i)-1]
                        obj = expr.diff(a)
                        if isinstance(obj, Derivative):
                            unevaluated_indices.append(i)
                        else:
                            expr = obj
                if len(self.indices)==len(unevaluated_indices):
                    return
                if not unevaluated_indices:
                    return Lambda(expr, *func.args)
                return FApply(FDerivative(*unevaluated_indices), Lambda(expr, *func.args))
        return

    def _eval_power(b, e):
        if isinstance(e, Basic.Integer) and e.is_positive:
            return FDerivative(*(int(e)*b.indices))

    subs = Basic._seq_subs

    def __call__(self, func):
        return FApply(self, func)


class Derivative(Basic, ArithMeths, RelMeths):
    """
    Carries out differentation of the given expression with respect to symbols.

    expr must define ._eval_derivative(symbol) method that returns differentation result or None.

    Derivative(Derivative(expr, x), y) -> Derivative(expr, x, y)
    """

    precedence = 70

    def __new__(cls, expr, *symbols, **assumptions):
        expr = Basic.sympify(expr)
        if not symbols: return expr
        symbols = map(Basic.sympify, symbols)
        for s in symbols:
            assert isinstance(s, Basic.Symbol),`s`
            if not expr.has(s):
                return Basic.Zero()
        unevaluated_symbols = []
        for s in symbols:
            obj = expr._eval_derivative(s)
            if obj is None:
                unevaluated_symbols.append(s)
            else:
                expr = obj
        if not unevaluated_symbols:
            return expr
        return Basic.__new__(cls, expr, *unevaluated_symbols)

    def as_apply(self):
        # Derivative(f(x),x) -> Apply(Lambda(f(_x),_x), x)
        symbols = []
        indices = []
        for s in self.symbols:
            if s not in symbols:
                symbols.append(s)
                indices.append(len(symbols))
            else:
                indices.append(symbols.index(s)+1)
        return Apply(FApply(FDerivative(*indices), Lambda(self.expr, *symbols)), *symbols)

    def _eval_derivative(self, s):
        if s not in self.symbols:
            obj = self.expr.diff(s)
            if isinstance(obj, Derivative):
                return Derivative(obj.expr, *(obj.symbols+self.symbols))
            return Derivative(obj, *self.symbols)
        return Derivative(self.expr, *((s,)+self.symbols))
        
    @property
    def expr(self):
        return self._args[0]

    @property
    def symbols(self):
        return self._args[1:]

    def tostr(self, level=0):
        r = 'D' + `tuple(self)`
        if self.precedence <= level:
            r = '(%s)' % (r)
        return r

    def subs(self, old, new):
        old = Basic.sympify(old)
        new = Basic.sympify(new)
        for a in list(old.atoms(Basic.Symbol)):
            if a in self.symbols:
                return self.as_apply().subs(old, new)                
        return self.__class__(*[s.subs(old, new) for s in self])


class DefinedFunction(Function, Singleton, Atom):
    """ Base class for defined functions.
    """
    
    is_commutative = True # the values of functions are commutative

    def __new__(cls, **assumptions):
        obj = Basic.__new__(cls,**assumptions)
        obj.name = obj.__class__.__name__.lower()
        return obj

    def torepr(self):
        return '%s()' % (self.__class__.__name__)



Basic.singleton['D'] = lambda : Derivative
Basic.singleton['FD'] = lambda : FDerivative
