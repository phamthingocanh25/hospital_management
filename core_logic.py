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
from pymysql.err import MySQLError

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'anh@2502'),
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

import bcrypt
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
def add_insurance_record(conn, patient_id, provider, policy_no, bhyt_no, eff_date, end_date, coverage_details):
    """Thêm một bản ghi bảo hiểm mới cho bệnh nhân vào database."""
    try:
        # Kiểm tra xem Patient ID có tồn tại không
        with conn.cursor() as cursor:
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, f"Patient with ID {patient_id} not found."

        # Validate dates (Cơ bản)
        if not validate_date(eff_date) or not validate_date(end_date):
            return False, "Invalid date format. Please use YYYY-MM-DD."
        if datetime.strptime(end_date, '%Y-%m-%d') < datetime.strptime(eff_date, '%Y-%m-%d'):
            return False, "End Date cannot be earlier than Effective Date."

        # Thêm bản ghi vào bảng Insurance
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Insurance (PatientID, InsuranceProvider, PolicyNumber, BHYTCardNumber, EffectiveDate, EndDate, CoverageDetails)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Xử lý BHYTCardNumber có thể là NULL
            bhyt_value = bhyt_no if bhyt_no else None
            coverage_value = coverage_details if coverage_details else None

            cursor.execute(sql, (patient_id, provider, policy_no, bhyt_value, eff_date, end_date, coverage_value))
            conn.commit()
        return True, "Insurance record added successfully."

    except MySQLError as e:
        conn.rollback()
        return False, f"Database error while adding insurance: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"An unexpected error occurred: {e}"    
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
            if patient_id and name:
                cursor.execute("SELECT * FROM Patients WHERE PatientID = %s AND PatientName LIKE %s", (patient_id, '%' + name + '%'))
            elif patient_id:
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

