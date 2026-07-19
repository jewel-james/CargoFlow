from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, default="user")

    bookings = relationship("Booking", back_populates="owner")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender = Column(String)
    sender_email = Column(String, nullable=True)
    sender_phone = Column(String, nullable=True)
    receiver = Column(String)
    origin = Column(String)
    destination = Column(String)
    weight = Column(Float)
    status = Column(String, default="Booked")
    payment_status = Column(String, default="Pending")
    date = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    cost = Column(Float)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)

    owner = relationship("User", back_populates="bookings")
    driver = relationship("Driver")
    vehicle = relationship("Vehicle")
    history = relationship("TrackingHistory", back_populates="booking")

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String)
    license_number = Column(String)
    phone = Column(String)
    status = Column(String, default="Available")
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    plate_number = Column(String)
    capacity = Column(String)
    status = Column(String, default="Available")

class TrackingHistory(Base):
    __tablename__ = "tracking_history"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    location = Column(String)
    time = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    status = Column(String)
    notes = Column(String, nullable=True)

    booking = relationship("Booking", back_populates="history")

class Distance(Base):
    __tablename__ = "distance_table"

    id = Column(Integer, primary_key=True, index=True)
    from_location = Column(String)
    to_location = Column(String)
    distance_km = Column(Integer)
