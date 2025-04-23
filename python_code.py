import os
import re
import pymysql
from pymysql.err import MySQLError
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import getpass
import bcrypt

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'admin_user'),
    'password': os.getenv('DB_PASSWORD', 'doctor_pass'),
    'database': os.getenv('DB_NAME', 'hospitalmanagementsystem'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'ssl': {'ca': os.getenv('SSL_CA_PATH')} if os.getenv('SSL_ENABLED') == 'true' else None
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
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Database Connection with Role-Based Access
def get_connection(role=None):
    """Establish secure database connection with role-based credentials"""
    config = DB_CONFIG.copy()
    
    # Override credentials based on role
    if role == 'doctor':
        config.update({
            'user': os.getenv('DOCTOR_USER', 'doctor_user'),
            'password': os.getenv('DOCTOR_PASS', 'doctor_pass')
        })
    elif role == 'receptionist':
        config.update({
            'user': os.getenv('RECEPTIONIST_USER', 'receptionist_user'),
            'password': os.getenv('RECEPTIONIST_PASS', 'recept_pass')
        })
    elif role == 'accountant':
        config.update({
            'user': os.getenv('ACCOUNTANT_USER', 'accountant_user'),
            'password': os.getenv('ACCOUNTANT_PASS', 'acct_pass')
        })
    
    try:
        connection = pymysql.connect(**config)
        return connection
    except MySQLError as e:
        print(f"❌ Database connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# Patient Management
def add_patient(name, dob, gender, address, phone, current_role):
    """Add new patient with validation and role-based access control"""
    if not validate_phone(phone):
        print("❌ Invalid phone number format")
        return False
    
    if not validate_date(dob):
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return False

    # Only admin and receptionist can add patients
    if current_role not in ['admin', 'receptionist']:
        print("❌ Access denied: Insufficient privileges")
        return False

    conn = get_connection(current_role)
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # Check if phone already exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PhoneNumber = %s", (phone,))
            if cursor.fetchone():
                print("❌ Phone number already exists")
                return False

            sql = """INSERT INTO Patients 
                     (PatientName, DateOfBirth, Gender, Address, PhoneNumber) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (name, dob, gender, address, phone))
        conn.commit()
        print("✅ Patient added successfully.")
        return True
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Doctor Management (Admin only)
def add_doctor(name, department_id, specialty, license_number, current_role):
    """Add new doctor with validation"""
    if current_role != 'admin':
        print("❌ Access denied: Only administrators can add doctors")
        return False

    conn = get_connection(current_role)
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # Check if department exists
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (department_id,))
            if not cursor.fetchone():
                print("❌ Department does not exist")
                return False

            # Check if license number is unique
            cursor.execute("SELECT DoctorID FROM Doctors WHERE LicenseNumber = %s", (license_number,))
            if cursor.fetchone():
                print("❌ License number already exists")
                return False

            sql = """INSERT INTO Doctors 
                     (DoctorName, DepartmentID, Specialty, LicenseNumber) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (name, department_id, specialty, license_number))
        conn.commit()
        print("✅ Doctor added successfully.")
        return True
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Appointment Management
def schedule_appointment(patient_id, doctor_id, date, time, current_role):
    """Schedule appointment with validation"""
    if not validate_date(date):
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return False
    
    if not validate_time(time):
        print("❌ Invalid time format. Use HH:MM")
        return False

    # Only admin, doctor (for themselves), and receptionist can schedule appointments
    if current_role not in ['admin', 'doctor', 'receptionist']:
        print("❌ Access denied: Insufficient privileges")
        return False

    conn = get_connection(current_role)
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                print("❌ Patient does not exist")
                return False

            # Check if doctor exists
            cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            if not cursor.fetchone():
                print("❌ Doctor does not exist")
                return False

            # Check for duplicate appointments
            cursor.execute("""SELECT AppointmentID FROM Appointments 
                              WHERE DoctorID = %s AND AppointmentDate = %s AND AppointmentTime = %s""",
                           (doctor_id, date, time))
            if cursor.fetchone():
                print("❌ Doctor already has an appointment at that time")
                return False

            sql = """INSERT INTO Appointments 
                     (PatientID, DoctorID, AppointmentDate, AppointmentTime) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (patient_id, doctor_id, date, time))
        conn.commit()
        print("📅 Appointment scheduled successfully.")
        return True
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Invoice Management
def create_invoice(patient_id, date, amount, current_role):
    """Create invoice with validation"""
    if not validate_date(date):
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return False
    
    if amount <= 0:
        print("❌ Amount must be positive")
        return False

    # Only admin and accountant can create invoices
    if current_role not in ['admin', 'accountant']:
        print("❌ Access denied: Insufficient privileges")
        return False

    conn = get_connection(current_role)
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                print("❌ Patient does not exist")
                return False

            sql = """INSERT INTO Invoices 
                     (PatientID, InvoiceDate, TotalAmount) 
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (patient_id, date, amount))
        conn.commit()
        print("🧾 Invoice created successfully.")
        return True
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Reporting Functions with Role-Based Access
def report_appointments_by_day(date=None, current_role=None, doctor_id=None):
    """Generate appointment report with role-based restrictions"""
    conn = get_connection(current_role)
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            if date:
                if not validate_date(date):
                    print("❌ Invalid date format. Use YYYY-MM-DD")
                    return False
                
                # Different queries based on role
                if current_role == 'doctor':
                    sql = """SELECT a.AppointmentID, p.PatientName, d.DoctorName, 
                                     a.AppointmentDate, a.AppointmentTime
                              FROM Appointments a
                              JOIN Patients p ON a.PatientID = p.PatientID
                              JOIN Doctors d ON a.DoctorID = d.DoctorID
                              WHERE a.AppointmentDate = %s AND a.DoctorID = %s
                              ORDER BY a.AppointmentTime"""
                    cursor.execute(sql, (date, doctor_id))
                else:
                    sql = """SELECT a.AppointmentID, p.PatientName, d.DoctorName, 
                                     a.AppointmentDate, a.AppointmentTime
                              FROM Appointments a
                              JOIN Patients p ON a.PatientID = p.PatientID
                              JOIN Doctors d ON a.DoctorID = d.DoctorID
                              WHERE a.AppointmentDate = %s
                              ORDER BY a.AppointmentTime"""
                    cursor.execute(sql, (date,))
                
                title = f"📅 Appointments for {date}"
            else:
                if current_role == 'doctor':
                    sql = """SELECT AppointmentDate, COUNT(*) AS TotalAppointments
                             FROM Appointments
                             WHERE DoctorID = %s
                             GROUP BY AppointmentDate
                             ORDER BY AppointmentDate"""
                    cursor.execute(sql, (doctor_id,))
                else:
                    sql = """SELECT AppointmentDate, COUNT(*) AS TotalAppointments
                             FROM Appointments
                             GROUP BY AppointmentDate
                             ORDER BY AppointmentDate"""
                    cursor.execute(sql)
                
                title = "📅 Daily Appointment Summary"

            results = cursor.fetchall()
            print(f"\n{title}:")
            
            if not results:
                print("No appointments found")
                return True
                
            if date:
                for row in results:
                    print(f"ID: {row['AppointmentID']}")
                    print(f"Patient: {row['PatientName']}")
                    if current_role != 'doctor':  # Doctors already know it's their appointments
                        print(f"Doctor: {row['DoctorName']}")
                    print(f"Time: {row['AppointmentTime']}")
                    print("-" * 30)
            else:
                for row in results:
                    print(f"{row['AppointmentDate']}: {row['TotalAppointments']} appointments")
        return True
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

