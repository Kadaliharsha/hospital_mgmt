import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root@39',
        database='HospitalManagementSystem',
    )

# Optional: Test connection when running this file directly
if __name__ == "__main__":
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        print("Connected to:", cursor.fetchone()[0])
        cursor.close()
        conn.close()
    except Error as e:
        print("Error while connecting to MySQL:", e)
