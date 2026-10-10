import unittest
from features.calculator import safe_evaluate

class TestCalculator(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(safe_evaluate("25 plus 50"), 75)

    def test_subtraction(self):
        self.assertEqual(safe_evaluate("50 minus 17"), 33)

    def test_multiplication(self):
        self.assertEqual(safe_evaluate("12 multiplied by 8"), 96)
        self.assertEqual(safe_evaluate("12 times 8"), 96)

    def test_division(self):
        self.assertEqual(safe_evaluate("100 divided by 4"), 25)

    def test_complex_expression(self):
        self.assertEqual(safe_evaluate("10 plus 5 times 2"), 20)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            safe_evaluate("10 divided by 0")

    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            safe_evaluate("hello world")

if __name__ == "__main__":
    unittest.main()
