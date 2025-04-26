import os
import re
import pymysql
from pymysql.err import MySQLError
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import getpass
import bcrypt
import random
import string

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'MaiAnh<3'),
    'database': os.getenv('DB_NAME', 'hospitalmanagementsystem'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Utility Functions
def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_time(time_str):
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_temp_password(length=12):
    """Generate random temporary password"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Database Connection
def get_db_connection():
    """Establish database connection"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except MySQLError as e:
        print(f"❌ Database connection error: {e}")
        return None

# Authentication System
def is_valid_username(username):
    if len(username) < 3 or len(username) > 15:
        return False, "❌ Username must be between 3 and 15 characters long."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "❌ Username can only contain letters, numbers, and underscores."
    return True, None

def is_strong_password(password):
        """Check if password is strong"""
        if len(password) < 8:
            return False, "❌ Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return False, "❌ Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "❌ Password must contain at least one lowercase letter."
        if not re.search(r"[0-9]", password):
            return False, "❌ Password must contain at least one digit."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "❌ Password must contain at least one special character."
        return True, None

def authenticate_user(username, password):
    """Authenticate user and return role and role-specific ID"""
    try:
        conn = get_db_connection()
        if not conn:
            return None, None, None, None, "Database connection failed"

        with conn.cursor() as cursor:  # Ensure that the result is in dictionary format
            cursor.execute("""
                SELECT u.username, u.password, u.role,
                       CASE WHEN u.role = 'doctor' THEN d.DoctorID ELSE NULL END as role_id
                FROM users u
                LEFT JOIN Doctors d ON u.username = d.DoctorUser
                WHERE BINARY u.username = %s
            """, (username,))

            user = cursor.fetchone()

            if user:
                db_password = user['password']
                # Kiểm tra mật khẩu (bcrypt sẽ tự động so sánh với mật khẩu đã được mã hóa)
                if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
                    return user['username'], user['role'], conn, user['role_id'], None
                else:
                    return None, None, None, None, "Incorrect password"
            else:
                return None, None, None, None, "User not found"
    except MySQLError as e:
        return None, None, None, None, f"An error occurred: {str(e)}"

def initialize_admin():
    """Create default admin account if not exists"""
    try:
        conn = get_db_connection()
        if not conn:
            return

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                hashed_pw = hash_password("Admin@123")
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    ('admin', hashed_pw, 'admin')
                )
                conn.commit()
                print("✅ Default admin created (username: admin, password: Admin@123)")
            else:
                print("✅ Admin account already exists")
    except MySQLError as e:
        print(f"❌ Error initializing admin: {e}")
    finally:
        if conn:
            conn.close()

# User Management
def register_user(conn, username, password, confirm_password, role):
    """Register user from GUI input"""
    if not is_valid_username(username)[0]:
        return False, is_valid_username(username)[1]
    
    if password != confirm_password:
        return False, "❌ Passwords do not match"
    
    if not is_strong_password(password)[0]:
        return False, "❌ Password must be at least 8 characters long and contain a mix of uppercase, lowercase, numbers, and special characters."

    valid_roles = ['admin', 'accountant', 'receptionist']
    if role.lower() not in valid_roles:
        return False, f"❌ Invalid role. Must be one of: {', '.join(valid_roles)}"

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "❌ Username already exists"

            hashed_pw = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, role.lower())
            )
            conn.commit()
            return True, f"✅ User '{username}' registered successfully as {role}."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Registration failed: {e}"

def change_password(conn, username, old_password, new_password):
    """Change password for the user"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra mật khẩu cũ
            cursor.execute("SELECT password FROM Users WHERE Username = %s", (username,))
            result = cursor.fetchone()  # Lấy một dòng duy nhất từ kết quả
            
            if result:
                curr_pass = result['password']  # Truy cập mật khẩu cũ qua chỉ mục (index) 0
                if bcrypt.checkpw(old_password.encode('utf-8'), curr_pass.encode('utf-8')):
                    # Mật khẩu cũ đúng, tiến hành cập nhật mật khẩu mới
                    if new_password == old_password:
                        return False, "❌ New password cannot be the same as the old password."
                    else:
                        # Mật khẩu mới không trùng mật khẩu cũ, tiến hành cập nhật
                        if not is_strong_password(new_password)[0]:
                            return False, "❌ Password must be at least 8 characters long and contain a mix of uppercase, lowercase, numbers, and special characters."
                        hashed_new_password = hash_password(new_password)
                        cursor.execute("UPDATE Users SET Password = %s WHERE Username = %s", (hashed_new_password, username))
                        conn.commit()
                    return True, "✅ Password changed successfully."
            else:
                return False, "❌ User not found."
            
    except MySQLError as e:
        return False, f"Database error: {e}"

def delete_user(conn, username):
    """Delete a user from the system"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                return False, "❌ User not found"

            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            return True, "✅ User deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete user: {e}"
    
