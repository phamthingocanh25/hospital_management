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
def authenticate_user():
    """Authenticate user and return role and role-specific ID"""
    print("\n--- Hospital Management System Login ---")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        conn = get_db_connection()
        if not conn:
            return None, None, None, None

        with conn.cursor() as cursor:
            # Get user info with role-specific ID if doctor
            cursor.execute("""
                SELECT u.username, u.password, u.role, 
                       CASE 
                           WHEN u.role = 'doctor' THEN d.DoctorID 
                           ELSE NULL 
                       END as role_id
                FROM users u
                LEFT JOIN Doctors d ON u.username = d.DoctorUser
                WHERE u.username = %s
            """, (username,))
            
            user = cursor.fetchone()

            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    print(f"\n🔑 Login successful! Welcome, {user['username']}.")
                    print(f"🔐 Role: {user['role']}")
                    
                    # Additional verification for doctors
                    if user['role'] == 'doctor' and not user['role_id']:
                        print("❌ Doctor profile not found in Doctors table")
                        conn.close()
                        return None, None, None, None
                    
                    return user['username'], user['role'], conn, user['role_id']
                else:
                    print("\n❌ Login failed: Incorrect password.")
            else:
                print("\n❌ Login failed: User not found.")

            conn.close()
            return None, None, None, None

    except MySQLError as e:
        print(f"\n❌ Login failed: {e}")
        return None, None, None, None

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
def register_user(conn):
    """Register a new user (admin, accountant, receptionist)"""
    print("\n--- Register New User ---")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    role = input("Role (admin/accountant/receptionist): ").lower()

    if password != confirm_password:
        print("❌ Passwords do not match")
        return False

    valid_roles = ['admin', 'accountant', 'receptionist']
    if role not in valid_roles:
        print(f"❌ Invalid role. Must be one of: {', '.join(valid_roles)}")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                print("❌ Username already exists")
                return False

            hashed_pw = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_pw, role)
            )
            conn.commit()
            print(f"✅ User {username} registered as {role} successfully.")
            return True
    except MySQLError as e:
        print(f"❌ Registration failed: {e}")
        conn.rollback()
        return False

def change_password(conn, username):
    """Change password for current user"""
    print("\n--- Change Password ---")
    current_password = getpass.getpass("Current Password: ")
    new_password = getpass.getpass("New Password: ")
    confirm_password = getpass.getpass("Confirm New Password: ")

    if new_password != confirm_password:
        print("❌ New passwords do not match")
        return False

    try:
        with conn.cursor() as cursor:
            # Verify current password
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                print("❌ User not found")
                return False
            
            if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                print("❌ Current password is incorrect")
                return False

            # Update password
            hashed_pw = hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password = %s WHERE username = %s",
                (hashed_pw, username)
            )
            conn.commit()
            print("✅ Password changed successfully.")
            return True
    except MySQLError as e:
        print(f"❌ Failed to change password: {e}")
        conn.rollback()
        return False

