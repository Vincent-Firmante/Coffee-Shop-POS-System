import datetime
from database import DatabaseManager


class AppModel:
    def __init__(self):
        self.db = DatabaseManager()

        self.credentials = {
            'manager': {'password': 'admin123', 'role': 'Manager'},
            'Cashier': {'password': 'password', 'role': 'Cashier'}
        }
        self.user_role = None
        self.current_pos_date = datetime.date.today()
        self.current_order = {}

    def authenticate(self, username, password):
        username = username.lower().strip()
        password = password.strip()
        if username in self.credentials:
            user_data = self.credentials[username]
            if user_data['password'] == password:
                self.user_role = user_data['role']
                return True
        self.user_role = None
        return False

    def update_password(self, username, old_password, new_password):

        username = username.lower().strip()

        if username not in self.credentials:
            return "User not found"

        if self.credentials[username]['password'] != old_password:
            return "Incorrect old password"

        if old_password == new_password:
            return "New password cannot be the same as old password"

        self.credentials[username]['password'] = new_password
        return "Success"

    def add_item_to_order(self, item_id):
        item_details = self.db.get_item_details(item_id)
        if not item_details:
            return False, "Item not found in menu."

        name, price, category = item_details

        if item_id in self.current_order:
            self.current_order[item_id]['qty'] += 1
        else:
            self.current_order[item_id] = {'name': name, 'price': price, 'qty': 1, 'category': category}

        return True, "Item added"

    def calculate_order_total(self):
        total = sum(item['price'] * item['qty'] for item in self.current_order.values())
        return total

    def process_order(self):
        if not self.current_order:
            return False

        order_list = list(self.current_order.values())
        sale_date = self.current_pos_date.strftime('%Y-%m-%d') + datetime.datetime.now().strftime(' %H:%M:%S')

        success = self.db.record_sale(order_list, sale_date)

        if success:
            total = self.calculate_order_total()
            self.current_order = {}  # Clear the order on success
            return True, total
        return False, 0

    def clear_order(self):
        self.current_order = {}

    def get_menu_items(self):
        return self.db.read_menu_items()

    def get_menu_categories(self):
        return self.db.read_categories()

    def get_all_sales_data(self, days_back=30):
        return self.db.get_sales_data_for_report(days_back)

    def generate_eod_summary(self):
        current_date_str = self.current_pos_date.strftime('%Y-%m-%d')
        return self.db.end_of_day_summary(current_date_str)

    def save_eod_and_advance_day(self):
        summary = self.generate_eod_summary()

        if not self.db.save_eod_summary(summary):
            return "Already Saved", summary

        self.current_pos_date += datetime.timedelta(days=1)
        return "Success", summary

    def get_historical_eod_records(self):
        return self.db.get_past_eod_records()

    def create_item(self, name, price, stock, category):
        return self.db.create_menu_item(name, price, stock, category)

    def update_item(self, item_id, name, price, stock, category):
        return self.db.update_menu_item(item_id, name, price, stock, category)

    def delete_item(self, item_id):
        return self.db.delete_menu_item(item_id)

    def clear_historical_data(self):
        return self.db.clear_all_sales_data()