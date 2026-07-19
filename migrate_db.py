import sqlite3

def migrate():
    conn = sqlite3.connect('cargo_v2.db')
    try:
        conn.execute("ALTER TABLE bookings ADD COLUMN payment_status VARCHAR DEFAULT 'Pending'")
        conn.commit()
        print("Migration successful")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