# Doctor Management
def add_doctor(conn, name, dept_id, specialization, username):
    """Add new doctor with automatic account creation"""
    print("\n--- Add New Doctor ---")

    # Generate a random temporary password
    temp_password = generate_temp_password()

    try:
        with conn.cursor() as cursor:
            # Check if department exists
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (dept_id,))
            if not cursor.fetchone():
                print("❌ Department does not exist")
                return False, "❌ Department does not exist"

            # Check if username already exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                print("❌ Username already exists")
                return False, "❌ Username already exists"

            # Add to Doctors table
            cursor.execute(""" 
                INSERT INTO Doctors (DoctorName, DepartmentID, Specialty, DoctorUser)
                VALUES (%s, %s, %s, %s)
            """, (name, dept_id, specialization, username))

            # Create user account with hashed password
            hashed_pw = hash_password(temp_password)
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, 'doctor')
            """, (username, hashed_pw))

            conn.commit()
            return True, f"✅ Doctor added successfully. Temporary password: {temp_password} - Please change immediately!"
    except MySQLError as e:
        print(f"❌ Failed to add doctor: {e}")
        conn.rollback()
        return False, f"❌ Failed to add doctor: {e}"

def delete_doctor(conn, doctor_id):
    """Delete a doctor from the system based on doctor_id"""
    print("\n--- Delete Doctor ---")
    try:
        with conn.cursor() as cursor:
            # Check if doctor exists
            cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            if not cursor.fetchone():
                return False, "❌ Doctor not found"

            # Delete doctor from Doctors table
            cursor.execute("DELETE FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            conn.commit()

            # Delete corresponding user from users table
            cursor.execute("DELETE FROM users WHERE username = (SELECT DoctorUser FROM Doctors WHERE DoctorID = %s)", (doctor_id,))
            conn.commit()

            return True, "✅ Doctor deleted successfully."
    except MySQLError as e:
        print(f"❌ Failed to delete doctor: {e}")
        conn.rollback()
        return False, f"❌ Failed to delete doctor: {e}"

# Patient Management
def add_patient(conn, name, date_of_birth, gender, address, phone_number):
    """Add new patient to the system"""
    print("\n--- Add New Patient ---")

    try:
        with conn.cursor() as cursor:
            # Add to Patients table
            cursor.execute("""
                INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, date_of_birth, gender, address, phone_number))
            conn.commit()

            return True, "✅ Patient added successfully."
    except MySQLError as e:
        print(f"❌ Failed to add patient: {e}")
        conn.rollback()
        return False, f"❌ Failed to add patient: {e}"

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

def delete_patient(conn, patient_id):
    """Delete a patient from the system"""
    print("\n--- Delete Patient ---")
    
    try:
        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "❌ Patient not found"

            # Delete patient from Patients table
            cursor.execute("DELETE FROM Patients WHERE PatientID = %s", (patient_id,))
            conn.commit()

            return True, "✅ Patient deleted successfully."
    except MySQLError as e:
        print(f"❌ Failed to delete patient: {e}")
        conn.rollback()
        return False, f"❌ Failed to delete patient: {e}"

