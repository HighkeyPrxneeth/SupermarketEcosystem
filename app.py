from flask import Flask, render_template, request
from mysql import connector as conn
from mysql.connector import errorcode

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
    phone = "+91" + request.args.get('phone')
    vehicle_type = request.args.get('vehicle_type', 'car')
    session, cust = register_parking(cursor, vehicle_type, vehicle_number, phone)
    if session == -1:
        return render_template('shop.html', error="No available slots")
    products = list_products(cursor)
    return render_template('shop.html', session=session, cust=cust, products=products, vehicle_number=vehicle_number, phone=phone)   

if __name__ == '__main__':
    app.run(debug=True)