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
from fpdf import FPDF

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

from mysql.connector import MySQLConnection, Error

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

    valid_roles = ['admin', 'accountant', 'receptionist', 'nurse', 'pharmacist', 'director', 'inventory_manager']
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
            cursor.execute("SELECT username FROM users WHERE BINARY username = %s", (username,))
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

def update_doctor_user(conn, doctor_id, username):
    """Gán username hệ thống cho bác sĩ"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra doctor tồn tại
            cursor.execute("SELECT * FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            if not cursor.fetchone():
                return False, "❌ Doctor ID not found."

            # Kiểm tra user tồn tại
            cursor.execute("SELECT * FROM Users WHERE Username = %s AND Role = 'doctor'", (username,))
            if not cursor.fetchone():
                return False, "❌ Username not found or not a doctor."

            # Cập nhật
            cursor.execute("UPDATE Doctors SET DoctorUser = %s WHERE DoctorID = %s", (username, doctor_id))
            conn.commit()
            return True, "✅ Doctor user assigned successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Database error: {e}"

def assign_doctor_user(conn, doctor_id, username):
    """Tạo user mới, băm mật khẩu và gán cho bác sĩ"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem username đã tồn tại chưa
            cursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "❌ Username already exists."

            # Tạo mật khẩu ngẫu nhiên
            raw_password = generate_temp_password()
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

            # Tạo user mới với role 'doctor'
            cursor.execute(
                "INSERT INTO Users (username, password, role) VALUES (%s, %s, 'doctor')",
                (username, hashed_password)
            )

            # Gán user cho bác sĩ
            cursor.execute("UPDATE Doctors SET DoctorUser = %s WHERE doctorID = %s", (username, doctor_id))
            conn.commit()
            return True, f"✅ User created and assigned to doctor.\n🔐 Password: {raw_password}"
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed: {e}"

def update_doctor_info(conn, doctor_id, name=None, speciality=None, dept_id=None, phone=None, email=None):
    try:
        cursor = conn.cursor()
        
        # Kiểm tra doctor_id tồn tại
        cursor.execute("SELECT * FROM Doctors WHERE doctorID = %s", (doctor_id,))
        if cursor.fetchone() is None:
            return False, "Doctor ID does not exist."

        # Tạo danh sách các trường cần cập nhật
        update_fields = []
        values = []

        if name:
            update_fields.append("doctorName = %s")
            values.append(name)
        if speciality:
            update_fields.append("Speciality = %s")
            values.append(speciality)
        if dept_id:
            update_fields.append("DepartmentID = %s")
            values.append(dept_id)
        if phone:
            update_fields.append("PhoneNumber = %s")
            values.append(phone)
        if email:
            update_fields.append("Email = %s")
            values.append(email)

        if not update_fields:
            return False, "No fields to update."

        # Gộp thành câu truy vấn SQL động
        query = f"UPDATE Doctors SET {', '.join(update_fields)} WHERE doctorID = %s"
        values.append(doctor_id)
        cursor.execute(query, values)
        conn.commit()

        return True, "Doctor information updated successfully."
    except Exception as e:
        return False, f"Error: {str(e)}"

def search_doctors(conn, doctor_id=None, doctor_name=None):
    try:
        with conn.cursor() as cursor:
            query = "SELECT DoctorID, DoctorName, Specialty, DepartmentID, PhoneNumber, Email FROM Doctors WHERE 1=1"
            params = []
            if doctor_id and doctor_name:
                query += " AND doctorID = %s AND doctorName LIKE %s"
                params.append(doctor_id)
                params.append(f"%{doctor_name}%")
            elif doctor_id:
                query += " AND doctorID = %s"
                params.append(doctor_id)
            elif doctor_name:
                query += " AND doctorName LIKE %s"
                params.append(f"%{doctor_name}%")
            cursor.execute(query, tuple(params))
            
            return True, cursor.fetchall()
    except Exception as e:
        return False, f"❌ Error fetching doctor data: {e}"

def disable_doctor(conn, doctorID):
    """Disable doctor account by updating the status"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM Doctors WHERE doctorID = %s", (doctorID,))
            result = cursor.fetchone()
            
            if not result:
                return False, "❌ Doctor not found"
            
            current_status = result['status']
            if current_status == 'disabled':
                return False, "❌ Doctor is already disabled"
            
            # Update status to disabled
            cursor.execute("UPDATE Doctors SET status = 'disabled' WHERE doctorID = %s", (doctorID,))
            conn.commit()
            return True, "✅ Doctor account disabled successfully."
    
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to disable doctor: {e}"

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
        conn.rollback()
        return False, f"❌ Failed to add patient: {e}"

def search_patient(conn, patient_id=None, name=None):
    """Search for a patient by ID or name"""
    try:
        with conn.cursor() as cursor:
            query = "SELECT PatientID, PatientName, DateOfBirth, Gender, Address, PhoneNumber FROM Patients WHERE 1=1"
            params = []
            if patient_id and name:
                query += " AND PatientID = %s AND PatientName LIKE %s"
                params.append(patient_id)
                params.append(f"%{name}%")
            elif patient_id:
                query += " AND PatientID = %s"
                params.append(patient_id)
            elif name:
                query += " AND PatientName LIKE %s"
                params.append(f"%{name}%")
            cursor.execute(query, tuple(params))

            return True, cursor.fetchall()
    except Exception as e:
        return False, f"❌ Error fetching patient data: {e}"

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

def update_patient_info(conn, patient_id=None, name=None, dob=None, gender=None, address=None, phone_number=None):
    """Update patient information"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patients WHERE PatientID = %s", (patient_id,))
        if cursor.fetchone() is None:
            return False, "Patient ID does not exist."
        update_fields = []
        values = []

        if name:
            update_fields.append("PatientName = %s")
            values.append(name)
        if dob:
            update_fields.append("DateOfBirth = %s")
            values.append(dob)
        if gender:
            update_fields.append("Gender = %s")
            values.append(gender)
        if address:
            update_fields.append("Address = %s")
            values.append(address)
        if phone_number:
            update_fields.append("PhoneNumber = %s")
            values.append(phone_number)
        if not update_fields:
            return False, "No fields to update."
        
        query = f"UPDATE Patients SET {', '.join(update_fields)} WHERE PatientID = %s"
        values.append(patient_id)
        cursor.execute(query, values)
        conn.commit()

        return True, "Patient information updated successfully."
    
    except Exception as e:
        return False, f"Error: {str(e)}"
    
def disable_patient_account(conn, patient_id):
    """Disable a patient's account by changing status"""
    try:
        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "Patient not found"
            cursor.execute("UPDATE Patients SET status = 'disabled' WHERE patientID = %s", (patient_id,))
            conn.commit()
            return True, "✅ Patient account disabled successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to disable patient account: {e}"

def get_all_patients(conn):
    """Get a list of all patients"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Patients WHERE status != 'disabled'")  # Assuming 'disabled' patients are excluded
            patients = cursor.fetchall()
            return patients
    except MySQLError as e:
        return [], f"❌ Failed to retrieve patients: {e}"

# Department Management    
def add_department(conn, name):
    """Add a new department to the system"""
    try:
        with conn.cursor() as cursor:
            if name:
                cursor.execute("INSERT INTO Departments (DepartmentName) VALUES (%s)", (name,))
                conn.commit()
                return True, "✅ Department added successfully."
            else:
                return False, "❌ Department name cannot be empty."  # Thêm return ở đây
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add department: {e}"

def update_department(conn, dept_id, name):
    """Update department information"""
    try:
        with conn.cursor() as cursor:
            if not dept_id or not name:
                return False, "❌ Department ID and New Name cannot be empty."
            # Check if department exists
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (dept_id,))
            if not cursor.fetchone():
                return False, "❌ Department not found."
            cursor.execute("""
                UPDATE Departments 
                SET DepartmentName = %s 
                WHERE DepartmentID = %s
            """, (name, dept_id))
            conn.commit()
            return True, "✅ Department updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update department: {e}"
 
def view_departments(conn):
    """View all departments"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT d1.DepartmentID, d1.DepartmentName, COUNT(d2.DoctorID) AS DoctorCount FROM departments d1 JOIN doctors d2 ON d1.DepartmentID=d2.DepartmentID GROUP BY DepartmentID")
            departments = cursor.fetchall()
            if departments:
                return True, departments
            else:
                return False, "No departments found."
    except MySQLError as e:
        return False, f"Failed to retrieve departments: {e}"
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

