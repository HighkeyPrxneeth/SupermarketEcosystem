import mysql.connector as conn

def init_db(cursor: conn.connection.MySQLCursor):
    cursor.execute("CREATE DATABASE project_db")
    cursor.execute("USE project_db")
    print("Initialised database!")

def create_tables(cursor: conn.connection.MySQLCursor):
    TABLES = {}
    TABLES['parking_slots'] = (
        "CREATE TABLE `parking_slots` (",
        "   `session_id` int(5) NOT NULL,",
        "   `slot_id` int(2) NOT NULL,",
        "   `slot_type` varchar(4), CHECK (slot_type IN (`bike`, `car`)),",
        "   `status` varchar(9), CHECK (status IN (`available`, `occupied`)),",
        "   `vehicle_no` varchar(10),",
        "   `check_in` timestamp,",
        "   `check_out` timestamp, CHECK( check_out > check_in),",
        "   `fee` decimal(3,2)",
        ")"
    )

def del_db(cursor: conn.connection.MySQLCursor):
    cursor.execute("DROP DATABASE project_db")
    print("Deleted database!")

try:
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost', database='project_db')
    cursor = cnx.cursor()
    del_db(cursor)
except conn.errors.ProgrammingError:
    print("Database not found!")
    cnx = conn.connect(user='dbs-lab-user', password='dbslab123', host='localhost')
    cursor = cnx.cursor()
    init_db(cursor)
    del_db(cursor)

