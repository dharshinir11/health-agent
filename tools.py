import json


def find_department(symptoms):

    symptoms = symptoms.lower()

    if "skin" in symptoms or "rash" in symptoms:
        return "Dermatology"

    if "fever" in symptoms or "headache" in symptoms:
        return "General Medicine"

    return "General Medicine"


def find_doctors(department):

    with open("doctors.json", "r") as file:
        doctors = json.load(file)

    return [
        doctor for doctor in doctors
        if doctor["department"] == department
    ]


def book_appointment(doctor, patient):

    appointment = {
        "patient": patient,
        "doctor": doctor["name"],
        "department": doctor["department"],
        "time": doctor["time"]
    }

    with open("appointments.json", "a") as file:
        file.write(str(appointment) + "\n")

    return appointment