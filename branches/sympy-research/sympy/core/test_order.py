from __init__ import *
import unittest

x = Symbol('x')
y = Symbol('y')
z = Symbol('z')
zero = Basic.Zero()
o = Basic.One()


class OrderTestCase(unittest.TestCase):

    def test_simple_1(self):
        self.assertEquals(Order(2*x),Order(x))
        self.assertEquals(Order(x)*3,Order(x))
        self.assertEquals(-28*Order(x),Order(x))
        self.assertEquals(Order(-23),Order(1))
        self.assertEquals(Order(exp(x)),Order(1,x))
        self.assertEquals(Order(exp(1/x)).expr,exp(1/x))
        self.assertEquals(Order(x*exp(1/x)).expr,x*exp(1/x))
        self.assertEquals(Order(x**(o/3)).expr,x**(o/3))
        self.assertEquals(Order(x**(5*o/3)).expr,x**(5*o/3))

    def test_simple_2(self):
        self.assertEquals(Order(2*x)*x,Order(x**2))
        self.assertEquals(Order(2*x)/x,Order(1,x))
        self.assertEquals(Order(2*x)*x*exp(1/x),Order(x**2*exp(1/x)))
        self.assertEquals((Order(2*x)*x*exp(1/x)/ln(x)**3).expr,x**2*exp(1/x)*ln(x)**-3)

    def test_simple_3(self):
        self.assertEquals(Order(x)+x,Order(x))
        self.assertEquals(Order(x)+2,2+Order(x))
        self.assertEquals(Order(x)+x**2,Order(x))
        self.assertEquals(Order(x)+1/x,1/x+Order(x))
        self.assertEquals(Order(1/x)+1/x**2,1/x**2+Order(1/x))
        self.assertEquals(Order(x)+exp(1/x),Order(x)+exp(1/x))
        
    def test_simple_4(self):
        self.assertEquals(Order(x)**2,Order(x**2))
        self.assertEquals(Order(x**3)**-2,Order(x**-6))

    def test_simple_5(self):
        self.assertEquals(Order(x)+Order(x**2),Order(x))
        self.assertEquals(Order(x)+Order(x**-2),Order(x**-2))
        self.assertEquals(Order(x)+Order(1/x),Order(1/x))

    def test_simple_6(self):
        self.assertEquals(Order(x)-Order(x),Order(x))
        self.assertEquals(Order(x)+Order(1),Order(1))
        self.assertEquals(Order(x)+Order(x**2),Order(x))
        self.assertEquals(Order(1/x)+Order(1),Order(1/x))
        self.assertEquals(Order(x)+Order(exp(1/x)),Order(exp(1/x)))
        self.assertEquals(Order(x**3)+Order(exp(2/x)),Order(exp(2/x)))
        self.assertEquals(Order(x**-3)+Order(exp(2/x)),Order(exp(2/x)))

    def test_contains_0(self):
        self.assertTrue(Order(1,x).contains(Order(1,x)))
        self.assertTrue(Order(1,x).contains(Order(1)))
        self.assertTrue(Order(1).contains(Order(1,x)))

    def test_contains_1(self):
        self.assertTrue(Order(x).contains(Order(x)))
        self.assertTrue(Order(x).contains(Order(x**2)))
        self.assertFalse(Order(x**2).contains(Order(x)))
        self.assertFalse(Order(x).contains(Order(1/x)))
        self.assertFalse(Order(1/x).contains(Order(exp(1/x))))
        self.assertFalse(Order(x).contains(Order(exp(1/x))))
        self.assertTrue(Order(1/x).contains(Order(x)))
        self.assertTrue(Order(exp(1/x)).contains(Order(x)))
        self.assertTrue(Order(exp(1/x)).contains(Order(1/x)))
        self.assertTrue(Order(exp(1/x)).contains(Order(exp(1/x))))
        self.assertTrue(Order(exp(2/x)).contains(Order(exp(1/x))))
        self.assertFalse(Order(exp(1/x)).contains(Order(exp(2/x))))

    def test_contains_2(self):
        self.assertTrue(Order(x).contains(Order(y)) is None)
        self.assertTrue(Order(x).contains(Order(y*x)))
        self.assertTrue(Order(y*x).contains(Order(x)))
        self.assertTrue(Order(y).contains(Order(x*y)))
        self.assertTrue(Order(x).contains(Order(y**2*x)))

    def test_contains_3(self):
        self.assertTrue(Order(x*y**2).contains(Order(x**2*y)) is None)
        self.assertTrue(Order(x**2*y).contains(Order(x*y**2)) is None)

    def test_add_1(self):
        self.assertEquals(Order(x+x), Order(x))
        self.assertEquals(Order(3*x-2*x**2), Order(x))
        self.assertEquals(Order(1+x), Order(1,x))
        self.assertEquals(Order(1+1/x), Order(1/x))
        self.assertEquals(Order(ln(x)+1/ln(x)), Order(ln(x)))
        self.assertEquals(Order(exp(1/x)+x), Order(exp(1/x)))
        self.assertEquals(Order(exp(1/x)+1/x**20), Order(exp(1/x)))

    def test_ln_args(self):
        self.assertEquals(Order(ln(2*x)).expr,ln(x)) # ln(2*x) -> ln(2)+ln(x)
        self.assertEquals(Order(ln(y*x)).expr,ln(x)+ln(y)) # ln(x*y) -> ln(x)+ln(y)
        self.assertEquals(Order(ln(x**3)).expr,ln(x)) # ln(x**3) -> 3*ln(x)
        self.assertEquals(Order(ln(2*x)).expr,ln(x)) # ln(2*x) -> ln(2)+ln(x)

    def test_multivar_0(self):
        self.assertEquals(Order(x*y).expr,x*y)
        self.assertEquals(Order(x*y**2).expr,x*y**2)
        self.assertEquals(Order(x*y,x).expr,x)
        self.assertEquals(Order(x*y**2,y).expr,y**2)
        self.assertEquals(Order(x*y*z).expr,x*y*z)
        self.assertEquals(Order(x/y).expr,x/y)
        self.assertEquals(Order(x*exp(1/y)).expr,x*exp(1/y))
        self.assertEquals(Order(exp(1/x)*exp(1/y)).expr,exp(1/x)*exp(1/y))
        self.assertEquals(Order(exp(x)*exp(1/y)).expr,exp(1/y))

    def test_multivar_1(self):
        self.assertEquals(Order(x+y).expr,x+y)
        self.assertEquals(Order(x+2*y).expr,x+y)
        self.assertEquals((Order(x+y)+x).expr,(x+y))
        self.assertEquals((Order(x+y)+x**2),Order(x+y))
        self.assertEquals((Order(x+y)+1/x),1/x+Order(x+y))
        self.assertEquals(Order(x**2+y*x).expr,x**2+y*x)
        
    def test_multivar_2(self):
        self.assertEquals(Order(x**2*y+y**2*x,x,y).expr,x**2*y+y**2*x)

    def test_multivar_mul_1(self):
        self.assertEquals(Order(x+y)*x,Order(x**2+y*x,x,y))

    def test_multivar_3(self):
        self.assertEquals((Order(x)+Order(y))[:],(Order(x),Order(y)))
        self.assertEquals(Order(x)+Order(y)+Order(x+y),Order(x+y))
        self.assertEquals((Order(x**2*y)+Order(y**2*x))[:],(Order(x*y**2),Order(y*x**2)))
        self.assertEquals((Order(x**2*y)+Order(y*x)),Order(x*y))
    
    def test_w(self):
        print
        for k,v in Order._cache.items():
            if isinstance(k, Basic.Symbol):
                print k,v

if __name__ == '__main__':

    job = 0
    if job==1:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("test_order.prof")
        benchtime, stones = prof.runcall(unittest.main)
        prof.close()
    elif job==2:
        import hotshot, hotshot.stats
        stats = hotshot.stats.load("test_order.prof")
        stats.strip_dirs()
        stats.sort_stats('cumulative', 'calls')
        stats.print_stats(30)
    else:
        unittest.main()


