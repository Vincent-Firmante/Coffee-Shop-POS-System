import unittest


class TestMainImport(unittest.TestCase):
    def test_import_main_module(self):
        import importlib
        m = importlib.import_module('main')
        self.assertIsNotNone(m)


if __name__ == '__main__':
    unittest.main()
