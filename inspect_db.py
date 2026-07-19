import models, database

def inspect_db():
    db = database.SessionLocal()
    print("--- Users ---")
    users = db.query(models.User).all()
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}")

    print("\n--- Drivers ---")
    drivers = db.query(models.Driver).all()
    for d in drivers:
        print(f"ID: {d.id}, Name: {d.name}, UserID: {d.user_id}, Status: {d.status}")
    
    print("\n--- Bookings ---")
    bookings = db.query(models.Booking).all()
    for b in bookings:
        print(f"ID: {b.id}, Tracking: {b.tracking_id}, Status: {b.status}, DriverID: {b.driver_id}")
    
    db.close()

if __name__ == "__main__":
    inspect_db()
