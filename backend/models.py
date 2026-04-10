from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from .database import Base
import enum
from datetime import datetime

class TableStatus(enum.Enum):
    available = "available"
    occupied  = "occupied"
    reserved  = "reserved"

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role     = Column(String, default="customer")  

class RestaurantTable(Base):
    __tablename__ = "tables"
    __table_args__ = {'extend_existing': True}
    id           = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(10), nullable=False)
    capacity     = Column(Integer, nullable=False)
    status       = Column(String(20), default="available")
    position_x   = Column(Float, default=0)
    position_y   = Column(Float, default=0)
    zone         = Column(String(50), default="indoor")

class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String(100), nullable=False)
    phone = Column(String(20))

class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = {'extend_existing': True}
    id               = Column(Integer, primary_key=True, index=True)
    table_id         = Column(Integer, ForeignKey("tables.id"))
    customer_id      = Column(Integer, ForeignKey("customers.id"))
    guest_count      = Column(Integer)
    phone            = Column(String, default="")
    reservation_time = Column(DateTime)
    status           = Column(String(20), default="pending")
    occasion         = Column(String(50), default=None)
    special_requests = Column(Text, default=None)

class OTPSession(Base):
    __tablename__ = "otp_sessions"
    __table_args__ = {'extend_existing': True}
    id         = Column(Integer, primary_key=True, index=True)
    phone      = Column(String(20), nullable=False)
    otp_code   = Column(String(6), nullable=False)
    is_used    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)