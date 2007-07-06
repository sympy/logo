
from __init__ import *
from limit import mrv, mrv_max, mrv_compare, mrv_leadterm, mrv2, MrvExpr
import unittest

x = Symbol('x',positive=True,real=True,unbounded=True)
z = Basic.Zero()
o = Basic.One()


class MrvCompareLeadTerm(unittest.TestCase):

    def test_simple_1(self):
        self.assertEquals(mrv_compare(x,x,x),'=')


    def test_simple_2(self):
        self.assertEquals(mrv_compare(x,ln(x),x),'>')
        self.assertEquals(mrv_compare(ln(x),x,x),'<')


class MrvTestCase(unittest.TestCase):

    def test_simple_x(self):
        expr = x + 1/x
        self.assertEquals(mrv(expr,x),set([x]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(r,expr)
        self.assertEquals(md,{x:x})

    def test_simple_poly(self):
        expr = x**2
        self.assertEquals(mrv(expr,x),set([x]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(r,expr)
        self.assertEquals(md,{x:x})

    def test_simple_log(self):
        expr = log(x)
        self.assertEquals(mrv(expr,x),set([x]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(r,expr)
        self.assertEquals(md,{x:x})

    def test_simple_exp(self):
        expr = exp(x)
        self.assertEquals(mrv(expr,x),set([exp(x)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(md,{expr:r})

    def test_simple_exp2(self):
        expr = exp(x**2)
        self.assertEquals(mrv(expr,x),set([exp(x**2)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(md,{expr:r})

    def test_page41_1(self):
        expr = exp(x+1/x)
        self.assertEquals(mrv(expr,x),set([expr]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(md,{expr:r})

    def test_page41_2(self):
        expr = exp(x+exp(-exp(x)))
        self.assertEquals(mrv(expr,x),set([exp(exp(x))]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(md.keys()[0],exp(exp(x)))

    def test_page41_3(self):
        expr = exp(x+exp(-x))
        self.assertEquals(mrv(expr,x),set([exp(x+exp(-x)),exp(x)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x+exp(-x)),exp(x)]))

    def test_page41_ex3_13(self):
        expr = exp(x+exp(-x**2))
        self.assertEquals(mrv(expr,x),set([exp(x**2)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x**2)]))

    def test_page41_4(self):
        expr = exp(1/x+exp(-x))
        self.assertEquals(mrv(expr,x),set([exp(x)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x)]))
        
    def test_page41_5(self):
        expr = exp(x**2)+x*exp(x)+ln(x)**x/x
        self.assertEquals(mrv(expr,x),set([exp(x**2)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x**2)]))

    def test_page41_6(self):
        expr = exp(x)*(exp(1/x+exp(-x))-exp(1/x))
        self.assertEquals(mrv(expr,x),set([exp(x)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x)]))

    def test_page41_7(self):
        expr = log(x**2+2*exp(exp(3*x**3*log(x))))
        self.assertEquals(mrv(expr,x),set([exp(exp(3*x**3*log(x)))]))

    def test_page41_8(self):
        expr = log(x-log(x))/log(x)
        self.assertEquals(mrv(expr,x),set([x]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([x]))

    def test_page43_ex3_15(self):
        expr = (exp(1/x-exp(-x))-exp(1/x))/exp(-x)
        self.assertEquals(mrv(expr,x),set([exp(x)]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x)]))

    def test_page44_ex3_17(self):
        expr = 1/exp(-x+exp(-x))-exp(x)
        self.assertEquals(mrv(expr,x),set([exp(x), exp(x-exp(-x))]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x), exp(x-exp(-x))]))

    def test_page47_ex3_21(self):
        h = exp(-x/(1+exp(-x)))
        expr = exp(h)*exp(-x/(1+h))*exp(exp(-x+h))/h**2-exp(x)+x
        expected = set([1/h,exp(x),exp(x-h),exp(x/(1+h))])
        self.assertEquals(mrv(expr,x).difference(expected),set())

    def test_page51_ex3_25(self):
        expr = (ln(ln(x)+ln(ln(x)))-ln(ln(x)))/ln(ln(x)+ln(ln(ln(x))))*ln(x)
        self.assertEquals(mrv(expr,x),set([x]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([x]))

    def test_page56_ex3_27(self):
        expr = exp(-x+exp(-x)*exp(-x*ln(x)))
        self.assertEquals(mrv(expr,x),set([exp(x*log(x))]))
        d,md = {},{}
        r = mrv2(expr,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x*log(x))]))

    def test_page60_sec3_5_1(self):
        expr1 = log(log(x*exp(x*exp(x))+1))
        self.assertEquals(mrv(expr1,x),set([exp(x*exp(x))]))
        d,md = {},{}
        r = mrv2(expr1,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x*exp(x))]))

    def test_page60_sec3_5_2(self):
        expr2 = exp(exp(log(log(x)+1/x)))
        c = mrv_compare(expr2,x,x)
        assert c=='=',`c`
        self.assertEquals(mrv(expr2,x),set([x]))
        d,md = {},{}
        r = mrv2(expr2,x,d,md)
        self.assertEquals(set(md.keys()),set([x]))

    def test_page60_sec3_5(self):
        expr1 = log(log(x*exp(x*exp(x))+1))
        expr2 = exp(exp(log(log(x)+1/x)))
        expr = expr1 - expr2
        self.assertEquals(mrv(expr,x),set([exp(x*exp(x))]))
        d,md = {},{}
        r = mrv2(expr1,x,d,md)
        self.assertEquals(set(md.keys()),set([exp(x*exp(x))]))

class MrvExprTestCase(unittest.TestCase):

    def test_simple_0(self):
        expr = 3
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),3)

    def test_simple_1(self):
        expr = x
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),oo)

    def test_simple_2(self):
        expr = 1/x
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),0)

    def test_simple_3(self):
        expr = exp(x)
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),oo)

    def test_simple_4(self):
        expr = exp(-x)
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),0)

    def test_page2(self):
        expr = x**7/exp(x)
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),0)

    def test_page4(self):
        expr = 1/((1/x)**(log(log(log(log(x))))-1))
        m = MrvExpr(expr, x)
        self.assertEquals(m.get_limit(),oo)

    def test_page12_ex2_5(self):
        expr = sqrt(ln(x+1))-sqrt(ln(x))
        m = MrvExpr(expr, x)
        print m
        print m.get_limit()
        #self.assertEquals(m.get_limit(),0)


