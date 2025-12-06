import unittest
from controller import AppController


class DummyModel:
    def __init__(self):
        self.current_order = {}
        self.user_role = 'Cashier'
    def add_item_to_order(self, item_id):
        return True, 'added'
    def calculate_order_total(self):
        return 0
    def remove_item_from_order(self, item_id):
        return True
    def clear_order(self):
        self.current_order = {}
    def process_order(self):
        return True, 0.0, None
    def get_menu_items(self):
        return []
    def get_menu_categories(self):
        return []
    def get_all_receipts(self, limit=None):
        return []
    def delete_receipt(self, uuid):
        return True


class DummyView:
    def __init__(self):
        self.updated = False
    def update_order_summary(self, *a, **k):
        self.updated = True
    def show_warning(self, title, message):
        self.last_warning = (title, message)
    def show_info(self, title, message):
        self.last_info = (title, message)
    def update_menu_display(self, items):
        self.menu = items
    def show_error(self, title, message):
        self.last_error = (title, message)


class TestController(unittest.TestCase):
    def setUp(self):
        self._orig_init = AppController.init_login_flow
        AppController.init_login_flow = lambda self: None
        self.model = DummyModel()
        self.controller = AppController(self.model, app=None)
        self.view = DummyView()
        self.controller.main_window = self.view

    def tearDown(self):
        AppController.init_login_flow = self._orig_init

    def test_handle_add_to_order_success(self):
        self.model.current_order = {}
        self.controller.handle_add_to_order(1)
        self.assertTrue(self.view.updated)

    def test_handle_remove_order_item(self):
        self.controller.handle_remove_order_item(1)
        self.assertTrue(self.view.updated)

    def test_handle_clear_order(self):
        self.model.current_order = {1: {'name':'a','price':1,'qty':1}}
        self.controller.handle_clear_order()
        self.assertEqual(self.model.current_order, {})

    def test_handle_process_payment_empty(self):
        self.model.current_order = {}
        self.controller.handle_process_payment()
        self.assertEqual(self.view.last_warning[0], 'Warning')

    def test_handle_delete_receipt(self):
        self.controller.handle_delete_receipt('uuid')
        self.assertTrue(hasattr(self.view, 'last_info'))


if __name__ == '__main__':
    unittest.main()
