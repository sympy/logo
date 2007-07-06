from __init__ import *
import unittest

x = Symbol('x')
y = Symbol('y')
z = Symbol('z')
zero = Basic.Zero()
o = Basic.One()


class OSeriesTestCase(unittest.TestCase):

    def test_simple_1(self):
        self.assertEqual(x.oseries(x),0)
        self.assertEqual(x.oseries(1/x),0)
        self.assertEqual(x.oseries(x**2),x)
        self.assertEqual(y.oseries(x),y)
        self.assertEqual(y.oseries(1/x),0)
        self.assertEqual((Rational(3,4)).oseries(x),Rational(3,4))
        self.assertEqual((Rational(3,4)).oseries(1/x),0)

    def test_mul_0(self):
        self.assertEqual((x*ln(x)).oseries(x**5),x*ln(x))
        self.assertEqual((x*ln(x)).oseries(x),x*ln(x))
        self.assertEqual((x*ln(x)).oseries(x*ln(x)),0)
        self.assertEqual((x*ln(x)).oseries(ln(x)),0)
        self.assertEqual((x*ln(x)).oseries(x**2*ln(x)),x*ln(x))
        self.assertEqual((x*ln(x)).oseries(1/x),0)

    def test_mul_1(self):
        self.assertEqual((x*ln(2+x)).oseries(x**5),x**2/2-x**3/8+x**4/24+x*log(2))
        self.assertEqual((x*ln(1+x)).oseries(x**5),x**2-x**3/2+x**4/3)

    def test_pow_0(self):
        self.assertEqual((x**2).oseries(x**5),x**2)
        self.assertEqual((x**2).oseries(x),0)
        self.assertEqual((1/x).oseries(x),1/x)
        self.assertEqual((x**(Rational(2,3))).oseries(x),(x**(Rational(2,3))))
        self.assertEqual((x**(Rational(3,2))).oseries(x),0)

    def test_pow_1(self):
        self.assertEqual(((1+x)**2).oseries(x**5),1+2*x+x**2)
        self.assertEqual(((1+x)**2).oseries(x**2),1+2*x)
        self.assertEqual(((1+x)**2).oseries(x),1)
        self.assertEqual(((1+x)**2).oseries(1/x),0)

    def test_geometric_1(self):
        self.assertEqual((1/(1-x)).oseries(x**5),1+x+x**2+x**3+x**4)
        self.assertEqual((x/(1-x)).oseries(x**5),x+x**2+x**3+x**4)
        self.assertEqual((x**3/(1-x)).oseries(x**5),x**3+x**4)

    def test_sqrt_1(self):
        self.assertEqual(sqrt(1+x).oseries(x**5),1+x/2-5*x**4/128-x**2/8+x**3/16)

    def test_exp_1(self):
        self.assertEqual(exp(x).oseries(x**5),1+x+x**2/2+x**3/6+x**4/24)
        self.assertEqual(exp(1/x).oseries(x**5),exp(1/x))
        self.assertEqual(exp(1/(1+x)).oseries(x**4),E*(1-x-13*x**3/6+3*x**2/2))
        self.assertEqual(exp(2+x).oseries(x**5),exp(2)*(1+x+x**2/2+x**3/6+x**4/24))

    def test_exp_sqrt_1(self):
        self.assertEqual(exp(1+sqrt(x)).oseries(x**2),exp(1)*(1+sqrt(x)+x/2+sqrt(x)*x/6))

    def test_power_x_x(self):
        self.assertEqual((exp(x*ln(x))).oseries(x**3),1+x*log(x)+x**2*log(x)**2/2+x**3*log(x)**3/6)
        self.assertEqual((x**x).oseries(x),1+x*ln(x))

if __name__ == '__main__':

    job = 0
    if job==1:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("test_oseries.prof")
        benchtime, stones = prof.runcall(unittest.main)
        prof.close()
    elif job==2:
        import hotshot, hotshot.stats
        stats = hotshot.stats.load("test_oseries.prof")
        stats.strip_dirs()
        stats.sort_stats('cumulative', 'calls')
        stats.print_stats(30)
    else:
        unittest.main()


