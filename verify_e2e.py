import app as flask_app
import models, database, json
from datetime import datetime

def test_dashboard_and_tracking():
    app = flask_app.app
    app.config['TESTING'] = True
    client = app.test_client()

    # 1. Setup Driver Account
    db = database.SessionLocal()
    driver_user = db.query(models.User).filter(models.User.role == "driver").first()
    if not driver_user:
        print("Error: No driver user found")
        return
    
    driver = db.query(models.Driver).filter(models.Driver.user_id == driver_user.id).first()
    if not driver:
         print(f"Error: No driver record for user {driver_user.username}")
         return
    
    print(f"Testing for Driver User: {driver_user.username} (ID: {driver_user.id}) -> Driver Record ID: {driver.id}")
    
    # 2. Simulate Booking Creation (Automated Assignment)
    with client.session_transaction() as sess:
        sess['user_id'] = 1 # Admin or User
        sess['role'] = 'admin'
    
    # Ensure driver is available
    driver.status = "Available"
    db.commit()

    print("Creating automated booking...")
    response = client.post('/book', data=dict(
        sender="Master Test",
        receiver="Receiver",
        origin="Alpha",
        destination="Omega",
        weight=15.0
    ), follow_redirects=True)
    
    # Get the new booking
    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.sender == "Master Test").order_by(models.Booking.id.desc()).first()
    print(f"Booking {booking.id} created with Tracking ID {booking.tracking_id}. Assigned Driver ID: {booking.driver_id}")
    assert booking.driver_id == driver.id
    db.close()

    # 3. Verify Driver Dashboard
    with client.session_transaction() as sess:
        sess['user_id'] = driver_user.id
        sess['role'] = 'driver'
    
    print("Fetching Driver Dashboard...")
    dash_resp = client.get('/driver_dashboard')
    dash_html = dash_resp.data.decode()
    if booking.tracking_id in dash_html:
        print("Success: Booking Tracking ID found on Driver Dashboard")
    else:
        print(f"Error: Tracking ID {booking.tracking_id} NOT found on Driver Dashboard")
        assert False

    # 4. Update Location and Verify Status change
    print("Updating location...")
    upd_resp = client.post('/update_location', json=dict(
        booking_id=booking.id,
        lat=13.0,
        lon=80.0
    ))
    print(f"Update Location Response: {upd_resp.data.decode()}")
    
    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.id == booking.id).first()
    print(f"Final Booking Status: {booking.status}")
    assert booking.status == "In Transit"
    db.close()
    
    print("\nEnd-to-End Verification Successful!")

if __name__ == "__main__":
    test_dashboard_and_tracking()
