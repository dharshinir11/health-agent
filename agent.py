from tools import find_department, find_doctors, book_appointment


def run_agent(user_message):

    department = find_department(user_message)

    doctors = find_doctors(department)

    if not doctors:
        return "Sorry, I couldn't find an available doctor."

    doctor = doctors[0]

    return {
        "department": department,
        "doctor": doctor,
        "message": (
            f"I recommend {department}. "
            f"Dr. {doctor['name']} is available at {doctor['time']}."
        )
    }