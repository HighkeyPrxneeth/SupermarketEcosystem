import mysql.connector as conn
import datetime

def register_parking(cursor: conn.connection.MySQLConnection, vehicle_type, vehicle_number, phone):
    # Check if vehicle is already parked
    cursor.execute(f"SELECT session_id FROM parking_slots WHERE vehicle_no = '{vehicle_number}' AND check_out IS NULL")
    result = cursor.fetchone()
    if result is not None:
        print("Vehicle already parked")
        session_id = result[0]
        cursor.execute(f"SELECT customer_id FROM customers WHERE parking_session_id = '{session_id}'")
        result = cursor.fetchone()
        customer_id = result[0] if result else None # Handle case where customer might not exist?
        return session_id, customer_id

    # Get latest session ID
    cursor.execute("SELECT MAX(session_id) FROM parking_slots")
    result = cursor.fetchone()
    latest_session_id = (result[0] or 0) + 1

    # Get occupied slots
    cursor.execute("SELECT slot_id FROM parking_slots WHERE check_out IS NULL")
    result = cursor.fetchall()
    occupied = [row[0] for row in result] #


    total_num_slots = 8
    all_slots = list(range(1, total_num_slots + 1)) 

    available_slot = None

    for slot in all_slots:
        if slot not in occupied:
            available_slot = slot
            break

    if available_slot is None:
        print("No available slots")
        return -1, -1 

    insert_slot_query = """
        INSERT INTO parking_slots (session_id, slot_id, slot_type, vehicle_no, check_in, fee)
        VALUES (%s, %s, %s, %s, NOW(), 0.00)
    """
    cursor.execute(insert_slot_query, (latest_session_id, available_slot, vehicle_type, vehicle_number))


    cursor.execute("SELECT MAX(customer_id) FROM customers")
    result = cursor.fetchone()
    latest_cust_id = (result[0] or 0) + 1

    insert_cust_query = """
        INSERT INTO customers (customer_id, parking_session_id, phone)
        VALUES (%s, %s, %s)
    """
    cursor.execute(insert_cust_query, (latest_cust_id, latest_session_id, phone))


    return latest_session_id, latest_cust_id

def list_products(cursor: conn.connection.MySQLConnection):
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    products = []
    for row in result:
        product = {
            'product_id': row[0],
            'name': row[1],
            'price': row[2],
            'quantity': row[3],
            'category': row[4]
        }
        products.append(product)
    return products

def make_transaction(cursor: conn.connection.MySQLConnection, order_data, customer_id):
    cursor.execute("SELECT MAX(sale_id) FROM transactions")
    result = cursor.fetchone()
    if result[0] is None:
        sale_id = 1
    else:
        sale_id = result[0] + 1
    total = order_data['summary']['total']
    discount = round(order_data['summary']['discount'], 2)
    cursor.execute(
        f"INSERT INTO transactions VALUES ('{sale_id}', '{customer_id}', {discount}, '{total}', NOW())",
    )
    print(f"Inserted into transactions: {sale_id}, {customer_id}, {discount}, {total}")
    for item in order_data['items']:
        product_id = item['id']
        quantity = item['quantity']
        subtotal = item['subtotal']
        cursor.execute(
            f"INSERT INTO sales_details VALUES ('{sale_id}', '{product_id}', {quantity}, {subtotal})",
        )
        cursor.execute(
            f"UPDATE products SET quantity = quantity - {quantity} WHERE product_id = '{product_id}'",
        )
    print(f"Updated products with sale_id: {sale_id}")
    cursor.execute(
        f"COMMIT",
    )
    return sale_id

def get_parking_session_by_customer_id(cursor: conn.connection.MySQLConnection, customer_id):
    cursor.execute("SELECT parking_session_id FROM customers WHERE customer_id = %s", (customer_id,))
    return cursor.fetchone()

def get_latest_customer(cursor: conn.connection.MySQLConnection):
    cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1")
    return cursor.fetchone()

def get_customer_parking_info(cursor: conn.connection.MySQLConnection, customer_id):
    cursor.execute(
        """SELECT p.check_in, p.vehicle_no, p.slot_id, p.slot_type, p.session_id
           FROM parking_slots p 
           JOIN customers c ON p.session_id = c.parking_session_id 
           WHERE c.customer_id = %s AND p.check_out IS NULL""", 
        (customer_id,)
    )
    return cursor.fetchone()

def get_latest_transaction(cursor: conn.connection.MySQLConnection, customer_id):
    cursor.execute(
        """SELECT t.sale_id, t.total, t.discount
           FROM transactions t
           WHERE t.customer_id = %s
           ORDER BY t.time DESC
           LIMIT 1""",
        (customer_id,)
    )
    return cursor.fetchone()

def get_customer_phone(cursor: conn.connection.MySQLConnection, customer_id):
    cursor.execute(
        "SELECT phone FROM customers WHERE customer_id = %s",
        (customer_id,)
    )
    return cursor.fetchone()

