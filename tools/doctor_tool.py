from database.models import get_session, Doctor, Department

def find_doctors(department_id: int) -> dict:
    """
    Find available doctors in a specific department.
    
    Args:
        department_id: ID of the department
        
    Returns:
        dict with list of doctors
    """
    session = get_session()
    
    try:
        doctors = session.query(Doctor).filter_by(department_id=department_id).all()
        
        if not doctors:
            return {
                "success": False,
                "error": "No doctors found in this department"
            }
        
        doctor_list = []
        for doctor in doctors:
            doctor_list.append({
                "id": doctor.id,
                "name": doctor.name,
                "specialization": doctor.specialization,
                "department_name": doctor.department.name
            })
        
        return {
            "success": True,
            "doctors": doctor_list,
            "count": len(doctor_list)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error finding doctors: {str(e)}"
        }
    finally:
        session.close()