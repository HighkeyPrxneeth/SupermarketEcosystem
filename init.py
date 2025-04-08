import mysql.connector as conn
from mysql.connector import errorcode

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
            `status` varchar(9), CHECK (status IN ('available', 'occupied')),
            `vehicle_no` varchar(10),
            `check_in` timestamp,
            `check_out` timestamp, CHECK (check_out > check_in),
            `fee` decimal(3,2),
            PRIMARY KEY (`session_id`, `slot_id`)
        )
        """
    )

    TABLES['customers'] = (
        """
        CREATE TABLE `customers` (
            `customer_id` int(5) NOT NULL,
            `parking_session_id` int(5) NOT NULL,
            `phone` varchar(14),
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
            `discount` decimal(3,2),
            `total` decimal(5,2),
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


def del_db(cursor: conn.connection.MySQLCursor):
    cursor.execute("DROP DATABASE project_db")
    print("Deleted database!")

try:
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost', database='project_db')
    cursor = cnx.cursor()
    create_tables(cursor)
    del_db(cursor)
    cursor.close()
except conn.errors.ProgrammingError:
    print("Database not found!")
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost')
    cursor = cnx.cursor()
    init_db(cursor)
    create_tables(cursor)
    del_db(cursor)
    cursor.close()

