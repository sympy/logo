# this is backward compatibilty, to be removed

from basic import Basic
from function import Function, Derivative
exp = lambda x: Basic.Exp()(x)
log = lambda x: Basic.Log()(x)
sqrt = lambda x: Basic.Sqrt()(x)
sign = lambda x: Basic.Sign()(x)
diff = lambda expr, *args, **assumptions: Basic.sympify(expr).diff(*args)
