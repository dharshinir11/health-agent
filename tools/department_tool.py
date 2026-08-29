from database.models import get_session, Department

def find_department(user_request: str) -> dict:
    """
    Determine the most appropriate department based on user's symptoms/request.
    
    Args:
        user_request: User's description of their symptoms or request
        
    Returns:
        dict with department information
    """
    session = get_session()
    
    # Simple keyword-based routing (mock implementation)
    # In a real system, this would use an LLM or more sophisticated NLP
    user_request_lower = user_request.lower()
    
    department_keywords = {
        'Dermatology': ['skin', 'rash', 'acne', 'eczema', 'psoriasis', 'hair', 'nail'],
        'Cardiology': ['chest pain', 'heart', 'cardiac', 'palpitation', 'blood pressure'],
        'Orthopedics': ['bone', 'joint', 'muscle', 'fracture', 'back pain', 'knee', 'shoulder'],
        'Pediatrics': ['child', 'baby', 'infant', 'kid', 'pediatric'],
        'General Medicine': ['fever', 'headache', 'cold', 'cough', 'flu', 'general', 'checkup', 'sick']
    }
    
    # Find matching department
    for dept_name, keywords in department_keywords.items():
        for keyword in keywords:
            if keyword in user_request_lower:
                department = session.query(Department).filter_by(name=dept_name).first()
                if department:
                    return {
                        "success": True,
                        "department_id": department.id,
                        "department_name": department.name,
                        "description": department.description,
                        "reasoning": f"Based on symptoms mentioned, {dept_name} seems appropriate"
                    }
    
    # Default to General Medicine if no match
    department = session.query(Department).filter_by(name="General Medicine").first()
    if department:
        return {
            "success": True,
            "department_id": department.id,
            "department_name": department.name,
            "description": department.description,
            "reasoning": "Defaulting to General Medicine for general consultation"
        }
    
    return {
        "success": False,
        "error": "Could not determine appropriate department"
    }