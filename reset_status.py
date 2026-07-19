import sqlite3

conn = sqlite3.connect('cargo_v2.db')
conn.execute("UPDATE drivers SET status = 'Available'")
conn.execute("UPDATE vehicles SET status = 'Available'")
conn.commit()
conn.close()
print("All drivers and vehicles reset to Available.")