def search_appointments(conn, role, username=None, year=None, month=None, day=None, status=None):
    """
    Search appointments with optional filters:
    - Admin/Receptionist/Accountant: All appointments.
    - Doctor: Only appointments of the logged-in doctor.
    """
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT a.AppointmentID, a.DoctorID, d.DoctorName,
                       a.PatientID, p.PatientName,
                       a.AppointmentDate, a.AppointmentTime, a.Status
                FROM Appointments a
                JOIN Doctors d ON a.DoctorID = d.DoctorID
                JOIN Patients p ON a.PatientID = p.PatientID
                WHERE 1=1
            """
            params = []

            # Filter for doctor role
            if role.lower() == 'doctor':
                cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorUser = %s", (username,))
                doctor = cursor.fetchone()
                if not doctor:
                    return False, "❌ Doctor profile not found for the given username."
                query += " AND a.DoctorID = %s"
                params.append(doctor['DoctorID'])

            # Date filters
            if year:
                query += " AND YEAR(a.AppointmentDate) = %s"
                params.append(year)
            if month:
                query += " AND MONTH(a.AppointmentDate) = %s"
                params.append(month)
            if day:
                query += " AND DAY(a.AppointmentDate) = %s"
                params.append(day)

            # Status filter
            if status:
                query += " AND a.Status = %s"
                params.append(status)

            query += " ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC"

            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            return True, results

    except Exception as e:
        return False, f"❌ Error fetching appointments: {e}"

def update_appointment_status(conn, appointment_id, new_status):
    """Update the status of an appointment"""
    try:
        with conn.cursor() as cursor:
            if not appointment_id or not new_status:
                return False, "Appointment ID and New Status are required."
            cursor.execute("SELECT AppointmentID FROM Appointments WHERE AppointmentID = %s", (appointment_id,))
            if not cursor.fetchone():
                return False, "Appointment not found."
            cursor.execute("""
                UPDATE Appointments
                SET Status = %s
                WHERE AppointmentID = %s
            """, (new_status, appointment_id))
            conn.commit()
            return True, "Appointment status updated successfully."
    except Exception as e:
        return False, f"Failed to update appointment status: {e}"

# Room Management
def add_room(conn, room_number, room_type_id, department_id, status="Available"):
    """Add a new room to the system"""
    try:
        with conn.cursor() as cursor:
            if not room_number:
                return False, "❌ Room number cannot be empty."
            
            # Kiểm tra xem loại phòng có tồn tại không
            cursor.execute("SELECT RoomTypeID FROM RoomTypes WHERE RoomTypeID = %s", (room_type_id,))
            if not cursor.fetchone():
                return False, "❌ Room type does not exist."

            # Kiểm tra xem khoa có tồn tại không
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (department_id,))
            if not cursor.fetchone():
                return False, "❌ Department does not exist."
            
            # Thêm phòng mới
            cursor.execute("""
                INSERT INTO Rooms (RoomNumber, RoomTypeID, DepartmentID, Status)
                VALUES (%s, %s, %s, %s)
            """, (room_number, room_type_id, department_id, status))

            conn.commit()
            return True, "✅ Room added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add room: {e}"
    
def update_room(conn, room_id, room_number, room_type_id, department_id, status):
    """Update room information"""
    try:
        with conn.cursor() as cursor:
            if not room_id:
                return False, "Room ID is required."
            if not any([room_number, room_type_id, department_id, status]):
                return False, "At least one field other than Room ID must be provided."
            # Kiểm tra xem phòng có tồn tại không
            cursor.execute("SELECT RoomID FROM Rooms WHERE RoomID = %s", (room_id,))
            if not cursor.fetchone():
                return False, "❌ Room not found."

            # Kiểm tra xem loại phòng có tồn tại không
            cursor.execute("SELECT RoomTypeID FROM RoomTypes WHERE RoomTypeID = %s", (room_type_id,))
            if not cursor.fetchone():
                return False, "❌ Room type does not exist."

            # Kiểm tra xem khoa có tồn tại không
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (department_id,))
            if not cursor.fetchone():
                return False, "❌ Department does not exist."

            # Cập nhật thông tin phòng
            cursor.execute("""
                UPDATE Rooms 
                SET RoomNumber = %s, RoomTypeID = %s, DepartmentID = %s, Status = %s 
                WHERE RoomID = %s
            """, (room_number, room_type_id, department_id, status, room_id))

            conn.commit()
            return True, "✅ Room updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update room: {e}"

def disable_room(conn, room_id):
    """Disable a room by changing its status"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE Rooms SET Status = 'Disabled' WHERE RoomID = %s", (room_id,))
            conn.commit()
            return True, "✅ Room disabled successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to disable room: {e}"
    
def search_rooms(conn, room_id=None, room_number=None, status=None):
    """Search for rooms by room_id, room_number, and status."""
    try:
        query = "SELECT * FROM Rooms WHERE 1=1"  # Base query

        params = []
        if room_id:
            query += " AND RoomID = %s"
            params.append(room_id)
        if room_number:
            query += " AND RoomNumber LIKE %s"
            params.append('%' + room_number + '%')
        if status:
            query += " AND Status = %s"
            params.append(status)

        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            rooms = cursor.fetchall()

        return True, rooms if rooms else None

    except MySQLError as e:
        return False, f"Error: {e}"

def search_room_types(conn, room_type_id=None, room_type_name=None):
    """Search for room types by ID, name, or both."""
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM RoomTypes WHERE 1=1"
            params = []

            if room_type_id:
                query += " AND RoomTypeID = %s"
                params.append(room_type_id)
            if room_type_name:
                query += " AND RoomTypeName LIKE %s"
                params.append(f"%{room_type_name}%")

            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

            if not results:
                return False, "⚠️ No room types found with the provided criteria."
            return True, results

    except Exception as e:
        return False, f"❌ Failed to retrieve room types: {e}"
    
def add_room_type(conn, type_name=None, base_cost=None, des=None):
    """Add a new room type to the system"""
    try:
        with conn.cursor() as cursor:
            if not type_name or not base_cost:
                return False, "❌ Type name and base cost cannot be empty."
            cursor.execute("INSERT INTO RoomTypes (TypeName, BaseCost) VALUES (%s, %s,%s)", (type_name, base_cost,des))
            conn.commit()
            return True, "✅ Room type added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add room type: {e}"
    
def update_room_type(conn, room_type_id, type_name, base_cost):
    """Update room type information"""
    try:
        with conn.cursor() as cursor:
            if not room_type_id:
                return False, "Room Type ID is required."
            if not any([type_name, base_cost]):
                return False, "❌ At least one field must be updated."
            cursor.execute("""
                UPDATE RoomTypes 
                SET TypeName = %s, BaseCost = %s 
                WHERE RoomTypeID = %s
            """, (type_name, base_cost, room_type_id))
            conn.commit()
            return True, "✅ Room type updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update room type: {e}"

def get_room_statistics(conn):
    """Thống kê phòng theo khoa và loại phòng"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d.DepartmentName,
                    rt.TypeName,
                    COUNT(r.RoomID) as TotalRooms,
                    SUM(CASE WHEN r.Status = 'Available' THEN 1 ELSE 0 END) as AvailableRooms,
                    SUM(CASE WHEN r.Status = 'Occupied' THEN 1 ELSE 0 END) as OccupiedRooms
                FROM Rooms r
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                GROUP BY d.DepartmentName, rt.TypeName
                ORDER BY d.DepartmentName, rt.TypeName
            """)
            return True, cursor.fetchall()
    except MySQLError as e:
        return False, f"Error getting room statistics: {e}"

