from database.models import get_session, Appointment, AppointmentSlot, Doctor
from datetime import datetime

def book_appointment(patient_name: str, doctor_id: int, date: str, time: str) -> dict:
    """
    Book an appointment for a patient with a doctor.
    
    Args:
        patient_name: Name of the patient
        doctor_id: ID of the doctor
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM AM/PM format
        
    Returns:
        dict with booking confirmation
    """
    session = get_session()
    
    try:
        # Validate inputs
        if not patient_name or not patient_name.strip():
            return {
                "success": False,
                "error": "Patient name is required"
            }
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": "Invalid date format. Please use YYYY-MM-DD format."
            }
        
        # Get doctor info
        doctor = session.query(Doctor).filter_by(id=doctor_id).first()
        if not doctor:
            return {
                "success": False,
                "error": "Doctor not found"
            }
        
        # Check if slot exists and is available
        slot = session.query(AppointmentSlot).filter_by(
            doctor_id=doctor_id,
            date=date,
            time=time,
            available=True
        ).first()
        
        if not slot:
            return {
                "success": False,
                "error": f"Slot not available for {doctor.name} at {time} on {date}",
                "doctor_name": doctor.name,
                "date": date,
                "time": time
            }
        
        # Create appointment
        appointment = Appointment(
            patient_name=patient_name.strip(),
            doctor_id=doctor_id,
            date=date,
            time=time,
            status='confirmed'
        )
        
        session.add(appointment)
        
        # Mark slot as unavailable
        slot.available = False
        
        session.commit()
        
        return {
            "success": True,
            "appointment_id": appointment.id,
            "patient_name": patient_name,
            "doctor_name": doctor.name,
            "department_name": doctor.department.name,
            "date": date,
            "time": time,
            "status": "confirmed",
            "message": f"Appointment successfully booked with {doctor.name} for {date} at {time}"
        }
    
    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "error": f"Error booking appointment: {str(e)}"
        }
    finally:
        session.close()