# Appointment Management
def schedule_appointment(conn, patient_id, doctor_id, appointment_date, appointment_time, status="Scheduled"):
    """
    Schedule a new appointment with the given information.
    """
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem bệnh nhân có tồn tại không
            cursor.execute("SELECT * FROM Patients WHERE PatientID = %s", (patient_id,))
            patient = cursor.fetchone()
            if not patient:
                return False, "❌ Patient not found."

            # Kiểm tra xem bác sĩ có tồn tại không
            cursor.execute("SELECT * FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            doctor = cursor.fetchone()
            if not doctor:
                return False, "❌ Doctor not found."

            # Lên lịch cuộc hẹn
            cursor.execute("""
                INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, doctor_id, appointment_date, appointment_time, status))

            conn.commit()
            return True, "✅ Appointment scheduled successfully."
    
    except MySQLError as e:
        print(f"❌ Error scheduling appointment: {e}")
        conn.rollback()
        return False, f"❌ Failed to schedule appointment: {e}"

def view_appointments(conn, role, username=None, year=None, month=None, day=None):
    """
    View appointments with optional filtering.
    - Admin/Receptionist: See all appointments.
    - Doctor: See only their own appointments.
    """
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT AppointmentID, DoctorID, PatientID, AppointmentDate, AppointmentTime
                FROM Appointments
            """
            params = []
            conditions = []

            if role.lower() == 'doctor':
                query += " WHERE DoctorID = (SELECT DoctorID FROM Doctors WHERE Username = %s)"
                params.append(username)
            else:
                query += " WHERE 1=1"

            if year:
                conditions.append("YEAR(AppointmentDate) = %s")
                params.append(year)
            if month:
                conditions.append("MONTH(AppointmentDate) = %s")
                params.append(month)
            if day:
                conditions.append("DAY(AppointmentDate) = %s")
                params.append(day)

            if conditions:
                query += " AND " + " AND ".join(conditions)

            query += " ORDER BY AppointmentDate DESC, AppointmentTime DESC"

            cursor.execute(query, tuple(params))
            return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"

def update_appointment_status(conn, appointment_id, new_status):
    """Update the status of an appointment"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Appointments
                SET Status = %s
                WHERE AppointmentID = %s
            """, (new_status, appointment_id))
            conn.commit()
            return True, "Appointment status updated successfully."
    except Exception as e:
        return False, f"Failed to update appointment status: {e}"

# Invoice Management
def create_invoice(conn, patient_id, total_amount):
    """Create an invoice for a patient with current date."""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra bệnh nhân tồn tại
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "❌ Patient not found."

            invoice_date = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount)
                VALUES (%s, %s, %s)
            """, (patient_id, invoice_date, total_amount))
            conn.commit()
            return True, "✅ Invoice created successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to create invoice: {e}"
    
def view_invoices(conn, patient_id=None):
    """View invoices (all or for specific patient)"""
    try:
        with conn.cursor() as cursor:  # Không dùng dictionary=True
            if patient_id:
                cursor.execute("""
                    SELECT InvoiceID, PatientID, InvoiceDate, TotalAmount
                    FROM Invoices WHERE PatientID = %s
                    ORDER BY InvoiceDate DESC
                """, (patient_id,))
            else:
                cursor.execute("""
                    SELECT InvoiceID, PatientID, InvoiceDate, TotalAmount
                    FROM Invoices
                    ORDER BY InvoiceDate DESC
                """)
            
            invoices = cursor.fetchall()  # Lấy tất cả dữ liệu về
            return True, invoices
    except MySQLError as e:
        return False, f"Database error: {e}"

# Department Management
def view_departments(conn):
    """View all departments"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments")
            departments = cursor.fetchall()
            if departments:
                return True, departments
            else:
                return False, "No departments found."
    except MySQLError as e:
        return False, f"Failed to retrieve departments: {e}"

# Reporting Functions
def generate_financial_report(conn, by='month', year=None):
    """Generate financial report by month or year."""
    try:
        with conn.cursor() as cursor:
            if by == 'month' and year:
                cursor.execute("""
                    SELECT MONTH(InvoiceDate) as Month, 
                           SUM(TotalAmount) as Total
                    FROM Invoices
                    WHERE YEAR(InvoiceDate) = %s
                    GROUP BY MONTH(InvoiceDate)
                    ORDER BY Month
                """, (year,))
                return True, ("MONTHLY FINANCIAL REPORT FOR " + str(year), cursor.fetchall())
            elif by == 'year':
                cursor.execute("""
                    SELECT YEAR(InvoiceDate) as Year, 
                           SUM(TotalAmount) as Total
                    FROM Invoices
                    GROUP BY YEAR(InvoiceDate)
                    ORDER BY Year
                """)
                return True, ("YEARLY FINANCIAL REPORT", cursor.fetchall())
            else:
                return False, "Invalid report type or missing year"
    except Exception as e:
        return False, f"Failed to generate report: {e}"

