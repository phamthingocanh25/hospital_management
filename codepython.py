import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

class HospitalManagementSystem:
    def __init__(self):
        """Initializes the database connection."""
        try:
            # --- IMPORTANT: Replace 'password' with your actual MySQL root password ---
            self.connection = mysql.connector.connect(
                host='localhost',
                database='HospitalManagementSystem', # Ensure this database exists
                user='root',
                password='anh@2502' # check and change localhost password của mọi người
            )
            if self.connection.is_connected():
                print(">>> Connection to MySQL database 'HospitalManagementSystem' established successfully.")
        except Error as e:
            print(f"[ERROR] Error connecting to MySQL: {e}")
            # Exit or raise exception if connection fails, as the system can't function
            raise ConnectionError(f"Failed to connect to the database: {e}") from e

    def __del__(self):
        """Closes the database connection upon object destruction."""
        if hasattr(self, 'connection') and self.connection and self.connection.is_connected():
            self.connection.close()
            print(">>> MySQL connection closed.")

    # --- Patient Management ---
    def add_patient(self, name, dob, gender, address, phone):
        """Adds a new patient to the Patients table."""
        query = """
        INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (name, dob, gender, address, phone))
            self.connection.commit()
            patient_id = cursor.lastrowid
            print(f"[SUCCESS] Patient '{name}' added successfully. New Patient ID: {patient_id}")
            cursor.close()
            return patient_id
        except Error as e:
            print(f"[ERROR] Failed to add patient '{name}': {e}")
            self.connection.rollback() # Rollback changes on error
            return None

    def update_patient(self, patient_id, name=None, dob=None, gender=None, address=None, phone=None):
        """Updates existing patient details based on PatientID."""
        updates = []
        params = []

        # Dynamically build the SET part of the query
        if name is not None:
            updates.append("PatientName = %s")
            params.append(name)
        if dob is not None:
            updates.append("DateOfBirth = %s")
            params.append(dob)
        if gender is not None:
            updates.append("Gender = %s")
            params.append(gender)
        if address is not None:
            updates.append("Address = %s")
            params.append(address)
        if phone is not None:
            updates.append("PhoneNumber = %s")
            params.append(phone)

        if not updates:
            print("[INFO] No update fields provided for Patient ID {patient_id}.")
            return False

        query = f"UPDATE Patients SET {', '.join(updates)} WHERE PatientID = %s"
        params.append(patient_id)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(params))
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"[SUCCESS] Patient ID {patient_id} updated successfully.")
                cursor.close()
                return True
            else:
                print(f"[INFO] No patient found with ID {patient_id} to update.")
                cursor.close()
                return False
        except Error as e:
            print(f"[ERROR] Failed to update patient ID {patient_id}: {e}")
            self.connection.rollback()
            return False

    def search_patients(self, name=None, phone=None):
        """Searches for patients by name and/or phone number."""
        query = "SELECT PatientID, PatientName, DateOfBirth, Gender, Address, PhoneNumber FROM Patients WHERE 1=1"
        params = []

        if name:
            query += " AND PatientName LIKE %s"
            params.append(f"%{name}%") # Use % for partial matching
        if phone:
            query += " AND PhoneNumber LIKE %s"
            params.append(f"%{phone}%")

        try:
            # Use dictionary=True for easy access to columns by name
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            patients = cursor.fetchall()
            cursor.close()
            return patients
        except Error as e:
            print(f"[ERROR] Failed to search patients: {e}")
            return []

    # --- Doctor Management ---
    def add_doctor(self, name, department_id, specialty):
        """Adds a new doctor to the Doctors table."""
        query = """
        INSERT INTO Doctors (DoctorName, DepartmentID, Specialty)
        VALUES (%s, %s, %s)
        """
        # Basic check: Ensure department_id is provided (assuming it's mandatory)
        if department_id is None:
             print("[ERROR] Department ID is required to add a doctor.")
             return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (name, department_id, specialty))
            self.connection.commit()
            doctor_id = cursor.lastrowid
            print(f"[SUCCESS] Doctor '{name}' added successfully. New Doctor ID: {doctor_id}")
            cursor.close()
            return doctor_id
        except Error as e:
            print(f"[ERROR] Failed to add doctor '{name}': {e}")
            self.connection.rollback()
            return None

    def get_doctors_by_department(self, department_id):
        """Retrieves doctors belonging to a specific department."""
        query = """
        SELECT d.DoctorID, d.DoctorName, d.Specialty, dep.DepartmentName
        FROM Doctors d
        JOIN Departments dep ON d.DepartmentID = dep.DepartmentID
        WHERE d.DepartmentID = %s
        ORDER BY d.DoctorName
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (department_id,))
            doctors = cursor.fetchall()
            cursor.close()
            return doctors
        except Error as e:
            print(f"[ERROR] Failed to get doctors for department ID {department_id}: {e}")
            return []

    # --- Appointment Management ---
    def schedule_appointment(self, doctor_id, patient_id, appointment_date, appointment_time):
        """Schedules a new appointment."""
        query = """
        INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime)
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            # Consider adding validation: Check if doctor/patient exists, check if time slot is free
            cursor.execute(query, (doctor_id, patient_id, appointment_date, appointment_time))
            self.connection.commit()
            appointment_id = cursor.lastrowid
            print(f"[SUCCESS] Appointment scheduled successfully for Patient ID {patient_id} with Doctor ID {doctor_id} on {appointment_date} at {appointment_time}. Appointment ID: {appointment_id}")
            cursor.close()
            return appointment_id
        except Error as e:
            # Provide more context in the error if possible (e.g., foreign key constraint)
            print(f"[ERROR] Failed to schedule appointment: {e}")
            self.connection.rollback()
            return None

    def get_todays_appointments(self):
        """Retrieves all appointments scheduled for the current date."""
        query = """
        SELECT a.AppointmentID, d.DoctorName, p.PatientName, a.AppointmentTime
        FROM Appointments a
        JOIN Doctors d ON a.DoctorID = d.DoctorID
        JOIN Patients p ON a.PatientID = p.PatientID
        WHERE a.AppointmentDate = CURDATE()
        ORDER BY a.AppointmentTime
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            appointments = cursor.fetchall()
            cursor.close()
            return appointments
        except Error as e:
            print(f"[ERROR] Failed to retrieve today's appointments: {e}")
            return []

    # --- Invoice Management ---
    def create_invoice(self, patient_id, amount, status='Unpaid'):
        """Creates a new invoice for a patient."""
        query = """
        INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, Status)
        VALUES (%s, CURDATE(), %s, %s)
        """
        try:
            cursor = self.connection.cursor()
             # Basic validation: Ensure amount is positive
            if not isinstance(amount, (int, float)) or amount <= 0:
                print("[ERROR] Invalid amount provided for invoice.")
                return None
            cursor.execute(query, (patient_id, amount, status))
            self.connection.commit()
            invoice_id = cursor.lastrowid
            print(f"[SUCCESS] Invoice created successfully for Patient ID {patient_id}. Amount: ${amount:.2f}. Invoice ID: {invoice_id}")
            cursor.close()
            return invoice_id
        except Error as e:
            print(f"[ERROR] Failed to create invoice for Patient ID {patient_id}: {e}")
            self.connection.rollback()
            return None

    def get_patient_invoices(self, patient_id):
        """Retrieves all invoices for a specific patient."""
        query = """
        SELECT InvoiceID, InvoiceDate, TotalAmount, Status
        FROM Invoices
        WHERE PatientID = %s
        ORDER BY InvoiceDate DESC
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (patient_id,))
            invoices = cursor.fetchall()
            cursor.close()
            return invoices
        except Error as e:
            print(f"[ERROR] Failed to retrieve invoices for Patient ID {patient_id}: {e}")
            return []

    # --- Reporting ---
    def generate_financial_report(self, start_date, end_date):
        """Generates a summary financial report between two dates."""
        query = """
        SELECT
            DATE_FORMAT(InvoiceDate, '%Y-%m') AS MonthYear, -- Changed alias for clarity
            COUNT(*) AS TotalInvoices,
            SUM(TotalAmount) AS TotalRevenue,
            -- Ensure NULL sums are treated as 0
            COALESCE(SUM(CASE WHEN Status = 'Paid' THEN TotalAmount ELSE 0 END), 0) AS PaidAmount,
            COALESCE(SUM(CASE WHEN Status = 'Unpaid' THEN TotalAmount ELSE 0 END), 0) AS UnpaidAmount
        FROM Invoices
        WHERE InvoiceDate BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m') -- Group by the formatted month/year
        ORDER BY MonthYear -- Order by the formatted month/year
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (start_date, end_date))
            report_data = cursor.fetchall()
            cursor.close()
            return report_data
        except Error as e:
            print(f"[ERROR] Failed to generate financial report for {start_date} to {end_date}: {e}")
            return []