def view_appointments(conn, role, username=None, year=None, month=None, day=None, status=None): # Thêm status=None
    """
    View appointments with optional filtering including status.
    - Admin/Receptionist/Accountant: See all appointments.
    - Doctor: See only their own appointments.
    """
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin chi tiết hơn: tên bệnh nhân, tên bác sĩ
            base_query = """
                SELECT a.AppointmentID, a.DoctorID, d.DoctorName, a.PatientID, p.PatientName,
                       a.AppointmentDate, a.AppointmentTime, a.Status
                FROM Appointments a
                JOIN Doctors d ON a.DoctorID = d.DoctorID
                JOIN Patients p ON a.PatientID = p.PatientID
            """
            params = []
            conditions = []

            # Lọc theo vai trò (nếu là doctor)
            if role.lower() == 'doctor':
                # Giả sử username của doctor được lưu trong cột DoctorUser của bảng Doctors
                # Cần đảm bảo username được truyền vào hàm này
                cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorUser = %s", (username,))
                doc_result = cursor.fetchone()
                if doc_result:
                     doctor_id_for_filter = doc_result['DoctorID']
                     conditions.append("a.DoctorID = %s")
                     params.append(doctor_id_for_filter)
                else:
                     # Xử lý trường hợp không tìm thấy DoctorID từ username (ví dụ trả về lỗi hoặc danh sách rỗng)
                     return False, "Doctor profile not found for the given username."


            # Lọc theo ngày tháng năm
            if year:
                conditions.append("YEAR(a.AppointmentDate) = %s")
                params.append(year)
            if month:
                conditions.append("MONTH(a.AppointmentDate) = %s")
                params.append(month)
            if day:
                conditions.append("DAY(a.AppointmentDate) = %s")
                params.append(day)

            # Lọc theo trạng thái (status) <<< THÊM ĐIỀU KIỆN NÀY
            if status:
                conditions.append("a.Status = %s")
                params.append(status)

            # Nối các điều kiện lọc vào câu truy vấn
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            # Sắp xếp kết quả
            base_query += " ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC"

            # Thực thi truy vấn
            cursor.execute(base_query, tuple(params))
            appointments = cursor.fetchall() # Lấy kết quả dưới dạng dictionary
            return True, appointments # Trả về danh sách các dictionary

    except MySQLError as e: # Bắt lỗi cụ thể của MySQL
        return False, f"Database error: {e}"
    except Exception as e: # Bắt các lỗi chung khác
        return False, f"An unexpected error occurred: {e}"

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
def create_detailed_invoice(conn, patient_id, prescription_id=None, room_id=None):
    """Create an invoice with detailed breakdown of charges"""
    try:
        with conn.cursor() as cursor:
            # Check patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "Patient not found"
            
            # Initialize totals
            prescription_total = 0
            room_charges = 0
            other_charges = 0
            insurance_discount = 0
            details = []
            
            # Calculate prescription charges if provided
            if prescription_id:
                cursor.execute("""
                    SELECT SUM(pd.QuantityPrescribed * m.Price) as total
                    FROM PrescriptionDetails pd
                    JOIN Medicine m ON pd.MedicineID = m.MedicineID
                    WHERE pd.PrescriptionID = %s
                """, (prescription_id,))
                result = cursor.fetchone()
                prescription_total = result['total'] or 0
                details.append(f"Prescription #{prescription_id}: {prescription_total:,.2f} VND")
            
            # Calculate room charges if provided
            if room_id:
                cursor.execute("""
                    SELECT r.RoomNumber, rt.DailyRate, 
                           DATEDIFF(CURDATE(), r.LastCleanedDate) as days
                    FROM Rooms r
                    JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                    WHERE r.RoomID = %s
                """, (room_id,))
                room = cursor.fetchone()
                if room:
                    room_charges = room['DailyRate'] * room['days']
                    details.append(f"Room #{room['RoomNumber']} ({room['days']} days): {room_charges:,.2f} VND")
            
            # Calculate insurance discount if patient has active insurance
            cursor.execute("""
                SELECT * FROM Insurance 
                WHERE PatientID = %s 
                AND EffectiveDate <= CURDATE() 
                AND EndDate >= CURDATE()
                ORDER BY EndDate DESC
                LIMIT 1
            """, (patient_id,))
            
            insurance = cursor.fetchone()
            if insurance:
                # Calculate discount based on insurance coverage
                # Prescription discount (80%)
                prescription_discount = prescription_total * 0.8
                # Room discount (50%)
                room_discount = room_charges * 0.5
                insurance_discount = prescription_discount + room_discount
                details.append(f"Insurance Discount: -{insurance_discount:,.2f} VND")
            
            # Calculate total amount
            total_amount = (prescription_total + room_charges + other_charges) - insurance_discount
            details.append(f"TOTAL AMOUNT: {total_amount:,.2f} VND")
            
            # Create invoice
            invoice_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, 
                                     PrescriptionID, RoomID, InsuranceDiscount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (patient_id, invoice_date, total_amount, 
                  prescription_id if prescription_id else None, 
                  room_id if room_id else None,
                  insurance_discount))
            
            invoice_id = cursor.lastrowid
            conn.commit()
            
            # Return success with details
            detail_text = "\n".join(details)
            return True, f"Invoice #{invoice_id} created successfully:\n\n{detail_text}"
            
    except MySQLError as e:
        conn.rollback()
        return False, f"Database error: {e}"
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
def get_patient_prescriptions(conn, patient_id):
    '''Lấy chi tiết đơn thuốc gần nhất hoặc theo logic khác'''
    try:
        with conn.cursor() as cursor:
            # Lấy PrescriptionID gần nhất (ví dụ)
            cursor.execute("SELECT PrescriptionID FROM Prescription WHERE PatientID = %s ORDER BY PrescriptionDate DESC LIMIT 1", (patient_id,))
            latest_pres = cursor.fetchone()
            if not latest_pres:
                return True, [] # Trả về list rỗng nếu không có đơn

            prescription_id = latest_pres['PrescriptionID']

            # Lấy chi tiết đơn thuốc đó
            cursor.execute(
                '''
                SELECT pd.Dosage, pd.QuantityPrescribed, m.MedicineName, m.MedicineCost
                FROM PrescriptionDetails pd
                JOIN Medicine m ON pd.MedicineID = m.MedicineID
                WHERE pd.PrescriptionID = %s
                ''', (prescription_id,)
            )
            details = cursor.fetchall()
            return True, details
    except Exception as e:
        print(f"Error getting prescriptions for {patient_id}: {e}")
        return False, f"DB Error: {e}"