# Role-Specific Menu Functions
def admin_menu(conn, username):
    """Admin menu with full access"""
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Register New User")
        print("2. Delete User")
        print("3. Add Doctor")
        print("4. Delete Doctor")
        print("5. Add Patient")
        print("6. Delete Patient")
        print("7. View Patients")
        print("8. Schedule Appointment")
        print("9. View Appointments")
        print("10. Create Invoice")
        print("11. View Invoices")
        print("12. View Departments")
        print("13. Financial Reports")
        print("14. Change Password")
        print("15. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            register_user(conn)
        elif choice == '2':
            delete_user(conn)
        elif choice == '3':
            add_doctor(conn)
        elif choice == '4':
            delete_doctor(conn)
        elif choice == '5':
            add_patient(conn)
        elif choice == '6':
            delete_patient(conn)
        elif choice == '7':
            view_patients(conn)
        elif choice == '8':
            schedule_appointment(conn)
        elif choice == '9':
            view_appointments(conn)
        elif choice == '10':
            create_invoice(conn)
        elif choice == '11':
            view_invoices(conn)
        elif choice == '12':
            view_departments(conn)
        elif choice == '13':
            generate_financial_report(conn)
        elif choice == '14':
            change_password(conn, username)
        elif choice == '15':
            print("Logging out...")
            return
        else:
            print("❌ Invalid option")

def doctor_menu(conn, doctor_id, username):
    """Doctor menu with restricted access"""
    while True:
        print("\n--- DOCTOR MENU ---")
        print("1. View My Appointments")
        print("2. View Patient Information")
        print("3. Change Password")
        print("4. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            view_appointments(conn, doctor_id)
        elif choice == '2':
            patient_id = input("Enter Patient ID: ")
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT PatientName, DateOfBirth, Gender, Address, PhoneNumber
                        FROM Patients
                        WHERE PatientID = %s
                    """, (patient_id,))
                    
                    patient = cursor.fetchone()
                    if patient:
                        print("\n--- Patient Information ---")
                        print(f"Name: {patient['PatientName']}")
                        print(f"DOB: {patient['DateOfBirth']}")
                        print(f"Gender: {patient['Gender']}")
                        print(f"Address: {patient['Address']}")
                        print(f"Phone: {patient['PhoneNumber']}")
                    else:
                        print("❌ Patient not found")
            except MySQLError as e:
                print(f"❌ Database error: {e}")
        elif choice == '3':
            change_password(conn, username)
        elif choice == '4':
            print("Logging out...")
            return
        else:
            print("❌ Invalid option")

def receptionist_menu(conn, username):
    """Receptionist menu with patient and appointment management"""
    while True:
        print("\n--- RECEPTIONIST MENU ---")
        print("1. Add Patient")
        print("2. Delete Patient")
        print("3. View Patients")
        print("4. Schedule Appointment")
        print("5. View Appointments")
        print("6. Change Password")
        print("7. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            add_patient(conn)
        elif choice == '2':
            delete_patient(conn)
        elif choice == '3':
            view_patients(conn)
        elif choice == '4':
            schedule_appointment(conn)
        elif choice == '5':
            view_appointments(conn)
        elif choice == '6':
            change_password(conn, username)
        elif choice == '7':
            print("Logging out...")
            return
        else:
            print("❌ Invalid option")

def accountant_menu(conn, username):
    """Accountant menu with financial management"""
    while True:
        print("\n--- ACCOUNTANT MENU ---")
        print("1. Create Invoice")
        print("2. View Invoices")
        print("3. Financial Reports")
        print("4. Change Password")
        print("5. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            create_invoice(conn)
        elif choice == '2':
            view_invoices(conn)
        elif choice == '3':
            generate_financial_report(conn)
        elif choice == '4':
            change_password(conn, username)
        elif choice == '5':
            print("Logging out...")
            return
        else:
            print("❌ Invalid option")

# Main Application
def main():
    """Main application entry point"""
    print("=== HOSPITAL MANAGEMENT SYSTEM ===")
    
    # Initialize admin account if not exists
    initialize_admin()
    
    while True:
        # Authenticate user
        print("\n--- LOGIN ---")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        conn = get_db_connection()
        if not conn:
            print("❌ Database connection error. Exiting...")
        if not role or not conn:
            print("❌ Authentication failed. Exiting...")
            continue
        print(f"\n🔑 Logged in as {username} with role {role}.")
        
        try:
            # Launch appropriate menu based on role
            if role == 'admin':
                admin_menu(conn, username)
            elif role == 'doctor':
                doctor_menu(conn, role_id, username)
            elif role == 'receptionist':
                receptionist_menu(conn, username)
            elif role == 'accountant':
                accountant_menu(conn, username)
        finally:
            conn.close()
            print("🔒 Session ended. Returning to login...\n")

if __name__ == "__main__":
    main()