# ==================================================
# Example Usage - Enhanced Output Formatting
# ==================================================
if __name__ == "__main__":
    print("\n" + "="*30 + " Hospital Management System Demo " + "="*30)
    try:
        hms = HospitalManagementSystem() # Connection established here

        # --- Add a new patient ---
        print("\n--- Adding New Patient ---")
        # Ensure date format matches your database expectations (YYYY-MM-DD is standard)
        new_patient_id = hms.add_patient(
            "John Doe",
            "1990-05-15",
            "M",
            "123 Main St, Anytown",
            "555-1234"
        )
        if new_patient_id:
             hms.add_patient(
                 "Jane Smith",
                 "1988-11-20",
                 "F",
                 "456 Oak Ave, Anytown",
                 "555-5678"
             )
             # Add Sarah Connor again if needed for searching demo
             hms.add_patient(
                 "Sarah Connor",
                 "1985-04-28",
                 "F",
                 "789 Future St, Los Angeles",
                 "555-0199"
             )

        # --- Search for patients ---
        print("\n--- Searching for Patients (Name: 'Doe') ---")
        patients_doe = hms.search_patients(name="Doe")
        if patients_doe:
            print(f"Found {len(patients_doe)} patient(s):")
            # Simple table-like format
            print("-" * 80)
            print(f"{'ID':<5} | {'Name':<20} | {'DOB':<12} | {'Gender':<6} | {'Phone':<15}")
            print("-" * 80)
            for patient in patients_doe:
                # Format date for display if needed
                dob_display = patient['DateOfBirth'].strftime('%Y-%m-%d') if isinstance(patient['DateOfBirth'], date) else str(patient['DateOfBirth'])
                print(f"{patient['PatientID']:<5} | {patient['PatientName']:<20} | {dob_display:<12} | {patient['Gender']:<6} | {patient['PhoneNumber']:<15}")
            print("-" * 80)
        else:
            print("No patients found matching the criteria.")

        # --- Get today's appointments (Assuming some were added manually or via schedule_appointment) ---
        print("\n--- Retrieving Today's Appointments ---")
        appointments_today = hms.get_todays_appointments()
        if appointments_today:
            print(f"Found {len(appointments_today)} appointment(s) for today ({datetime.now().strftime('%Y-%m-%d')}):")
            print("-" * 70)
            print(f"{'Time':<10} | {'Doctor':<25} | {'Patient':<25} | {'Appt ID':<7}")
            print("-" * 70)
            for appt in appointments_today:
                # Format time for display
                time_display = appt['AppointmentTime'].strftime('%H:%M:%S') if hasattr(appt['AppointmentTime'], 'strftime') else str(appt['AppointmentTime'])
                print(f"{time_display:<10} | {appt['DoctorName']:<25} | {appt['PatientName']:<25} | {appt['AppointmentID']:<7}")
            print("-" * 70)
        else:
            print("No appointments scheduled for today.")

        # --- Create some invoices (assuming patient ID 1 and 2 exist) ---
        print("\n--- Creating Invoices ---")
        if new_patient_id: # Use the ID returned earlier
            hms.create_invoice(new_patient_id, 150.75) # For John Doe
            hms.create_invoice(new_patient_id, 55.00, status='Paid') # Add a paid one
        if new_patient_id and new_patient_id + 1: # Assuming Jane is ID+1
             hms.create_invoice(new_patient_id + 1, 210.50) # For Jane Smith

        # --- Generate financial report for the current month ---
        print("\n--- Generating Financial Report (Current Month) ---")
        today = datetime.now().date()
        first_day_of_month = today.replace(day=1)
        # Ensure end_date includes the entire current day if needed, or just use today
        financial_data = hms.generate_financial_report(first_day_of_month, today)

        if financial_data:
            print(f"Financial Summary from {first_day_of_month} to {today}:")
            print("-" * 85)
            print(f"{'Month':<10} | {'Total Invoices':<15} | {'Total Revenue':<18} | {'Paid Amount':<18} | {'Unpaid Amount':<18}")
            print("-" * 85)
            grand_total_revenue = 0
            grand_total_paid = 0
            grand_total_unpaid = 0
            for row in financial_data:
                total_revenue = row['TotalRevenue'] or 0 # Handle None from SUM if no rows match
                paid_amount = row['PaidAmount'] or 0
                unpaid_amount = row['UnpaidAmount'] or 0
                grand_total_revenue += total_revenue
                grand_total_paid += paid_amount
                grand_total_unpaid += unpaid_amount
                print(f"{row['MonthYear']:<10} | {row['TotalInvoices']:<15} | ${total_revenue:<17.2f} | ${paid_amount:<17.2f} | ${unpaid_amount:<17.2f}")
            print("-" * 85)
            # Display Grand Totals - THIS IS THE CALCULATION DISPLAY
            print(f"{'GRAND TOTAL':<10} | {'':<15} | ${grand_total_revenue:<17.2f} | ${grand_total_paid:<17.2f} | ${grand_total_unpaid:<17.2f}")
            print("-" * 85)

        else:
            print(f"No financial data found for the period {first_day_of_month} to {today}.")

    except ConnectionError as ce:
         print(f"\n[CRITICAL] Database connection failed. Cannot run demo. Error: {ce}")
    except Error as db_err:
        # Catch potential lingering DB errors during demo execution
        print(f"\n[ERROR] An unexpected database error occurred during the demo: {db_err}")
    except Exception as e:
        # Catch any other non-database errors
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        # The __del__ method handles closure, but explicit closure in main is good practice
        # if 'hms' in locals() and hasattr(hms, 'connection') and hms.connection.is_connected():
        #     hms.connection.close()
        #     print(">>> MySQL connection explicitly closed in main.")
        print("\n" + "="*32 + " End of Demo " + "="*33)