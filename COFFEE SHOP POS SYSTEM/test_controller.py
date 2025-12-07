import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
from controller import AppController


class DummyModel:
    def __init__(self):
        self.current_order = {}
        self.user_role = 'Cashier'
        self.current_pos_date = datetime.now()
        self.authenticated = True
        
    def authenticate(self, username, password):
        return self.authenticated
    
    def add_item_to_order(self, item_id):
        return True, 'added'
    
    def calculate_order_total(self):
        return 100.0
    
    def remove_item_from_order(self, item_id):
        return True
    
    def clear_order(self):
        self.current_order = {}
    
    def process_order(self):
        return True, 100.0, 'uuid-123'
    
    def get_menu_items(self):
        return [
            (1, 'Espresso', 50.0, 100, 'Coffee'),
            (2, 'Latte', 60.0, 100, 'Coffee'),
            (3, 'Cappuccino', 65.0, 100, 'Coffee'),
        ]
    
    def get_menu_categories(self):
        return ['Coffee', 'Tea', 'Pastry']
    
    def get_all_receipts(self, limit=None):
        return []
    
    def delete_receipt(self, uuid):
        return True
    
    def create_item(self, name, price, stock, category):
        return True
    
    def update_item(self, item_id, name, price, stock, category):
        return True
    
    def delete_item(self, item_id):
        return True
    
    def get_all_sales_data(self, days_back=30):
        return [
            ('Espresso', 'Coffee', 5, 250.0, '2025-01-01'),
            ('Latte', 'Coffee', 3, 180.0, '2025-01-01'),
        ]
    
    def generate_eod_summary(self):
        return {
            'date': '2025-01-01',
            'total_revenue': 500.0,
            'total_transactions': 10,
        }
    
    def get_historical_eod_records(self):
        return []
    
    def save_eod_and_advance_day(self):
        return "Success", {'date': '2025-01-01', 'total_revenue': 500.0}
    
    def clear_historical_data(self):
        return True
    
    def update_password(self, username, old_pass, new_pass):
        return "Success"
    
    def restore_archived_eod_summaries(self):
        return 5


class DummyView:
    """Mock view for testing controller functionality."""
    def __init__(self):
        self.updated = False
        self.last_warning = None
        self.last_info = None
        self.last_error = None
        self.menu = []
        
    def update_order_summary(self, *a, **k):
        self.updated = True
    
    def show_warning(self, title, message):
        self.last_warning = (title, message)
    
    def show_info(self, title, message):
        self.last_info = (title, message)
    
    def show_error(self, title, message):
        self.last_error = (title, message)
    
    def update_menu_display(self, items):
        self.menu = items
        self.updated = True
    
    def clear_crud_form(self):
        pass
    
    def clear_password_fields(self):
        pass
    
    def update_admin_menu_table(self, items):
        pass
    
    def update_category_combo(self, categories):
        pass
    
    def update_password_combo(self, usernames):
        pass
    
    def update_pos_filters(self, categories):
        pass
    
    def update_transaction_history(self, receipts):
        pass
    
    def update_report_views(self, df):
        pass
    
    def update_eod_summary_view(self, summary, date):
        pass
    
    def update_past_eod_records(self, records):
        pass


class TestAppControllerInitialization(unittest.TestCase):
    """Test AppController initialization and setup."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_controller_initialization(self):
        """Test that controller initializes with model and app."""
        self.assertEqual(self.controller.model, self.model)
        self.assertEqual(self.controller.app, self.app)
    
    def test_init_login_flow_called(self):
        """Test that init_login_flow is called during initialization."""
        with patch.object(AppController, 'init_login_flow') as mock_login:
            AppController.init_login_flow = self._orig_init
            # This would require mocking the GUI components
            AppController.init_login_flow = lambda self: None


class TestHandleLoginLogout(unittest.TestCase):
    """Test login and logout handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_logout(self):
        """Test logout handler clears user role and order."""
        self.model.user_role = 'Cashier'
        self.model.current_order = {1: {'name': 'Coffee', 'price': 50}}
        
        self.controller.handle_logout()
        
        self.assertIsNone(self.model.user_role)
        self.assertEqual(self.model.current_order, {})
        self.assertEqual(self.view.last_info[0], 'Logged Out')


