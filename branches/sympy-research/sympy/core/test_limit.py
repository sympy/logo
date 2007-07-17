
from __init__ import *
from limit import mrv_compare, mrv2
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

class _MrvTestCase:#(unittest.TestCase):

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
        expr = (x**(1/n)-1)/(x**(1/m)-1)
        self.assertEquals(expr.limit(x,1),m/n)

    def test_page14_ex2_9(self):
        x = Symbol('x')
        n = Symbol('n')
        expr = x**n/exp(x)
        self.assertEquals(expr.limit(x,oo),0)

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
        #x = Symbol('x')
        expr = exp(exp(exp(exp(x-1/exp(x)))))/exp(exp(exp(exp(x))))
        expr = exp(exp(exp(exp(x-1/exp(x))))-exp(exp(exp(x))))
        #expr = exp(exp(exp(x-1/exp(x))))-exp(exp(exp(x)))
        self.assertEquals(expr.limit(x,oo),0)
        #e = MrvExpr(expr, x)
        #print e
        
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
        self.assertEquals(expr.limit(x,oo),2)
        
    def test_page47_ex3_21_1(self):
        expr = exp((-x) / (1 + exp(-x)))
        self.assertEquals(expr.limit(x,oo),0)

    def test_page51_ex3_25(self):
        expr = (ln(ln(x)+ln(ln(x)))-ln(ln(x)))/ln(ln(x)+ln(ln(ln(x))))*ln(x)
        self.assertEquals(expr.limit(x,oo),1)

    def test_bug_0(self):
        expr = ln(x+x**2)/ln(x) # (ln(x)+ln(1+x))/ln(x)
        self.assertEquals(expr.limit(x,0),0)

    def test_page77_ex5_2(self):
        expr = exp(sin(1/x+exp(-x))-sin(1/x))
        self.assertEquals(expr.limit(x,oo),1)

class MrvLimitTestCaseWorkInProgress(unittest.TestCase):

    def _test_page7(self): # enable it after defining erf
        x = Symbol('x')
        expr = (erf(x-exp(x-exp(-exp(x))))-erf(x))*exp(exp(x))*exp(x**2)
        self.assertEquals(expr.limit(x,0),-2/sqrt(pi))

    def _test_page14_complicated(self): # returns incorrect result 0
        x = Symbol('x')
        r = Symbol('r',positive=True, bounded=True)
        R = sqrt(sqrt(x**4+2*x**2*(r**2+1)+(r**2-1)**2)+x**2+r**2-1)
        expr = x/R
        self.assertEquals(expr.limit(x,0),sqrt((1-r**2)/2))

    def _test_page60_sec3_5(self): # produces incorrect limit oo
        expr = ln(ln(x*exp(x*exp(x))+1))-exp(exp(ln(ln(x))+1/x))
        self.assertEquals(expr.limit(x,oo),0)

    def _test_page78_ex5_3(self): # enable after defining csc, cot functions
        x = Symbol('x')
        expr = exp(csc(x))/exp(cot(x))
        self.assertEquals(expr.limit(x,0),1)

    def _test_page86(self): # need interval calculus
        expr = exp(-x)/cos(x)
        self.assertEquals(expr.limit(x,oo),nan)

    def _test_page97(self): # fails with infinite recursion
        expr = (3**x+5**x)**(1/x)
        self.assertEquals(expr.limit(x,oo),5)

    def _test_page107(self): # returns incorrect result 0
        w = Symbol('w')
        expr = w/(sqrt(1+w)*sin(x)**2+sqrt(1-w)*cos(x)**2-1)
        self.assertEquals(expr.limit(w,0),2/(1-2*cos(x)**2))

    def _test_page108(self): # returns incorrect result 0
        w = exp(-x)
        expr = w/(sqrt(1+w)*sin(1/x)**2+sqrt(1-w)*cos(1/x)**2-1)
        self.assertEquals(expr.limit(x,oo),-2)

    def _test_page111(self): # returns incorrect result 0
        expr = ln(1-(ln(exp(x)/x-1)+ln(x))/x)/x
        self.assertEquals(expr.limit(x,oo),-1)

    def _test_page112(self): # need branch cut support
        x = Symbol('x')
        expr = ln(-1+x*I)
        self.assertEquals(expr.limit(x,0),pi*I)
        expr = ln(-1-x*I)
        self.assertEquals(expr.limit(x,0),-pi*I)

    def _test_page114(self): # returns incorrect result -1, need csgn
        expr = 1/(x*(1+(1/x-1)**(1/x-1)))
        self.assertEquals(expr.limit(x,oo),-1/(I*pi+1))

    def _test_page116(self): # returns incorrect?? result -oo
        expr = ln(x*(x+1)/ln(exp(x)+exp(ln(x)**2)*exp(x**2))+1/ln(x))
        self.assertEquals(expr.limit(x,oo),0)

