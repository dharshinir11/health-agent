from .models import init_db, get_session, Department, Doctor, AppointmentSlot
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with initial data"""
    engine = init_db()
    session = get_session()
    
    # Check if data already exists
    if session.query(Department).count() > 0:
        print("Database already seeded!")
        return
    
    # Create departments
    departments = [
        Department(name="General Medicine", description="General health checkups and common illnesses"),
        Department(name="Dermatology", description="Skin, hair, and nail conditions"),
        Department(name="Cardiology", description="Heart and cardiovascular system"),
        Department(name="Orthopedics", description="Bones, joints, and muscles"),
        Department(name="Pediatrics", description="Medical care for children")
    ]
    
    session.add_all(departments)
    session.commit()
    
    # Create doctors
    doctors = [
        Doctor(name="Dr. Ananya Sharma", department_id=1, specialization="MBBS, MD - General Medicine"),
        Doctor(name="Dr. Rahul Verma", department_id=1, specialization="MBBS, MD - Internal Medicine"),
        Doctor(name="Dr. Priya Patel", department_id=2, specialization="MBBS, MD - Dermatology"),
        Doctor(name="Dr. Amit Kumar", department_id=2, specialization="MBBS, MD - Dermatology"),
        Doctor(name="Dr. Sneha Reddy", department_id=3, specialization="MBBS, MD - Cardiology"),
        Doctor(name="Dr. Vikram Singh", department_id=3, specialization="MBBS, DM - Cardiology"),
        Doctor(name="Dr. Neha Gupta", department_id=4, specialization="MBBS, MS - Orthopedics"),
        Doctor(name="Dr. Rajesh Iyer", department_id=4, specialization="MBBS, MS - Orthopedics"),
        Doctor(name="Dr. Kavya Nair", department_id=5, specialization="MBBS, MD - Pediatrics"),
        Doctor(name="Dr. Arjun Mehta", department_id=5, specialization="MBBS, MD - Pediatrics")
    ]
    
    session.add_all(doctors)
    session.commit()
    
    # Create appointment slots for the next 7 days
    time_slots = [
        "09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"
    ]
    
    today = datetime.now()
    
    for doctor in doctors:
        for day_offset in range(7):  # Next 7 days
            date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            
            # Each doctor has 3-5 random slots per day
            num_slots = random.randint(3, 5)
            selected_slots = random.sample(time_slots, num_slots)
            
            for time in selected_slots:
                slot = AppointmentSlot(
                    doctor_id=doctor.id,
                    date=date,
                    time=time,
                    available=True
                )
                session.add(slot)
    
    session.commit()
    print("Database seeded successfully!")
    print(f"Departments: {len(departments)}")
    print(f"Doctors: {len(doctors)}")
    print(f"Appointment slots created for next 7 days")

if __name__ == "__main__":
    seed_database()