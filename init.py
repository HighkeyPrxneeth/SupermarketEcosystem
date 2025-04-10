import mysql.connector as conn
from mysql.connector import errorcode
import pandas as pd

def init_db(cursor: conn.connection.MySQLCursor):
    cursor.execute("CREATE DATABASE project_db")
    cursor.execute("USE project_db")
    print("Initialised database!")

def create_tables(cursor: conn.connection.MySQLCursor):
    TABLES = {}
    TABLES['parking_slots'] = (
        """
        CREATE TABLE `parking_slots` (
            `session_id` int(5) NOT NULL,
            `slot_id` int(2) NOT NULL,
            `slot_type` varchar(4), CHECK (slot_type IN ('bike', 'car')),
            `vehicle_no` varchar(13),
            `check_in` timestamp,
            `check_out` timestamp, CHECK (check_out > check_in),
            `fee` decimal(5,2),
            PRIMARY KEY (`session_id`, `slot_id`)
        )
        """
    )

    TABLES['customers'] = (
        """
        CREATE TABLE `customers` (
            `customer_id` int(5) NOT NULL,
            `parking_session_id` int(5) NOT NULL,
            `phone` varchar(13),
            PRIMARY KEY (`customer_id`),
            FOREIGN KEY (`parking_session_id`) REFERENCES `parking_slots` (`session_id`)
        )
        """
    )

    TABLES['transactions'] = (
        """
        CREATE TABLE `transactions` (
            `sale_id` int(5) NOT NULL,
            `customer_id` int(5) NOT NULL,
            `discount` decimal(8,2),
            `total` decimal(8,2),
            `time` timestamp,
            PRIMARY KEY (`sale_id`),
            FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
        )
        """
    )

    TABLES['products'] = (
        """
        CREATE TABLE `products` (
            `product_id` int(5) NOT NULL,
            `name` varchar(20),
            `price` decimal(5,2),
            `quantity` int(5),
            `category` varchar(20),
            `reorder_level` int(5),
            PRIMARY KEY (`product_id`)
        )
        """
    )

    TABLES['sales_details'] = (
        """
        CREATE TABLE `sales_details` (
            `sale_id` int(5) NOT NULL,
            `product_id` int(5) NOT NULL,
            `quantity` int(5),
            `subtotal` decimal(5,2),
            PRIMARY KEY (`sale_id`, `product_id`),
            FOREIGN KEY (`sale_id`) REFERENCES `transactions` (`sale_id`),
            FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
        )
        """
    )

    TABLES['restocks'] = (
        """
        CREATE TABLE `restocks` (
            `restock_id` int(5) NOT NULL,
            `product_id` int(5) NOT NULL,
            `supplier` varchar(20),
            `quantity` int(5),
            `restock_date` date,
            PRIMARY KEY (`restock_id`),
            FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
        )
        """
    )

    for TABLE in TABLES:
        print(f"Creating table {TABLE}")
        try:
            cursor.execute(TABLES[TABLE])
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
                return

    print("All tables created!")


def insert_data(cursor: conn.connection.MySQLCursor):
    data = {
        'parking_slots': pd.read_csv('data/parking_slots.csv'),
        'customers': pd.read_csv('data/customers.csv'),
        'transactions': pd.read_csv('data/transactions.csv'),
        'products': pd.read_csv('data/products.csv'),
        'sales_details': pd.read_csv('data/sales_details.csv'),
        'restocks': pd.read_csv('data/restocks.csv')
    }
    for table, df in data.items():
        print(f"Inserting data into {table}")
        for i, row in df.iterrows():
            sql_row = tuple(row)
            sql_row = str(sql_row).replace("nan", "NULL")
            cursor.execute(f"INSERT INTO {table} VALUES {sql_row}")
        cursor.execute("COMMIT")
    
    print("All data inserted!")


def del_db(cursor: conn.connection.MySQLCursor):
    cursor.execute("DROP DATABASE project_db")
    print("Deleted database!")


if __name__ == "__main__":
    try:
        cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost', database='project_db')
        cursor = cnx.cursor()
        del_db(cursor)
        init_db(cursor)
        create_tables(cursor)
        insert_data(cursor)
        del_db(cursor)
        cursor.close()
    except conn.errors.ProgrammingError:
        print("Database not found!")
        cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost')
        cursor = cnx.cursor()
        init_db(cursor)
        create_tables(cursor)
        insert_data(cursor)
        del_db(cursor)
        cursor.close()
