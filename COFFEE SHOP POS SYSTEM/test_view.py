import unittest
import sys
import json
from datetime import datetime
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from view import (
    create_label, create_button, create_input, GraphCanvas,
    LoginDialog, ReceiptDetailsDialog, CoffeeShopPOSView
)


class TestViewHelpers(unittest.TestCase):
    
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_create_label_basic(self):
       
        label = create_label('Test Label')
        self.assertEqual(label.text(), 'Test Label')
        self.assertFalse(label.font().bold())

    def test_create_label_bold(self):
        label = create_label('Bold Label', 14, True)
        self.assertEqual(label.text(), 'Bold Label')
        self.assertTrue(label.font().bold())
        self.assertEqual(label.font().pointSize(), 14)

    def test_create_label_custom_size(self):
        """Test creating label with custom font size."""
        label = create_label('Sized Label', 18, False)
        self.assertEqual(label.font().pointSize(), 18)
        self.assertFalse(label.font().bold())

    def test_create_button_primary(self):
        """Test creating a primary button."""
        button = create_button('Primary Button', 'primary')
        self.assertEqual(button.text(), 'Primary Button')
        self.assertIn('A0522D', button.styleSheet())

    def test_create_button_secondary(self):
        """Test creating a secondary button."""
        button = create_button('Secondary Button', 'secondary')
        self.assertEqual(button.text(), 'Secondary Button')
        self.assertIn('D2B48C', button.styleSheet())

    def test_create_button_danger(self):
        """Test creating a danger button."""
        button = create_button('Delete Button', 'danger')
        self.assertEqual(button.text(), 'Delete Button')
        self.assertIn('CC0000', button.styleSheet())

    def test_create_input_normal(self):
        """Test creating a normal text input."""
        input_field = create_input('Enter text')
        self.assertEqual(input_field.placeholderText(), 'Enter text')
        self.assertNotEqual(input_field.echoMode(), 2)

    def test_create_input_password(self):
        """Test creating a password input."""
        input_field = create_input('Password', is_password=True)
        self.assertEqual(input_field.placeholderText(), 'Password')
        self.assertEqual(input_field.echoMode(), 2)


class TestGraphCanvas(unittest.TestCase):
    """Test GraphCanvas plotting functionality."""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_graph_canvas_initialization(self):
        """Test GraphCanvas initialization."""
        canvas = GraphCanvas('Test Graph')
        self.assertIsNotNone(canvas.fig)
        self.assertIsNotNone(canvas.ax)

    def test_clear_plot(self):
        """Test clearing a plot."""
        canvas = GraphCanvas('Test')
        canvas.clear_plot('Cleared')
        # Plot should be cleared with "No Data Available" message
        self.assertIsNotNone(canvas.ax)

    def test_plot_top_selling_items_with_data(self):
        """Test plotting top selling items."""
        canvas = GraphCanvas('Top Items')
        df = pd.DataFrame({
            'item_name': ['Coffee', 'Tea', 'Pastry', 'Juice', 'Cake'],
            'quantity': [10, 8, 5, 3, 2]
        })
        canvas.plot_top_selling_items(df)
        self.assertIsNotNone(canvas.ax)

    def test_plot_top_selling_items_empty(self):
        """Test plotting with empty data."""
        canvas = GraphCanvas('Top Items')
        df = pd.DataFrame()
        canvas.plot_top_selling_items(df)
        self.assertIsNotNone(canvas.ax)

    def test_plot_sales_by_category_with_data(self):
        """Test plotting sales by category."""
        canvas = GraphCanvas('Category Sales')
        df = pd.DataFrame({
            'category': ['Coffee', 'Tea', 'Pastry'],
            'total': [500.0, 300.0, 200.0]
        })
        canvas.plot_sales_by_category(df)
        self.assertIsNotNone(canvas.ax)

    def test_plot_sales_by_category_empty(self):
        """Test plotting category sales with empty data."""
        canvas = GraphCanvas('Category Sales')
        df = pd.DataFrame()
        canvas.plot_sales_by_category(df)
        self.assertIsNotNone(canvas.ax)

    def test_plot_daily_sales_with_data(self):
        """Test plotting daily sales."""
        canvas = GraphCanvas('Daily Sales')
        df = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'total': [100.0, 150.0, 200.0]
        })
        canvas.plot_daily_sales(df)
        self.assertIsNotNone(canvas.ax)

    def test_plot_daily_sales_empty(self):
        """Test plotting daily sales with empty data."""
        canvas = GraphCanvas('Daily Sales')
        df = pd.DataFrame()
        canvas.plot_daily_sales(df)
        self.assertIsNotNone(canvas.ax)