def assign_patient_to_room(conn, patient_id, room_type_id):
    """Gán bệnh nhân vào phòng trống đầu tiên của loại phòng chỉ định"""
    try:
        with conn.cursor() as cursor:
            # Tìm phòng trống
            cursor.execute("""
                SELECT RoomID FROM Rooms 
                WHERE RoomTypeID = %s 
                AND Status = 'Available'
                LIMIT 1
                FOR UPDATE
            """, (room_type_id,))
            
            room = cursor.fetchone()
            
            if not room:
                return False, "No available rooms of this type"
                
            # Cập nhật trạng thái phòng
            cursor.execute("""
                UPDATE Rooms 
                SET Status = 'Occupied', 
                    CurrentPatientID = %s,
                    LastCleanedDate = CURDATE()
                WHERE RoomID = %s
            """, (patient_id, room['RoomID']))
            
            conn.commit()
            return True, f"Patient assigned to room {room['RoomID']}"
            
    except MySQLError as e:
        conn.rollback()
        return False, f"Error assigning room: {e}"

def save_calculated_invoice(conn, patient_id, med_cost, room_cost, svc_cost, total_discount, final_amount, notes):
    """Lưu hóa đơn đã được tính toán từ GUI vào cơ sở dữ liệu."""
    try:
        with conn.cursor() as cursor:
            invoice_date = datetime.now().strftime("%Y-%m-%d")
            is_bhyt_applied = total_discount > 0 # Hoặc logic kiểm tra nhà cung cấp BH nếu cần

            # Đảm bảo các giá trị là số hợp lệ
            med_cost = float(med_cost) if med_cost else 0.0
            room_cost = float(room_cost) if room_cost else 0.0
            svc_cost = float(svc_cost) if svc_cost else 0.0
            final_amount = float(final_amount) if final_amount else 0.0

            cursor.execute("""
                INSERT INTO Invoices (
                    PatientID, InvoiceDate,
                    RoomCost, MedicineCost, ServiceCost, # Chi phí gốc
                    TotalAmount, # Tổng cuối cùng cần thanh toán
                    PaymentStatus, IsBHYTApplied, Notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                patient_id, invoice_date,
                room_cost, med_cost, svc_cost, # Lưu chi phí gốc
                final_amount, # Lưu tổng cuối cùng
                'Unpaid', # Trạng thái ban đầu
                is_bhyt_applied,
                notes # Lưu chi tiết đã hiển thị
            ))
            new_invoice_id = cursor.lastrowid
            conn.commit()
            return True, "Invoice saved successfully.", new_invoice_id
    except MySQLError as e:
        conn.rollback()
        print(f"Database error saving calculated invoice: {e}")
        return False, f"Database error: {e}", None
    except Exception as ex:
        conn.rollback()
        print(f"Unexpected error saving calculated invoice: {ex}")
        return False, f"Unexpected error: {ex}", None

def search_patient_room(conn, patient_id=None, patient_name=None):
    """Search for the current room of a patient by ID or name."""
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT r.RoomNumber, rt.TypeName, rt.BaseCost, r.LastCleanedDate
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Patients p ON r.CurrentPatientID = p.PatientID
                WHERE 1=1
            """
            params = []

            if patient_id:
                query += " AND p.PatientID = %s"
                params.append(patient_id)
            if patient_name:
                query += " AND p.PatientName LIKE %s"
                params.append(f"%{patient_name}%")

            cursor.execute(query, tuple(params))
            room = cursor.fetchone()

            if room:
                last_cleaned = room.get('LastCleanedDate') or datetime.now().date()
                days_stayed = (datetime.now().date() - last_cleaned).days + 1
                room['DaysStayed'] = max(1, days_stayed)
                return True, room
            else:
                return False, "⚠️ No room currently assigned to the provided patient."

    except Exception as e:
        return False, f"❌ Error fetching patient room: {e}"

# Service Management
def add_service(conn, service_name, service_code, service_cost, des):
    """Add a new service to the system"""
    try:
        with conn.cursor() as cursor:
            # Ensure all required fields are provided
            if not service_name or not service_code or not service_cost:
                return False, "❌ Service Name, Service Code, and Service Cost are required."
            cursor.execute("""
            INSERT INTO Services (ServiceName, ServiceCode, ServiceCost, Description)
            VALUES (%s, %s, %s, %s)
            """, (service_name, service_code, service_cost, des))
            conn.commit()
            return True, "✅ Service added successfully."   
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add service: {e}"
    
def update_service(conn, service_id, service_name, service_cost):
    """Update service information"""
    try:
        with conn.cursor() as cursor:
            if not service_id or not any([service_name, service_cost]):
                return False, "❌ Service ID and at least one other field must be provided."
            cursor.execute("""
                UPDATE Services 
                SET ServiceName = %s, ServiceCost = %s 
                WHERE ServiceID = %s
            """, (service_name, service_cost, service_id))
            conn.commit()
            return True, "✅ Service updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update service: {e}"
   
def search_services(conn, service_id=None, service_name=None):
    """Search for services by ID, name, or both."""
    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM Services WHERE 1=1"
            params = []
            if service_id and service_name:
                query += " AND ServiceID = %s AND ServiceName LIKE %s"
                params.append(service_id)
                params.append(f"%{service_name}%")
            elif service_id:
                query += " AND ServiceID = %s"
                params.append(service_id)
            elif service_name:
                query += " AND ServiceName LIKE %s"
                params.append(f"%{service_name}%")
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

            if not results:
                return False, "⚠️ No service found with the provided criteria."
            return True, results

    except Exception as e:
        return False, f"❌ Error fetching service data: {e}"
   
# PatientService Management
def add_patient_service(conn, patient_id, service_id, doctor_id, service_date, quantity, cost_at_time, notes):
    """Thêm dịch vụ cho bệnh nhân"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO PatientServices 
                (PatientID, ServiceID, DoctorID, ServiceDate, Quantity, CostAtTime, Notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (patient_id, service_id, doctor_id, service_date, quantity, cost_at_time, notes))
        conn.commit()
        return True, "✅ Service assigned to patient successfully."
    except Exception as e:
        conn.rollback()
        return False, f"❌ Failed to add service: {str(e)}"
    
def delete_patient_service(conn, patient_service_id):
    """Delete a service from a patient's account"""
    try:
        with conn.cursor() as cursor:
            if not patient_service_id:
                return False, "Please input Patient Service ID."
            cursor.execute("DELETE FROM PatientServices WHERE PatientServiceID = %s", (patient_service_id,))
            conn.commit()
            return True, "✅ Patient service deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete patient service: {e}"
    
def search_patient_services(conn, patient_id=None, patient_name=None):
    """Search for all services used by a patient by ID or name."""
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT ps.PatientServiceID, s.ServiceName, ps.Quantity, s.ServiceCost
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                JOIN Patients p ON ps.PatientID = p.PatientID
                WHERE 1=1
            """
            params = []

            if patient_id:
                query += " AND p.PatientID = %s"
                params.append(patient_id)
            if patient_name:
                query += " AND p.PatientName LIKE %s"
                params.append(f"%{patient_name}%")

            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

            if not results:
                return False, "⚠️ No patient services found with the provided criteria."
            return True, results

    except Exception as e:
        return False, f"❌ Error fetching patient services: {e}"
    
def calculate_total_service_cost(conn, patient_id):
    """Calculate the total cost of all services for a specific patient"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(ps.Quantity * s.ServiceCost) AS TotalCost
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                WHERE ps.PatientID = %s
            """, (patient_id,))
            result = cursor.fetchone()
            total_cost = result['TotalCost'] if result['TotalCost'] else 0.0
            return True, total_cost
    except MySQLError as e:
        return False, f"❌ Failed to calculate total service cost: {e}"
    
def attach_service_to_invoice(conn, invoice_id, patient_service_id):
    """Attach a service to an invoice"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem hóa đơn có tồn tại không
            cursor.execute("SELECT InvoiceID FROM Invoices WHERE InvoiceID = %s", (invoice_id,))
            if not cursor.fetchone():
                return False, "❌ Invoice not found."

            # Kiểm tra xem dịch vụ có tồn tại không
            cursor.execute("SELECT PatientServiceID FROM PatientServices WHERE PatientServiceID = %s", (patient_service_id,))
            if not cursor.fetchone():
                return False, "❌ Patient service not found."

            # Gán dịch vụ vào hóa đơn
            cursor.execute("""
                INSERT INTO InvoiceServices (InvoiceID, PatientServiceID)
                VALUES (%s, %s)
            """, (invoice_id, patient_service_id))

            conn.commit()
            return True, "✅ Service attached to invoice successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to attach service to invoice: {e}"

# Prescription Management
def create_prescription(conn, patient_id, doctor_id, prescription_date):
    """Create a new prescription for a patient"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem bệnh nhân có tồn tại không
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "❌ Patient not found."

            # Kiểm tra xem bác sĩ có tồn tại không
            cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            if not cursor.fetchone():
                return False, "❌ Doctor not found."

            # Tạo đơn thuốc mới
            cursor.execute("""
                INSERT INTO Prescriptions (PatientID, DoctorID, PrescriptionDate)
                VALUES (%s, %s, %s)
            """, (patient_id, doctor_id, prescription_date))

            conn.commit()
            return True, "✅ Prescription created successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to create prescription: {e}"
     
def delete_prescription_detail(conn, prescription_detail_id):
    """Delete a medicine from a prescription"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM PrescriptionDetails WHERE PrescriptionDetailID = %s", (prescription_detail_id,))
            conn.commit()
            return True, "✅ Prescription detail deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete prescription detail: {e}"

