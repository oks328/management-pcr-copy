import mysql.connector
from mysql.connector import Error


def get_db_connection():
    try:
        connection = mysql.connector.connect(
           host='localhost',       # Changed from '144.21.57.156'
           port=3306,              # Standard XAMPP MySQL port (was 6767)
           database='ipcr_db',     # Keep the database name
           user='root',            # Default XAMPP user
           password='',            # Default XAMPP password is empty
           connection_timeout=5
        )
        if connection.is_connected():
            print("Connection established to Localhost")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    
    
def get_user_by_email(cursor, email):
    cursor.callproc('get_user_by_email', (email,))
    for result in cursor.stored_results():
        return result.fetchall()
    return []
    

def register_user(cursor, emp_id, email, password_hash):
    cursor.callproc('register_user', (emp_id, email, password_hash))
    