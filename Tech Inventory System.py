import gc # Garbage collection module for memory management
import mysql.connector # MySQL Connector for Python
from mysql.connector import Error # Exception handling for MySQL errors
 
class InventorySystem: # Main class for inventory management
    def __init__(self): # Initialize database configuration and setup
        # Configuration for the initial server connection (no database specified)
        self.server_config = { 
            'host': 'localhost', 
            'user': 'root',      
            'password': ''
        }
        self.db_config = { # Database connection parameters
            'host': 'localhost', 
            'user': 'root',      
            'password': '',      
            'database': 'inventory_db'
        }
        self.init_db() # Ensure the database and table are created on initialization

    def get_connection(self): # Method to establish a connection to the MySQL database
        """Creates and returns a connection to the XAMPP MySQL database."""
        try: # Attempt to connect to the database using the provided configuration
            return mysql.connector.connect(**self.db_config)
        except Error as e: # Handle any connection errors and print an error message
            print(f"Error connecting to MySQL: {e}")
            return None # Return None if connection fails

    def init_db(self): # Method to initialize the database and create the products table if it doesn't exist
        """Creates the database and the SQL table if they don't already exist."""
        try:
            server_conn = mysql.connector.connect(**self.server_config)
            if server_conn.is_connected():
                cursor = server_conn.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
                server_conn.commit()
                cursor.close()
                server_conn.close()
        except Error as e:
            print(f"Critical Error setting up database: {e}")
            return

        conn = self.get_connection() # Get a connection to the database
        if conn and conn.is_connected(): # Check if the connection was successful before proceeding
            cursor = conn.cursor() # Create a cursor object to execute SQL commands
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS products (
                    pid VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    qty INT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    is_spoiled BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.commit() # Commit the changes to the database
            cursor.close() # Close the cursor after executing the command
            conn.close() # Close the database connection after initialization

    def add_record(self):
            print("\n--- Add New Record ---")
            
            # Validation loop for Product ID
            while True:
                pid = input("Enter Product ID: ").strip()
                if pid: # Checks if input is not empty
                    break
                print("Wrong input, input ID") 
                
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
                print(f"Error: Product ID '{pid}' already exists.")
            except ValueError:
                print("Invalid Input: Please enter numbers for Quantity and Price.")

    def edit_record(self): # Method to edit an existing product record in the database
        pid = input("\nEnter Product ID to edit: ").strip()
        
        conn = self.get_connection()
        if conn: # If the connection is successful, proceed to check if the record exists and allow the user to edit it
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products WHERE pid = %s", (pid,))
            result = cursor.fetchone()
            
            if not result: # If the record does not exist, print an error message and exit the method
                print(f"Error: Record '{pid}' not found.")
                cursor.close()
                conn.close()
                return
                
            name = result[0] # Store the name of the product for later use in alerts and messages
            print("1. Change Quantity | 2. Mark as Spoiled")
            choice = input("Choice: ")
            
            try: # Attempt to update the record based on the user's choice and handle any input errors
                if choice == "1":
                    new_qty = int(input("New Quantity: "))
                    cursor.execute("UPDATE products SET qty = %s WHERE pid = %s", (new_qty, pid))
                    if new_qty < 10: # If the new quantity is below the threshold, print an alert message to restock the item
                        print(f"ALERT: {name} stock is low!")
                    else: # If the quantity is updated successfully and is not low, print a success message
                        print("Quantity updated successfully.")
                        
                elif choice == "2": # If the user chooses to mark the item as spoiled, update the record accordingly and print a confirmation message
                    cursor.execute("UPDATE products SET is_spoiled = TRUE WHERE pid = %s", (pid,))
                    print("Item marked as spoiled.")
                
                conn.commit()
            except ValueError: # Handle the case where the new quantity input is not a valid number and print an error message
                print("Error: Quantity must be a whole number.")
            finally: # Ensure that the cursor and connection are closed after the operation is completed, regardless of success or failure
                cursor.close()
                conn.close()

    def delete_record(self):
        pid = input("\nEnter ID to delete: ").strip()
        
        conn = self.get_connection()
        if conn: # If the connection is successful, proceed to check if the record exists and allow the user to delete it
            cursor = conn.cursor() 
            cursor.execute("SELECT name FROM products WHERE pid = %s", (pid,))
            result = cursor.fetchone()
            
            if result: # If the record exists, store the name for later use in the confirmation message, delete the record from the database, and print a success message
                name = result[0]
                cursor.execute("DELETE FROM products WHERE pid = %s", (pid,))
                conn.commit()
                print(f"Record {pid} ({name}) removed.")
            else: # If the record does not exist, print an error message indicating that the ID was not found in the database
                print("Error: ID does not exist.")
            
            cursor.close()
            conn.close()

    def compute_metrics(self):
        conn = self.get_connection()
        if conn: # If the connection is successful, proceed to compute inventory metrics such as total value, spoilage count, and restock needs, and print the results in a summary format
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
'''The main function serves as the entry point for the inventory management system. It creates an instance of the InventorySystem class and continuously displays a menu for the user to interact with until they choose to exit. The user can add, edit, delete records, or compute inventory metrics through this menu. When the user selects the exit option, the system performs cleanup by invoking garbage collection to free up memory before closing.'''

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