class TestLoginDialog(unittest.TestCase):
    """Test LoginDialog functionality."""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_login_dialog_initialization(self):
        """Test LoginDialog initializes correctly."""
        dialog = LoginDialog()
        self.assertEqual(dialog.windowTitle(), 'POS System Login')
        self.assertIsNotNone(dialog.username_input)
        self.assertIsNotNone(dialog.password_input)
        dialog.close()

    def test_login_dialog_username_input(self):
        """Test setting username in login dialog."""
        dialog = LoginDialog()
        dialog.username_input.setText('manager')
        self.assertEqual(dialog.username_input.text(), 'manager')
        dialog.close()

    def test_login_dialog_password_input(self):
        """Test password input is masked."""
        dialog = LoginDialog()
        dialog.password_input.setText('password123')
        self.assertEqual(dialog.password_input.text(), 'password123')
        self.assertEqual(dialog.password_input.echoMode(), 2)
        dialog.close()

    def test_login_signal_emitted(self):
        """Test login signal is emitted with credentials."""
        dialog = LoginDialog()
        dialog.username_input.setText('user')
        dialog.password_input.setText('pass')
        
        signal_received = []
        dialog.login_attempted.connect(lambda u, p: signal_received.append((u, p)))
        dialog._emit_login_signal()
        
        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], ('user', 'pass'))
        dialog.close()

    def test_show_login_error(self):
        """Test showing login error message."""
        dialog = LoginDialog()
        with patch('view.QMessageBox.critical') as mock_critical:
            dialog.show_login_error('Invalid credentials')
            mock_critical.assert_called_once()
        dialog.close()


class TestReceiptDetailsDialog(unittest.TestCase):
    """Test ReceiptDetailsDialog functionality."""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_receipt_dialog_initialization(self):
        """Test ReceiptDetailsDialog initialization."""
        receipt = {
            'receipt_uuid': 'uuid-123',
            'sale_date': '2025-01-01',
            'total': 100.0,
            'items': [{'name': 'Coffee', 'qty': 2, 'price': 50.0}],
            'created_at': '2025-01-01 10:00:00'
        }
        dialog = ReceiptDetailsDialog(receipt)
        self.assertEqual(dialog.windowTitle(), 'Receipt Details')
        dialog.close()

    def test_receipt_dialog_with_json_items(self):
        """Test receipt dialog with JSON items."""
        receipt = {
            'receipt_uuid': 'uuid-123',
            'sale_date': '2025-01-01',
            'total': 100.0,
            'items': json.dumps([{'name': 'Coffee', 'qty': 2, 'price': 50.0}]),
            'created_at': '2025-01-01 10:00:00'
        }
        dialog = ReceiptDetailsDialog(receipt)
        self.assertIsNotNone(dialog)
        dialog.close()

    def test_receipt_dialog_empty_receipt(self):
        """Test receipt dialog with empty receipt."""
        dialog = ReceiptDetailsDialog({})
        self.assertIsNotNone(dialog)
        dialog.close()

    def test_delete_signal_emitted(self):
        """Test delete signal is emitted."""
        receipt = {
            'receipt_uuid': 'uuid-123',
            'sale_date': '2025-01-01',
            'total': 100.0,
            'items': [],
            'created_at': '2025-01-01 10:00:00'
        }
        dialog = ReceiptDetailsDialog(receipt)
        
        signal_received = []
        dialog.delete_requested.connect(lambda rid: signal_received.append(rid))
        
        with patch('view.QMessageBox.question', return_value=4):  # Yes
            dialog._confirm_and_delete()
        
        dialog.close()


