import unittest
import sys
from PyQt5.QtWidgets import QApplication

from view import create_label, create_button, create_input


class TestViewHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_create_label(self):
        lbl = create_label('Hello', 12, True)
        self.assertEqual(lbl.text(), 'Hello')

    def test_create_button_and_input(self):
        btn = create_button('Click', 'primary')
        self.assertEqual(btn.text(), 'Click')
        inp = create_input('Enter', is_password=False)
        self.assertEqual(inp.placeholderText(), 'Enter')


if __name__ == '__main__':
    unittest.main()
