Coffee Shop POS System

A simple desktop Point of Sale (POS) application for a coffee shop, built with Python and PyQt5.

Sales: Quick and easy order processing with a clear interface.

Inventory: Manage and update menu items and prices.

Database: Uses SQLite for reliable, local data storage.

Reporting: Generate End-of-Day (EOD) summaries and view basic sales charts (pandas/matplotlib).

Data Security: Protected function for clearing historical data.

Setup & Run

Requirements

You need Python 3 and the following libraries: PyQt5, pandas, matplotlib.

Quick Install

Get the code:

git clone [your-repo-link]
cd coffee-pos-system

Install tools:

pip install PyQt5 pandas matplotlib

Usage

Launch:

python coffee.py


Database: The app automatically creates coffee_pos.db for storage.

Start: Use the Products tab to set up your menu, then the Sales tab to take orders.

Structure

This application is primarily a single Python script that uses internal classes like DatabaseManager, SalesTab, and ReportingTab for organization.
