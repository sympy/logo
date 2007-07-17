from __init__ import *
import unittest

class AssumptionsTestCase(unittest.TestCase):

    def test_symbol_unset(self):
        x = Symbol('x',real=True, integer=True)
        self.assertEqual(x.is_real,True)
        self.assertEqual(x.is_integer,True)
        self.assertEqual(x.is_imaginary,False)
        self.assertEqual(x.is_noninteger,False)
        x.assume(real=None)
        self.assertEqual(x.is_real,None)
        self.assertEqual(x.is_integer,None)

    def test_zero(self):
        z = Integer(0)
        self.assertEqual(z.is_commutative, True)
        self.assertEqual(z.is_integer, True)
        self.assertEqual(z.is_rational, True)
        self.assertEqual(z.is_real, True)
        self.assertEqual(z.is_complex, True)
        self.assertEqual(z.is_noninteger, False)
        self.assertEqual(z.is_irrational, False)
        self.assertEqual(z.is_imaginary, False)
        self.assertEqual(z.is_noncomplex, False)
        self.assertEqual(z.is_positive, False)
        self.assertEqual(z.is_negative, False)
        self.assertEqual(z.is_nonpositive, True)
        self.assertEqual(z.is_nonnegative, True)
        self.assertEqual(z.is_even, True)
        self.assertEqual(z.is_odd, False)
        self.assertEqual(z.is_bounded, True)
        self.assertEqual(z.is_unbounded, False)
        self.assertEqual(z.is_finite, False)
        self.assertEqual(z.is_infinitesimal, True)
        self.assertEqual(z.is_comparable, True)
        #self.assertEqual(z.is_prime, False)
        #self.assertEqual(z.is_composite, True)

    def test_one(self):
        z = Integer(1)
        self.assertEqual(z.is_commutative, True)
        self.assertEqual(z.is_integer, True)
        self.assertEqual(z.is_rational, True)
        self.assertEqual(z.is_real, True)
        self.assertEqual(z.is_complex, True)
        self.assertEqual(z.is_noninteger, False)
        self.assertEqual(z.is_irrational, False)
        self.assertEqual(z.is_imaginary, False)
        self.assertEqual(z.is_noncomplex, False)
        self.assertEqual(z.is_positive, True)
        self.assertEqual(z.is_negative, False)
        self.assertEqual(z.is_nonpositive, False)
        self.assertEqual(z.is_nonnegative, True)
        self.assertEqual(z.is_even, False)
        self.assertEqual(z.is_odd, True)
        self.assertEqual(z.is_bounded, True)
        self.assertEqual(z.is_unbounded, False)
        self.assertEqual(z.is_finite, True)
        self.assertEqual(z.is_infinitesimal, False)
        self.assertEqual(z.is_comparable, True)
        #self.assertEqual(z.is_prime, True)
        #self.assertEqual(z.is_composite, False)

    def test_negativeone(self):
        z = Integer(-1)
        self.assertEqual(z.is_commutative, True)
        self.assertEqual(z.is_integer, True)
        self.assertEqual(z.is_rational, True)
        self.assertEqual(z.is_real, True)
        self.assertEqual(z.is_complex, True)
        self.assertEqual(z.is_noninteger, False)
        self.assertEqual(z.is_irrational, False)
        self.assertEqual(z.is_imaginary, False)
        self.assertEqual(z.is_noncomplex, False)
        self.assertEqual(z.is_positive, False)
        self.assertEqual(z.is_negative, True)
        self.assertEqual(z.is_nonpositive, True)
        self.assertEqual(z.is_nonnegative, False)
        self.assertEqual(z.is_even, False)
        self.assertEqual(z.is_odd, True)
        self.assertEqual(z.is_bounded, True)
        self.assertEqual(z.is_unbounded, False)
        self.assertEqual(z.is_finite, True)
        self.assertEqual(z.is_infinitesimal, False)
        self.assertEqual(z.is_comparable, True)
        #self.assertEqual(z.is_prime, True)
        #self.assertEqual(z.is_composite, False)

    def test_pos_rational(self):
        r = Rational(3,4)
        self.assertEqual(r.is_commutative, True)
        self.assertEqual(r.is_integer, False)
        self.assertEqual(r.is_rational, True)
        self.assertEqual(r.is_real, True)
        self.assertEqual(r.is_complex, True)
        self.assertEqual(r.is_noninteger, True)
        self.assertEqual(r.is_irrational, False)
        self.assertEqual(r.is_imaginary, False)
        self.assertEqual(r.is_noncomplex, False)
        self.assertEqual(r.is_positive, True)
        self.assertEqual(r.is_negative, False)
        self.assertEqual(r.is_nonpositive, False)
        self.assertEqual(r.is_nonnegative, True)
        self.assertEqual(r.is_even, None)
        self.assertEqual(r.is_odd, None)
        self.assertEqual(r.is_bounded, True)
        self.assertEqual(r.is_unbounded, False)
        self.assertEqual(r.is_finite, True)
        self.assertEqual(r.is_infinitesimal, False)
        self.assertEqual(r.is_comparable, True)
        self.assertEqual(r.is_prime, None)
        self.assertEqual(r.is_composite, None)
        
        r = Rational(1,4)
        self.assertEqual(r.is_nonpositive, False)
        self.assertEqual(r.is_positive, True)
        self.assertEqual(r.is_negative, False)
        self.assertEqual(r.is_nonnegative, True)
        r = Rational(5,4)
        self.assertEqual(r.is_negative, False)
        self.assertEqual(r.is_positive, True)
        self.assertEqual(r.is_nonpositive, False)
        self.assertEqual(r.is_nonnegative, True)
        r = Rational(5,3)
        self.assertEqual(r.is_nonnegative, True)
        self.assertEqual(r.is_positive, True)
        self.assertEqual(r.is_negative, False)
        self.assertEqual(r.is_nonpositive, False)

    def test_neg_rational(self):
        r = Rational(-3,4)
        self.assertEqual(r.is_positive, not True)
        self.assertEqual(r.is_nonpositive, not False)
        self.assertEqual(r.is_negative, not False)
        self.assertEqual(r.is_nonnegative, not True)
        r = Rational(-1,4)
        self.assertEqual(r.is_nonpositive, not False)
        self.assertEqual(r.is_positive, not True)
        self.assertEqual(r.is_negative, not False)
        self.assertEqual(r.is_nonnegative, not True)
        r = Rational(-5,4)
        self.assertEqual(r.is_negative, not False)
        self.assertEqual(r.is_positive, not True)
        self.assertEqual(r.is_nonpositive, not False)
        self.assertEqual(r.is_nonnegative, not True)
        r = Rational(-5,3)
        self.assertEqual(r.is_nonnegative, not True)
        self.assertEqual(r.is_positive, not True)
        self.assertEqual(r.is_negative, not False)
        self.assertEqual(r.is_nonpositive, not False)

    def test_pi(self):
        z = Pi
        self.assertEqual(z.is_commutative, True)
        self.assertEqual(z.is_integer, None)
        self.assertEqual(z.is_rational, False)
        self.assertEqual(z.is_real, True)
        self.assertEqual(z.is_complex, True)
        self.assertEqual(z.is_noninteger, None)
        self.assertEqual(z.is_irrational, True)
        self.assertEqual(z.is_imaginary, False)
        self.assertEqual(z.is_noncomplex, False)
        self.assertEqual(z.is_positive, True)
        self.assertEqual(z.is_negative, False)
        self.assertEqual(z.is_nonpositive, False)
        self.assertEqual(z.is_nonnegative, True)
        self.assertEqual(z.is_even, None)
        self.assertEqual(z.is_odd, None)
        self.assertEqual(z.is_bounded, True)
        self.assertEqual(z.is_unbounded, False)
        self.assertEqual(z.is_finite, True)
        self.assertEqual(z.is_infinitesimal, False)
        self.assertEqual(z.is_comparable, True)
        self.assertEqual(z.is_prime, None)
        self.assertEqual(z.is_composite, None)

    def test_E(self):
        z = E
        self.assertEqual(z.is_commutative, True)
        self.assertEqual(z.is_integer, None)
        self.assertEqual(z.is_rational, False)
        self.assertEqual(z.is_real, True)
        self.assertEqual(z.is_complex, True)
        self.assertEqual(z.is_noninteger, None)
        self.assertEqual(z.is_irrational, True)
        self.assertEqual(z.is_imaginary, False)
        self.assertEqual(z.is_noncomplex, False)
        self.assertEqual(z.is_positive, True)
        self.assertEqual(z.is_negative, False)
        self.assertEqual(z.is_nonpositive, False)
        self.assertEqual(z.is_nonnegative, True)
        self.assertEqual(z.is_even, None)
        self.assertEqual(z.is_odd, None)
        self.assertEqual(z.is_bounded, True)
        self.assertEqual(z.is_unbounded, False)
        self.assertEqual(z.is_finite, True)
        self.assertEqual(z.is_infinitesimal, False)
        self.assertEqual(z.is_comparable, True)
        self.assertEqual(z.is_prime, None)
        self.assertEqual(z.is_composite, None)

    def test_I(self):
        z = I
        self.assertEqual(z.is_commutative, True)
        self.assertEqual(z.is_integer, None)
        self.assertEqual(z.is_rational, None)
        self.assertEqual(z.is_real, False)
        self.assertEqual(z.is_complex, True)
        self.assertEqual(z.is_noninteger, None)
        self.assertEqual(z.is_irrational, None)
        self.assertEqual(z.is_imaginary, True)
        self.assertEqual(z.is_noncomplex, False)
        self.assertEqual(z.is_positive, None)
        self.assertEqual(z.is_negative, None)
        self.assertEqual(z.is_nonpositive, None)
        self.assertEqual(z.is_nonnegative, None)
        self.assertEqual(z.is_even, None)
        self.assertEqual(z.is_odd, None)
        self.assertEqual(z.is_bounded, True)
        self.assertEqual(z.is_unbounded, False)
        self.assertEqual(z.is_finite, True)
        self.assertEqual(z.is_infinitesimal, False)
        self.assertEqual(z.is_comparable, None)
        self.assertEqual(z.is_prime, None)
        self.assertEqual(z.is_composite, None)

    def test_symbol_positive(self):
        x = Basic.Symbol('x',positive=True)
        self.assertEqual(x.is_positive, True)
        self.assertEqual(x.is_nonpositive, False)
        self.assertEqual(x.is_negative, False)
        self.assertEqual(x.is_nonnegative, True)

    def test_neg_symbol_positive(self):
        x = -Basic.Symbol('x',positive=True)
        self.assertEqual(x.is_positive, False)
        self.assertEqual(x.is_nonpositive, True)
        self.assertEqual(x.is_negative, True)
        self.assertEqual(x.is_nonnegative, False)

    def test_symbol_nonpositive(self):
        x = Basic.Symbol('x',nonpositive=True)
        self.assertEqual(x.is_positive, False)
        self.assertEqual(x.is_nonpositive, True)
        self.assertEqual(x.is_negative, None)
        self.assertEqual(x.is_nonnegative, None)

    def test_neg_symbol_nonpositive(self):
        x = -Basic.Symbol('x',nonpositive=True)
        self.assertEqual(x.is_positive, None)
        self.assertEqual(x.is_nonpositive, None)
        self.assertEqual(x.is_negative, False)
        self.assertEqual(x.is_nonnegative, True)



if __name__ == '__main__':
    unittest.main()