def get_purchased_items(cursor: conn.connection.MySQLConnection, sale_id):
    cursor.execute(
        """SELECT p.name, s.quantity, s.subtotal
           FROM sales_details s
           JOIN products p ON s.product_id = p.product_id
           WHERE s.sale_id = %s""",
        (sale_id,)
    )
    purchased_items = []
    for name, quantity, subtotal in cursor.fetchall():
        purchased_items.append({
            'name': name,
            'quantity': quantity,
            'subtotal': float(subtotal)
        })
    return purchased_items

def get_sales_summary(cursor: conn.connection.MySQLConnection):
    """Gets overall sales statistics."""
    try:
        # Total Sales Amount
        cursor.execute("SELECT SUM(total) FROM transactions")
        total_sales = cursor.fetchone()[0] or 0.0

        # Total Discount Given
        cursor.execute("SELECT SUM(discount) FROM transactions")
        total_discount = cursor.fetchone()[0] or 0.0

        # Number of Transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        num_transactions = cursor.fetchone()[0] or 0

        # Average Purchase Amount
        avg_purchase = total_sales / num_transactions if num_transactions > 0 else 0.0

        return {
            'total_sales': float(total_sales),
            'total_discount': float(total_discount),
            'num_transactions': num_transactions,
            'avg_purchase': float(avg_purchase)
        }
    except Exception as e:
        print(f"Error in get_sales_summary: {e}")
        return {
            'total_sales': 0.0,
            'total_discount': 0.0,
            'num_transactions': 0,
            'avg_purchase': 0.0
        }

def get_restock_suggestions(cursor: conn.connection.MySQLConnection):
    """Finds products below their reorder level."""
    try:
        cursor.execute(
            """SELECT product_id, name, quantity, reorder_level, category
               FROM products
               WHERE quantity < reorder_level
               ORDER BY (reorder_level - quantity) DESC"""
        )
        suggestions = []
        for row in cursor.fetchall():
            suggestions.append({
                'id': row[0],
                'name': row[1],
                'current_stock': row[2],
                'reorder_level': row[3],
                'category': row[4],
                'needed': row[3] - row[2]  # Calculate how many are needed
            })
        return suggestions
    except Exception as e:
        print(f"Error in get_restock_suggestions: {e}")
        return []

def get_parking_status(cursor: conn.connection.MySQLConnection):
    """Gets the current status of all parking slots."""
    total_slots = 8


    slots = {i: {'status': 'Available', 'details': None} for i in range(1, total_slots + 1)}
    try:
        # Fetch occupied slots
        cursor.execute(
            """SELECT slot_id, vehicle_no, check_in, slot_type
               FROM parking_slots
               WHERE check_out IS NULL"""
        )
        occupied_slots = cursor.fetchall()
        for slot_id, vehicle_no, check_in, slot_type in occupied_slots:
            if slot_id in slots: # Check if fetched slot_id is within our expected range
                slots[slot_id]['status'] = 'Occupied'
                slots[slot_id]['details'] = {
                    'vehicle_no': vehicle_no,
                    # Format check_in time for better display
                    'check_in': check_in.strftime('%Y-%m-%d %H:%M') if isinstance(check_in, datetime.datetime) else str(check_in),
                    'type': slot_type
                }
        return slots
    except Exception as e:
        print(f"Error in get_parking_status: {e}")
        # Return default status if error occurs
        return {i: {'status': 'Unknown', 'details': None} for i in range(1, total_slots + 1)}


def get_most_sold_products(cursor: conn.connection.MySQLConnection, limit=5):
    """Gets the top N most sold products by quantity."""
    try:
        cursor.execute(
            """SELECT p.name, SUM(sd.quantity) as total_quantity, p.category
               FROM sales_details sd
               JOIN products p ON sd.product_id = p.product_id
               GROUP BY sd.product_id, p.name, p.category
               ORDER BY total_quantity DESC
               LIMIT %s""",
            (limit,)
        )
        products = []
        for name, quantity, category in cursor.fetchall():
            products.append({
                'name': name,
                'total_quantity': int(quantity),
                'category': category
            })
        return products
    except Exception as e:
        print(f"Error in get_most_sold_products: {e}")
        return []

def get_sales_by_category(cursor: conn.connection.MySQLConnection):
    """Gets total sales amount per product category."""
    try:
        cursor.execute(
            """SELECT p.category, SUM(sd.subtotal) as category_sales
               FROM sales_details sd
               JOIN products p ON sd.product_id = p.product_id
               GROUP BY p.category
               ORDER BY category_sales DESC"""
        )
        categories = []
        for category, total_sales in cursor.fetchall():
             categories.append({
                'category': category,
                'total_sales': float(total_sales)
             })
        return categories
    except Exception as e:
        print(f"Error in get_sales_by_category: {e}")
        return []