def delete_prescription(conn, prescription_id):
    """Delete a prescription"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Prescription WHERE PrescriptionID = %s", (prescription_id,))
            conn.commit()
            return True, "✅ Prescription deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete prescription: {e}"

def list_prescriptions(conn, patient_id):
    """List all prescriptions for a specific patient"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.PrescriptionID, p.PrescriptionDate, d.DoctorName
                FROM Prescriptions p
                JOIN Doctors d ON p.DoctorID = d.DoctorID
                WHERE p.PatientID = %s
                ORDER BY p.PrescriptionDate DESC
            """, (patient_id,))
            prescriptions = cursor.fetchall()
            return True, prescriptions
    except MySQLError as e:
        return False, f"❌ Failed to retrieve prescriptions: {e}"

# Emergency Management
def add_emergency_contact(conn, patient_id, contact_name, relationship, phone_number, address):
    """Add an emergency contact for a patient"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem bệnh nhân có tồn tại không
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "❌ Patient not found."

            # Thêm liên hệ khẩn cấp
            cursor.execute("""
                INSERT INTO EmergencyContacts (PatientID, ContactName, Relationship, PhoneNumber, Address)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, contact_name, relationship, phone_number, address))

            conn.commit()
            return True, "✅ Emergency contact added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add emergency contact: {e}"

def update_emergency_contact(conn, contact_id, contact_name, relationship, phone_number, address):
    """Update an emergency contact for a patient"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem liên hệ khẩn cấp có tồn tại không
            cursor.execute("SELECT ContactID FROM EmergencyContacts WHERE ContactID = %s", (contact_id,))
            if not cursor.fetchone():
                return False, "❌ Emergency contact not found."

            update_fields = []
            update_values = []
            if contact_name:
                update_fields.append("ContactName = %s")
                update_values.append(contact_name)
            if relationship:
                update_fields.append("Relationship = %s")
                update_values.append(relationship)
            if phone_number:
                update_fields.append("PhoneNumber = %s")
                update_values.append(phone_number)
            if address:
                update_fields.append("Address = %s")
                update_values.append(address)
            if not update_fields:
                return False, "No fields to update."
            
            query = f"""
                UPDATE EmergencyContacts SET {', '.join(update_fields)}
                WHERE ContactID = %s"""
            update_values.append(contact_id)
            cursor.execute(query, tuple(update_values))
            conn.commit()
            return True, "✅ Emergency contact updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update emergency contact: {e}"
    
def delete_emergency_contact(conn, contact_id):
    """Delete an emergency contact for a patient"""
    try:
        with conn.cursor() as cursor:
            if not contact_id:
                return False, "Please input Contact ID."
            # Kiểm tra xem liên hệ khẩn cấp có tồn tại không
            cursor.execute("SELECT ContactID FROM EmergencyContact WHERE ContactID = %s", (contact_id,))
            if not cursor.fetchone():
                return False, "❌ Emergency contact not found."

            # Xóa liên hệ khẩn cấp
            cursor.execute("DELETE FROM EmergencyContact WHERE ContactID = %s", (contact_id,))

            conn.commit()
            return True, "✅ Emergency contact deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete emergency contact: {e}"
    
def get_emergency_contacts(conn, patient_id):
    """Retrieve emergency contacts for a given patient ID."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ContactName, Relationship, PhoneNumber
                FROM EmergencyContact
                WHERE PatientID = %s
            """, (patient_id,))
            results = cursor.fetchall()
            return True, results
    except MySQLError as e:
        return False, f"❌ Failed to fetch emergency contacts: {e}"

# Medicine Management
def add_medicine(conn, name, unit, quantity, cost):
    """Add a new medicine to the Medicines table"""
    try:
        if not all([name, unit]):
            return False, "❌ Medicine name and unit are required."

        if quantity < 0 or cost < 0:
            return False, "❌ Quantity and cost must be non-negative."

        with conn.cursor() as cursor:
            query = """
                INSERT INTO Medicines (MedicineName, Unit, Quantity, Cost)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, unit, quantity, cost))
            conn.commit()
            return True, "✅ Medicine added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Database error: {e}"
    except Exception as e:
        return False, f"❌ Unexpected error: {e}"
    
def update_medicine(conn, medicine_id, medicine_name, unit, quantity, medicine_cost):
    """Update medicine information"""
    try:
        with conn.cursor() as cursor:
            if not medicine_id or not any([medicine_name, unit, quantity, medicine_cost]):
                return False, "❌ Medicine ID and at least one other field must be provided."
            # Check if medicine exists
            cursor.execute("SELECT MedicineID FROM Medicine WHERE MedicineID = %s", (medicine_id,))
            if not cursor.fetchone():
                return False, "❌ Medicine not found."
            cursor.execute("""
                UPDATE Medicine 
                SET MedicineName = %s, Unit = %s, Quantity = %s, MedicineCost = %s 
                WHERE MedicineID = %s
            """, (medicine_name, unit, quantity, medicine_cost, medicine_id))
            conn.commit()
            return True, "✅ Medicine updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update medicine: {e}"
    
def search_medicine(conn, medicine_id=None, medicine_name=None):
    """Search for a medicine by ID or name"""
    try:
        with conn.cursor() as cursor:
            if medicine_id and medicine_name:
                cursor.execute("SELECT * FROM Medicine WHERE MedicineID = %s AND MedicineName LIKE %s", (medicine_id, '%' + medicine_name + '%'))
            elif medicine_id:
                cursor.execute("SELECT * FROM Medicine WHERE MedicineID = %s", (medicine_id,))
            elif medicine_name:
                cursor.execute("SELECT * FROM Medicine WHERE MedicineName LIKE %s", ('%' + medicine_name + '%',))
            else:
                cursor.execute("SELECT * FROM Medicine")

            medicine = cursor.fetchall()  # Get the first result (if any)
            if not medicine:
                return False, "No medicine found with the provided ID or name."
            return True, medicine

    except MySQLError as e:
        return False, f"Error: {e}"
       
def delete_medicine(conn, medicine_id):
    """Delete a medicine from the system"""
    try:
        with conn.cursor() as cursor:
            if not medicine_id:
                return False, "Please input Medicine ID."
            cursor.execute("DELETE FROM Medicine WHERE MedicineID = %s", (medicine_id,))
            conn.commit()
            return True, "✅ Medicine deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete medicine: {e}"
    
# MedicineBatch Management
def add_medicine_batch(conn, medicine_id, batch_number, quantity, import_date, expiry_date, supplier_name, medicine_cost):
    """Call stored procedure to add a new medicine batch"""
    try:
        with conn.cursor() as cursor:
            cursor.callproc("sp_AddMedicineBatch", (
                medicine_id,
                batch_number,
                quantity,
                import_date,
                expiry_date,
                supplier_name,
                medicine_cost
            ))
            conn.commit()
            return True, "✅ Medicine batch added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add medicine batch: {e}"

def update_medicine_batch(conn, batch_id, quantity, status):
    """Update a medicine batch's quantity and status"""
    try:
        with conn.cursor() as cursor:
            if not batch_id or not any([quantity, status]):
                return False, "❌ Batch ID and at least one other field must be provided."
            # Kiểm tra xem lô thuốc có tồn tại không
            cursor.execute("SELECT BatchID FROM MedicineBatch WHERE BatchID = %s", (batch_id,))
            if not cursor.fetchone():
                return False, "❌ Medicine batch not found."

            # Cập nhật lô thuốc
            cursor.execute("""
                UPDATE MedicineBatch 
                SET Quantity = %s, Status = %s 
                WHERE BatchID = %s
            """, (quantity, status, batch_id))

            conn.commit()
            return True, "✅ Medicine batch updated successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to update medicine batch: {e}"
    
