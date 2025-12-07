import unittest
import datetime
from unittest.mock import Mock, patch, MagicMock
from model import AppModel


class TestAppModelInitialization(unittest.TestCase):

    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_model_initialization(self):
       
        model = AppModel()
        self.assertIsNone(model.user_role)
        self.assertEqual(model.current_order, {})
        self.assertEqual(model.current_pos_date, datetime.date.today())


class TestAuthentication(unittest.TestCase):
    
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_authenticate_success(self):
        self.model.db.get_user.return_value = {
            'username': 'manager',
            'password': 'admin123',
            'role': 'Manager'
        }
        
        result = self.model.authenticate('manager', 'admin123')
        
        self.assertTrue(result)
        self.assertEqual(self.model.user_role, 'Manager')

    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        self.model.db.get_user.return_value = {
            'username': 'manager',
            'password': 'admin123',
            'role': 'Manager'
        }
        
        result = self.model.authenticate('manager', 'wrongpass')
        
        self.assertFalse(result)
        self.assertIsNone(self.model.user_role)

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user."""
        self.model.db.get_user.return_value = None
        
        result = self.model.authenticate('nonexistent', 'password')
        
        self.assertFalse(result)
        self.assertIsNone(self.model.user_role)

    def test_authenticate_cashier_role(self):
        """Test authentication sets cashier role."""
        self.model.db.get_user.return_value = {
            'username': 'cashier',
            'password': 'cashier123',
            'role': 'Cashier'
        }
        
        result = self.model.authenticate('cashier', 'cashier123')
        
        self.assertTrue(result)
        self.assertEqual(self.model.user_role, 'Cashier')

    def test_authenticate_username_case_insensitive(self):
        """Test that username is case-insensitive."""
        self.model.db.get_user.return_value = {
            'username': 'manager',
            'password': 'admin123',
            'role': 'Manager'
        }
        
        result = self.model.authenticate('MANAGER', 'admin123')
        
        self.assertTrue(result)
        self.model.db.get_user.assert_called_with('manager')

    def test_authenticate_whitespace_stripped(self):
        """Test that whitespace is stripped."""
        self.model.db.get_user.return_value = {
            'username': 'manager',
            'password': 'admin123',
            'role': 'Manager'
        }
        
        result = self.model.authenticate('  manager  ', '  admin123  ')
        
        self.assertTrue(result)


class TestPasswordManagement(unittest.TestCase):
    """Test password update functionality."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_update_password_success(self):
        """Test successful password update."""
        self.model.db.get_user.return_value = {
            'username': 'user1',
            'password': 'oldpass',
            'role': 'Cashier'
        }
        self.model.db.update_user_password.return_value = True
        
        result = self.model.update_password('user1', 'oldpass', 'newpass')
        
        self.assertEqual(result, 'Success')
        self.model.db.update_user_password.assert_called_once_with('user1', 'newpass')

    def test_update_password_incorrect_old(self):
        """Test password update with incorrect old password."""
        self.model.db.get_user.return_value = {
            'username': 'user1',
            'password': 'oldpass',
            'role': 'Cashier'
        }
        
        result = self.model.update_password('user1', 'wrongpass', 'newpass')
        
        self.assertEqual(result, 'Incorrect old password')

    def test_update_password_same_as_old(self):
        """Test password update with same password."""
        self.model.db.get_user.return_value = {
            'username': 'user1',
            'password': 'oldpass',
            'role': 'Cashier'
        }
        
        result = self.model.update_password('user1', 'oldpass', 'oldpass')
        
        self.assertEqual(result, 'New password cannot be the same as old password')

    def test_update_password_user_not_found(self):
        """Test password update for non-existent user."""
        self.model.db.get_user.return_value = None
        
        result = self.model.update_password('nonexistent', 'pass', 'newpass')
        
        self.assertEqual(result, 'User not found')

    def test_update_password_db_failure(self):
        """Test password update database failure."""
        self.model.db.get_user.return_value = {
            'username': 'user1',
            'password': 'oldpass',
            'role': 'Cashier'
        }
        self.model.db.update_user_password.return_value = False
        
        result = self.model.update_password('user1', 'oldpass', 'newpass')
        
        self.assertEqual(result, 'Failed to update password')

    def test_get_usernames(self):
        """Test retrieving usernames."""
        self.model.db.list_users.return_value = [
            {'username': 'manager', 'role': 'Manager'},
            {'username': 'cashier', 'role': 'Cashier'},
        ]
        
        usernames = self.model.get_usernames()
        
        self.assertEqual(usernames, ['manager', 'cashier'])

    def test_create_user(self):
        """Test creating a user."""
        self.model.db.create_user.return_value = True
        
        result = self.model.create_user('newuser', 'password', 'Cashier')
        
        self.assertTrue(result)
        self.model.db.create_user.assert_called_once_with('newuser', 'password', 'Cashier')

    def test_create_user_default_role(self):
        """Test creating user with default role."""
        self.model.db.create_user.return_value = True
        
        result = self.model.create_user('newuser', 'password')
        
        self.assertTrue(result)
        self.model.db.create_user.assert_called_once_with('newuser', 'password', 'Cashier')

    def test_delete_user(self):
        """Test deleting a user."""
        self.model.db.delete_user.return_value = True
        
        result = self.model.delete_user('user_to_delete')
        
        self.assertTrue(result)
        self.model.db.delete_user.assert_called_once_with('user_to_delete')