def financial_report_by_month(year=None, current_role=None):
    """Generate financial report with role-based restrictions"""
    # Only admin and accountant can view financial reports
    if current_role not in ['admin', 'accountant']:
        print("❌ Access denied: Insufficient privileges")
        return False

    conn = get_connection(current_role)
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            if year:
                sql = """SELECT MONTH(InvoiceDate) AS Month, 
                                SUM(TotalAmount) AS Revenue
                         FROM Invoices
                         WHERE YEAR(InvoiceDate) = %s
                         GROUP BY MONTH(InvoiceDate)
                         ORDER BY Month"""
                cursor.execute(sql, (year,))
                title = f"💰 Monthly Revenue Report for {year}"
            else:
                sql = """SELECT YEAR(InvoiceDate) AS Year, 
                                MONTH(InvoiceDate) AS Month, 
                                SUM(TotalAmount) AS Revenue
                         FROM Invoices
                         GROUP BY YEAR(InvoiceDate), MONTH(InvoiceDate)
                         ORDER BY Year, Month"""
                cursor.execute(sql)
                title = "💰 Monthly Revenue Report"

            results = cursor.fetchall()
            print(f"\n{title}:")
            
            if not results:
                print("No financial data found")
                return True
                
            total = 0
            for row in results:
                month = row['Month']
                revenue = row['Revenue']
                if 'Year' in row:
                    print(f"{row['Year']}-{month:02d}: {revenue:,.2f} VND")
                else:
                    print(f"Month {month:02d}: {revenue:,.2f} VND")
                total += revenue
            
            if len(results) > 1:
                print("-" * 30)
                print(f"Total Revenue: {total:,.2f} VND")
        return True
    except MySQLError as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

