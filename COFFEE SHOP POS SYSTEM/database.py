import sqlite3
import datetime
import json

class DatabaseManager:
    def __init__(self, db_path='coffee_pos.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._init_db()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def _init_db(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS menu
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT
                                NOT
                                NULL
                                UNIQUE,
                                price
                                REAL
                                NOT
                                NULL,
                                stock
                                INTEGER
                                NOT
                                NULL,
                                category
                                TEXT
                                NOT
                                NULL
                            )
                            """)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS sales
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                item_name
                                TEXT
                                NOT
                                NULL,
                                category
                                TEXT
                                NOT
                                NULL,
                                quantity
                                INTEGER
                                NOT
                                NULL,
                                price
                                REAL
                                NOT
                                NULL,
                                total
                                REAL
                                NOT
                                NULL,
                                sale_date
                                TEXT
                                NOT
                                NULL
                            )
                            """)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS eod_summary
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                report_date
                                TEXT
                                NOT
                                NULL
                                UNIQUE,
                                total_revenue
                                REAL
                                NOT
                                NULL,
                                top_items_json
                                TEXT,
                                low_stock_json
                                TEXT
                            )
                            """)
        self.conn.commit()
        self._seed_data()

    def _seed_data(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM menu")
            if self.cursor.fetchone()[0] == 0:
                initial_items = [
                    ('Brewed Coffee', 75.00, 100, 'Coffee'),
                    ('Latte', 80.00, 150, 'Coffee'),
                    ('Frappuccino', 180.00, 120, 'Coffee'),
                    ('Mocha', 95.00, 90, 'Coffee'),
                    ('Croissant', 60.00, 50, 'Pastry'),
                    ('Blueberry Muffin',170.00, 60, 'Pastry'),
                    ('Iced Tea', 105.00, 80, 'Beverage'),
                    ('Fries', 40.00, 30, 'Food'),
                ]
                self.cursor.executemany("INSERT INTO menu (name, price, stock, category) VALUES (?, ?, ?, ?)",
                                        initial_items)
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error seeding data: {e}")

    def create_menu_item(self, name, price, stock, category):
        try:
            self.cursor.execute("INSERT INTO menu (name, price, stock, category) VALUES (?, ?, ?, ?)",
                                (name, price, stock, category))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False

    def read_menu_items(self):
        self.cursor.execute("SELECT id, name, price, stock, category FROM menu ORDER BY name ASC")
        return self.cursor.fetchall()

    def read_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM menu ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def update_menu_item(self, item_id, name, price, stock, category):
        try:
            self.cursor.execute("UPDATE menu SET name=?, price=?, stock=?, category=? WHERE id=?",
                                (name, price, stock, category, item_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def delete_menu_item(self, item_id):
        try:
            self.cursor.execute("DELETE FROM menu WHERE id=?", (item_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def get_item_details(self, item_id):
        self.cursor.execute("SELECT name, price, category FROM menu WHERE id = ?", (item_id,))
        return self.cursor.fetchone()

    def record_sale(self, order_items, sale_date):
        try:
            for item in order_items:
                name = item['name']
                qty = item['qty']
                price = item['price']
                category = item['category']
                total = price * qty

                self.cursor.execute(
                    "INSERT INTO sales (item_name, category, quantity, price, total, sale_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, category, qty, price, total, sale_date)
                )
                self.cursor.execute("UPDATE menu SET stock = stock - ? WHERE name = ?", (qty, name))
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def get_sales_data_for_report(self, days_back=30):
        date_limit = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            f"SELECT item_name, category, quantity, total, strftime('%Y-%m-%d', sale_date) FROM sales WHERE sale_date >= ?",
            (date_limit,))
        return self.cursor.fetchall()

    def end_of_day_summary(self, target_date_str):
        self.cursor.execute(
            "SELECT SUM(total) FROM sales WHERE strftime('%Y-%m-%d', sale_date) = ?", (target_date_str,))
        total_revenue = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("""
                            SELECT item_name, SUM(quantity) as total_qty
                            FROM sales
                            WHERE strftime('%Y-%m-%d', sale_date) = ?
                            GROUP BY item_name
                            ORDER BY total_qty DESC LIMIT 3
                            """, (target_date_str,))
        top_items = self.cursor.fetchall()

        self.cursor.execute("""
                            SELECT name, stock
                            FROM menu
                            WHERE stock < 10
                            ORDER BY stock ASC
                            """)
        low_stock = self.cursor.fetchall()

        return {
            'date': target_date_str,
            'total_revenue': total_revenue,
            'top_items': top_items,
            'low_stock': low_stock
        }

    def save_eod_summary(self, summary_data):
        try:
            top_items_json = json.dumps(summary_data['top_items'])
            low_stock_json = json.dumps(summary_data['low_stock'])
            self.cursor.execute(
                "INSERT INTO eod_summary (report_date, total_revenue, top_items_json, low_stock_json) VALUES (?, ?, ?, ?)",
                (summary_data['date'], summary_data['total_revenue'], top_items_json, low_stock_json)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error saving EOD summary: {e}")
            return False

    def get_past_eod_records(self):
        self.cursor.execute(
            "SELECT report_date, total_revenue, top_items_json, low_stock_json FROM eod_summary ORDER BY report_date DESC"
        )
        records = self.cursor.fetchall()
        parsed_records = []
        for date, revenue, top_json, low_json in records:
            parsed_records.append({
                'date': date,
                'revenue': revenue,
                'top_items': json.loads(top_json),
                'low_stock': json.loads(low_json)
            })
        return parsed_records

    def clear_all_sales_data(self):
        try:
            self.cursor.execute("DELETE FROM sales")
            self.cursor.execute("DELETE FROM eod_summary")
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False