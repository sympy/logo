"""
There are three types of functions:
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

One can perform certain operations with functions, the
result will be a lambda function. Allowed operations are
addition and multiplication. Function multiplication is
elementise ie (f*g)(x) is equivalent to f(x) * g(x).
Multiplication by a number is equivalent to muliplication
by a constant function.
Composition of functions is achived via ** operation.
Eg

  f+2*exp**sin -> lambda _x: f(x)+2*exp(sin(x))

In the above functions did not have arguments, then
it is said that functions are in unevaluated form.
When calling a function with arguments, then we get
an instance of the function value. Eg

  exp(1) -> 1
  (2*f)(x)  -> 2 * f(x)
  Lambda(x, exp(x)*x)(y) -> exp(y)*y

One can construct undefined function values by from Symbol
object:
  f = Symbol('f')
  fx = f(x)
  fx.func -> Function('f')
  fx.args -> (Symbol('x'),)
As seen above, function values have attributes .func
and .args.
"""

from basic import Basic, Singleton, Atom
from methods import ArithMeths, NoRelMeths, RelMeths

class Apply(Basic, ArithMeths, RelMeths):
    """ Represents unevaluated function value.

    Apply(func, arg1, arg2, ..., **assumptions) <-> func(arg1, arg2, .., **assumptions)
    """

    precedence = 70

    def __new__(cls, *args, **assumptions):
        return Basic.__new__(cls, *(map(Basic.sympify,args)),**assumptions)

    @property
    def func(self):
        return self._args[0]

    @property
    def args(self):
        return self._args[1:]

    def tostr(self, level=0):
        p = self.precedence
        r = '%s(%s)' % (self.func.tostr(), ', '.join([a.tostr(p) for a in self.args]))
        if p <= level:
            return '(%s)' % (r)
        return r


class Function(Basic, ArithMeths, NoRelMeths):
    """ Base class for function objects.
    """

    nofargs = None
    args = None
    body = None

    def __call__(self, *args, **assumptions):
        n = self.nofargs
        if n is not None and n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)'\
                            % (self, n, len(args)))
        return Apply(self, *args, **assumptions)


class DefinedFunction(Function, Singleton, Atom):
    """ Base class for defined functions.
    """
    def __new__(cls, **assumptions):
        return Basic.__new__(cls,**assumptions)

    def tostr(self, level=0):
        return self.__class__.__name__.lower()

    def torepr(self):
        return '%s()' % (self.__class__.__name__)
    
        
class Exp(DefinedFunction):
    """ Exp() -> exp
    """

    nofargs = 1

    def derivative(self, argindex=1):
        return self

    def antiderivative(self, argindex=1):
        return self

    def __call__(self, arg, **assumptions):
        arg = Basic.sympify(arg)
        if isinstance(arg, Basic.Zero):
            return Basic.One()
        return Function.__call__(self, arg, **assumptions)

class Lambda(Function):
    """
    Lambda(expr, arg1, arg2, ..., **assumptions) -> lambda arg1, arg2,...,**assumptions : expr
    """
    precedence = 1

    def __new__(cls, expr, *args, **assumptions):
        expr = Basic.sympify(expr)
        args = map(Basic.sympify, args)
        dummy_args = []
        for a in args:
            a = Basic.sympify(a)
            if not isinstance(a, Basic.Symbol):
                raise TypeError("%s %s-th argument must be Symbol instance (got %r)" \
                                % (cls.__name__, len(dummy_args)+1,a))
            d = a.as_dummy()
            expr = expr.subs(a, d)
            dummy_args.append(d)
        return Function.__new__(cls, expr, *dummy_args, **assumptions)

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

    def __call__(self, *args, **assumptions):
        if len(args)!=self.nofargs:
            raise TypeError("%s takes exactly %d arguments (got %d)" \
                            % (self, self.nofargs, len(args)))
        expr = self.body
        for d,a in zip(self.args, args):
            expr = expr.subs(d, a)
        return expr

    def as_coeff_terms(self):
        c,t = self.body.as_coeff_terms()
        return c, [Lambda(Basic.Mul(*t),*self.args)]

    def _eval_power(b, e):
        """
        (lambda x:f(x)) ** e -> (lambda x:f(x)**e)
        (lambda x:f(x)) ** func -> lambda x:f(func(x))

        (f**g)(x) -> f(g(x))
        """
        raise NotImplementedError

Basic.singleton['exp'] = Exp    