def initialize_admin():
    """Tạo admin mặc định nếu chưa có trong database"""
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="MaiAnh<3",
            database="hospitalmanagementsystem",
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = 'admin_user';")
            if cursor.fetchone():
                print("✅ Admin user đã tồn tại.")
            else:
                # Hash mật khẩu mặc định
                hashed_pw = bcrypt.hashpw("Admin@123".encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s);",
                    ('admin_user', hashed_pw.decode('utf-8'), 'admin')
                )
                print("✅ Admin mặc định đã được tạo (username: admin_user, password: Admin@123)")
        conn.close()
    except pymysql.MySQLError as e:
        print(f"❌ Database error: {e}")

def register_user(username, plain_password, role):
    hashed_pw = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='MaiAnh<3',
        database='hospitalmanagementsystem',
        autocommit=True
    )
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                       (username, hashed_pw, role))
    conn.close()
    print(f"✅ User {username} registered.")

# Authentication System
def authenticate_user():
    print("\n--- Hospital Management System Login ---")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="MaiAnh<3",
            database="hospitalmanagementsystem",
            autocommit=True
        )

        with connection.cursor() as cursor:
            # Truy vấn thông tin user
            cursor.execute("SELECT password, role FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result:
                hashed_pw_from_db, role = result
                # Kiểm tra mật khẩu
                if bcrypt.checkpw(password.encode('utf-8'), hashed_pw_from_db.encode('utf-8')):
                    print(f"\n🔑 Login successful! Welcome, {username}.")
                    print(f"🔐 Role: {role}")
                    return role, connection
                else:
                    print("\n❌ Login failed: Incorrect password.")
            else:
                print("\n❌ Login failed: User not found.")

            connection.close()
            return None, None

    except pymysql.MySQLError as e:
        print(f"\n❌ Login failed: {e}")
        return None, None

# Hàm xử lý menu cho từng vai trò
def handle_role_menu(role, conn):
    with conn.cursor() as cursor:
        if role == "doctor":
            doctor_menu(cursor)
        elif role == "accountant":
            accountant_menu(cursor)
        elif role == "admin":
            admin_menu(cursor)
        elif role == "receptionist":
            receptionist_menu(cursor)
        else:
            print("⚠️ Unknown role. No access granted.")


# Admin Menu
def admin_menu(cursor):
    """Admin menu with full access"""
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add Patient")
        print("2. Add Doctor")
        print("3. Schedule Appointment")
        print("4. Create Invoice")
        print("5. View Appointments (Specific Day)")
        print("6. View Appointments (All Days)")
        print("7. Financial Report (By Month)")
        print("8. Financial Report (By Year)")
        print("9. Register New User")
        print("10. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            print("Adding patient...")
        elif choice == '2':
            print("Adding doctor...")
        elif choice == '3':
            print("Scheduling appointment...")
        elif choice == '4':
            print("Creating invoice...")
        elif choice == '5':
            day = input("Enter specific day (YYYY-MM-DD): ")
            cursor.execute(f"SELECT * FROM appointments WHERE appointment_date = '{day}';")
            for row in cursor.fetchall():
                print(row)
        elif choice == '6':
            cursor.execute("SELECT * FROM appointments;")
            for row in cursor.fetchall():
                print(row)
        elif choice == '7':
            month = input("Enter month (YYYY-MM): ")
            cursor.execute(f"SELECT * FROM invoices WHERE invoice_date LIKE '{month}-%';")
            for row in cursor.fetchall():
                print(row)
        elif choice == '8':
            year = input("Enter year (YYYY): ")
            cursor.execute(f"SELECT * FROM invoices WHERE invoice_date LIKE '{year}-%';")
            for row in cursor.fetchall():
                print(row)
        elif choice == '9':
            username = input("Enter new username: ")
            password = getpass.getpass("Enter new password: ")
            role = input("Enter role (admin/doctor/receptionist/accountant): ")
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                           (username, hashed_pw.decode('utf-8'), role))
            print(f"User {username} registered successfully.")
        elif choice == '10':
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")

# Doctor Menu
def doctor_menu(cursor):
    """Doctor menu with limited access"""
    while True:
        print("\n--- DOCTOR MENU ---")
        print("1. View My Patients")
        print("2. View My Appointments")
        print("3. Logout")
        
        choice = input("Choose an option: ")

        if choice == '1':
            cursor.execute("SELECT * FROM patients WHERE doctor_assigned = 'doctor_user';")
            for row in cursor.fetchall():
                print(row)
        elif choice == '2':
            cursor.execute("SELECT * FROM appointments WHERE doctor_name = 'doctor_user';")
            for row in cursor.fetchall():
                print(row)
        elif choice == '3':
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")

# Receptionist Menu
def receptionist_menu(cursor):
    """Receptionist menu with limited access"""
    while True:
        print("\n--- RECEPTIONIST MENU ---")
        print("1. View Patients")
        print("2. View Appointments")
        print("3. Logout")
        
        choice = input("Choose an option: ")

        if choice == '1':
            cursor.execute("SELECT * FROM patients;")
            for row in cursor.fetchall():
                print(row)
        elif choice == '2':
            cursor.execute("SELECT * FROM appointments;")
            for row in cursor.fetchall():
                print(row)
        elif choice == '3':
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")

# Accountant Menu
def accountant_menu(cursor):
    """Accountant menu with limited access"""
    while True:
        print("\n--- ACCOUNTANT MENU ---")
        print("1. View Patients")
        print("2. View Invoices")
        print("3. Logout")
        
        choice = input("Choose an option: ")

        if choice == '1':
            cursor.execute("SELECT * FROM patients;")
            for row in cursor.fetchall():
                print(row)
        elif choice == '2':
            cursor.execute("SELECT * FROM invoices;")
            for row in cursor.fetchall():
                print(row)
        elif choice == '3':
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")

# Main execution
role, conn = authenticate_user()

if conn:
    handle_role_menu(role, conn)
else:
    print("🚫 Cannot proceed without login.")

# Menu Systems for Each Role
def admin_menu():
    """Administrator menu with full access"""
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add Patient")
        print("2. Add Doctor")
        print("3. Schedule Appointment")
        print("4. Create Invoice")
        print("5. View Appointments (Specific Day)")
        print("6. View Appointments (All Days)")
        print("7. Financial Report (By Month)")
        print("8. Financial Report (By Year)")
        print("9. Register New User")
        print("10. Logout")
        
        choice = input("Choose an option (1-9): ")
        
        if choice == "1":
            print("\nAdd New Patient")
            name = input("Full Name: ")
            dob = input("Date of Birth (YYYY-MM-DD): ")
            gender = input("Gender (M/F/O): ").upper()
            address = input("Address: ")
            phone = input("Phone Number: ")
            add_patient(name, dob, gender, address, phone, 'admin')
            
        elif choice == "2":
            print("\nAdd New Doctor")
            name = input("Doctor Name: ")
            dept_id = input("Department ID: ")
            specialty = input("Specialty: ")
            license = input("License Number: ")
            add_doctor(name, dept_id, specialty, license, 'admin')
            
        elif choice == "3":
            print("\nSchedule Appointment")
            pid = input("Patient ID: ")
            did = input("Doctor ID: ")
            date = input("Appointment Date (YYYY-MM-DD): ")
            time = input("Time (HH:MM): ")
            schedule_appointment(pid, did, date, time, 'admin')
            
        elif choice == "4":
            print("\nCreate Invoice")
            pid = input("Patient ID: ")
            date = input("Invoice Date (YYYY-MM-DD): ")
            amount = input("Total Amount (VND): ")
            create_invoice(pid, date, amount, 'admin')
            
        elif choice == "5":
            date = input("\nEnter date to view appointments (YYYY-MM-DD): ")
            report_appointments_by_day(date, 'admin')
            
        elif choice == "6":
            report_appointments_by_day(current_role='admin')
            
        elif choice == "7":
            year = input("\nEnter year to view financial report (YYYY): ")
            financial_report_by_month(year, 'admin')
            
        elif choice == "8":
            financial_report_by_month(current_role='admin')
            
        elif choice == "9":
            register_username = input("Enter new username: ")
            register_password = getpass.getpass("Enter new password: ")
            register_role = input("Enter role (admin/doctor/receptionist/accountant): ")
            register_user(register_username, register_password, register_role)
            break
        
        elif choice == "10":
            print("Logging out...")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def doctor_menu(doctor_id):
    """Doctor menu with restricted access"""
    while True:
        print("\n--- DOCTOR MENU ---")
        print("1. View My Appointments (Day)")
        print("2. View My Appointments (All)")
        print("3. Schedule Appointment (For Myself)")
        print("4. View Patient Information")
        print("5. Logout")
        
        choice = input("Choose an option (1-5): ")
        
        if choice == "1":
            date = input("\nEnter date to view appointments (YYYY-MM-DD): ")
            report_appointments_by_day(date, 'doctor', doctor_id)
            
        elif choice == "2":
            report_appointments_by_day(current_role='doctor', doctor_id=doctor_id)
            
        elif choice == "3":
            print("\nSchedule Appointment")
            pid = input("Patient ID: ")
            date = input("Appointment Date (YYYY-MM-DD): ")
            time = input("Time (HH:MM): ")
            schedule_appointment(pid, doctor_id, date, time, 'doctor')
            
        elif choice == "4":
            pid = input("\nEnter Patient ID: ")
            # In a real system, you would verify the patient has appointments with this doctor
            conn = get_connection('doctor')
            if conn:
                try:
                    with conn.cursor() as cursor:
                        sql = """SELECT PatientName, DateOfBirth, Gender 
                                 FROM Patients 
                                 WHERE PatientID = %s"""
                        cursor.execute(sql, (pid,))
                        patient = cursor.fetchone()
                        if patient:
                            print("\nPatient Details:")
                            print(f"Name: {patient['PatientName']}")
                            print(f"DOB: {patient['DateOfBirth']}")
                            print(f"Gender: {patient['Gender']}")
                        else:
                            print("❌ Patient not found or access denied")
                except MySQLError as e:
                    print(f"❌ Database error: {e}")
                finally:
                    conn.close()
            
        elif choice == "5":
            print("Logging out...")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

def receptionist_menu():
    """Receptionist menu with patient and appointment management"""
    while True:
        print("\n--- RECEPTIONIST MENU ---")
        print("1. Add Patient")
        print("2. Schedule Appointment")
        print("3. View Appointments (Day)")
        print("4. View Appointments (All)")
        print("5. Logout")
        
        choice = input("Choose an option (1-5): ")
        
        if choice == "1":
            print("\nAdd New Patient")
            name = input("Full Name: ")
            dob = input("Date of Birth (YYYY-MM-DD): ")
            gender = input("Gender (M/F/O): ").upper()
            address = input("Address: ")
            phone = input("Phone Number: ")
            add_patient(name, dob, gender, address, phone, 'receptionist')
            
        elif choice == "2":
            print("\nSchedule Appointment")
            pid = input("Patient ID: ")
            did = input("Doctor ID: ")
            date = input("Appointment Date (YYYY-MM-DD): ")
            time = input("Time (HH:MM): ")
            schedule_appointment(pid, did, date, time, 'receptionist')
            
        elif choice == "3":
            date = input("\nEnter date to view appointments (YYYY-MM-DD): ")
            report_appointments_by_day(date, 'receptionist')
            
        elif choice == "4":
            report_appointments_by_day(current_role='receptionist')
            
        elif choice == "5":
            print("Logging out...")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

def accountant_menu():
    """Accountant menu with financial focus"""
    while True:
        print("\n--- ACCOUNTANT MENU ---")
        print("1. Create Invoice")
        print("2. Financial Report (By Month)")
        print("3. Financial Report (By Year)")
        print("4. Logout")
        
        choice = input("Choose an option (1-4): ")
        
        if choice == "1":
            print("\nCreate Invoice")
            pid = input("Patient ID: ")
            date = input("Invoice Date (YYYY-MM-DD): ")
            amount = input("Total Amount (VND): ")
            create_invoice(pid, date, amount, 'accountant')
            
        elif choice == "2":
            year = input("\nEnter year to view financial report (YYYY): ")
            financial_report_by_month(year, 'accountant')
            
        elif choice == "3":
            financial_report_by_month(current_role='accountant')
            
        elif choice == "4":
            print("Logging out...")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

# Main Application
def main():
    """Main application entry point with role-based access"""
    print("=== HOSPITAL MANAGEMENT SYSTEM ===")
    
    # Authenticate user
    role = authenticate_user()
    if not role:
        return
    
    # Doctor needs ID for appointment management
    doctor_id = None
    if role == 'doctor':
        conn = get_connection(role)
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorName LIKE %s", 
                                (f"%{os.getenv('DOCTOR_USER', 'doctor_user')}%",))
                    doctor = cursor.fetchone()
                    if doctor:
                        doctor_id = doctor['DoctorID']
                    else:
                        print("❌ Doctor profile not found")
                        return
            except MySQLError as e:
                print(f"❌ Database error: {e}")
                return
            finally:
                conn.close()
    
    # Launch appropriate menu based on role
    if role == 'admin':
        admin_menu()
    elif role == 'doctor' and doctor_id:
        doctor_menu(doctor_id)
    elif role == 'receptionist':
        receptionist_menu()
    elif role == 'accountant':
        accountant_menu()

if __name__ == "__main__":
    initialize_admin()
    main()