class TestOrderManagement(unittest.TestCase):
    """Test order management functionality."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_add_item_to_order_success(self):
        """Test adding item to order."""
        self.model.db.get_item_details.return_value = ('Espresso', 50.0, 'Coffee')
        
        success, msg = self.model.add_item_to_order(1)
        
        self.assertTrue(success)
        self.assertEqual(msg, 'Item added')
        self.assertIn(1, self.model.current_order)
        self.assertEqual(self.model.current_order[1]['qty'], 1)

    def test_add_item_to_order_not_found(self):
        """Test adding non-existent item."""
        self.model.db.get_item_details.return_value = None
        
        success, msg = self.model.add_item_to_order(999)
        
        self.assertFalse(success)
        self.assertEqual(msg, 'Item not found in menu.')

    def test_add_item_to_order_increment_quantity(self):
        """Test adding same item increments quantity."""
        self.model.db.get_item_details.return_value = ('Espresso', 50.0, 'Coffee')
        
        self.model.add_item_to_order(1)
        self.model.add_item_to_order(1)
        
        self.assertEqual(self.model.current_order[1]['qty'], 2)

    def test_remove_item_from_order_success(self):
        """Test removing item from order."""
        self.model.current_order = {1: {'name': 'Espresso', 'price': 50.0, 'qty': 1}}
        
        result = self.model.remove_item_from_order(1)
        
        self.assertTrue(result)
        self.assertNotIn(1, self.model.current_order)

    def test_remove_item_from_order_not_found(self):
        """Test removing non-existent item."""
        result = self.model.remove_item_from_order(999)
        
        self.assertFalse(result)

    def test_clear_order(self):
        """Test clearing order."""
        self.model.current_order = {
            1: {'name': 'Espresso', 'price': 50.0, 'qty': 1},
            2: {'name': 'Latte', 'price': 60.0, 'qty': 2}
        }
        
        self.model.clear_order()
        
        self.assertEqual(self.model.current_order, {})

    def test_calculate_order_total_empty(self):
        """Test calculating total for empty order."""
        self.model.current_order = {}
        
        total = self.model.calculate_order_total()
        
        self.assertEqual(total, 0)

    def test_calculate_order_total_single_item(self):
        """Test calculating total for single item."""
        self.model.current_order = {
            1: {'name': 'Espresso', 'price': 50.0, 'qty': 1}
        }
        
        total = self.model.calculate_order_total()
        
        self.assertAlmostEqual(total, 50.0)

    def test_calculate_order_total_multiple_items(self):
        """Test calculating total for multiple items."""
        self.model.current_order = {
            1: {'name': 'Espresso', 'price': 50.0, 'qty': 1},
            2: {'name': 'Latte', 'price': 60.0, 'qty': 2}
        }
        
        total = self.model.calculate_order_total()
        
        self.assertAlmostEqual(total, 170.0)

    def test_calculate_order_total_with_quantity(self):
        """Test calculating total with various quantities."""
        self.model.current_order = {
            1: {'name': 'Espresso', 'price': 50.0, 'qty': 3}
        }
        
        total = self.model.calculate_order_total()
        
        self.assertAlmostEqual(total, 150.0)

    def test_process_order_success(self):
        """Test processing order successfully."""
        self.model.current_order = {
            1: {'name': 'Espresso', 'price': 50.0, 'qty': 1}
        }
        self.model.db.record_sale.return_value = True
        self.model.db.save_receipt.return_value = 'receipt_id'
        
        success, total, receipt = self.model.process_order()
        
        self.assertTrue(success)
        self.assertAlmostEqual(total, 50.0)
        self.assertIsNotNone(receipt)
        self.assertEqual(self.model.current_order, {})

    def test_process_order_empty(self):
        """Test processing empty order."""
        self.model.current_order = {}
        
        success, total, receipt = self.model.process_order()
        
        self.assertFalse(success)
        self.assertEqual(total, 0)
        self.assertIsNone(receipt)

    def test_process_order_db_failure(self):
        """Test processing order with database failure."""
        self.model.current_order = {
            1: {'name': 'Espresso', 'price': 50.0, 'qty': 1}
        }
        self.model.db.record_sale.return_value = False
        
        success, total, receipt = self.model.process_order()
        
        self.assertFalse(success)
        self.assertEqual(total, 0)
        self.assertIsNone(receipt)


class TestMenuManagement(unittest.TestCase):
    """Test menu item management."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_get_menu_items(self):
        """Test retrieving menu items."""
        expected_items = [(1, 'Espresso', 50.0, 100, 'Coffee')]
        self.model.db.read_menu_items.return_value = expected_items
        
        items = self.model.get_menu_items()
        
        self.assertEqual(items, expected_items)

    def test_get_menu_categories(self):
        """Test retrieving menu categories."""
        expected_cats = ['Coffee', 'Tea', 'Pastry']
        self.model.db.read_categories.return_value = expected_cats
        
        categories = self.model.get_menu_categories()
        
        self.assertEqual(categories, expected_cats)

    def test_create_item(self):
        """Test creating menu item."""
        self.model.db.create_menu_item.return_value = True
        
        result = self.model.create_item('Mocha', 70.0, 50, 'Coffee')
        
        self.assertTrue(result)
        self.model.db.create_menu_item.assert_called_once_with('Mocha', 70.0, 50, 'Coffee')

    def test_update_item(self):
        """Test updating menu item."""
        self.model.db.update_menu_item.return_value = True
        
        result = self.model.update_item(1, 'Espresso Premium', 60.0, 80, 'Coffee')
        
        self.assertTrue(result)
        self.model.db.update_menu_item.assert_called_once_with(1, 'Espresso Premium', 60.0, 80, 'Coffee')

    def test_delete_item(self):
        """Test deleting menu item."""
        self.model.db.delete_menu_item.return_value = True
        
        result = self.model.delete_item(1)
        
        self.assertTrue(result)
        self.model.db.delete_menu_item.assert_called_once_with(1)


