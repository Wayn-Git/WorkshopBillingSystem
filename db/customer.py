from .connection import get_db

def add_customer(name, gst_no, phone):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customer (name, gst_no, phone) VALUES (?, ?, ?)",
        (name, gst_no, phone)
    )
    customer_id = cur.lastrowid # CRITICAL: Return the new ID
    conn.commit()
    conn.close()
    return customer_id

def get_customer(customer_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM customer WHERE id = ?", (customer_id,)
    ).fetchone()
    conn.close()
    return row