def search_medicine_batches(conn, batch_id=None, expiry_date=None, status=None):
    try:
        query = """
            SELECT * FROM MedicineBatch
            WHERE 1=1
        """
        params = []
        
        if batch_id:
            query += " AND BatchID = %s"
            params.append(batch_id)
        
        if expiry_date:
            query += " AND ExpiryDate = %s"
            params.append(expiry_date)
        
        if status:
            query += " AND Status = %s"
            params.append(status)
        
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return True, cursor.fetchall()
    except Exception as e:
        return False, str(e)

def list_medicine_batches(conn, batch_id, expiry_date, medicine_cost, text_area):
    success, batches = search_medicine_batches(conn, batch_id, expiry_date, medicine_cost)
    
    if not success or not batches:
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "No batches found.\n")
        return
    
    text_area.delete(1.0, tk.END)
    
    # Header row
    text_area.insert(tk.END, "BatchID | MedicineID | BatchNumber | Quantity | ImportDate | ExpiryDate | SupplierName | MedicineCost | Status\n")
    text_area.insert(tk.END, "-" * 100 + "\n")
    
    for batch in batches:
        text_area.insert(tk.END, f"{batch['BatchID']} | {batch['MedicineID']} | {batch['BatchNumber']} | {batch['Quantity']} | {batch['ImportDate']} | {batch['ExpiryDate']} | {batch['SupplierName']} | {batch['MedicineCost']} | {batch['Status']}\n")

def delete_medicine_batch(conn, batch_id):
    """Delete a medicine batch from the system"""
    try:
        with conn.cursor() as cursor:
            if not batch_id:
                return False, "Please input Batch ID."
            # Kiểm tra xem lô thuốc có tồn tại không
            cursor.execute("SELECT BatchID FROM MedicineBatch WHERE BatchID = %s", (batch_id,))
            if not cursor.fetchone():
                return False, "❌ Medicine batch not found."

            # Xóa lô thuốc
            cursor.execute("DELETE FROM MedicineBatch WHERE BatchID = %s", (batch_id,))

            conn.commit()
            return True, "✅ Medicine batch deleted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to delete medicine batch: {e}"
       
def adjust_medicine_quantity(conn, batch_id, used_quantity):
    """Adjust the quantity of a medicine batch after use"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem lô thuốc có tồn tại không
            cursor.execute("SELECT BatchID FROM MedicineBatch WHERE BatchID = %s", (batch_id,))
            if not cursor.fetchone():
                return False, "❌ Medicine batch not found."

            # Cập nhật số lượng lô thuốc
            cursor.execute("""
                UPDATE MedicineBatch 
                SET Quantity = Quantity - %s 
                WHERE BatchID = %s
            """, (used_quantity, batch_id))

            conn.commit()
            return True, "✅ Medicine batch quantity adjusted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to adjust medicine batch quantity: {e}"
    
# Inventory Management
def add_inventory_item(conn, item_name, quantity, unit, status='active'):
    try:
        with conn.cursor() as cursor:
            # Ensure all required fields are provided
            if not item_name or not quantity or not unit or not status:
                return False, "❌ All fields are required."
            
            cursor.execute("""
            INSERT INTO Inventory (itemName, quantity, unit, status)
            VALUES (%s, %s, %s, %s)
            """, (item_name, quantity, unit, status))
            conn.commit()
            return True, "✅ Inventory item added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add item: {e}"

def update_inventory_item(conn, inventory_id, item_name, quantity, unit, status):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Inventory
                SET itemName=%s, quantity=%s, unit=%s, status=%s
                WHERE inventoryID = %s
            """, (item_name, quantity, unit, status, inventory_id))
            conn.commit()
            return True, "✅ Inventory item updated."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Update failed: {e}"

def disable_inventory_item(conn, inventory_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Inventory SET status='inactive' WHERE inventoryID = %s
            """, (inventory_id,))
            conn.commit()
            return True, "✅ Inventory item disabled."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to disable: {e}"

def search_inventory_item(conn, item_id=None, item_name=None, status=None):
    """Search inventory items based on item_id, item_name, and status."""
    try:
        # Building the query dynamically based on provided parameters
        query = "SELECT * FROM Inventory WHERE 1=1"
        params = []

        if item_id:
            query += " AND InventoryID LIKE %s"
            params.append('%' + item_id + '%')
        
        if item_name:
            query += " AND ItemName LIKE %s"
            params.append('%' + item_name + '%')

        if status:
            query += " AND Status LIKE %s"
            params.append('%' + status + '%')

        # Execute the query
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

        if results:
            return True, results
        else:
            return False, "No matching inventory found."
    
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

def adjust_inventory(conn, inventoryID, quantity):
    """Adjust the quantity of an inventory item"""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra xem mặt hàng tồn kho có tồn tại không
            cursor.execute("SELECT InventoryID FROM Inventory WHERE InventoryID = %s", (inventoryID,))
            if not cursor.fetchone():
                return False, "❌ Inventory item not found."

            # Cập nhật số lượng mặt hàng tồn kho
            cursor.execute("""
                UPDATE Inventory 
                SET Quantity = Quantity + %s 
                WHERE InventoryID = %s
            """, (quantity, inventoryID))

            conn.commit()
            return True, "✅ Inventory item quantity adjusted successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to adjust inventory item quantity: {e}"
    finally:
        conn.close()

# insurance management
def add_insurance_record(conn, patientID, InsuranceProvider, PolicyNumber,
                         BHYTCardNumber, EffectiveDate, EndDate, CoverageDetails):
    try:
        cursor = conn.cursor()

        # Kiểm tra bệnh nhân tồn tại
        cursor.execute("SELECT patientID FROM Patients WHERE patientID = %s", (patientID,))
        if cursor.fetchone() is None:
            return False, f"❌ Patient ID {patientID} does not exist."

        query = """
            INSERT INTO Insurance (patientID, InsuranceProvider, PolicyNumber,
                                   BHYTCardNumber, EffectiveDate, EndDate, CoverageDetails)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            patientID, InsuranceProvider, PolicyNumber,
            BHYTCardNumber, EffectiveDate, EndDate, CoverageDetails
        ))
        conn.commit()
        return True, "✅ Insurance record added successfully."

    except Exception as e:
        conn.rollback()
        return False, f"❌ Failed to add insurance record: {str(e)}"