class TestSalesReporting(unittest.TestCase):
    """Test sales reporting functionality."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_get_all_sales_data_default(self):
        """Test getting sales data with default days."""
        expected_data = [('Espresso', 'Coffee', 5, 250.0, '2025-01-01')]
        self.model.db.get_sales_data_for_report.return_value = expected_data
        
        data = self.model.get_all_sales_data()
        
        self.assertEqual(data, expected_data)
        self.model.db.get_sales_data_for_report.assert_called_once_with(30)

    def test_get_all_sales_data_custom_days(self):
        """Test getting sales data with custom days."""
        expected_data = []
        self.model.db.get_sales_data_for_report.return_value = expected_data
        
        data = self.model.get_all_sales_data(days_back=7)
        
        self.model.db.get_sales_data_for_report.assert_called_once_with(7)


class TestEndOfDay(unittest.TestCase):
    """Test End-of-Day functionality."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()
        self.model.current_pos_date = datetime.date(2025, 1, 1)

    def test_generate_eod_summary(self):
        """Test generating EOD summary."""
        expected_summary = {
            'date': '2025-01-01',
            'total_revenue': 500.0,
            'top_items': [('Espresso', 10)],
            'low_stock': []
        }
        self.model.db.end_of_day_summary.return_value = expected_summary
        
        summary = self.model.generate_eod_summary()
        
        self.assertEqual(summary, expected_summary)
        self.model.db.end_of_day_summary.assert_called_once_with('2025-01-01')

    def test_save_eod_and_advance_day_success(self):
        """Test saving EOD and advancing day successfully."""
        initial_date = self.model.current_pos_date
        summary = {'date': '2025-01-01', 'total_revenue': 500.0}
        self.model.db.save_eod_summary.return_value = True
        self.model.db.end_of_day_summary.return_value = summary
        
        status, returned_summary = self.model.save_eod_and_advance_day()
        
        self.assertEqual(status, 'Success')
        self.assertEqual(self.model.current_pos_date, initial_date + datetime.timedelta(days=1))

    def test_save_eod_and_advance_day_already_saved(self):
        """Test saving EOD when already saved."""
        initial_date = self.model.current_pos_date
        summary = {'date': '2025-01-01', 'total_revenue': 500.0}
        self.model.db.save_eod_summary.return_value = False
        self.model.db.end_of_day_summary.return_value = summary
        
        status, returned_summary = self.model.save_eod_and_advance_day()
        
        self.assertEqual(status, 'Already Saved')
        self.assertEqual(self.model.current_pos_date, initial_date)

    def test_get_historical_eod_records(self):
        """Test getting historical EOD records."""
        expected_records = [
            {'date': '2025-01-01', 'revenue': 500.0}
        ]
        self.model.db.get_past_eod_records.return_value = expected_records
        
        records = self.model.get_historical_eod_records()
        
        self.assertEqual(records, expected_records)