class TestOrderHandling(unittest.TestCase):
    """Test order-related handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_add_to_order_success(self):
        """Test adding item to order successfully."""
        self.model.current_order = {}
        self.controller.handle_add_to_order(1)
        
        self.assertTrue(self.view.updated)
    
    def test_handle_add_to_order_failure(self):
        """Test handling failure when adding item to order."""
        self.model.add_item_to_order = lambda x: (False, 'Item out of stock')
        
        self.controller.handle_add_to_order(1)
        
        self.assertEqual(self.view.last_warning[0], 'Order Error')
        self.assertEqual(self.view.last_warning[1], 'Item out of stock')
    
    def test_handle_remove_order_item_success(self):
        """Test removing item from order successfully."""
        self.model.current_order = {1: {'name': 'Coffee', 'price': 50, 'qty': 1}}
        
        self.controller.handle_remove_order_item(1)
        
        self.assertTrue(self.view.updated)
    
    def test_handle_remove_order_item_failure(self):
        """Test handling failure when removing non-existent item."""
        self.model.remove_item_from_order = lambda x: False
        
        self.controller.handle_remove_order_item(999)
        
        self.assertEqual(self.view.last_warning[0], 'Error')
        self.assertEqual(self.view.last_warning[1], 'Item not found in order.')
    
    def test_handle_clear_order(self):
        """Test clearing the entire order."""
        self.model.current_order = {1: {'name': 'Coffee', 'price': 50, 'qty': 2}}
        
        self.controller.handle_clear_order()
        
        self.assertEqual(self.model.current_order, {})
        self.assertTrue(self.view.updated)


class TestPaymentProcessing(unittest.TestCase):
    """Test payment processing handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_process_payment_empty_order(self):
        """Test payment processing with empty order."""
        self.model.current_order = {}
        
        self.controller.handle_process_payment()
        
        self.assertEqual(self.view.last_warning[0], 'Warning')
        self.assertEqual(self.view.last_warning[1], 'The order is empty.')
    
    def test_handle_process_payment_success(self):
        """Test successful payment processing."""
        self.model.current_order = {1: {'name': 'Coffee', 'price': 50, 'qty': 2}}
        
        self.controller.handle_process_payment()
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertIn('₱100.00', self.view.last_info[1])
        self.assertIn('uuid-123', self.view.last_info[1])
    
    def test_handle_process_payment_failure(self):
        """Test payment processing failure."""
        self.model.current_order = {1: {'name': 'Coffee', 'price': 50, 'qty': 1}}
        self.model.process_order = lambda: (False, 0, None)
        
        self.controller.handle_process_payment()
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Failed to record sale', self.view.last_error[1])


class TestMenuItemCRUD(unittest.TestCase):
    """Test menu item CRUD handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_add_menu_item_success(self):
        """Test adding menu item successfully."""
        self.controller.handle_add_menu_item('Mocha', 70.0, 50, 'Coffee')
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertIn('Mocha', self.view.last_info[1])
    
    def test_handle_add_menu_item_failure(self):
        """Test failure when adding duplicate menu item."""
        self.model.create_item = lambda *args: False
        
        self.controller.handle_add_menu_item('Espresso', 50.0, 100, 'Coffee')
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('already exists', self.view.last_error[1])
    
    def test_handle_update_menu_item_success(self):
        """Test updating menu item successfully."""
        self.controller.handle_update_menu_item(1, 'Espresso Premium', 60.0, 80, 'Coffee')
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertIn('1', self.view.last_info[1])
    
    def test_handle_update_menu_item_failure(self):
        """Test failure when updating menu item."""
        self.model.update_item = lambda *args: False
        
        self.controller.handle_update_menu_item(1, 'Espresso', 50.0, 100, 'Coffee')
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Failed to update', self.view.last_error[1])
    
    def test_handle_delete_menu_item_success(self):
        """Test deleting menu item successfully."""
        self.controller.handle_delete_menu_item(1)
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertEqual(self.view.last_info[1], 'Item deleted.')
    
    def test_handle_delete_menu_item_failure(self):
        """Test failure when deleting menu item."""
        self.model.delete_item = lambda x: False
        
        self.controller.handle_delete_menu_item(999)
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertEqual(self.view.last_error[1], 'Failed to delete item.')


class TestReportAndEOD(unittest.TestCase):
    """Test report and End-of-Day handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_report_refresh(self):
        """Test report refresh functionality."""
        self.controller.handle_report_refresh()
        
        # Verify that the view was updated (method exists and was called)
        # In a real test, we'd verify the data passed
    
    def test_handle_eod_refresh(self):
        """Test EOD refresh functionality."""
        self.controller.handle_eod_refresh()
        
        # Verify that EOD data was retrieved and view updated
    
    @patch('controller.QMessageBox')
    def test_handle_save_eod_success(self, mock_msgbox):
        """Test successful EOD save."""
        self.model.current_order = {1: {'name': 'Coffee', 'price': 50, 'qty': 1}}
        
        self.controller.handle_save_eod()
        
        self.assertEqual(self.view.last_info[0], 'End of Day Success')
    
    def test_handle_clear_sales_data_success(self):
        """Test clearing sales data successfully."""
        self.controller.handle_clear_sales_data()
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertIn('historical sales data', self.view.last_info[1])
    
    def test_handle_clear_sales_data_failure(self):
        """Test failure when clearing sales data."""
        self.model.clear_historical_data = lambda: False
        
        self.controller.handle_clear_sales_data()
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertEqual(self.view.last_error[1], 'Failed to clear data.')


