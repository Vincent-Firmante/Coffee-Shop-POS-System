import pandas as pd
from PyQt5.QtWidgets import QDialog, QMessageBox
from view import LoginDialog, CoffeeShopPOSView


class AppController:

    def __init__(self, model, app):
        self.model = model
        self.app = app
        self.login_dialog = None
        self.main_window = None
        self.init_login_flow()

    def init_login_flow(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_dialog = LoginDialog()
        self.login_dialog.login_attempted.connect(self.handle_login_attempt)

        if self.login_dialog.exec_() != QDialog.Accepted:
            self.app.quit()

    def handle_login_attempt(self, username, password):
        if self.model.authenticate(username, password):
            self.login_dialog.accept()
            self.init_main_window()
        else:
            self.login_dialog.show_login_error("Invalid username or password.")

    def init_main_window(self):
        self.main_window = CoffeeShopPOSView(self.model.user_role)

        self.main_window.logout_requested.connect(self.handle_logout)
        self.main_window.order_item_clicked.connect(self.handle_add_to_order)
        self.main_window.clear_order_requested.connect(self.handle_clear_order)
        self.main_window.process_payment_requested.connect(self.handle_process_payment)
        self.main_window.eod_action_requested.connect(self.handle_save_eod)
        self.main_window.clear_sales_requested.connect(self.handle_clear_sales_data)
        self.main_window.password_change_requested.connect(self.handle_change_password)
        self.main_window.tab_changed.connect(self.handle_tab_change)


        self.main_window.menu_item_added.connect(self.handle_add_menu_item)
        self.main_window.menu_item_updated.connect(self.handle_update_menu_item)
        self.main_window.menu_item_deleted.connect(self.handle_delete_menu_item)

        # --- Initial Load ---
        self.refresh_all_data()
        self.main_window.show()

    def refresh_all_data(self):
        menu_items = self.model.get_menu_items()
        self.main_window.update_menu_display(menu_items)
        self.main_window.update_order_summary(self.model.current_order, self.model.calculate_order_total())

        if self.model.user_role == 'Manager':
            self.main_window.update_admin_menu_table(menu_items)
            self.main_window.update_category_combo(self.model.get_menu_categories())
            self.main_window.update_password_combo(sorted(self.model.credentials.keys()))

    def handle_tab_change(self, tab_name):
        if "End of Day" in tab_name:
            self.handle_eod_refresh()
        elif "Sales Reports" in tab_name:
            self.handle_report_refresh()

    def handle_logout(self):
        self.model.user_role = None
        self.model.clear_order()
        self.main_window.show_info("Logged Out", "You have been successfully logged out.")
        self.init_login_flow()

    def handle_add_to_order(self, item_id):
        success, message = self.model.add_item_to_order(item_id)
        if success:
            self.main_window.update_order_summary(self.model.current_order, self.model.calculate_order_total())
        else:
            self.main_window.show_warning("Order Error", message)

    def handle_clear_order(self):
        self.model.clear_order()
        self.main_window.update_order_summary(self.model.current_order, self.model.calculate_order_total())

    def handle_process_payment(self):
        if not self.model.current_order:
            self.main_window.show_warning("Warning", "The order is empty.")
            return

        success, result = self.model.process_order()

        if success:
            total = result
            self.main_window.show_info("Success", f"Payment processed successfully!\nTotal: ₱{total:.2f}")
            self.refresh_all_data()
        else:
            self.main_window.show_error("Error", "Failed to record sale. Check stock levels or database connection.")

    def handle_add_menu_item(self, name, price, stock, category):
        if self.model.create_item(name, price, stock, category):
            self.main_window.show_info("Success", f"Item '{name}' added to menu.")
            self.main_window.clear_crud_form()
            self.refresh_all_data()
        else:
            self.main_window.show_error("Error", "Item name already exists or database error.")

    def handle_update_menu_item(self, item_id, name, price, stock, category):
        if self.model.update_item(item_id, name, price, stock, category):
            self.main_window.show_info("Success", f"Item ID {item_id} updated successfully.")
            self.main_window.clear_crud_form()
            self.refresh_all_data()
        else:
            self.main_window.show_error("Error", f"Failed to update item ID {item_id}. Item name may already exist.")

    def handle_delete_menu_item(self, item_id):
        if self.model.delete_item(item_id):
            self.main_window.show_info("Success", "Item deleted.")
            self.main_window.clear_crud_form()
            self.refresh_all_data()
        else:
            self.main_window.show_error("Error", "Failed to delete item.")

    def handle_report_refresh(self):
        raw_data = self.model.get_all_sales_data(days_back=30)
        sales_df = pd.DataFrame(raw_data, columns=['item_name', 'category', 'quantity', 'total', 'date'])

        if not sales_df.empty:
            sales_df['quantity'] = pd.to_numeric(sales_df['quantity'])
            sales_df['total'] = pd.to_numeric(sales_df['total'])

        self.main_window.update_report_views(sales_df)

    def handle_eod_refresh(self):
        summary = self.model.generate_eod_summary()
        historical_records = self.model.get_historical_eod_records()
        self.main_window.update_eod_summary_view(summary, self.model.current_pos_date)
        self.main_window.update_past_eod_records(historical_records)

    def handle_save_eod(self):
        summary = self.model.generate_eod_summary()

        if summary['total_revenue'] == 0:
            reply = QMessageBox.question(self.main_window, 'Confirm End of Day',
                                         f"No sales recorded for {self.model.current_pos_date.strftime('%Y-%m-%d')}. Do you still want to close the day and start the next day?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        status, saved_summary = self.model.save_eod_and_advance_day()

        if status == "Success":
            self.main_window.show_info("End of Day Success",
                                       f"EOD for {saved_summary['date']} saved. Revenue: ₱{saved_summary['total_revenue']:.2f}.\n\n"
                                       f"Starting a New POS Day: **{self.model.current_pos_date.strftime('%Y-%m-%d')}**")
        elif status == "Already Saved":
            self.main_window.show_error("Error",
                                        f"EOD Summary for {saved_summary['date']} is **already saved**. Cannot save twice for the same day.")

        self.refresh_all_data()  # Refreshes menu (stock), POS, and EOD tab content
        self.handle_eod_refresh()
        self.handle_report_refresh()

    def handle_clear_sales_data(self):
        if self.model.clear_historical_data():
            self.main_window.show_info("Success", "All historical sales data and EOD summaries have been cleared.")
            self.refresh_all_data()
            self.handle_eod_refresh()
            self.handle_report_refresh()
        else:
            self.main_window.show_error("Error", "Failed to clear data.")

    def handle_change_password(self, username, old_pass, new_pass, confirm_pass):

        status = self.model.update_password(username, old_pass, new_pass)

        if status == "Success":
            self.main_window.show_info("Success", f"Password for user '{username}' has been successfully changed.")
            self.main_window.clear_password_fields()
        elif status == "Incorrect old password":
            self.main_window.show_error("Error", "The Old Password entered is incorrect.")
        else:  # Covers "User not found" or other errors
            self.main_window.show_error("Error", f"Failed to change password: {status}")