def update_insurance_record(conn, insurance_id, patient_id, provider, policy_no, bhyt_no, eff_date, end_date, coverage_details):
    """Cập nhật thông tin bảo hiểm cho bệnh nhân."""
    try:
        # Kiểm tra xem bản ghi bảo hiểm có tồn tại không
        with conn.cursor() as cursor:
            if not insurance_id or not any([patient_id, provider, policy_no, bhyt_no, eff_date, end_date, coverage_details]):
                return False, "Insurance ID and at least one other field must be provided."
            cursor.execute("SELECT InsuranceID FROM Insurance WHERE InsuranceID = %s", (insurance_id,))
            if not cursor.fetchone():
                return False, f"Insurance record with ID {insurance_id} not found."

        # Validate dates (Cơ bản)
        if not validate_date(eff_date) or not validate_date(end_date):
            return False, "Invalid date format. Please use YYYY-MM-DD."
        if datetime.strptime(end_date, '%Y-%m-%d') < datetime.strptime(eff_date, '%Y-%m-%d'):
            return False, "End Date cannot be earlier than Effective Date."

        # Cập nhật bản ghi vào bảng Insurance
        with conn.cursor() as cursor:
            sql = """
                UPDATE Insurance 
                SET PatientID = %s, InsuranceProvider = %s, PolicyNumber = %s,
                    BHYTCardNumber = %s, EffectiveDate = %s, EndDate = %s,
                    CoverageDetails = %s
                WHERE InsuranceID = %s
            """
            # Xử lý BHYTCardNumber có thể là NULL
            bhyt_value = bhyt_no if bhyt_no else None
            coverage_value = coverage_details if coverage_details else None

            cursor.execute(sql, (patient_id, provider, policy_no, bhyt_value, eff_date, end_date, coverage_value, insurance_id))
            conn.commit()
        return True, "Insurance record updated successfully."

    except MySQLError as e:
        conn.rollback()
        return False, f"Database error while updating insurance: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"An unexpected error occurred: {e}"
    
def delete_insurance_record(conn, insurance_id):
    """Xóa bản ghi bảo hiểm của bệnh nhân."""
    try:
        # Kiểm tra xem bản ghi bảo hiểm có tồn tại không
        with conn.cursor() as cursor:
            if not insurance_id:
                return False, "❌ Insurance ID is required."
            cursor.execute("SELECT InsuranceID FROM Insurance WHERE InsuranceID = %s", (insurance_id,))
            if not cursor.fetchone():
                return False, f"Insurance record with ID {insurance_id} not found."

        # Xóa bản ghi bảo hiểm
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Insurance WHERE InsuranceID = %s", (insurance_id,))
            conn.commit()
        return True, "Insurance record deleted successfully."

    except MySQLError as e:
        conn.rollback()
        return False, f"Database error while deleting insurance: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"An unexpected error occurred: {e}"
    
def search_insurance(conn, patient_id=None):
    """Search insurance records based on patient_id."""
    try:
        query = """
            SELECT i.*, p.PatientName
            FROM Insurance i
            JOIN Patients p ON i.PatientID = p.PatientID
            WHERE 1=1
        """
        params = []

        # Nếu có patient_id, thêm điều kiện lọc
        if patient_id:
            query += " AND i.PatientID = %s"
            params.append(patient_id)

        query += " ORDER BY i.InsuranceRecordID ASC"

        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

        if results:
            return True, results
        else:
            return False, "No matching insurance records found."
    
    except MySQLError as e:
        return False, f"An error occurred: {str(e)}"

def calculate_insurance_discount(conn, patient_id, service_type, original_cost):
    """Tính toán chiết khấu bảo hiểm cho bệnh nhân"""
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin bảo hiểm hiện tại của bệnh nhân
            cursor.execute("""
                SELECT * FROM Insurance 
                WHERE PatientID = %s 
                AND EffectiveDate <= CURDATE() 
                AND EndDate >= CURDATE()
                ORDER BY EndDate DESC
                LIMIT 1
            """, (patient_id,))
            
            insurance = cursor.fetchone()
            
            if not insurance:
                return original_cost, 0  # Không có bảo hiểm, không giảm giá
            
            # Giả sử mỗi loại dịch vụ có % chi trả khác nhau
            # Trong thực tế cần có bảng InsuranceCoverage để lưu % cho từng loại dịch vụ
            coverage_percent = 0
            
            if service_type == "medicine":
                coverage_percent = 80  # BHYT chi trả 80% tiền thuốc
            elif service_type == "examination":
                coverage_percent = 100  # Khám BHYT được miễn phí
            elif service_type == "room":
                coverage_percent = 50  # Phòng được hỗ trợ 50%
            
            discount_amount = original_cost * coverage_percent / 100
            final_cost = original_cost - discount_amount
            
            return final_cost, discount_amount
            
    except MySQLError as e:
        print(f"Error calculating insurance discount: {e}")
        return original_cost, 0

