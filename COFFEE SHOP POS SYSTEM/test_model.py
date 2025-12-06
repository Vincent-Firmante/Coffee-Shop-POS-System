import unittest
from model import AppModel
from database import DatabaseManager


class TestAppModel(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(':memory:')
        self.model = AppModel()
        self.model.db = self.db

    def test_authenticate_and_roles(self):
        ok = self.model.authenticate('manager', 'admin123')
        self.assertTrue(ok)
        self.assertEqual(self.model.user_role, 'Manager')

    def test_password_update(self):
        self.db.create_user('u1', 'old', 'Cashier')
        res = self.model.update_password('u1', 'wrong', 'new')
        self.assertEqual(res, 'Incorrect old password')
        res2 = self.model.update_password('u1', 'old', 'old')
        self.assertEqual(res2, 'New password cannot be the same as old password')
        res3 = self.model.update_password('u1', 'old', 'new')
        self.assertEqual(res3, 'Success')

    def test_order_flow(self):
        self.db.create_menu_item('MOCK', 10.0, 10, 'Test')
        items = self.db.read_menu_items()
        item = [i for i in items if i[1] == 'MOCK'][0]
        item_id = item[0]
        ok, msg = self.model.add_item_to_order(item_id)
        self.assertTrue(ok)
        total = self.model.calculate_order_total()
        self.assertAlmostEqual(total, 10.0)
        success, total_val, receipt = self.model.process_order()
        self.assertTrue(success)
        self.assertAlmostEqual(total_val, 10.0)
        self.assertTrue(self.model.current_order == {})


if __name__ == '__main__':
    unittest.main()
