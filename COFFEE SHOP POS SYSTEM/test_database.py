import unittest
from database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(':memory:')

    def test_create_and_read_menu_item(self):
        ok = self.db.create_menu_item('TestItem', 12.5, 10, 'TestCat')
        self.assertTrue(ok)
        items = self.db.read_menu_items()
        self.assertTrue(any(i[1] == 'TestItem' for i in items))

    def test_get_item_details_and_stock_update(self):
        self.db.create_menu_item('StockItem', 20.0, 5, 'Food')
        items = self.db.read_menu_items()
        found = [i for i in items if i[1] == 'StockItem']
        self.assertTrue(found)
        item_id = found[0][0]
        details = self.db.get_item_details(item_id)
        self.assertEqual(details[0], 'StockItem')

    def test_user_crud(self):
        ok = self.db.create_user('tuser', 'tpass', 'Cashier')
        self.assertTrue(ok)
        u = self.db.get_user('tuser')
        self.assertIsNotNone(u)
        self.assertEqual(u['username'], 'tuser')
        users = self.db.list_users()
        self.assertTrue(any(x['username'] == 'tuser' for x in users))
        ok2 = self.db.update_user_password('tuser', 'newpass')
        self.assertTrue(ok2)
        u2 = self.db.get_user('tuser')
        self.assertEqual(u2['password'], 'newpass')
        ok3 = self.db.delete_user('tuser')
        self.assertTrue(ok3)

    def test_record_sale_and_receipt(self):
        self.db.create_menu_item('SaleItem', 30.0, 3, 'Food')
        items = self.db.read_menu_items()
        item = [i for i in items if i[1] == 'SaleItem'][0]
        item_id = item[0]
        before_items = self.db.read_menu_items()
        before_row = [i for i in before_items if i[1] == 'SaleItem'][0]
        before_stock = before_row[3]
        details = self.db.get_item_details(item_id)
        order_items = [{'name': details[0], 'qty': 2, 'price': details[1], 'category': details[2]}]
        ok = self.db.record_sale(order_items, '2025-01-01 10:00:00')
        self.assertTrue(ok)
        after_items = self.db.read_menu_items()
        after_row = [i for i in after_items if i[1] == 'SaleItem'][0]
        after_stock = after_row[3]
        self.assertEqual(after_stock, before_stock - 2)

    def test_receipt_save_get_delete(self):
        items = [{'name': 'A', 'qty': 1, 'price': 10.0, 'category': 'X'}]
        rid = 'test-rid-123'
        rowid = self.db.save_receipt(rid, '2025-01-01 10:00:00', 10.0, items)
        self.assertIsNotNone(rowid)
        r = self.db.get_receipt(rid)
        self.assertIsNotNone(r)
        self.assertEqual(r['receipt_uuid'], rid)
        ok = self.db.delete_receipt(rid)
        self.assertTrue(ok)

    def test_eod_and_archives(self):
        summary = {'date': '2025-01-01', 'total_revenue': 0.0, 'top_items': [], 'low_stock': []}
        ok = self.db.save_eod_summary(summary)
        self.assertIn(ok, (True, False))
        records = self.db.get_past_eod_records()
        self.assertIsInstance(records, list)
        ok2 = self.db.clear_all_sales_data()
        self.assertIn(ok2, (True, False))


if __name__ == '__main__':
    unittest.main()
