from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    
    doctors = relationship("Doctor", back_populates="department")

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    specialization = Column(String(200))
    
    department = relationship("Department", back_populates="doctors")
    slots = relationship("AppointmentSlot", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class AppointmentSlot(Base):
    __tablename__ = 'appointment_slots'
    
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    date = Column(String(20), nullable=False)  # Format: YYYY-MM-DD
    time = Column(String(20), nullable=False)  # Format: HH:MM AM/PM
    available = Column(Boolean, default=True)
    
    doctor = relationship("Doctor", back_populates="slots")

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_name = Column(String(100), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    status = Column(String(50), default='confirmed')
    created_at = Column(String(50), default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    doctor = relationship("Doctor", back_populates="appointments")

def init_db():
    """Initialize database and create tables"""
    db_path = os.path.join(os.path.dirname(__file__), 'healthcare.db')
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    db_path = os.path.join(os.path.dirname(__file__), 'healthcare.db')
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Session = sessionmaker(bind=engine)
    return Session()