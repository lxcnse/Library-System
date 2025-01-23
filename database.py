import mysql.connector
from mysql.connector import Error


class Connection:
    __HOST = "" # Replace with your host
    __USER = "" # Replace with your username
    __PASSWORD = "" # Replace with your password
    __DATABASE = "" # Replace with your database name

    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=Connection.__HOST,
                user=Connection.__USER,
                password=Connection.__PASSWORD,
                database=Connection.__DATABASE,
                charset="utf8mb4",
                collation='utf8mb4_general_ci'
            )
            if self.conn.is_connected():
                print("Successfully connected to the database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            self.conn = None

    def close_connection(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Database connection closed")