class TestReceiptManagement(unittest.TestCase):
    """Test receipt management functionality."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_get_all_receipts(self):
        """Test getting all receipts."""
        expected_receipts = [
            {'receipt_uuid': 'uuid-1', 'total': 100.0}
        ]
        self.model.db.get_all_receipts.return_value = expected_receipts
        
        receipts = self.model.get_all_receipts()
        
        self.assertEqual(receipts, expected_receipts)

    def test_get_all_receipts_with_limit(self):
        """Test getting receipts with limit."""
        expected_receipts = []
        self.model.db.get_all_receipts.return_value = expected_receipts
        
        receipts = self.model.get_all_receipts(limit=5)
        
        self.model.db.get_all_receipts.assert_called_once_with(limit=5)

    def test_get_all_receipts_exception(self):
        """Test getting receipts with exception."""
        self.model.db.get_all_receipts.side_effect = Exception('DB error')
        
        receipts = self.model.get_all_receipts()
        
        self.assertEqual(receipts, [])

    def test_delete_receipt_success(self):
        """Test deleting receipt."""
        self.model.db.delete_receipt.return_value = True
        
        result = self.model.delete_receipt('uuid-123')
        
        self.assertTrue(result)
        self.model.db.delete_receipt.assert_called_once_with('uuid-123')

    def test_delete_receipt_failure(self):
        """Test deleting receipt with failure."""
        self.model.db.delete_receipt.return_value = False
        
        result = self.model.delete_receipt('uuid-123')
        
        self.assertFalse(result)

    def test_delete_receipt_exception(self):
        """Test deleting receipt with exception."""
        self.model.db.delete_receipt.side_effect = Exception('DB error')
        
        result = self.model.delete_receipt('uuid-123')
        
        self.assertFalse(result)

    def test_get_archived_eod_records(self):
        """Test getting archived EOD records."""
        expected_records = []
        self.model.db.get_archived_eod_records.return_value = expected_records
        
        records = self.model.get_archived_eod_records()
        
        self.assertEqual(records, expected_records)

    def test_restore_archived_eod_summaries_success(self):
        """Test restoring archived EOD summaries."""
        self.model.db.restore_all_archived_eod_records.return_value = 5
        
        result = self.model.restore_archived_eod_summaries()
        
        self.assertEqual(result, 5)

    def test_restore_archived_eod_summaries_exception(self):
        """Test restoring archived EOD summaries with exception."""
        self.model.db.restore_all_archived_eod_records.side_effect = Exception('DB error')
        
        result = self.model.restore_archived_eod_summaries()
        
        self.assertIsNone(result)


class TestDataClearing(unittest.TestCase):
    """Test data clearing functionality."""
    
    def setUp(self):
        self.model = AppModel()
        self.model.db = Mock()

    def test_clear_historical_data(self):
        """Test clearing historical data."""
        self.model.db.clear_all_sales_data.return_value = True
        
        result = self.model.clear_historical_data()
        
        self.assertTrue(result)
        self.model.db.clear_all_sales_data.assert_called_once()


if __name__ == '__main__':
    unittest.main()
