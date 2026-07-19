import models, database, auth
from sqlalchemy.orm import Session

# Create tables
models.Base.metadata.create_all(bind=database.engine)

db = database.SessionLocal()

# Seed data
try:
    # Seed admin user
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user:
        hashed_pw = auth.get_password_hash("admin123")
        admin = models.User(username="admin", password=hashed_pw, role="admin")
        db.add(admin)
        print("Admin user created.")

    # Seed drivers (Replace existing)
    db.query(models.Driver).delete()
    drivers = [
        models.Driver(name="Arjun Nair", license_number="KL-01-2023001", phone="+91-9847012345"),
        models.Driver(name="Rahul Sharma", license_number="DL-04-2022112", phone="+91-9910054321"),
        models.Driver(name="Sandeep Kumar", license_number="HR-26-2021005", phone="+91-9812067890"),
        models.Driver(name="Mohammed Irfan", license_number="KA-05-2023998", phone="+91-9740011223"),
        models.Driver(name="Vishnu Raj", license_number="TN-01-2022554", phone="+91-9444055667")
    ]
    db.bulk_save_objects(drivers)
    print(f"{len(drivers)} Indian drivers seeded.")

    # Seed vehicles (Replace existing)
    db.query(models.Vehicle).delete()
    vehicles = [
        models.Vehicle(model="Tata Ace", plate_number="KL-01-AB-1234", capacity="0.75 Ton"),
        models.Vehicle(model="Mahindra Bolero Pickup", plate_number="MH-12-PQ-5678", capacity="1.5 Tons"),
        models.Vehicle(model="Ashok Leyland Dost", plate_number="TN-02-XY-9012", capacity="1.25 Tons"),
        models.Vehicle(model="Tata 407", plate_number="DL-08-CD-3456", capacity="2.5 Tons"),
        models.Vehicle(model="Eicher Pro 2049", plate_number="HR-55-JK-7890", capacity="4.9 Tons")
    ]
    db.bulk_save_objects(vehicles)
    print(f"{len(vehicles)} Indian commercial vehicles seeded.")

    # Seed distances
    db.query(models.Distance).delete()
    distances = [
        models.Distance(from_location="Kollam", to_location="Trivandrum", distance_km=70),
        models.Distance(from_location="Kollam", to_location="Kochi", distance_km=140),
        models.Distance(from_location="Trivandrum", to_location="Kochi", distance_km=210),
        models.Distance(from_location="Kollam", to_location="Alappuzha", distance_km=85),
        models.Distance(from_location="Kochi", to_location="Alappuzha", distance_km=55),
        
        # Reverse distances
        models.Distance(from_location="Trivandrum", to_location="Kollam", distance_km=70),
        models.Distance(from_location="Kochi", to_location="Kollam", distance_km=140),
        models.Distance(from_location="Kochi", to_location="Trivandrum", distance_km=210),
        models.Distance(from_location="Alappuzha", to_location="Kollam", distance_km=85),
        models.Distance(from_location="Alappuzha", to_location="Kochi", distance_km=55),
        
        # Adding Kottayam basic distances to avoid missing data, as mentioned in the dropdown list
        models.Distance(from_location="Kottayam", to_location="Kochi", distance_km=65),
        models.Distance(from_location="Kochi", to_location="Kottayam", distance_km=65),
        models.Distance(from_location="Kottayam", to_location="Alappuzha", distance_km=45),
        models.Distance(from_location="Alappuzha", to_location="Kottayam", distance_km=45),
        models.Distance(from_location="Kottayam", to_location="Kollam", distance_km=105),
        models.Distance(from_location="Kollam", to_location="Kottayam", distance_km=105),
        models.Distance(from_location="Kottayam", to_location="Trivandrum", distance_km=150),
        models.Distance(from_location="Trivandrum", to_location="Kottayam", distance_km=150),
    ]
    
    # Self distances
    locations = ["Kollam", "Trivandrum", "Kochi", "Alappuzha", "Kottayam"]
    for loc in locations:
        distances.append(models.Distance(from_location=loc, to_location=loc, distance_km=0))

    db.bulk_save_objects(distances)
    print(f"{len(distances)} distance pairs seeded.")

    db.commit()
    print("Database initialized successfully with SQLAlchemy and seed data.")
finally:
    db.close()
