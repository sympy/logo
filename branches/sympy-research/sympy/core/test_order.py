from __init__ import *
import unittest

x = Symbol('x')
y = Symbol('y')
z = Basic.Zero()
o = Basic.One()


class OrderTestCase(unittest.TestCase):

    def test_simple_1(self):
        self.assertEquals(Order(2*x),Order(x))
        self.assertEquals(Order(x)*3,Order(x))
        self.assertEquals(-28*Order(x),Order(x))

    def test_simple_2(self):
        self.assertEquals(Order(2*x)*x,Order(x**2))
        self.assertEquals(Order(2*x)/x,Order(1))

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
        self.assertEquals(Order(x)+Order(1),Order(1))
        self.assertEquals(Order(1/x)+Order(1),Order(1/x))
        self.assertEquals(Order(x)+Order(exp(1/x)),Order(exp(1/x)))
        self.assertEquals(Order(x**3)+Order(exp(2/x)),Order(exp(2/x)))
        self.assertEquals(Order(x**-3)+Order(exp(2/x)),Order(exp(2/x)))

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

    def test_multivar_1(self):
        self.assertEquals(Order(x+y).expr,x+y)
        self.assertEquals(Order(x+2*y).expr,x+y)
        self.assertEquals(Order(x+y)+x,Order(x+y))
        self.assertEquals((Order(x+y)+x**2),Order(x+y))
        self.assertEquals((Order(x+y)+1/x),1/x+Order(x+y))

if __name__ == '__main__':
    unittest.main()