class MrvLimitTestCase(unittest.TestCase):

    def test_simple(self):
        x = Symbol('x')
        self.assertEquals(x.limit(x,2),2)

    def test_simple_inf(self):
        x = Symbol('x')
        self.assertEquals(x.limit(x,oo),oo)

    def test_page2(self):
        x = Symbol('x')
        self.assertEquals((x**7/exp(x)).limit(x,oo),0)

    def test_page4(self):
        x = Symbol('x')
        expr = 1/(x**(log(log(log(log(1/x))))-1))
        self.assertEquals(expr.limit(x,0),oo)

    def test_page4_1(self):
        x = Symbol('x')
        expr = (log(log(log(log(x))))-1)*log(x)
        self.assertEquals(expr.limit(x,oo),oo)

    def test_page4_2(self):
        x = Symbol('x')
        expr = (log(log(log(x)))-1)*x
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_page7(self): # enable it after defining erf
        x = Symbol('x')
        expr = (erf(x-exp(x-exp(-exp(x))))-erf(x))*exp(exp(x))*exp(x**2)
        self.assertEquals(expr.limit(x,0),-2/sqrt(pi))

    def test_page12_ex2_5(self):
        x = Symbol('x')
        expr = sqrt(ln(x+1))-sqrt(ln(x))
        self.assertEquals(expr.limit(x,oo),0)

    def test_page12_ex2_6(self):
        x = Symbol('x')
        s = Symbol('s')
        expr = ((1+x)**s-1)/x
        self.assertEquals(expr.limit(x,0),s)

    def test_page13_ex2_7(self):
        x = Symbol('x')
        n = Symbol('n',positive=1)
        m = Symbol('m',positive=1)
        #n,m = Integer(1),Integer(2)
        expr = (x**(1/n)-1)/(x**(1/m)-1)
        self.assertEquals(expr.limit(x,1),m/n)

    def test_page14_ex2_9(self):
        x = Symbol('x')
        n = Symbol('n')
        expr = x**n/exp(x)
        self.assertEquals(expr.limit(x,oo),0)

    def _test_page14_complicated(self):
        x = Symbol('x')
        r = Symbol('r',positive=True, bounded=True)
        R = sqrt(sqrt(x**4+2*x**2*(r**2+1)+(r**2-1)**2)+x**2+r**2-1)
        expr = x/R
        self.assertEquals(expr.limit(x,0),sqrt((1-r**2)/2))

    def test_page15_ex2_10(self):
        x = Symbol('x')
        expr = x/(x-1)-1/ln(x)
        self.assertEquals(expr.limit(x,1),Rational(1,2))

    def test_page15_ex2_11(self):
        x = Symbol('x')
        expr = x*ln(x)
        self.assertEquals(expr.limit(x,0),0)

        x = Symbol('x')
        expr = x**x
        self.assertEquals(expr.limit(x,0),1)

    def test_page16_ex2_13(self):
        x = Symbol('x')
        expr = sin(x)/x
        self.assertEquals(expr.limit(x,0),1)

    def _test_page16_ex2_14(self):  # enable it after defining erf
        x = Symbol('x')
        expr = exp(exp(phi(phi(x))))/x
        self.assertEquals(expr.limit(x,oo),exp(-Rational(1,2)))

    def test_page18_ex2_15(self):
        x = Symbol('x')
        expr = exp(exp(exp(exp(x-1/exp(x)))))/exp(exp(exp(exp(x))))
        expr = exp(exp(exp(exp(x-1/exp(x))))-exp(exp(exp(x))))
        #expr = exp(exp(exp(x-1/exp(x))))-exp(exp(exp(x)))
        self.assertEquals(expr.limit(x,oo),0)
        e = MrvExpr(expr, x)
        print e
        
    def test_page27_ex2_17(self):
        x = Symbol('x')
        expr = exp(x)*(sin(1/x+exp(-x))-sin(1/x))
        self.assertEquals(expr.limit(x,oo),1)

    def test_page43_ex3_15(self):
        x = Symbol('x')
        expr = (exp(1/x-exp(-x))-exp(1/x))/exp(-x)
        self.assertEquals(expr.limit(x,oo),-1)

    def test_page44_ex3_17(self):
        x = Symbol('x')
        expr = 1/exp(-x+exp(-x))-exp(x)
        self.assertEquals(expr.limit(x,oo),-1)

    def test_page47_ex3_21(self):
        h = exp(-x/(1+exp(-x)))
        expr = exp(h)*exp(-x/(1+h))*exp(exp(-x+h))/h**2-exp(x)+x
        #expr = exp(h-x/(1+h)+exp(-x+h)+2*x/(1+exp(-x)))-exp(x)+x
        #self.assertEquals(expr.limit(x,oo),2)
        e = MrvExpr(expr, x)
        
    def test_page47_ex3_21_1(self):
        expr = exp((-x) / (1 + exp(-x)))
        self.assertEquals(expr.limit(x,oo),0)

    def test_page51_ex3_25(self):
        expr = (ln(ln(x)+ln(ln(x)))-ln(ln(x)))/ln(ln(x)+ln(ln(ln(x))))*ln(x)
        self.assertEquals(expr.limit(x,oo),1)

        
    def test_bug_0(self):
        expr = ln(x+x**2)/ln(x) # (ln(x)+ln(1+x))/ln(x)
        self.assertEquals(expr.limit(x,0),0)
        
if __name__ == '__main__':

    job = 0
    if job==1:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("test_limit.prof")
        benchtime, stones = prof.runcall(unittest.main)
        prof.close()
    elif job==2:
        import hotshot, hotshot.stats
        #prof = hotshot.Profile("test_limit.prof")
        #benchtime, stones = prof.runcall(unittest.main)
        #prof.close()
        stats = hotshot.stats.load("test_limit.prof")
        stats.strip_dirs()
        stats.sort_stats('cumulative', 'calls')
        stats.print_stats(30)
    else:
        unittest.main()