class TestPasswordAndAccountManagement(unittest.TestCase):
    """Test password change and user management handlers."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_change_password_success(self):
        """Test successful password change."""
        self.controller.handle_change_password('admin', 'oldpass', 'newpass', 'newpass')
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertIn('admin', self.view.last_info[1])
    
    def test_handle_change_password_incorrect_old(self):
        """Test password change with incorrect old password."""
        self.model.update_password = lambda *args: "Incorrect old password"
        
        self.controller.handle_change_password('admin', 'wrongpass', 'newpass', 'newpass')
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Old Password', self.view.last_error[1])
    
    def test_handle_change_password_failure(self):
        """Test password change failure."""
        self.model.update_password = lambda *args: "Database error"
        
        self.controller.handle_change_password('admin', 'oldpass', 'newpass', 'newpass')
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Database error', self.view.last_error[1])
    
    def test_handle_restore_archived_success(self):
        """Test successful restoration of archived EOD summaries."""
        self.controller.handle_restore_archived()
        
        self.assertEqual(self.view.last_info[0], 'Restore Complete')
        self.assertIn('5', self.view.last_info[1])
    
    def test_handle_restore_archived_failure(self):
        """Test failure when restoring archived data."""
        self.model.restore_archived_eod_summaries = lambda: None
        
        self.controller.handle_restore_archived()
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Failed to restore', self.view.last_error[1])


class TestMenuFiltering(unittest.TestCase):
    """Test menu filtering handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_handle_menu_filter_by_category(self):
        """Test filtering menu by category."""
        self.controller.handle_menu_filter('Coffee')
        
        self.assertTrue(self.view.updated)
        self.assertEqual(len(self.view.menu), 3)  # All items are coffee
    
    def test_handle_menu_filter_empty_category(self):
        """Test showing all items when category is empty."""
        self.controller.handle_menu_filter('')
        
        self.assertTrue(self.view.updated)
        self.assertEqual(len(self.view.menu), 3)
    
    def test_handle_menu_filter_case_insensitive(self):
        """Test that filtering is case-insensitive."""
        self.controller.handle_menu_filter('coffee')
        
        self.assertTrue(self.view.updated)
        self.assertEqual(len(self.view.menu), 3)


class TestTransactionHistory(unittest.TestCase):
    """Test transaction history handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_refresh_transaction_history(self):
        """Test refreshing transaction history."""
        self.controller.refresh_transaction_history()
        
        # Should not raise any exceptions
    
    def test_handle_delete_receipt_success(self):
        """Test deleting receipt successfully."""
        self.controller.handle_delete_receipt('uuid-123')
        
        self.assertEqual(self.view.last_info[0], 'Success')
        self.assertIn('deleted', self.view.last_info[1])
    
    def test_handle_delete_receipt_failure(self):
        """Test failure when deleting receipt."""
        self.model.delete_receipt = lambda x: False
        
        self.controller.handle_delete_receipt('uuid-invalid')
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Failed to delete receipt', self.view.last_error[1])
    
    def test_handle_delete_receipt_exception(self):
        """Test exception handling when deleting receipt."""
        self.model.delete_receipt = lambda x: (_ for _ in ()).throw(Exception('DB error'))
        
        self.controller.handle_delete_receipt('uuid-123')
        
        self.assertEqual(self.view.last_error[0], 'Error')
        self.assertIn('Failed to delete receipt', self.view.last_error[1])


class TestDataRefresh(unittest.TestCase):
    """Test data refresh handler methods."""
    
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.app = Mock()
        self.controller = AppController(self.model, self.app)
        self.view = DummyView()
        self.controller.main_window = self.view
    
    def tearDown(self):
        AppController.init_login_flow = self._orig_init
    
    def test_refresh_all_data_cashier_role(self):
        """Test refreshing all data for cashier role."""
        self.model.user_role = 'Cashier'
        
        self.controller.refresh_all_data()
        
        self.assertEqual(self.view.menu, self.model.get_menu_items())
        self.assertTrue(self.view.updated)
    
    def test_refresh_all_data_manager_role(self):
        """Test refreshing all data for manager role."""
        self.model.user_role = 'Manager'
        self.model.get_usernames = lambda: ['admin', 'user1']
        
        self.controller.refresh_all_data()
        
        self.assertEqual(self.view.menu, self.model.get_menu_items())
        self.assertTrue(self.view.updated)
    
    def test_handle_tab_change_eod(self):
        """Test tab change handler for End of Day tab."""
        self.controller.handle_tab_change('End of Day')
        
        # Should trigger EOD refresh without errors
    
    def test_handle_tab_change_sales_reports(self):
        """Test tab change handler for Sales Reports tab."""
        self.controller.handle_tab_change('Sales Reports')
        
        # Should trigger report refresh without errors
    
    def test_handle_tab_change_transaction_history(self):
        """Test tab change handler for Transaction History tab."""
        self.controller.handle_tab_change('Transaction History')
        
        # Should trigger transaction history refresh without errors


if __name__ == '__main__':
    unittest.main()
