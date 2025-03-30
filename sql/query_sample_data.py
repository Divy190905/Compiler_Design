"""
Sample data for the query language.
"""

def load_sample_data(interpreter):
    """Load sample data into the interpreter's database."""
    # Sample employees data
    employees = [
        {"id": 1, "name": "John Doe", "department": "Engineering", "salary": 75000},
        {"id": 2, "name": "Jane Smith", "department": "Marketing", "salary": 65000},
        {"id": 3, "name": "Bob Johnson", "department": "Engineering", "salary": 80000},
        {"id": 4, "name": "Alice Williams", "department": "HR", "salary": 60000},
        {"id": 5, "name": "Charlie Brown", "department": "Engineering", "salary": 90000},
        {"id": 6, "name": "Diana Garcia", "department": "Marketing", "salary": 70000},
        {"id": 7, "name": "Edward Lee", "department": "Finance", "salary": 85000},
        {"id": 8, "name": "Fiona Chen", "department": "HR", "salary": 55000},
    ]
    
    # Sample products data
    products = [
        {"id": 101, "name": "Laptop", "category": "Electronics", "price": 1200.00, "stock": 50},
        {"id": 102, "name": "Smartphone", "category": "Electronics", "price": 800.00, "stock": 100},
        {"id": 103, "name": "Desk Chair", "category": "Furniture", "price": 150.00, "stock": 30},
        {"id": 104, "name": "Coffee Table", "category": "Furniture", "price": 200.00, "stock": 20},
        {"id": 105, "name": "Headphones", "category": "Electronics", "price": 100.00, "stock": 75},
        {"id": 106, "name": "Bookshelf", "category": "Furniture", "price": 180.00, "stock": 15},
        {"id": 107, "name": "Tablet", "category": "Electronics", "price": 350.00, "stock": 40},
        {"id": 108, "name": "Office Desk", "category": "Furniture", "price": 250.00, "stock": 10},
    ]
    
    # Load data into the interpreter
    interpreter.load_table("employees", employees)
    interpreter.load_table("products", products)
    
    print("Sample data loaded successfully.")
    print("Available tables: 'employees', 'products'")
    print()
    print("employees columns: id, name, department, salary")
    print("products columns: id, name, category, price, stock")
