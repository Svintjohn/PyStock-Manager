import gc # Garbage collection module for memory management
import mysql.connector # MySQL Connector for Python
from mysql.connector import Error # Exception handling for MySQL errors

class InventorySystem:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',      
            'password': '',      
            'database': 'inventory_db'
        }
        self.init_db()

    def get_connection(self):
        """Creates and returns a connection to the XAMPP MySQL database."""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def init_db(self):
        """Creates the SQL table if it doesn't already exist."""
        conn = self.get_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    pid VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    qty INT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    is_spoiled BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()

    def add_record(self):
        print("\n--- Add New Record ---")
        pid = input("Enter Product ID: ").strip()
        if not pid:
            print("Error: ID cannot be empty.")
            return
            
        name = input("Enter Name: ")
        
        try:
            qty = int(input("Enter Quantity: "))
            price = float(input("Enter Price: "))
            
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                sql = "INSERT INTO products (pid, name, qty, price) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (pid, name, qty, price))
                conn.commit()
                print(f"Successfully added {name}.")
                cursor.close()
                conn.close()
                
        except mysql.connector.IntegrityError:
            print(f"Error: Product ID '{pid}' already exists in the database.")
        except ValueError:
            print("Invalid Input: Please enter numbers for Quantity and Price.")

    def edit_record(self):
        pid = input("\nEnter Product ID to edit: ").strip()
        
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products WHERE pid = %s", (pid,))
            result = cursor.fetchone()
            
            if not result:
                print(f"Error: Record '{pid}' not found.")
                cursor.close()
                conn.close()
                return
                
            name = result[0]
            print("1. Change Quantity | 2. Mark as Spoiled")
            choice = input("Choice: ")
            
            try:
                if choice == "1":
                    new_qty = int(input("New Quantity: "))
                    cursor.execute("UPDATE products SET qty = %s WHERE pid = %s", (new_qty, pid))
                    if new_qty < 10:
                        print(f"ALERT: {name} stock is low!")
                    else:
                        print("Quantity updated successfully.")
                        
                elif choice == "2":
                    cursor.execute("UPDATE products SET is_spoiled = TRUE WHERE pid = %s", (pid,))
                    print("Item marked as spoiled.")
                
                conn.commit()
            except ValueError:
                print("Error: Quantity must be a whole number.")
            finally:
                cursor.close()
                conn.close()

    def delete_record(self):
        pid = input("\nEnter ID to delete: ").strip()
        
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products WHERE pid = %s", (pid,))
            result = cursor.fetchone()
            
            if result:
                name = result[0]
                cursor.execute("DELETE FROM products WHERE pid = %s", (pid,))
                conn.commit()
                print(f"Record {pid} ({name}) removed.")
            else:
                print("Error: ID does not exist.")
            
            cursor.close()
            conn.close()

    def compute_metrics(self):
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if database is completely empty
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                print("\nInventory is currently empty.")
                cursor.close()
                conn.close()
                return

            cursor.execute("SELECT SUM(qty * price) FROM products")
            total_inv = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE is_spoiled = TRUE")
            spoilage_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE qty < 10")
            restock_needed = cursor.fetchone()[0]

            print("\n--- INVENTORY SUMMARY ---")
            print(f"Total Value: ${float(total_inv):,.2f}")
            print(f"Spoiled Items: {spoilage_count}")
            print(f"Items to Restock: {restock_needed}")
            
            cursor.close()
            conn.close()

    def exit_and_cleanup(self):
        gc.collect() 
        print("Memory cleared. System closed.")

# --- MAIN LOOP ---
def main():
    system = InventorySystem()
    while True:
        print("\n--- Tech Inventory Menu  ---")
        print("1. Add | 2. Edit | 3. Delete | 4. Report | 5. Exit")
        choice = input("Select Action: ")

        if choice == "1": system.add_record()
        elif choice == "2": system.edit_record()
        elif choice == "3": system.delete_record()
        elif choice == "4": system.compute_metrics()
        elif choice == "5": 
            system.exit_and_cleanup()
            break
        else:
            print("Invalid selection. Try again.")

if __name__ == "__main__":
    main()
