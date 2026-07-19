from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import random, string, datetime, math, urllib.request, json, os
from functools import wraps

import models, database, auth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')

# --- Dependencies / Helpers ---

def get_db():
    db = database.SessionLocal()
    try:
        return db
    finally:
        db.close()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def driver_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'driver':
            flash('Driver access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        db = database.SessionLocal()
        user = db.query(models.User).filter(models.User.username == username).first()
        if user:
            flash('Username already exists!', 'error')
            db.close()
            return redirect(url_for('register'))

        hashed_password = auth.get_password_hash(password)
        new_user = models.User(username=username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = database.SessionLocal()
        user = db.query(models.User).filter(models.User.username == username).first()
        
        if user and auth.verify_password(password, user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            db.close()
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_shipments'))
            elif user.role == 'driver':
                return redirect(url_for('driver_dashboard'))
            return redirect(url_for('index'))
        else:
            db.close()
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        sender = request.form['sender']
        sender_email = request.form.get('sender_email')
        sender_phone = request.form.get('sender_phone')
        receiver = request.form['receiver']
        origin = request.form['origin']
        destination = request.form['destination']
        weight = float(request.form['weight'])
        
        db = database.SessionLocal()
        
        if origin == destination:
            db.close()
            flash("Pickup and Drop-off locations cannot be the same.", "error")
            return redirect(url_for('book'))

        distance_record = db.query(models.Distance).filter(
            ((models.Distance.from_location == origin) & (models.Distance.to_location == destination)) |
            ((models.Distance.from_location == destination) & (models.Distance.to_location == origin))
        ).first()
        distance = distance_record.distance_km if distance_record else 0
        
        # Automated Resource Assignment: Prioritize drivers with user accounts
        driver = db.query(models.Driver).filter(
            models.Driver.status == "Available",
            models.Driver.user_id.isnot(None)
        ).first() or db.query(models.Driver).filter(models.Driver.status == "Available").first()
        
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.status == "Available").first()
        
        if not driver or not vehicle:
            db.close()
            flash("No resources available at the moment.", "error")
            return redirect(url_for('book'))

        tracking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        cost = (weight * 10.5) + (distance * 5)

        new_booking = models.Booking(
            tracking_id=tracking_id,
            user_id=session['user_id'],
            sender=sender,
            sender_email=sender_email,
            sender_phone=sender_phone,
            receiver=receiver,
            origin=origin,
            destination=destination,
            weight=weight,
            cost=cost,
            status="Assigned",
            driver_id=driver.id,
            vehicle_id=vehicle.id
        )
        
        # Update driver and vehicle status
        driver.status = "Assigned"
        vehicle.status = "Assigned"
        
        db.add(new_booking)
        db.commit()
        db.close()

        return render_template('result.html', tracking_id=tracking_id, cost=cost)

    return render_template('book.html')

@app.route('/my-shipments')
@login_required
def my_shipments():
    db = database.SessionLocal()
    bookings = db.query(models.Booking).options(
        joinedload(models.Booking.driver),
        joinedload(models.Booking.vehicle)
    ).filter(models.Booking.user_id == session['user_id']).all()
    
    html = render_template('my_shipments.html', shipments=bookings)
    db.close()
    return html

@app.route('/retrieve-tracking', methods=['GET', 'POST'])
def retrieve_tracking():
    if request.method == 'POST':
        search_query = request.form['search_query']
        db = database.SessionLocal()
        # In a real app, you'd match by email/phone which we'd add to models
        # For now, matching simplified as per previous mixed main.py
        # Assuming sender_email or sender_phone exists in model (it does)
        bookings = db.query(models.Booking).options(
            joinedload(models.Booking.driver),
            joinedload(models.Booking.vehicle)
        ).filter(
            (models.Booking.sender_email == search_query) | 
            (models.Booking.sender_phone == search_query)
        ).all()
        
        if not bookings:
            db.close()
            flash('No bookings found with that information.', 'error')
            return render_template('retrieve_tracking.html')
        
        html = render_template('my_shipments.html', shipments=bookings, title="Retrieval Results")
        db.close()
        return html
    
    return render_template('retrieve_tracking.html')

@app.route('/track', methods=['GET', 'POST'])
@login_required
def track():
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']

        db = database.SessionLocal()
        booking = db.query(models.Booking).filter(models.Booking.tracking_id == tracking_id).first()
        
        if booking:
            history = db.query(models.TrackingHistory).filter(models.TrackingHistory.booking_id == booking.id).order_by(models.TrackingHistory.time.desc()).all()
            db.close()
            return render_template('track_result.html', status=booking.status, payment_status=booking.payment_status, tracking_id=tracking_id, history=history, booking_id=booking.id)
        else:
            db.close()
            return render_template('track.html', error="Invalid Tracking ID")

    return render_template('track.html')

@app.route('/api/get_distance', methods=['GET'])
def get_distance():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    db = database.SessionLocal()
    dist = db.query(models.Distance).filter(
        ((models.Distance.from_location == origin) & (models.Distance.to_location == destination)) |
        ((models.Distance.from_location == destination) & (models.Distance.to_location == origin))
    ).first()
    db.close()
    return jsonify({'distance': dist.distance_km if dist else 0})

# --- Admin Routes ---

@app.route('/admin/shipments')
@admin_required
def admin_shipments():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    per_page = 5
    offset = (page - 1) * per_page

    db = database.SessionLocal()
    query = db.query(models.Booking)

    if status_filter:
        query = query.filter(models.Booking.status == status_filter)
    if search:
        query = query.filter(models.Booking.tracking_id.like(f"%{search}%"))

    total_count = query.count()
    total_pages = math.ceil(total_count / per_page)

    shipments = query.options(
        joinedload(models.Booking.driver),
        joinedload(models.Booking.vehicle)
    ).order_by(models.Booking.date.desc()).offset(offset).limit(per_page).all()
    
    drivers = db.query(models.Driver).filter(models.Driver.status == 'Available').all()
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.status == 'Available').all()
    
    html = render_template('admin_shipments.html', shipments=shipments, drivers=drivers, vehicles=vehicles, 
                           page=page, total_pages=total_pages, status_filter=status_filter, search=search)
    db.close()
    return html

@app.route('/admin/update_shipment', methods=['POST'])
@admin_required
def update_shipment():
    try:
        shipment_id = request.form.get('shipment_id')
        status = request.form.get('status')
        driver_id = request.form.get('driver_id')
        vehicle_id = request.form.get('vehicle_id')

        if not shipment_id or not status:
            return jsonify({"status": "error", "message": "Shipment ID and Status are required"}), 400

        db = database.SessionLocal()
        booking = db.query(models.Booking).filter(models.Booking.id == shipment_id).first()
        
        if not booking:
            db.close()
            return jsonify({"status": "error", "message": "Shipment not found"}), 404

        # Validate and Assign Resources
        if driver_id and driver_id.strip():
            d_id = int(driver_id)
            driver = db.query(models.Driver).get(d_id)
            if not driver:
                db.close()
                return jsonify({"status": "error", "message": "Invalid Driver ID"}), 400
            
            # Update driver status
            booking.driver_id = d_id
            driver.status = "Assigned"
            print("Driver status before commit:", driver.status)
        else:
            # If unassigning, mark previous driver as Available
            if booking.driver_id:
                old_driver = db.query(models.Driver).get(booking.driver_id)
                if old_driver:
                    old_driver.status = "Available"
            booking.driver_id = None

        if vehicle_id and vehicle_id.strip():
            v_id = int(vehicle_id)
            vehicle = db.query(models.Vehicle).get(v_id)
            if not vehicle:
                db.close()
                return jsonify({"status": "error", "message": "Invalid Vehicle ID"}), 400
            
            # Update vehicle status
            booking.vehicle_id = v_id
            vehicle.status = "Assigned"
            print("Vehicle status before commit:", vehicle.status)
        else:
            # If unassigning, mark previous vehicle as Available
            if booking.vehicle_id:
                old_vehicle = db.query(models.Vehicle).get(booking.vehicle_id)
                if old_vehicle:
                    old_vehicle.status = "Available"
            booking.vehicle_id = None

        # Update booking status
        booking.status = status
        
        if status == "Delivered":
            booking.payment_status = "Received"
        
        # Release resources if marked as Delivered
        if status == "Delivered":
            if booking.driver_id:
                driver = db.query(models.Driver).get(booking.driver_id)
                if driver: driver.status = "Available"
            if booking.vehicle_id:
                vehicle = db.query(models.Vehicle).get(booking.vehicle_id)
                if vehicle: vehicle.status = "Available"

        db.commit()
        db.close()
        
        return jsonify({"status": "success", "message": "Shipment updated successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin/delete_shipment/<int:shipment_id>', methods=['POST'])
@admin_required
def delete_shipment(shipment_id):
    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.id == shipment_id).first()
    if booking:
        db.query(models.TrackingHistory).filter(models.TrackingHistory.booking_id == booking.id).delete()
        db.delete(booking)
        db.commit()
        flash('Shipment cleared successfully.', 'success')
    else:
        flash('Shipment not found.', 'error')
    db.close()
    return redirect(url_for('admin_shipments'))

@app.route('/admin/clear_delivered', methods=['POST'])
@admin_required
def clear_delivered():
    db = database.SessionLocal()
    bookings = db.query(models.Booking).filter(models.Booking.status == 'Delivered').all()
    count = 0
    for b in bookings:
        db.query(models.TrackingHistory).filter(models.TrackingHistory.booking_id == b.id).delete()
        db.delete(b)
        count += 1
    db.commit()
    db.close()
    if count > 0:
        flash(f'Successfully cleared {count} delivered shipments!', 'success')
    else:
        flash('No delivered shipments to clear.', 'info')
    return redirect(url_for('admin_shipments'))

@app.route('/admin/add_tracking_update', methods=['POST'])
@admin_required
def add_tracking_update():
    booking_id = request.form['booking_id']
    location = request.form['location']
    status = request.form['status']
    notes = request.form.get('notes', '')

    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking:
        booking.status = status
        # Release resources if marked as Delivered
        if status == "Delivered":
            if booking.driver_id:
                driver = db.query(models.Driver).get(booking.driver_id)
                if driver: driver.status = "Available"
            if booking.vehicle_id:
                vehicle = db.query(models.Vehicle).get(booking.vehicle_id)
                if vehicle: vehicle.status = "Available"
        new_history = models.TrackingHistory(
            booking_id=booking_id,
            location=location,
            status=status,
            notes=notes
        )
        db.add(new_history)
        db.commit()
    db.close()
    
    flash('Tracking update added successfully!', 'success')
    return redirect(url_for('admin_shipments'))

@app.route('/admin/drivers', methods=['GET', 'POST'])
@admin_required
def admin_drivers():
    db = database.SessionLocal()
    if request.method == 'POST':
        name = request.form['name']
        license = request.form['license']
        phone = request.form['phone']
        if name and license and phone:
            new_driver = models.Driver(name=name, license_number=license, phone=phone)
            db.add(new_driver)
            db.commit()
            flash('Driver added successfully!', 'success')
        else:
            flash('All fields are required!', 'error')
        db.close()
        return redirect(url_for('admin_drivers'))

    drivers = db.query(models.Driver).all()
    db.close()
    return render_template('admin_drivers.html', drivers=drivers)

@app.route('/admin/delete_driver/<int:driver_id>', methods=['POST'])
@admin_required
def delete_driver(driver_id):
    db = database.SessionLocal()
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if driver:
        # Unassign any bookings that had this driver
        db.query(models.Booking).filter(models.Booking.driver_id == driver.id).update({'driver_id': None})
        db.delete(driver)
        db.commit()
        flash('Driver deleted successfully!', 'success')
    else:
        flash('Driver not found.', 'error')
    db.close()
    return redirect(url_for('admin_drivers'))

@app.route('/admin/vehicles', methods=['GET', 'POST'])
@admin_required
def admin_vehicles():
    db = database.SessionLocal()
    if request.method == 'POST':
        model = request.form['model']
        plate = request.form['plate']
        capacity = request.form['capacity']
        if model and plate and capacity:
            new_vehicle = models.Vehicle(model=model, plate_number=plate, capacity=capacity)
            db.add(new_vehicle)
            db.commit()
            flash('Vehicle added successfully!', 'success')
        else:
            flash('All fields are required!', 'error')
        db.close()
        return redirect(url_for('admin_vehicles'))

    vehicles = db.query(models.Vehicle).all()
    return render_template('admin_vehicles.html', vehicles=vehicles)

@app.route('/admin/delete_vehicle/<int:vehicle_id>', methods=['POST'])
@admin_required
def delete_vehicle(vehicle_id):
    db = database.SessionLocal()
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if vehicle:
        # Unassign any bookings that had this vehicle
        db.query(models.Booking).filter(models.Booking.vehicle_id == vehicle.id).update({'vehicle_id': None})
        db.delete(vehicle)
        db.commit()
        flash('Vehicle deleted successfully!', 'success')
    else:
        flash('Vehicle not found.', 'error')
    db.close()
    return redirect(url_for('admin_vehicles'))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    db = database.SessionLocal()
    stats = {}
    stats['total_shipments'] = db.query(models.Booking).count()
    stats['delivered'] = db.query(models.Booking).filter(models.Booking.status == 'Delivered').count()
    stats['pending'] = db.query(models.Booking).filter(models.Booking.status != 'Delivered').count()
    stats['total_revenue'] = db.query(func.sum(models.Booking.cost)).scalar() or 0
    
    status_counts = db.query(models.Booking.status.label('status_name'), func.count(models.Booking.id).label('count')).group_by(models.Booking.status).all()
    
    latest_booking = db.query(models.Booking).order_by(models.Booking.id.desc()).first()
    stats['latest_booking_cost'] = latest_booking.cost if latest_booking else 0
    
    db.close()
    return render_template('admin_analytics.html', stats=stats, status_counts=status_counts)

# --- Driver Routes ---

@app.route('/driver_dashboard')
@driver_required
def driver_dashboard():
    db = database.SessionLocal()
    # Find the driver record linked to this user
    driver = db.query(models.Driver).filter(models.Driver.user_id == session['user_id']).first()
    
    if not driver:
        db.close()
        flash('No driver profile found for this account.', 'error')
        return redirect(url_for('index'))
    
    # Fetch shipments assigned to this driver
    shipments = db.query(models.Booking).filter(models.Booking.driver_id == driver.id).all()
    db.close()
    return render_template('driver_dashboard.html', shipments=shipments, driver=driver)

@app.route('/update_location', methods=['POST'])
@driver_required
def update_location():
    data = request.get_json()
    booking_id = data.get('booking_id')
    lat = data.get('lat')
    lon = data.get('lon')
    
    if not booking_id or not lat or not lon:
        return jsonify({"status": "error", "message": "Missing data"}), 400
    
    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    if booking:
        # Automatic Status Update: Assigned -> In Transit on first location update
        if booking.status == "Assigned":
            booking.status = "In Transit"
            print(f"Shipment {booking_id} status updated to In Transit")
            # Add a tracking history entry for this status change
            status_history = models.TrackingHistory(
                booking_id=booking_id,
                location="Shipment started (In Transit)",
                status="In Transit",
                time=datetime.datetime.now()
            )
            db.add(status_history)
        
        # Ensure status is at least In Transit once location is posted
        elif booking.status == "Booked":
             booking.status = "In Transit"

        # Reverse Geocoding using Nominatim (OpenStreetMap)
        city_name = None
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
            headers = {"User-Agent": "CargoExpress-System/1.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as response:
                geodata = json.loads(response.read().decode())
                address = geodata.get('address', {})
                city_name = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
                if not city_name:
                    city_name = address.get('state') or address.get('country')
        except Exception as e:
            print(f"Geocoding Error: {e}")

        # Format: "City Name (lat, lon)"
        lat_rounded = round(float(lat), 2)
        lon_rounded = round(float(lon), 2)
        
        if city_name:
            location_str = f"{city_name} ({lat_rounded}, {lon_rounded})"
        else:
            location_str = f"({lat_rounded}, {lon_rounded})"

        # Update Driver's latest coordinates
        driver = db.query(models.Driver).filter(models.Driver.id == booking.driver_id).first()
        if driver:
            driver.lat = lat_rounded
            driver.lon = lon_rounded

        new_history = models.TrackingHistory(
            booking_id=booking_id,
            location=location_str,
            status=booking.status,
            notes="Browser GPS Update"
        )
        db.add(new_history)
        db.commit()
        db.close()
        return jsonify({"status": "success", "message": "Location updated!"})
    
    db.close()
    return jsonify({"status": "error", "message": "Shipment not found"}), 404

@app.route('/api/get_location/<int:booking_id>')
def get_location(booking_id):
    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    if not booking or not booking.driver_id:
        db.close()
        return jsonify({"status": "error", "message": "Location unavailable"}), 404
        
    driver = db.query(models.Driver).get(booking.driver_id)
    if not driver or driver.lat is None:
        db.close()
        return jsonify({"status": "error", "message": "No live GPS data yet"}), 404

    # Reverse Geocoding for display (optional or can be cached)
    # Reusing formatting logic
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={driver.lat}&lon={driver.lon}&zoom=10"
        headers = {"User-Agent": "CargoExpress-System/1.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=1.5) as response:
            geodata = json.loads(response.read().decode())
            address = geodata.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
            state = address.get('state')
            country = address.get('country')
            
            if city and state:
                location_text = f"{city}, {state} ({driver.lat}, {driver.lon})"
            elif state:
                location_text = f"{state}, {country} ({driver.lat}, {driver.lon})"
            else:
                 location_text = f"({driver.lat}, {driver.lon})"
    except:
        location_text = f"({driver.lat}, {driver.lon})"

    db.close()
    return jsonify({
        "status": "success", 
        "lat": driver.lat, 
        "lon": driver.lon,
        "formatted": location_text
    })

@app.route('/complete_delivery/<int:booking_id>', methods=['POST'])
@driver_required
def complete_delivery(booking_id):
    db = database.SessionLocal()
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    if not booking:
        db.close()
        return jsonify({"status": "error", "message": "Shipment not found"}), 404
        
    # Mark as Delivered
    booking.status = "Delivered"
    booking.payment_status = "Received"
    
    # Release Resources
    if booking.driver_id:
        driver = db.query(models.Driver).get(booking.driver_id)
        if driver:
            driver.status = "Available"
            
    if booking.vehicle_id:
        vehicle = db.query(models.Vehicle).get(booking.vehicle_id)
        if vehicle:
            vehicle.status = "Available"
            
    # Add final tracking history
    history = models.TrackingHistory(
        booking_id=booking.id,
        location="Destination (Delivered)",
        status="Delivered",
        time=datetime.datetime.now(),
        notes="Delivered by driver"
    )
    db.add(history)
    
    db.commit()
    db.close()
    return jsonify({"status": "success", "message": "Shipment marked as Delivered. Resources released!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
