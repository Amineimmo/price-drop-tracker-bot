import sqlite3

def setup_database():
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            url TEXT,
            target_price REAL,
            UNIQUE(user_id, url)
        )
    """)
    connection.commit()
    connection.close()
setup_database()

def add_product(user_id, url, target_price):
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO products (user_id, url, target_price) VALUES (?, ?, ?)", 
            (user_id, url, target_price)
        )
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()

def get_user_products(user_id):
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, url, target_price FROM products WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    connection.close()
    return rows

def get_all_products():
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, user_id, url, target_price FROM products")
    rows = cursor.fetchall()
    connection.close()
    return rows

def delete_product(product_id, user_id):
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
    deleted = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return deleted