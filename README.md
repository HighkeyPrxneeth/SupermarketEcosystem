# Supermarket Ecosystem Management 
## Overview

This project simulates a modern supermarket ecosystem that integrates customer shopping with automated parking management. Customers register their vehicle upon arrival, shop using a web interface, and receive a final bill that includes both their purchases and a dynamically calculated parking fee, potentially discounted based on their spending. An admin panel provides insights into sales, inventory, and parking status.

The system is built primarily as a demonstration using Flask and MySQL, focusing on the interaction between different components rather than being a production-ready application.

## Features

**Customer-Facing:**

1.  **Vehicle Registration:** Customers enter their vehicle number (Bike/Car) and phone number on the landing page.
2.  **Parking Slot Assignment:** The system attempts to find and assign an available parking slot (from a total of 8 slots).
3.  **Shopping Interface:**
    *   Displays available products fetched from the database.
    *   Interactive cart functionality (add, remove, update quantity) managed client-side.
4.  **Checkout Process:**
    *   Summarizes the order (subtotal, tax, potential coupon discounts).
    *   Simulates payment method selection (Card, UPI, Wallet, Cash).
    *   Processes the order, updating product quantities and recording the transaction.
5.  **Integrated Parking Bill:**
    *   Calculates parking duration based on check-in time.
    *   Applies hourly parking rates (different for bikes/cars).
    *   Applies discounts to the parking fee based on the total purchase amount (e.g., free parking over ₹500, 50% off over ₹300).
    *   Generates a final receipt showing purchased items, purchase total, parking details, parking fee, and grand total.

**Admin Panel:**

1.  **Secure Login:** Basic username/password protection for admin access.
2.  **Dashboard Overview:** Displays key metrics using summary cards:
    *   Total Sales Amount
    *   Total Transactions
    *   Total Discounts Given
    *   Average Purchase Amount
3.  **Parking Status:**
    *   Visual representation of all 8 parking slots (Available/Occupied).
    *   Details for occupied slots (Vehicle No, Type, Check-in Time).
    *   Pie/Doughnut chart showing occupancy ratio.
4.  **Restock Suggestions:** Lists products whose current quantity is below their defined reorder level.
5.  **Sales Insights:**
    *   Bar chart showing the Top 5 most sold products by quantity.
    *   Bar chart displaying total sales revenue generated per product category.

## Technology Stack

*   **Backend:** Python, Flask
*   **Database:** MySQL (`mysql-connector-python` library)
*   **Frontend:** HTML, CSS, JavaScript
*   **Charting:** Chart.js

## Core Concepts & Implementation Highlights

1.  **Flask Backend:** Serves as the core web server, handling HTTP requests, routing (`@app.route`), rendering HTML templates (Jinja2), managing sessions (for admin login), and interacting with the database.

2.  **Database Interaction (`init.py`, `db.py`):**
    *   `init.py`: Handles the initial database and table creation, and populates tables with seed data from CSV files upon startup (useful for development). Includes logic to drop and recreate the database.
    *   `db.py`: Contains modular functions for all database operations (registering parking, listing products, making transactions, fetching admin data, etc.), promoting cleaner code in `app.py`.

3.  **Customer Workflow (`index` -> `shop` -> `checkout` -> `parking_bill`):**
    *   Vehicle and phone data entered on the index page are passed as URL parameters to the `/shop` route.
    *   The `register_parking` function in `db.py` finds an available slot (from 1 to 8), creates records in `parking_slots` and `customers`, linking them via `session_id` and `customer_id`.
    *   Shopping cart state is managed client-side using JavaScript (`shop.js`) and temporarily stored in `sessionStorage` before checkout.
    *   Checkout data is sent via Fetch API (`checkout.js`) to the `/process-payment` endpoint, which calls `make_transaction` in `db.py` to update `transactions`, `sales_details`, and `products` tables.
    *   The `/parking-bill` route uses the `customer_id` to retrieve parking (`get_customer_parking_info`), transaction (`get_latest_transaction`), and purchase details (`get_purchased_items`) to calculate the final bill, including time-based parking fees and purchase-based discounts.

4.  **Admin Panel (`/admin`, `db.py`):**
    *   Uses Flask's session mechanism for basic login state (`session['admin_logged_in']`).
    *   An `@admin_required` decorator protects admin routes, redirecting unauthorized users to the login page.
    *   The `/admin` route calls various `get_...` functions from `db.py` to fetch aggregated data (sales summary, parking status, restock needs, top products, category sales).
    *   Data is passed to the `admin_dashboard.html` template.
    *   Client-side JavaScript uses Chart.js to render interactive charts based on the data passed from Flask (using `| tojson` filter in the template).

5.  **Parking Management Logic:**
    *   The `parking_slots` table tracks individual parking sessions with check-in/check-out times (though check-out is only simulated at billing time).
    *   Slot availability is determined by querying `parking_slots` for entries where `check_out IS NULL`.
    *   The calculation in `/parking-bill` uses `datetime` math to find the duration and applies tiered discounts based on the linked transaction's total.

## Database Schema

*   **`parking_slots`**: Stores details about each parking session (slot ID, vehicle, times, fee).
*   **`customers`**: Links a customer (identified by phone) to their active parking session.
*   **`transactions`**: Records overall sales transactions (customer ID, total, discount, time).
*   **`products`**: Stores product information (name, price, current quantity, category, reorder level).
*   **`sales_details`**: Links products and quantities sold to specific transactions (line items).
*   **`restocks`**: (Data loaded but not actively used in current features) Tracks product restocking events.

## Potential Future Enhancements

*   Implement a proper vehicle check-out process to update `parking_slots.check_out`.
*   Add actual inventory management actions (e.g., admin button to mark items as restocked).
*   Implement user accounts for customers instead of just phone numbers.
*   Integrate a real payment gateway API.
*   Add more sophisticated analytics (e.g., sales trends over time, customer purchase history).
*   Implement coupon code validation logic on the backend.
