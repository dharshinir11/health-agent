from database.models import get_session, AppointmentSlot, Doctor
from datetime import datetime

def check_availability(doctor_id: int, date: str) -> dict:
    """
    Check available appointment slots for a doctor on a specific date.
    
    Args:
        doctor_id: ID of the doctor
        date: Date in YYYY-MM-DD format
        
    Returns:
        dict with available slots
    """
    session = get_session()
    
    try:
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
        
        # Get available slots
        slots = session.query(AppointmentSlot).filter_by(
            doctor_id=doctor_id,
            date=date,
            available=True
        ).all()
        
        if not slots:
            return {
                "success": False,
                "error": f"No available slots for {doctor.name} on {date}",
                "doctor_name": doctor.name,
                "date": date
            }
        
        slot_list = []
        for slot in slots:
            slot_list.append({
                "slot_id": slot.id,
                "time": slot.time,
                "available": slot.available
            })
        
        return {
            "success": True,
            "doctor_name": doctor.name,
            "doctor_id": doctor_id,
            "date": date,
            "available_slots": slot_list,
            "count": len(slot_list)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking availability: {str(e)}"
        }
    finally:
        session.close()