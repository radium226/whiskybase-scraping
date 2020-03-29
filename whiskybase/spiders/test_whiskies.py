import unittest

from whiskybase.spiders import extract_currency

class TestExtract(unittest.TestCase):

    def test_currency(self):
        self.assertTrue(extract_currency("€ 9,837") == "€")
        self.assertTrue(extract_currency("9,837 €") == "€")

if __name__ == '__main__':
    unittest.main()