class MrvLimitTestCaseComparison(unittest.TestCase):

    # page 122-..
    def _test_8_1(self): # ok
        expr = exp(x)*(exp(1/x-exp(-x))-exp(1/x))
        self.assertEquals(expr.limit(x,oo),-1)

    def _test_8_2(self): # returns incorrect result -oo
        expr = exp(x)*(exp(1/x+exp(-x)+exp(-x**2))-exp(1/x-exp(-exp(x))))
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_3(self): # fails with assertion error
        expr = exp(exp(x-exp(-x))/(1-1/x))-exp(exp(x))
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_8_4(self): # runs forever
        expr = exp(exp(exp(x)/(1-1/x)))-exp(exp(exp(x)/(1-1/x-ln(x)**(-ln(x)))))
        self.assertEquals(expr.limit(x,oo),-oo)

    def _test_8_5(self): # fails with value error
        expr = exp(exp(exp(x+exp(-x))))/exp(exp(exp(x)))
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_8_6(self): # returns incorrect result 1
        expr = exp(exp(exp(x)))/exp(exp(exp(x-exp(-exp(x)))))
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_8_7(self): # fails with infinite recursion
        expr = exp(exp(exp(x)))/exp(exp(exp(x-exp(-exp(exp(x))))))
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_8(self): # fails with infinite recursion
        expr = exp(exp(x))/exp(exp(x-exp(-exp(exp(x)))))
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_9(self): # returns incorrect result oo
        expr = ln(x)**2 * exp(sqrt(ln(x))*(ln(ln(x)))**2*exp(sqrt(ln(ln(x)))*ln(ln(ln(x)))**3)) / sqrt(x)
        self.assertEquals(expr.limit(x,oo),0)

    def _test_8_10(self): # returns incorrect result 0
        expr = (x*ln(x)*(ln(x*exp(x)-x**2))**2)/ln(ln(x**2+2*exp(exp(3*x**3*ln(x)))))
        self.assertEquals(expr.limit(x,oo),Rational(1,3))

    def _test_8_11(self): # returns incorrect result -oo
        expr = (exp(x*exp(-x)/(exp(-x)+exp(-2*x**2/(1+x))))-exp(x))/x
        self.assertEquals(expr.limit(x,oo),-exp(2))

    def _test_8_12(self): # fails with infinite recursion
        expr = (3**x+5**x)**(1/x)
        self.assertEquals(expr.limit(x,oo),5)

    def _test_8_13(self): # ok
        expr = x/ln(x**(ln(x**(ln(2)/ln(x)))))
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_8_14(self): # fails with infinite recursion
        expr = exp(exp(2*ln(x**5+x)*ln(ln(x))))/exp(exp(10*ln(x)*ln(ln(x))))
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_8_15(self): # ok
        expr = 4 * exp(exp(5*x**(-Rational(5,7))/2+21*x**(Rational(6,11))/8+2*x**-8+54*x**(Rational(49,45))/17))**8 \
               / ln(ln(-ln(4*x**(-Rational(5,14))/3))) ** Rational(7,6) / 9
        self.assertEquals(expr.limit(x,oo),oo)

    def _test_8_16(self): # ok
        expr = (exp(4*x*exp(-x)/(1/exp(x)+1/exp(2*x**2/(x+1))))-exp(x))/exp(x)**4
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_17(self): # fails with infinite recursion
        expr = exp(x*exp(-x)/(exp(-x)+exp(-2*x**2/(x+1))))/exp(x)
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_18(self): # ok
        expr = exp(exp(-x/(1+exp(-x))))*exp(-x/(1+exp(-x/(1+exp(-x))))) * exp(exp(-x+exp(-x/(1+exp(-x))))) / exp(-x/(1+exp(-x)))**2 - exp(x) + x
        self.assertEquals(expr.limit(x,oo),2)

    def _test_8_19(self): # ok
        expr = (ln(ln(x)+ln(ln(x)))-ln(ln(x)))/ln(ln(x)+ln(ln(ln(x))))*ln(x)
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_20(self): # returns incorrect result 1
        expr = exp(ln(ln(x+exp(ln(x)*ln(ln(x)))))/ln(ln(ln(exp(x)+x+ln(x)))))
        self.assertEquals(expr.limit(x,oo),exp(1))

    def _test_8_21(self): # fails with assertion error
        expr = exp(x)*(sin(1/x+exp(-x))-sin(1/x+exp(-x**2)))
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_22(self): # ok
        expr = exp(exp(x))*(exp(sin(1/x+exp(-exp(x))))-exp(sin(1/x)))
        self.assertEquals(expr.limit(x,oo),1)

    def _test_8_23(self): # need erf
        expr = (erf(x-exp(-exp(x)))-erf(x))*exp(exp(x))*exp(x**2)
        self.assertEquals(expr.limit(x,oo),-2/sqrt(pi))

    # ...

    def _test_8_37(self): # need to finish max_,min_ implementations to handle unbounded args
        expr = max_(x, exp(x))/ln(min_(exp(-x),exp(-exp(x))))
        self.assertEquals(expr.limit(x,oo),1)
        
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
        stats.print_stats(50)
    else:
        unittest.main()