# Doctor Management
def add_doctor(conn):
    """Add new doctor with automatic account creation"""
    print("\n--- Add New Doctor ---")
    name = input("Doctor Name: ")
    dept_id = input("Department ID: ")
    specialty = input("Specialty: ")
    username = input("Username for doctor: ")
    
    # Generate a random temporary password
    temp_password = generate_temp_password()
    
    try:
        with conn.cursor() as cursor:
            # Check if department exists
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (dept_id,))
            if not cursor.fetchone():
                print("❌ Department does not exist")
                return False

            # Check if username already exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                print("❌ Username already exists")
                return False

            # Add to Doctors table
            cursor.execute("""
                INSERT INTO Doctors (DoctorName, DepartmentID, Specialty, DoctorUser)
                VALUES (%s, %s, %s, %s)
            """, (name, dept_id, specialty, username))
            
            # Create user account with hashed password
            hashed_pw = hash_password(temp_password)
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, 'doctor')
            """, (username, hashed_pw))
            
            conn.commit()
            print("✅ Doctor added successfully.")
            print(f"⚠️ Temporary password: {temp_password} - Please change immediately!")
            return True
    except MySQLError as e:
        print(f"❌ Failed to add doctor: {e}")
        conn.rollback()
        return False

# Patient Management
def add_patient(conn):
    """Add new patient to the system"""
    print("\n--- Add New Patient ---")
    name = input("Full Name: ")
    dob = input("Date of Birth (YYYY-MM-DD): ")
    gender = input("Gender (M/F/O): ").upper()
    address = input("Address: ")
    phone = input("Phone Number: ")

    if not validate_phone(phone) or not validate_date(dob):
        print("❌ Invalid phone number or date format")
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, dob, gender, address, phone))
            conn.commit()
            print("✅ Patient added successfully.")
            return True
    except MySQLError as e:
        print(f"❌ Failed to add patient: {e}")
        conn.rollback()
        return False

def view_patients(conn):
    """View all patients in the system"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT PatientID, PatientName, DateOfBirth, Gender, PhoneNumber 
                FROM Patients
                ORDER BY PatientName
            """)
            patients = cursor.fetchall()
            
            print("\n--- PATIENT LIST ---")
            for patient in patients:
                print(f"\nID: {patient['PatientID']}")
                print(f"Name: {patient['PatientName']}")
                print(f"DOB: {patient['DateOfBirth']}")
                print(f"Gender: {patient['Gender']}")
                print(f"Phone: {patient['PhoneNumber']}")
            print("\nTotal patients:", len(patients))
            return True
    except MySQLError as e:
        print(f"❌ Failed to retrieve patients: {e}")
        return False

# Appointment Management
def schedule_appointment(conn):
    """Schedule a new appointment"""
    print("\n--- Schedule New Appointment ---")
    patient_id = input("Patient ID: ")
    doctor_id = input("Doctor ID: ")
    date = input("Appointment Date (YYYY-MM-DD): ")
    time = input("Appointment Time (HH:MM): ")

    if not validate_date(date) or not validate_time(time):
        print("❌ Invalid date or time format")
        return False

    try:
        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                print("❌ Patient not found")
                return False

            # Check if doctor exists
            cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            if not cursor.fetchone():
                print("❌ Doctor not found")
                return False

            # Check for existing appointment at same time
            cursor.execute("""
                SELECT AppointmentID FROM Appointments 
                WHERE DoctorID = %s AND AppointmentDate = %s AND AppointmentTime = %s
            """, (doctor_id, date, time))
            if cursor.fetchone():
                print("❌ Doctor already has an appointment at that time")
                return False

            # Schedule appointment
            cursor.execute("""
                INSERT INTO Appointments ( DoctorID,PatientID, AppointmentDate, AppointmentTime)
                VALUES (%s, %s, %s, %s)
            """, ( doctor_id,patient_id, date, time))
            conn.commit()
            print("✅ Appointment scheduled successfully.")
            return True
    except MySQLError as e:
        print(f"❌ Failed to schedule appointment: {e}")
        conn.rollback()
        return False

def view_appointments(conn, doctor_id=None):
    """View appointments (all or for specific doctor)"""
    try:
        with conn.cursor() as cursor:
            if doctor_id:
                # View appointments for specific doctor
                cursor.execute("""
                    SELECT a.AppointmentID, p.PatientName, a.AppointmentDate, a.AppointmentTime
                    FROM Appointments a
                    JOIN Patients p ON a.PatientID = p.PatientID
                    WHERE a.DoctorID = %s
                    ORDER BY a.AppointmentDate, a.AppointmentTime
                """, (doctor_id,))
                title = "--- YOUR APPOINTMENTS ---"
            else:
                # View all appointments
                cursor.execute("""
                    SELECT a.AppointmentID, p.PatientName, d.DoctorName, 
                           a.AppointmentDate, a.AppointmentTime
                    FROM Appointments a
                    JOIN Patients p ON a.PatientID = p.PatientID
                    JOIN Doctors d ON a.DoctorID = d.DoctorID
                    ORDER BY a.AppointmentDate, a.AppointmentTime
                """)
                title = "--- ALL APPOINTMENTS ---"
            
            appointments = cursor.fetchall()
            print(f"\n{title}")
            for appt in appointments:
                print(f"\nID: {appt['AppointmentID']}")
                print(f"Date: {appt['AppointmentDate']} | Time: {appt['AppointmentTime']}")
                print(f"Patient: {appt['PatientName']}")
                if not doctor_id:
                    print(f"Doctor: {appt['DoctorName']}")
            print("\nTotal appointments:", len(appointments))
            return True
    except MySQLError as e:
        print(f"❌ Failed to retrieve appointments: {e}")
        return False

# Invoice Management
def create_invoice(conn):
    """Create a new invoice for patient"""
    print("\n--- Create New Invoice ---")
    try:
        patient_id = input("Patient ID: ")
        
        # Xử lý amount cẩn thận
        while True:
            amount_input = input("Amount: ")
            try:
                amount = float(amount_input)
                if amount <= 0:
                    print("❌ Amount must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number for amount")
        
        date = datetime.now().strftime('%Y-%m-%d')

        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                print("❌ Patient not found")
                return False

            # Create invoice với kiểm tra lỗi
            try:
                cursor.execute("""
                    INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount)
                    VALUES (%s, %s, %s)
                """, (patient_id, date, amount))
                conn.commit()
                print("✅ Invoice created successfully.")
                return True
            except MySQLError as e:
                print(f"❌ Failed to create invoice. Database error: {e}")
                # In ra thông báo lỗi chi tiết từ MySQL
                if e.args[0] == 1264:  # Out of range value for column
                    print("⚠️ The amount value is too large for the database column")
                elif e.args[0] == 1366:  # Incorrect decimal value
                    print("⚠️ Invalid amount format for database")
                conn.rollback()
                return False
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Department Management
def view_departments(conn):
    """View all departments in the system"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT d.DepartmentID, d.DepartmentName, 
                       COUNT(doc.DoctorID) as DoctorCount
                FROM Departments d
                LEFT JOIN Doctors doc ON d.DepartmentID = doc.DepartmentID
                GROUP BY d.DepartmentID, d.DepartmentName
                ORDER BY d.DepartmentName
            """)
            departments = cursor.fetchall()
            
            print("\n--- DEPARTMENT LIST ---")
            for dept in departments:
                print(f"\nID: {dept['DepartmentID']}")
                print(f"Name: {dept['DepartmentName']}")
                print(f"Doctors: {dept['DoctorCount']}")
            return True
    except MySQLError as e:
        print(f"❌ Failed to retrieve departments: {e}")
        return False

# Reporting Functions
def generate_financial_report(conn):
    """Generate financial report by month/year"""
    print("\n--- Financial Report ---")
    print("1. By Month")
    print("2. By Year")
    choice = input("Choose report type: ")

    try:
        with conn.cursor() as cursor:
            if choice == '1':
                year = input("Enter year (YYYY): ")
                cursor.execute("""
                    SELECT MONTH(InvoiceDate) as Month, 
                           SUM(TotalAmount) as Total
                    FROM Invoices
                    WHERE YEAR(InvoiceDate) = %s
                    GROUP BY MONTH(InvoiceDate)
                    ORDER BY Month
                """, (year,))
                title = f"MONTHLY FINANCIAL REPORT FOR {year}"
            elif choice == '2':
                cursor.execute("""
                    SELECT YEAR(InvoiceDate) as Year, 
                           SUM(TotalAmount) as Total
                    FROM Invoices
                    GROUP BY YEAR(InvoiceDate)
                    ORDER BY Year
                """)
                title = "YEARLY FINANCIAL REPORT"
            else:
                print("❌ Invalid choice")
                return False
            
            results = cursor.fetchall()
            print(f"\n{title}")
            print("-" * 40)
            total = 0
            for row in results:
                if choice == '1':
                    print(f"Month {row['Month']}: {row['Total']:,.2f} VND")
                else:
                    print(f"Year {row['Year']}: {row['Total']:,.2f} VND")
                total += row['Total']
            print("-" * 40)
            print(f"GRAND TOTAL: {total:,.2f} VND")
            return True
    except MySQLError as e:
        print(f"❌ Failed to generate report: {e}")
        return False

# Role-Specific Menu Functions
def admin_menu(conn, username):
    """Admin menu with full access"""
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Register New User")
        print("2. Add Doctor")
        print("3. Add Patient")
        print("4. View Patients")
        print("5. Schedule Appointment")
        print("6. View Appointments")
        print("7. Create Invoice")
        print("8. View Invoices")
        print("9. View Departments")
        print("10. Financial Reports")
        print("11. Change Password")
        print("12. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            register_user(conn)
        elif choice == '2':
            add_doctor(conn)
        elif choice == '3':
            add_patient(conn)
        elif choice == '4':
            view_patients(conn)
        elif choice == '5':
            schedule_appointment(conn)
        elif choice == '6':
            view_appointments(conn)
        elif choice == '7':
            create_invoice(conn)
        elif choice == '8':
            view_invoices(conn)
        elif choice == '9':
            view_departments(conn)
        elif choice == '10':
            generate_financial_report(conn)
        elif choice == '11':
            change_password(conn, username)
        elif choice == '12':
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
        print("2. View Patients")
        print("3. Schedule Appointment")
        print("4. View Appointments")
        print("5. Change Password")
        print("6. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            add_patient(conn)
        elif choice == '2':
            view_patients(conn)
        elif choice == '3':
            schedule_appointment(conn)
        elif choice == '4':
            view_appointments(conn)
        elif choice == '5':
            change_password(conn, username)
        elif choice == '6':
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
        username, role, conn, role_id = authenticate_user()
        if not role or not conn:
            print("❌ Authentication failed. Exiting...")
            break
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
