import mysql.connector as conn

def register_parking(cursor: conn.connection.MySQLConnection, vehicle_type, vehicle_number, phone):
    cursor.execute(f"SELECT session_id FROM parking_slots WHERE vehicle_no = '{vehicle_number}' AND check_out IS NULL")
    result = cursor.fetchone()
    if result is not None:
        print("Vehicle already parked")
        session_id = result[0]
        cursor.execute(f"SELECT customer_id FROM customers WHERE parking_session_id = '{session_id}'")
        result = cursor.fetchone()
        customer_id = result[0]
        return session_id, customer_id
    cursor.execute("SELECT MAX(session_id) FROM parking_slots")
    result = cursor.fetchone()
    if result[0] is None:
        latest_session_id = 1
    else:
        latest_session_id = result[0] + 1
    cursor.execute("SELECT slot_id FROM parking_slots WHERE check_out IS NULL")
    result = cursor.fetchall()
    occupied = []
    for row in result:
        occupied.append(row[0])
    slots = [1, 2, 3, 4, 5]
    available_slot = None
    for slot in slots:
        if slot not in occupied:
            available_slot = slot
            break
    if available_slot is None:
        print("No available slots")
        return -1, -1
    cursor.execute(
        f"INSERT INTO parking_slots VALUES ({latest_session_id}, {available_slot}, '{vehicle_type}', '{vehicle_number}', NOW(), NULL, 0.00)",
    )
    cursor.execute("SELECT MAX(customer_id) FROM customers")
    result = cursor.fetchone()
    if result[0] is None:
        latest_cust_id = 1
    else:
        latest_cust_id = result[0] + 1
    cursor.execute(
        f"INSERT INTO customers VALUES ('{latest_cust_id}', '{latest_session_id}', '{phone}')",
    )
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