import mysql.connector

def create_database():
    try:
        # Try connecting with blank password (common for XAMPP/WAMP)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        print("Connected to MySQL with blank password.")
    except Exception as e:
        try:
            # Try connecting with 'password'
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password"
            )
            print("Connected to MySQL with password 'password'.")
        except Exception as e2:
            print("Could not connect to MySQL. Ensure MySQL is running and accessible on port 3306 by user 'root'.")
            return

    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS cio_db")
    print("Database 'cio_db' ensured.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_database()
