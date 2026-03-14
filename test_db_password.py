import mysql.connector

def test_passwords():
    common_passwords = ["", "password", "root", "1234", "12345", "123456", "mysql", "admin"]
    
    for pwd in common_passwords:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=pwd
            )
            print(f"SUCCESS: The root password is: '{pwd}'")
            conn.close()
            return
        except Exception:
            pass
            
    print("FAILED: Could not find the password in the common list.")

if __name__ == "__main__":
    test_passwords()