class TestCoffeeShopPOSView(unittest.TestCase):
    """Test CoffeeShopPOSView main window."""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.view = CoffeeShopPOSView('Cashier')

    def tearDown(self):
        self.view.close()

    def test_pos_view_initialization_cashier(self):
        """Test POS view initializes for Cashier."""
        self.assertEqual(self.view.user_role, 'Cashier')
        self.assertIn('Cashier', self.view.role_label.text())

    def test_pos_view_initialization_manager(self):
        """Test POS view initializes for Manager."""
        manager_view = CoffeeShopPOSView('Manager')
        self.assertEqual(manager_view.user_role, 'Manager')
        self.assertIn('Manager', manager_view.role_label.text())
        manager_view.close()

    def test_create_menu_card(self):
        """Test creating a menu card."""
        card = self.view._create_menu_card(1, 'Espresso', 50.0, 100, 'Coffee')
        self.assertIsNotNone(card)
        self.assertEqual(card.property('item_id'), 1)

    def test_update_menu_display_with_items(self):
        """Test updating menu display."""
        items = [
            (1, 'Espresso', 50.0, 100, 'Coffee'),
            (2, 'Latte', 60.0, 100, 'Coffee'),
        ]
        self.view.update_menu_display(items)
        self.assertEqual(self.view.menu_grid_layout.count(), 2)

    def test_update_menu_display_empty(self):
        """Test updating menu display with empty list."""
        self.view.update_menu_display([])
        self.assertEqual(self.view.menu_grid_layout.count(), 0)

    def test_update_menu_display_filters_out_of_stock(self):
        """Test that out-of-stock items are filtered."""
        items = [
            (1, 'Espresso', 50.0, 100, 'Coffee'),
            (2, 'Latte', 60.0, 0, 'Coffee'),
        ]
        self.view.update_menu_display(items)
        # Should only display 1 item (Latte is out of stock)
        self.assertEqual(self.view.menu_grid_layout.count(), 1)

    def test_update_order_summary(self):
        """Test updating order summary."""
        order = {
            1: {'name': 'Coffee', 'price': 50.0, 'qty': 2},
            2: {'name': 'Tea', 'price': 40.0, 'qty': 1}
        }
        self.view.update_order_summary(order, 140.0)
        
        self.assertEqual(self.view.order_table.rowCount(), 2)
        self.assertIn('140.00', self.view.total_label.text())

    def test_update_order_summary_empty(self):
        """Test updating empty order summary."""
        self.view.update_order_summary({}, 0.0)
        
        self.assertEqual(self.view.order_table.rowCount(), 0)
        self.assertIn('0.00', self.view.total_label.text())

    def test_update_pos_filters(self):
        """Test updating POS category filters."""
        categories = ['Coffee', 'Tea', 'Pastry']
        self.view.update_pos_filters(categories)
        
        self.assertEqual(self.view.stored_categories, categories)

    def test_update_transaction_history(self):
        """Test updating transaction history."""
        receipts = [
            {
                'receipt_uuid': 'uuid-1',
                'sale_date': '2025-01-01',
                'items': [{'name': 'Coffee', 'qty': 2}],
                'total': 100.0,
                'created_at': '2025-01-01 10:00:00'
            }
        ]
        self.view.update_transaction_history(receipts)
        self.assertEqual(self.view.history_table.rowCount(), 1)

    def test_update_transaction_history_json_items(self):
        """Test updating transaction history with JSON items."""
        receipts = [
            {
                'receipt_uuid': 'uuid-1',
                'sale_date': '2025-01-01',
                'items': json.dumps([{'name': 'Coffee', 'qty': 2}]),
                'total': 100.0,
                'created_at': '2025-01-01 10:00:00'
            }
        ]
        self.view.update_transaction_history(receipts)
        self.assertEqual(self.view.history_table.rowCount(), 1)

    def test_update_report_views_with_data(self):
        """Test updating report views."""
        df = pd.DataFrame({
            'item_name': ['Coffee', 'Tea'],
            'category': ['Coffee', 'Tea'],
            'quantity': [10, 5],
            'total': [500.0, 200.0],
            'date': ['2025-01-01', '2025-01-01']
        })
        if hasattr(self.view, 'top_items_canvas'):
            self.view.update_report_views(df)

    def test_update_report_views_empty(self):
        """Test updating report views with empty data."""
        df = pd.DataFrame()
        if hasattr(self.view, 'top_items_canvas'):
            self.view.update_report_views(df)

    def test_show_info_message(self):
        """Test showing info message."""
        with patch('view.QMessageBox.information') as mock_info:
            self.view.show_info('Title', 'Message')
            mock_info.assert_called_once()

    def test_show_warning_message(self):
        """Test showing warning message."""
        with patch('view.QMessageBox.warning') as mock_warning:
            self.view.show_warning('Title', 'Message')
            mock_warning.assert_called_once()

    def test_show_error_message(self):
        """Test showing error message."""
        with patch('view.QMessageBox.critical') as mock_error:
            self.view.show_error('Title', 'Message')
            mock_error.assert_called_once()

    def test_logout_button_emits_signal(self):
        """Test logout button emits signal."""
        signal_received = []
        self.view.logout_requested.connect(lambda: signal_received.append(True))
        self.view.logout_btn.click()
        
        self.assertEqual(len(signal_received), 1)

    def test_clear_crud_form_clears_fields(self):
        """Test clearing CRUD form."""
        if hasattr(self.view, 'name_input'):
            self.view.name_input.setText('Test Item')
            self.view.clear_crud_form()
            self.assertEqual(self.view.name_input.text(), '')

    def test_clear_password_fields(self):
        """Test clearing password fields."""
        if hasattr(self.view, 'old_password_input'):
            self.view.old_password_input.setText('oldpass')
            self.view.new_password_input.setText('newpass')
            self.view.clear_password_fields()
            
            self.assertEqual(self.view.old_password_input.text(), '')
            self.assertEqual(self.view.new_password_input.text(), '')

    def test_update_category_combo(self):
        """Test updating category combo box."""
        if hasattr(self.view, 'category_combo'):
            categories = ['Coffee', 'Tea', 'Pastry']
            self.view.update_category_combo(categories)
            self.assertGreater(self.view.category_combo.count(), 0)

    def test_update_password_combo(self):
        """Test updating password combo."""
        if hasattr(self.view, 'pass_username_combo'):
            usernames = ['admin', 'user1', 'user2']
            self.view.update_password_combo(usernames)
            self.assertEqual(self.view.pass_username_combo.count(), 3)

    def test_update_admin_menu_table(self):
        """Test updating admin menu table."""
        items = [
            (1, 'Espresso', 50.0, 100, 'Coffee'),
            (2, 'Latte', 60.0, 80, 'Coffee'),
        ]
        if hasattr(self.view, 'menu_table'):
            self.view.update_admin_menu_table(items)
            self.assertEqual(self.view.menu_table.rowCount(), 2)

    def test_update_eod_summary_view(self):
        """Test updating EOD summary view."""
        summary = {
            'total_revenue': 500.0,
            'top_items': [('Coffee', 10)],
            'low_stock': [('Pastry', 3)]
        }
        if hasattr(self.view, 'eod_rev_label'):
            self.view.update_eod_summary_view(summary, datetime.now())
            self.assertIn('500.00', self.view.eod_rev_label.text())

    def test_update_past_eod_records(self):
        """Test updating past EOD records."""
        records = [
            {
                'date': '2025-01-01',
                'revenue': 500.0,
                'top_items': [('Coffee', 10)],
                'low_stock': []
            }
        ]
        if hasattr(self.view, 'past_eod_table'):
            self.view.update_past_eod_records(records)
            self.assertEqual(self.view.past_eod_table.rowCount(), 1)


class TestViewSignals(unittest.TestCase):
    """Test view signal emissions."""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.view = CoffeeShopPOSView('Cashier')

    def tearDown(self):
        self.view.close()

    def test_order_item_clicked_signal(self):
        """Test order item clicked signal."""
        signal_received = []
        self.view.order_item_clicked.connect(lambda item_id: signal_received.append(item_id))
        # Simulate clicking a menu card (would be done by user interaction)

    def test_process_payment_requested_signal(self):
        """Test process payment signal."""
        signal_received = []
        self.view.process_payment_requested.connect(lambda: signal_received.append(True))
        # Signal would be emitted when checkout button is clicked

    def test_clear_order_requested_signal(self):
        """Test clear order signal."""
        signal_received = []
        self.view.clear_order_requested.connect(lambda: signal_received.append(True))
        # Signal would be emitted when clear all button is clicked

    def test_tab_changed_signal(self):
        """Test tab changed signal."""
        signal_received = []
        self.view.tab_changed.connect(lambda name: signal_received.append(name))
        # Change tabs to trigger signal
        self.view.tabs.setCurrentIndex(0)


if __name__ == '__main__':
    unittest.main()
