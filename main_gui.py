def search_patient(conn, patient_id=None, name=None):
    """Search for a patient by ID or name"""
    try:
        with conn.cursor() as cursor:
            if patient_id:
                cursor.execute("SELECT * FROM Patients WHERE PatientID = %s", (patient_id,))
            elif name:
                cursor.execute("SELECT * FROM Patients WHERE PatientName LIKE %s", ('%' + name + '%',))
            else:
                return False, "Please provide either patient ID or name to search."

            patient = cursor.fetchall()  # Get the first result (if any)
            if not patient:
                return False, "No patient found with the provided ID or name."
            return True, patient

    except MySQLError as e:
        return False, f"Error: {e}"