# Invoice Management
def create_detailed_invoice(conn, patient_id, prescription_id=None, room_id=None, service_costs=None):
    """
    Tạo hóa đơn chi tiết. Sửa đổi để áp dụng chiết khấu dựa trên CoverageDetails và CoveragePercent.
    service_costs: Dictionary {'Service Name': cost}
    """
    try:
        # Lấy thông tin bảo hiểm một lần
        insurance_info = get_active_insurance_info(conn, patient_id)
        coverage_type = None
        coverage_percent = 0.00
        if insurance_info:
            coverage_type = insurance_info.get('CoverageDetails')
            coverage_percent = insurance_info.get('CoveragePercent', 0.00)

        with conn.cursor() as cursor:
            # Kiểm tra bệnh nhân tồn tại
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "Patient not found", None

            # Khởi tạo tổng
            prescription_total = 0.00
            room_total = 0.00
            service_total = 0.00
            total_before_discount = 0.00
            total_discount = 0.00
            details = [] # Chi tiết hóa đơn dạng text

            # 1. Tính chi phí thuốc (nếu có) và áp dụng chiết khấu NẾU khớp
            if prescription_id:
                cursor.execute("""
                    SELECT SUM(pd.QuantityPrescribed * m.MedicineCost) as total
                    FROM PrescriptionDetails pd
                    JOIN Medicine m ON pd.MedicineID = m.MedicineID
                    WHERE pd.PrescriptionID = %s
                """, (prescription_id,))
                result = cursor.fetchone()
                prescription_total = result.get('total', 0.00) or 0.00
                if prescription_total > 0:
                    details.append(f"Prescription #{prescription_id}: {prescription_total:,.2f} VND")
                    # Áp dụng chiết khấu nếu bảo hiểm cho 'medicine'
                    if coverage_type == 'medicine' and coverage_percent > 0:
                        med_discount = prescription_total * (coverage_percent / 100.0)
                        total_discount += med_discount
                        details.append(f"  - Insurance Discount (Medicine {coverage_percent}%): -{med_discount:,.2f} VND")

            # 2. Tính chi phí phòng (nếu có) và áp dụng chiết khấu NẾU khớp
            if room_id:
                cursor.execute("""
                    SELECT r.RoomNumber, rt.BaseCost,
                           GREATEST(1, DATEDIFF(CURDATE(), r.LastCleanedDate)) as days
                    FROM Rooms r
                    JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                    WHERE r.RoomID = %s AND r.CurrentPatientID = %s
                """, (room_id, patient_id))
                room = cursor.fetchone()
                if room:
                    days_stayed = room.get('days', 1)
                    daily_rate = room.get('BaseCost', 0.00)
                    room_total = daily_rate * days_stayed
                    details.append(f"Room #{room['RoomNumber']} ({days_stayed} days): {room_total:,.2f} VND")
                    # Áp dụng chiết khấu nếu bảo hiểm cho 'room'
                    if coverage_type == 'room' and coverage_percent > 0:
                        room_discount = room_total * (coverage_percent / 100.0)
                        total_discount += room_discount
                        details.append(f"  - Insurance Discount (Room {coverage_percent}%): -{room_discount:,.2f} VND")

            # 3. Tính chi phí dịch vụ khác (nếu có) và áp dụng chiết khấu NẾU khớp
            if service_costs and isinstance(service_costs, dict):
                 for service_name, cost in service_costs.items():
                    if cost > 0:
                        service_total += cost
                        details.append(f"Service - {service_name}: {cost:,.2f} VND")
                        # Áp dụng chiết khấu nếu bảo hiểm cho 'service'
                        if coverage_type == 'service' and coverage_percent > 0:
                            svc_discount = cost * (coverage_percent / 100.0)
                            total_discount += svc_discount
                            details.append(f"  - Insurance Discount (Service {coverage_percent}%): -{svc_discount:,.2f} VND")

            # 4. Tính tổng cuối cùng
            total_before_discount = prescription_total + room_total + service_total
            final_total_amount = total_before_discount - total_discount
            final_total_amount = max(0.00, final_total_amount)

            details.append("-" * 30)
            details.append(f"SUBTOTAL: {total_before_discount:,.2f} VND")
            if total_discount > 0:
                 details.append(f"INSURANCE COVERAGE ({coverage_type.upper()} {coverage_percent}%): -{total_discount:,.2f} VND")
            details.append(f"FINAL AMOUNT DUE: {final_total_amount:,.2f} VND")

            # 5. Tạo hóa đơn trong DB
            invoice_date = datetime.now().strftime("%Y-%m-%d")
            is_bhyt_applied = total_discount > 0

            cursor.execute("""
                INSERT INTO Invoices (
                    PatientID, InvoiceDate,
                    RoomCost, MedicineCost, ServiceCost,
                    TotalAmount,
                    PaymentStatus, IsBHYTApplied, Notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                patient_id, invoice_date,
                room_total, prescription_total, service_total,
                final_total_amount,
                'Unpaid', is_bhyt_applied, "\n".join(details)
            ))

            invoice_id = cursor.lastrowid
            conn.commit()

            detail_text = "\n".join(details)
            return True, f"Invoice #{invoice_id} created successfully:\n\n{detail_text}", invoice_id

    except MySQLError as e:
        conn.rollback()
        return False, f"Database error creating invoice: {e}", None
    except Exception as ex:
        conn.rollback()
        return False, f"Unexpected error creating invoice: {ex}", None
 
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

def get_active_insurance_info(conn, patient_id):
    """
    Hàm trợ giúp: Lấy thông tin bảo hiểm còn hiệu lực.
    Trả về một dictionary hoặc None. (Đã bỏ CoveragePercent)
    """
    try:
        with conn.cursor() as cursor:
            # Lấy các cột cần thiết, bỏ CoveragePercent
            cursor.execute("""
                SELECT InsuranceProvider, PolicyNumber, BHYTCardNumber,
                       EffectiveDate, EndDate, CoverageDetails
                FROM Insurance
                WHERE PatientID = %s
                AND EffectiveDate <= CURDATE()
                AND EndDate >= CURDATE()
                ORDER BY EndDate DESC
                LIMIT 1
            """, (patient_id,))
            insurance = cursor.fetchone()
            return insurance
    except MySQLError as e:
        print(f"Error fetching insurance info for PatientID {patient_id}: {e}")
        return None
    except Exception as ex:
        print(f"Unexpected error fetching insurance info: {ex}")
        return None

def calculate_discount_from_percentage(original_cost, percentage):
    try:
        original_cost = float(original_cost)
        percentage = float(percentage)
        percentage = max(0.0, min(100.0, percentage)) # Clamp 0-100
        discount_amount = original_cost * (percentage / 100.0)
        final_cost = original_cost - discount_amount
        final_cost = max(0.0, final_cost) # Ensure non-negative
        return final_cost, discount_amount
    except (ValueError, TypeError):
        return original_cost, 0.0 # Return original if input invalid
    except Exception as e:
        print(f"Error in calculate_discount_from_percentage: {e}")
        return original_cost, 0.0
 
# --- END ADDED FUNCTION ---

def save_calculated_invoice(conn, patient_id, med_cost_orig, room_cost_orig, svc_cost_orig, total_discount, final_amount, notes):
    """Lưu hóa đơn đã được tính toán từ GUI vào cơ sở dữ liệu."""
    try:
        # Validate inputs
        p_id_int = int(patient_id)
        med_cost_f = float(med_cost_orig)
        room_cost_f = float(room_cost_orig)
        svc_cost_f = float(svc_cost_orig)
        discount_f = float(total_discount)
        final_amount_f = float(final_amount)

        # Basic sanity check
        if final_amount_f < 0:
            print("Warning: Final amount is negative. Saving as 0.00")
            final_amount_f = 0.0
        # Could add check: abs((med+room+svc) - discount - final) < tolerance

    except ValueError:
        return False, "Invalid numeric data for invoice amounts.", None

    try:
        with conn.cursor() as cursor:
            invoice_date = datetime.now().strftime("%Y-%m-%d")
            is_bhyt_applied = discount_f > 0 # Simple check if any discount was applied

            # Ensure Invoices table has these columns with appropriate types
            # (e.g., MedicineCost, RoomCost, ServiceCost, ManualDiscount, TotalAmount, Notes)
            cursor.execute("""
                INSERT INTO Invoices (
                    PatientID, InvoiceDate,
                    MedicineCost, RoomCost, ServiceCost, /* Original costs */
                    ManualDiscount, /* Store the calculated discount */
                    TotalAmount, /* Final amount due */
                    PaymentStatus, IsBHYTApplied, Notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p_id_int, invoice_date,
                med_cost_f, room_cost_f, svc_cost_f, # Store original costs
                discount_f, # Store the manual discount applied
                final_amount_f, # Store final amount
                'Unpaid', # Default status
                is_bhyt_applied,
                notes # Store the detailed bill text
            ))
            new_invoice_id = cursor.lastrowid
            conn.commit()
            return True, "Invoice saved successfully.", new_invoice_id
    except MySQLError as e:
        conn.rollback()
        print(f"Database error saving calculated invoice: {e}")
        return False, f"Database error: {e}", None
    except Exception as ex:
        conn.rollback()
        print(f"Unexpected error saving calculated invoice: {ex}")
        return False, f"Unexpected error: {ex}", None

def generate_invoice_pdf(conn, invoice_id, output_path):
    """Generate PDF invoice with professional layout"""
    try:
        with conn.cursor() as cursor:
            # Get invoice details
            cursor.execute("""
                SELECT i.*, p.PatientName, p.PhoneNumber, p.Address
                FROM Invoices i
                JOIN Patients p ON i.PatientID = p.PatientID
                WHERE i.InvoiceID = %s
            """, (invoice_id,))
            
            invoice = cursor.fetchone()
            
            if not invoice:
                return False, "Invoice not found"
            
            # Get invoice items (simplified - in real system you'd have separate tables)
            # This is just an example
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "HOSPITAL INVOICE", 0, 1, "C")
            pdf.ln(10)
            
            # Hospital info
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, "Hospital Name: ABC General Hospital", 0, 1)
            pdf.cell(0, 10, "Address: 123 Medical Street, City", 0, 1)
            pdf.cell(0, 10, "Phone: (123) 456-7890", 0, 1)
            pdf.ln(10)
            
            # Invoice info
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Invoice #{invoice_id}", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Date: {invoice['InvoiceDate']}", 0, 1)
            pdf.ln(5)
            
            # Patient info
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Bill To:", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Patient: {invoice['PatientName']}", 0, 1)
            pdf.cell(0, 10, f"Patient ID: {invoice['PatientID']}", 0, 1)
            if invoice['Address']:
                pdf.cell(0, 10, f"Address: {invoice['Address']}", 0, 1)
            if invoice['PhoneNumber']:
                pdf.cell(0, 10, f"Phone: {invoice['PhoneNumber']}", 0, 1)
            pdf.ln(10)
            
            # Invoice items (simplified)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(100, 10, "Description", 1, 0, "C")
            pdf.cell(40, 10, "Amount (VND)", 1, 1, "C")
            
            pdf.set_font("Arial", "", 12)
            pdf.cell(100, 10, "Medical Services", 1, 0)
            pdf.cell(40, 10, f"{invoice['TotalAmount']:,.2f}", 1, 1, "R")
            
            # Total
            pdf.set_font("Arial", "B", 12)
            pdf.cell(100, 10, "TOTAL", 1, 0, "R")
            pdf.cell(40, 10, f"{invoice['TotalAmount']:,.2f}", 1, 1, "R")
            pdf.ln(20)
            
            # Footer
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, "Thank you for choosing our hospital!", 0, 1, "C")
            pdf.cell(0, 10, "Please pay within 15 days", 0, 1, "C")
            
            pdf.output(output_path)
            return True, f"Invoice PDF generated at {output_path}"
            
    except Exception as e:
        return False, f"Error generating invoice PDF: {e}"
