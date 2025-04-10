from flask import Flask, render_template, request, redirect
from mysql import connector as conn
from mysql.connector import errorcode
import datetime

from init import *
from db import *

try:
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost', database='project_db')
    cursor = cnx.cursor()
    del_db(cnx.cursor())
    init_db(cursor)
    create_tables(cursor)
    insert_data(cursor)
except conn.errors.ProgrammingError:
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost')
    cursor = cnx.cursor()
    init_db(cursor)
    create_tables(cursor)
    insert_data(cursor)
    

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    vehicle_number = request.args.get('vehicle_number')
    phone = "+91" + request.args.get('phone', '')
    vehicle_type = request.args.get('vehicle_type', 'car')
    
    # Handle case when coming from another page with customer ID
    customer_id = request.args.get('cust')
    if customer_id:
        # Look up existing session for this customer
        cursor.execute("SELECT parking_session_id FROM customers WHERE customer_id = %s", (customer_id,))
        result = cursor.fetchone()
        if result:
            session_id = result[0]
            return render_template('shop.html', 
                                  session=session_id, 
                                  cust=customer_id, 
                                  products=list_products(cursor), 
                                  vehicle_number=vehicle_number, 
                                  phone=phone)
    
    # Regular flow for new customers
    if not vehicle_number or not phone:
        return redirect('/')
        
    session_id, cust_id = register_parking(cursor, vehicle_type, vehicle_number, phone)
    if session_id == -1:
        return render_template('shop.html', error="No available slots")
    
    # IMPORTANT: Commit the transaction to save the customer data
    cnx.commit()
        
    return render_template('shop.html', 
                          session=session_id, 
                          cust=cust_id, 
                          products=list_products(cursor), 
                          vehicle_number=vehicle_number, 
                          phone=phone)

@app.route('/checkout')
def checkout():
    # Get the customer ID from the request parameters
    customer_id = request.args.get('cust')
    
    # If no customer ID, try to get the latest registered customer
    if not customer_id:
        try:
            # Get the most recent customer
            cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                customer_id = result[0]
                print(f"Using latest customer ID: {customer_id}")
        except Exception as e:
            print(f"Error retrieving customer: {e}")
    
    # This will render the checkout page with the customer ID
    return render_template('checkout.html', cust=customer_id)

@app.route('/process-payment', methods=['POST'])
def process_payment():
    if request.json:
        order_data = request.json
        customer_id = request.args.get('cust', 1)  # Default to 1 if not provided
        # Get the total amount and discount from the order data
        total_amount = order_data['summary']['total']
        discount = order_data['summary'].get('discount', 0)
        discount_rate = 0  # Default discount rate
        
        # If discount exists, calculate the discount rate (0-1 range)
        if discount > 0:
            discount_rate = discount / order_data['summary']['subtotal']
        
        # Insert into transactions table and get sale_id
        sale_id = make_transaction(cursor, order_data, customer_id)
        
        return {
            'status': 'success',
            'message': 'Payment processed successfully',
            'order_id': sale_id
        }
    else:
        return {
            'status': 'error',
            'message': 'No data received'
        }, 400

@app.route('/parking-bill')
def parking_bill():
    # Get the customer ID from the request parameters
    customer_id = request.args.get('cust')
    print(f"Parking bill request received with customer_id: {customer_id}")
    
    if not customer_id:
        print("No customer ID provided")
        return redirect('/shop')
    

    # Get customer parking information
    cursor.execute(
        """SELECT p.check_in, p.vehicle_no, p.slot_id, p.slot_type, p.session_id
            FROM parking_slots p 
            JOIN customers c ON p.session_id = c.parking_session_id 
            WHERE c.customer_id = %s AND p.check_out IS NULL""", 
        (customer_id,)
    )
    
    parking_info = cursor.fetchone()
    if not parking_info:
        print(f"No parking info found for customer_id: {customer_id}")
        return redirect('/shop')
        
    check_in_time, vehicle_number, slot_id, vehicle_type, session_id = parking_info
    
    # Get the latest transaction for this customer
    cursor.execute(
        """SELECT t.sale_id, t.total, t.discount
            FROM transactions t
            WHERE t.customer_id = %s
            ORDER BY t.time DESC
            LIMIT 1""",
        (customer_id,)
    )
    
    transaction = cursor.fetchone()
    if not transaction:
        print(f"No transaction found for customer_id: {customer_id}")
        return redirect('/shop')
        
    sale_id, purchase_total, discount = transaction
    
    # Get customer phone
    cursor.execute(
        "SELECT phone FROM customers WHERE customer_id = %s",
        (customer_id,)
    )
    
    phone = cursor.fetchone()[0]
    
    # Calculate parking duration
    current_time = datetime.datetime.now()
    parking_duration = current_time - check_in_time
    hours_parked = parking_duration.total_seconds() / 3600  # Convert to hours
    
    # Calculate parking fee (example: ₹50 per hour for cars, ₹30 for bikes)
    base_rate = 50 if vehicle_type == 'car' else 30
    parking_fee = base_rate * hours_parked
    
    # Apply discount on parking based on purchase amount
    parking_discount = 0
    if purchase_total >= 500:  # Free parking for purchases over ₹500
        parking_discount = parking_fee
    elif purchase_total >= 300:  # 50% off parking for purchases over ₹300
        parking_discount = parking_fee * 0.5
        
    final_parking_fee = max(0, parking_fee - parking_discount)
    
    # Format the values for display
    hours_parked_formatted = f"{int(hours_parked)}h {int((hours_parked % 1) * 60)}m"
    
    # Get purchased items
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
    
    return render_template(
        'parking_bill.html',
        customer_id=customer_id,
        sale_id=sale_id,
        vehicle_number=vehicle_number,
        slot_id=slot_id,
        phone=phone,
        check_in_time=check_in_time,
        current_time=current_time,
        hours_parked=hours_parked_formatted,
        parking_fee=float(parking_fee),
        parking_discount=float(parking_discount),
        final_parking_fee=float(final_parking_fee),
        purchase_total=float(purchase_total),
        grand_total=float(purchase_total) + float(final_parking_fee),
        purchased_items=purchased_items
    )


if __name__ == '__main__':
    app.run(debug=True)