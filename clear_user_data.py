import sqlite3

conn = sqlite3.connect('cargo_v2.db')
cursor = conn.cursor()

# Delete tracking history first (foreign key dependency)
cursor.execute("DELETE FROM tracking_history")
print(f"Deleted tracking history: {cursor.rowcount} rows")

# Delete bookings
cursor.execute("DELETE FROM bookings")
print(f"Deleted bookings: {cursor.rowcount} rows")

# Delete regular users (keep admin and driver accounts)
cursor.execute("DELETE FROM users WHERE role = 'user'")
print(f"Deleted regular users: {cursor.rowcount} rows")

# Reset all drivers and vehicles back to Available
cursor.execute("UPDATE drivers SET status = 'Available'")
cursor.execute("UPDATE vehicles SET status = 'Available'")
print("Reset all drivers and vehicles to Available.")

conn.commit()
conn.close()
print("\nDone! Drivers, vehicles, admin, and distances are all preserved.")
