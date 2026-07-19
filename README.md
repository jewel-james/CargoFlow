# 🚚 CargoFlow
### Smart Cargo Booking & Real-Time Tracking System

CargoFlow is a full-stack web application for regional road cargo logistics. It allows users to book shipments, get instant cost estimates, and track their cargo in real time using driver GPS — all through a clean, modern web interface.

Built as a portfolio project using **Python Flask** and **SQLite**, it demonstrates real-world features like role-based authentication, automated driver assignment, live GPS tracking via the browser, and an admin management dashboard.

---

## ✨ Features

### 👤 User
- Register and login securely (bcrypt password hashing)
- Book a shipment with sender/receiver details, origin, destination, and weight
- Instant cost estimate based on distance and weight
- Receive a unique **Tracking ID** on booking
- Track shipment status and location history in real time
- View all personal shipments

### 🚗 Driver
- Dedicated driver dashboard showing assigned shipments
- Share live GPS location via browser — automatically updates tracking
- Status automatically changes from `Assigned → In Transit` on first GPS ping
- Mark shipment as **Delivered** to release resources

### 🛠️ Admin
- Full shipment management (view, update status, reassign drivers/vehicles, delete)
- Driver management (add/delete drivers)
- Vehicle management (add/delete vehicles)
- Business analytics dashboard (total shipments, revenue, status breakdown)
- Add manual tracking updates with location and notes

### ⚙️ System
- **Automated resource assignment** — when a user books, the system picks an available driver and vehicle automatically
- **Reverse geocoding** via OpenStreetMap Nominatim — GPS coordinates converted to city names
- **Resource release** — driver and vehicle auto-freed when delivery is marked complete
- Role-based access control (user / driver / admin)

---

## 🛠️ Technologies Used

| Category | Technologies |
|----------|--------------|
| Backend | Python 3.12, Flask |
| Database | SQLite, SQLAlchemy |
| Frontend | HTML5, CSS3, Jinja2 |
| Authentication | bcrypt |
| Location Services | Browser Geolocation API |
| Geocoding | OpenStreetMap Nominatim |
---

## 📁 Folder Structure

```
cargoflow/
├── app.py                  # Main Flask application — all routes
├── models.py               # SQLAlchemy ORM models (User, Booking, Driver, Vehicle, etc.)
├── database.py             # Database engine and session setup
├── auth.py                 # Password hashing utilities
├── create_db.py            # DB initializer and seed data script
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout
│   ├── landing.html        # Public homepage
│   ├── index.html          # Logged-in homepage
│   ├── login.html
│   ├── register.html
│   ├── book.html           # Booking form
│   ├── result.html         # Booking confirmation
│   ├── track.html          # Tracking input
│   ├── track_result.html   # Tracking result with history timeline
│   ├── my_shipments.html   # User's shipment list
│   ├── retrieve_tracking.html
│   ├── driver_dashboard.html
│   ├── admin_shipments.html
│   ├── admin_drivers.html
│   ├── admin_vehicles.html
│   └── admin_analytics.html
│
└── static/
    └── css/
        └── styles.css
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
git clone https://github.com/jewel-james/CargoFlow.git

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```
Edit `.env` and set a strong `SECRET_KEY`.

### 5. Initialize the database
```bash
python create_db.py
```
This creates `cargo_v2.db` with the admin user, sample drivers, vehicles, and city distance data.

---

## ▶️ Running the App

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## 🔑 Default Credentials

## 🔑 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Driver | driver1 | password123 |

> These credentials are provided for demonstration purposes only.

---

## 🔄 How It Works — Full Flow

```
User Books Shipment
      ↓
System Auto-Assigns Available Driver + Vehicle
      ↓
Driver Logs In → Sees Shipment on Dashboard
      ↓
Driver Shares GPS Location → Status: "In Transit"
      ↓
Tracking History Updated (City name from GPS)
      ↓
Driver Marks Delivered → Driver & Vehicle Released
```

---

## 🚀Roadmap

- [ ] Email/SMS notifications on booking and delivery
- [ ] Google Maps integration for live map view
- [ ] Multi-city route planning
- [ ] Payment gateway integration
- [ ] Mobile-responsive PWA version
- [ ] REST API for third-party integrations
- [ ] Docker containerization for easy deployment

---

## 📄 License

## 📄 License

This project is intended for educational and portfolio purposes.
