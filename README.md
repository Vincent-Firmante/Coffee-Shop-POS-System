Firmante, Vincent C
: Alicaway, Keisha M.
: Baon, John Aeron I.

# Coffee Shop POS System

A simple Point-of-Sale (POS) system built with Python and PyQt5 for managing coffee shop operations.

#Features

- **Point of Sale**: Add items to orders and process payments
- **Menu Management**: Create, update, and delete menu items (Manager only)
- **Transaction History**: View all sales receipts
- **Sales Reports**: Charts showing top items, revenue by category, and daily trends (Manager only)
- **End-of-Day**: Generate daily summaries and manage EOD records (Manager only)
- **User Management**: Create users, change passwords, and manage cashier access (Manager only)
- **Cashier Access Control**: Restrict cashier access to specific features

#Requirements

- Python 3.7+
- PyQt5
- pandas
- matplotlib

## Installation

pip install PyQt5 pandas matplotlib

## Running the Application

python main.py

#Default User's

| Username | Password  | Role    |
|----------|-----------|---------|
| manager  | admin123  | Manager |
| cashier  | password  | Cashier |

## Database

The application uses SQLite3 (`coffee_pos.db`) for persistent storage:
- `menu` - Menu items and inventory
- `sales` - Sales transactions
- `users` - User accounts and permissions
- `receipts` - Receipt records
- `eod_summary` - End-of-day summaries

## Project Structure

├── main.py          # Application entry point
├── view.py          # UI components
├── model.py         # Business logic
├── controller.py    # Event handling
├── database.py      # Database operations
├── test_*.py        # Unit tests
└── README.md        # This file

## Workflow

### Cashier
1. Login with cashier account
2. Select menu categories and add items to order
3. Adjust and remove items as needed
4. Process payment to complete the sale
5. View transaction history

### Manager
1. Login with manager account
2. Navigate to Menu Management to add/update/delete items
3. Check Sales Reports for performance metrics
4. Use End of Day to close the day and view summaries
5. Manage user accounts and permissions in Settings



Managers can control cashier access to:
- View Transaction History
- View Sales Reports
- View End-of-Day Summaries

Restricted tabs appear disabled and cannot be accessed.

## Testing

Run unit tests:

python -m pytest

Test files:
- `test_controller.py` - Controller tests
- `test_view.py` - UI component tests
- `test_model.py` - Business logic tests
- `test_database.py` - Database operation tests

