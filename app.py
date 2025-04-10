from flask import Flask, render_template, request, redirect, session, flash, url_for 
from mysql import connector as conn
from mysql.connector import errorcode
import datetime
import math
from functools import wraps 

from init import *
from db import *

app = Flask(__name__)
app.secret_key = 'odnweu9ndn993n89d39dn3nj89dh3nnmoidmeuinfoienmfoismdofnusinf94noiesmf'


ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


try:
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost', database='project_db')
    cnx.autocommit = True
    cursor = cnx.cursor()
    del_db(cnx.cursor())
    init_db(cursor)
    create_tables(cursor)
    insert_data(cursor)
except conn.errors.ProgrammingError:
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost')
    cnx.autocommit = True
    cursor = cnx.cursor()
    init_db(cursor)
    create_tables(cursor)
    insert_data(cursor)
    
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
        result = get_parking_session_by_customer_id(cursor, customer_id)
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
            result = get_latest_customer(cursor)
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
    parking_info = get_customer_parking_info(cursor, customer_id)
    if not parking_info:
        print(f"No parking info found for customer_id: {customer_id}")
        return redirect('/shop')
        
    check_in_time, vehicle_number, slot_id, vehicle_type, session_id = parking_info
    
    # Get the latest transaction for this customer
    transaction = get_latest_transaction(cursor, customer_id)
    if not transaction:
        print(f"No transaction found for customer_id: {customer_id}")
        return redirect('/shop')
        
    sale_id, purchase_total, discount = transaction
    
    # Get customer phone
    phone = get_customer_phone(cursor, customer_id)[0]
    
    # Calculate parking duration
    current_time = datetime.datetime.now()
    parking_duration = current_time - check_in_time
    hours_parked_raw = parking_duration.total_seconds() / 3600  # Convert to hours
    
    # Round up to the next hour (ceiling) - even 1 minute counts as a full hour
    hours_parked_billed = math.ceil(hours_parked_raw)
    
    # Calculate parking fee (₹20 per hour for cars, ₹10 for bikes)
    base_rate = 20 if vehicle_type == 'car' else 10
    parking_fee = base_rate * hours_parked_billed
    
    # Format the values for display - keep the raw hours for display purposes
    hours_parked_formatted = f"{int(hours_parked_raw)}h {int((hours_parked_raw % 1) * 60)}m"
    
    # Apply discount on parking based on purchase amount
    parking_discount = 0
    if purchase_total >= 500:  # Free parking for purchases over ₹500
        parking_discount = parking_fee
    elif purchase_total >= 300:  # 50% off parking for purchases over ₹300
        parking_discount = parking_fee * 0.5
        
    final_parking_fee = max(0, parking_fee - parking_discount)
    
    # Get purchased items
    purchased_items = get_purchased_items(cursor, sale_id)
    
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


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        # Fetch data using functions from db.py
        sales_summary = get_sales_summary(cursor)
        restock_suggestions = get_restock_suggestions(cursor)
        parking_status = get_parking_status(cursor)
        most_sold_products = get_most_sold_products(cursor)
        sales_by_category = get_sales_by_category(cursor)

        # Calculate parking availability
        occupied_count = sum(1 for slot in parking_status.values() if slot['status'] == 'Occupied')
        available_count = len(parking_status) - occupied_count

        parking_summary = {
            'total': len(parking_status),
            'occupied': occupied_count,
            'available': available_count
        }

        # ---> ADD datetime=datetime HERE <---
        return render_template(
            'admin_dashboard.html',
            sales_summary=sales_summary,
            restock_suggestions=restock_suggestions,
            parking_status=parking_status,
            parking_summary=parking_summary,
            most_sold_products=most_sold_products,
            sales_by_category=sales_by_category,
            format_currency=lambda amount: f"₹{amount:,.2f}", # Helper for templates
            datetime=datetime  # Pass the imported datetime module to the template
        )
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        flash(f"An error occurred while loading the dashboard: {e}", "danger")
        # Also add datetime here for the error case rendering
        return render_template(
            'admin_dashboard.html',
            sales_summary={'total_sales': 0, 'total_discount': 0, 'num_transactions': 0, 'avg_purchase': 0},
            restock_suggestions=[],
            parking_status={},
            parking_summary={'total': 0, 'occupied': 0, 'available': 0},
            most_sold_products=[],
            sales_by_category=[],
            format_currency=lambda amount: f"₹{amount:,.2f}",
            error=f"Failed to load dashboard data: {e}",
            datetime=datetime # Pass datetime here too
        )


if __name__ == '__main__':
    app.run(debug=True) # Keep debug=True for development