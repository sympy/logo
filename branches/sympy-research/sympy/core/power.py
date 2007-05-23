
from basic import Basic
from methods import ArithMeths, RelMeths

class Pow(Basic, ArithMeths, RelMeths):

    def __new__(cls, a, b):
        a = Basic.sympify(a)
        b = Basic.sympify(b)
        if isinstance(b, Basic.Zero):
            return Basic.One()
        if isinstance(b, Basic.One):
            return a
        obj = a._eval_power(b)
        if obj is None:
            obj = Basic.__new__(cls, a, b)
        return obj

    @property
    def base(self):
        return self._args[0]

    @property
    def exp(self):
        return self._args[1]

    def _eval_power(self, other):
        if isinstance(other, Basic.Number):
            if isinstance(self.exp, Basic.Number):
                return Pow(self.base, self.exp * other)
        return

    def tostr(self, level=0):
        precedence = self.precedence
        r = '%s ** %s' % (self.base.tostr(precedence),
                          self.exp.tostr(precedence))
        if precedence<=level:
            return '(%s)' % (r)
        return r

Basic.Pow = Pow
