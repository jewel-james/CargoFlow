from database import SessionLocal
from models import User, Booking, TrackingHistory

def clear_tables():
    db = SessionLocal()
    try:
        # Delete dependent tables first if needed
        db.query(TrackingHistory).delete()
        db.query(Booking).delete()
        db.query(User).delete()
        db.commit()
        print("Success")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_tables()
