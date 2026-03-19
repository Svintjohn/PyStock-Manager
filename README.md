# Tech Inventory System (Python + MySQL)

A simple and efficient desktop-based inventory management system. This application allows users to add, edit, delete, and generate reports for technology products. It uses Python for the logic and a MySQL database (via XAMPP) for persistent data storage.

This was developed as a final project for the Design and Implementation of Programming Languages (6DIPROGLANG) course.

## Features
* **Add Records:** Insert new products with their ID, name, quantity, and price.
* **Edit Records:** Update existing product quantities or mark items as spoiled/damaged.
* **Delete Records:** Remove products from the database completely.
* **Inventory Report:** Automatically calculates total inventory value, counts spoiled items, and flags items that need restocking (quantity under 10).
* **Automatic Database Setup:** The script automatically creates the required database tables on its first run.

## Prerequisites
To run this project, you need to have the following installed on your computer:
* **Python 3.x**
* **XAMPP** (for the local MySQL server)
* **MySQL Connector for Python**