# generate_prescription
def generate_prescription_pdf(conn, prescription_id, output_path):
    """Tạo PDF đơn thuốc"""
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin đơn thuốc
            cursor.execute("""
                SELECT p.*, doc.DoctorName, pat.PatientName, pat.DateOfBirth, pat.Gender
                FROM Prescription p
                JOIN Doctors doc ON p.DoctorID = doc.DoctorID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE p.PrescriptionID = %s
            """, (prescription_id,))
            
            prescription = cursor.fetchone()
            
            if not prescription:
                return False, "Prescription not found"
                
            # Lấy chi tiết đơn thuốc
            cursor.execute("""
                SELECT pd.*, m.MedicineName, m.Unit
                FROM PrescriptionDetails pd
                JOIN Medicine m ON pd.MedicineID = m.MedicineID
                WHERE pd.PrescriptionID = %s
            """, (prescription_id,))
            
            details = cursor.fetchall()
            
            # Tạo PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "HOSPITAL PRESCRIPTION", 0, 1, "C")
            pdf.ln(10)
            
            # Patient info
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Patient: {prescription['PatientName']}", 0, 1)
            pdf.cell(0, 10, f"DOB: {prescription['DateOfBirth']}  Gender: {prescription['Gender']}", 0, 1)
            pdf.ln(5)
            
            # Doctor info
            pdf.cell(0, 10, f"Doctor: {prescription['DoctorName']}", 0, 1)
            pdf.cell(0, 10, f"Date: {prescription['PrescriptionDate']}", 0, 1)
            pdf.ln(10)
            
            # Diagnosis
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Diagnosis:", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, prescription['Diagnosis'] or "Not specified")
            pdf.ln(10)
            
            # Medicines
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Prescribed Medicines:", 0, 1)
            pdf.ln(5)
            
            # Table header
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(80, 10, "Medicine", 1, 0, "C", 1)
            pdf.cell(30, 10, "Dosage", 1, 0, "C", 1)
            pdf.cell(30, 10, "Frequency", 1, 0, "C", 1)
            pdf.cell(30, 10, "Duration", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 12)
            for med in details:
                pdf.cell(80, 10, med['MedicineName'], 1)
                pdf.cell(30, 10, med['Dosage'], 1)
                pdf.cell(30, 10, med['Frequency'], 1)
                pdf.cell(30, 10, med['Duration'] or "-", 1)
                pdf.ln()
            
            # Notes
            if prescription['Notes']:
                pdf.ln(10)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Additional Notes:", 0, 1)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 10, prescription['Notes'])
            
            # Footer
            pdf.ln(20)
            pdf.cell(0, 10, "Doctor's Signature: ________________________", 0, 1, "R")
            
            pdf.output(output_path)
            return True, f"PDF generated at {output_path}"
            
    except Exception as e:
        return False, f"Error generating PDF: {e}"

# Statistical Reporting Functions
def generate_statistics_report(conn, start_date=None, end_date=None):
    """Generate statistics report based on registration date."""
    try:
        with conn.cursor() as cursor:
            if start_date and end_date:
                cursor.execute("""
                    SELECT COUNT(*) as TotalPatients, 
                           DATE_FORMAT(RegistrationDate, '%Y-%m') as MonthYear
                    FROM Patients
                    WHERE RegistrationDate BETWEEN %s AND %s
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """, (start_date, end_date))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as TotalPatients, 
                           DATE_FORMAT(RegistrationDate, '%Y-%m') as MonthYear
                    FROM Patients
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """)
            return True, ("STATISTICS REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
def generate_patient_report(conn, start_date=None, end_date=None):
    """Generate patient report based on registration date."""
    try:
        with conn.cursor() as cursor:
            if start_date and end_date:
                cursor.execute("""
                    SELECT COUNT(*) as TotalPatients, 
                           DATE_FORMAT(RegistrationDate, '%Y-%m') as MonthYear
                    FROM Patients
                    WHERE RegistrationDate BETWEEN %s AND %s
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """, (start_date, end_date))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as TotalPatients, 
                           DATE_FORMAT(RegistrationDate, '%Y-%m') as MonthYear
                    FROM Patients
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """)
            return True, ("PATIENT REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
def generate_appointment_report(conn, start_date=None, end_date=None):
    """Generate appointment report based on appointment date."""
    try:
        with conn.cursor() as cursor:
            if start_date and end_date:
                cursor.execute("""
                    SELECT COUNT(*) as TotalAppointments, 
                           DATE_FORMAT(AppointmentDate, '%Y-%m') as MonthYear
                    FROM Appointments
                    WHERE AppointmentDate BETWEEN %s AND %s
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """, (start_date, end_date))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as TotalAppointments, 
                           DATE_FORMAT(AppointmentDate, '%Y-%m') as MonthYear
                    FROM Appointments
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """)
            return True, ("APPOINTMENT REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
def generate_doctor_report(conn, doctor_id=None):
    """Generate doctor report based on appointments."""
    try:
        with conn.cursor() as cursor:
            if doctor_id:
                cursor.execute("""
                    SELECT COUNT(*) as TotalAppointments, 
                           DATE_FORMAT(AppointmentDate, '%Y-%m') as MonthYear
                    FROM Appointments
                    WHERE DoctorID = %s
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """, (doctor_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as TotalAppointments, 
                           DATE_FORMAT(AppointmentDate, '%Y-%m') as MonthYear
                    FROM Appointments
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """)
            return True, ("DOCTOR REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
def generate_department_report(conn, department_id=None):
    """Generate department report based on appointments."""
    try:
        with conn.cursor() as cursor:
            if department_id:
                cursor.execute("""
                    SELECT COUNT(*) as TotalAppointments, 
                           DATE_FORMAT(AppointmentDate, '%Y-%m') as MonthYear
                    FROM Appointments
                    WHERE DepartmentID = %s
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """, (department_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as TotalAppointments, 
                           DATE_FORMAT(AppointmentDate, '%Y-%m') as MonthYear
                    FROM Appointments
                    GROUP BY MonthYear
                    ORDER BY MonthYear
                """)
            return True, ("DEPARTMENT REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
def get_medicine_report(conn, start_date=None, end_date=None):
    """Generate medicine report based on prescriptions."""
    try:
        with conn.cursor() as cursor:
            if start_date and end_date:
                cursor.execute("""
                    SELECT m.MedicineName, SUM(pd.QuantityPrescribed) as TotalPrescribed
                    FROM PrescriptionDetails pd
                    JOIN Medicine m ON pd.MedicineID = m.MedicineID
                    JOIN Prescription p ON pd.PrescriptionID = p.PrescriptionID
                    WHERE p.PrescriptionDate BETWEEN %s AND %s
                    GROUP BY m.MedicineName
                    ORDER BY TotalPrescribed DESC
                """, (start_date, end_date))
            else:
                cursor.execute("""
                    SELECT m.MedicineName, SUM(pd.QuantityPrescribed) as TotalPrescribed
                    FROM PrescriptionDetails pd
                    JOIN Medicine m ON pd.MedicineID = m.MedicineID
                    JOIN Prescription p ON pd.PrescriptionID = p.PrescriptionID
                    GROUP BY m.MedicineName
                    ORDER BY TotalPrescribed DESC
                """)
            return True, ("MEDICINE REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
def get_service_report(conn, start_date=None, end_date=None):
    """Generate service report based on services used."""
    try:
        with conn.cursor() as cursor:
            if start_date and end_date:
                cursor.execute("""
                    SELECT s.ServiceName, SUM(s.ServiceCost) as TotalCost
                    FROM ServicesUsed s
                    JOIN Appointments a ON s.AppointmentID = a.AppointmentID
                    WHERE a.AppointmentDate BETWEEN %s AND %s
                    GROUP BY s.ServiceName
                    ORDER BY TotalCost DESC
                """, (start_date, end_date))
            else:
                cursor.execute("""
                    SELECT s.ServiceName, SUM(s.ServiceCost) as TotalCost
                    FROM ServicesUsed s
                    JOIN Appointments a ON s.AppointmentID = a.AppointmentID
                    GROUP BY s.ServiceName
                    ORDER BY TotalCost DESC
                """)
            return True, ("SERVICE REPORT", cursor.fetchall())
    except Exception as e:
        return False, f"Failed to generate report: {e}"
    
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