def get_patient_room(conn, patient_id):
    '''Lấy thông tin phòng hiện tại của bệnh nhân'''
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT r.RoomNumber, rt.TypeName, rt.BaseCost, r.LastCleanedDate
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE r.CurrentPatientID = %s
                ''', (patient_id,)
            )
            room = cursor.fetchone()
            if room:
                # Tính số ngày ở (logic ví dụ, cần ngày nhập viện hoặc logic khác)
                start_date = room.get('LastCleanedDate') or datetime.now().date() # Cần ngày bắt đầu hợp lý
                days = (datetime.now().date() - start_date).days + 1 # Ít nhất 1 ngày
                room['DaysStayed'] = max(1, days) # Đảm bảo ít nhất 1 ngày
                return True, room
            else:
                return True, None # Không ở phòng nào
    except Exception as e:
         print(f"Error getting room for {patient_id}: {e}")
         return False, f"DB Error: {e}"


def get_all_services(conn):
    '''Lấy danh sách tất cả dịch vụ và giá'''
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ServiceID, ServiceName, ServiceCost FROM Services ORDER BY ServiceName")
            services = cursor.fetchall()
            return True, services
    except Exception as e:
        print(f"Error getting all services: {e}")
        return False, f"DB Error: {e}"

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

def get_room_types_with_availability(conn):
    '''Lấy danh sách loại phòng, giá và số lượng phòng trống.'''
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    rt.RoomTypeID, rt.TypeName, rt.BaseCost,
                    COUNT(r.RoomID) AS TotalRooms,
                    SUM(CASE WHEN r.Status = 'Available' THEN 1 ELSE 0 END) AS AvailableCount
                FROM RoomTypes rt
                LEFT JOIN Rooms r ON rt.RoomTypeID = r.RoomTypeID
                GROUP BY rt.RoomTypeID, rt.TypeName, rt.BaseCost
                ORDER BY rt.TypeName;
                '''
            )
            room_types = cursor.fetchall()
            return True, room_types
    except Exception as e:
        print(f"Error getting room types with availability: {e}")
        return False, f"DB Error: {e}"
# insurance management
def create_insurance(conn, patient_id, provider, policy_no, bhyt_no, eff_date, end_date, coverage_details):
    """Create a new insurance record for a patient"""
    try:
        # Validate dates
        if not validate_date(eff_date) or not validate_date(end_date):
            return False, "Invalid date format. Please use YYYY-MM-DD."
        
        if datetime.strptime(end_date, '%Y-%m-%d') < datetime.strptime(eff_date, '%Y-%m-%d'):
            return False, "End date cannot be earlier than effective date."

        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "Patient not found"

            # Insert insurance record
            cursor.execute("""
                INSERT INTO Insurance (PatientID, InsuranceProvider, PolicyNumber, BHYTCardNumber, 
                                     EffectiveDate, EndDate, CoverageDetails)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (patient_id, provider, policy_no, bhyt_no or None, eff_date, end_date, coverage_details or None))
            
            conn.commit()
            return True, "Insurance record created successfully"
            
    except MySQLError as e:
        conn.rollback()
        return False, f"Database error: {e}"
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

#Rooms managements
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
    
def get_available_rooms(conn):
    """Lấy danh sách các phòng đang có trạng thái 'Available'."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.RoomNumber, rt.TypeName, d.DepartmentName, rt.BaseCost
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                WHERE r.Status = 'Available'
                ORDER BY d.DepartmentName, r.RoomNumber
            """)
            available_rooms = cursor.fetchall()
            return True, available_rooms # Returns True and list of dicts (or empty list)
    except MySQLError as e:
        print(f"Database error fetching available rooms: {e}")
        return False, f"Database error: {e}"
    except Exception as ex:
        print(f"Unexpected error fetching available rooms: {ex}")
        return False, f"An unexpected error occurred: {ex}"
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
# Department Management
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
