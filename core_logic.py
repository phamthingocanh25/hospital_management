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
import tkinter as tk
from mysql.connector import MySQLConnection, Error
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
def search_system_users(conn, username=None, role=None):
    try:
        with conn.cursor() as cursor:
            # Base query selecting relevant user information
            query = """
                SELECT
                    id AS UserID, -- Alias id to UserID for consistency with GUI expectation
                    username AS Username,
                    role AS Role,
                    CASE
                        WHEN IsActive = 1 THEN 'Active'
                        ELSE 'Inactive'
                    END AS Status -- Map IsActive boolean/tinyint to string status
                FROM users
                WHERE 1=1
            """
            params = []

            # Add conditions based on provided filters
            if username:
                query += " AND username LIKE %s"
                params.append(f"%{username}%") # Use LIKE for partial matching

            if role:
                # Ensure role is converted to lowercase for case-insensitive matching if needed
                # Assuming roles in DB are stored consistently (e.g., lowercase)
                query += " AND role = %s"
                params.append(role.lower()) # Match against lowercase role

            query += " ORDER BY Username ASC" # Order results by username

            cursor.execute(query, tuple(params))
            users = cursor.fetchall()

            # Return True and the list of users (which might be empty)
            return True, users

    except MySQLError as e:
        print(f"Database Error in search_system_users: {e}")
        # Potentially rollback if this function were part of a larger transaction
        # conn.rollback()
        return False, f"Database error searching users: {e}"
    except Exception as e:
        print(f"Unexpected Error in search_system_users: {e}")
        # conn.rollback() # If part of a transaction
        return False, f"An unexpected error occurred: {e}"

def get_departments_list(conn):
    """Fetches a list of departments (ID and Name) for dropdowns."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments ORDER BY DepartmentName")
            departments = cursor.fetchall() # Fetchall returns a list of dicts
            return True, departments
    except MySQLError as e:
        print(f"DB Error fetching departments list: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        print(f"Unexpected error fetching departments list: {e}")
        return False, f"Unexpected Error: {e}"

def get_patient_prescriptions(conn, patient_id):
    """
    Fetches all prescription details (medicines, quantity, cost) for a given patient,
    regardless of whether they have been invoiced yet. Suitable for invoice creation.
    """
    if not patient_id:
        return False, "Patient ID is required."

    try:
        with conn.cursor() as cursor:
            # This query joins Prescription, PrescriptionDetails, and Medicine
            # to get all necessary details for the invoice treeview.
            sql = """
                SELECT
                    pd.PrescriptionDetailID, -- Good to have for potential future actions
                    p.PrescriptionID,
                    p.PrescriptionDate,
                    m.MedicineName,
                    pd.Dosage,
                    pd.QuantityPrescribed,
                    m.MedicineCost -- Get the current cost from the Medicine table
                FROM PrescriptionDetails pd
                JOIN Prescription p ON pd.PrescriptionID = p.PrescriptionID
                JOIN Medicine m ON pd.MedicineID = m.MedicineID
                WHERE p.PatientID = %s
                -- Optional: Add criteria here if you only want prescriptions
                -- within a certain date range or those not yet fully invoiced.
                -- For creating a new invoice, usually you want all recent/unbilled items.
                ORDER BY p.PrescriptionDate DESC, pd.PrescriptionDetailID ASC;
            """
            cursor.execute(sql, (patient_id,))
            prescriptions_details = cursor.fetchall()

            # Return True even if the list is empty, the GUI will handle 'No items found'.
            return True, prescriptions_details

    except MySQLError as e:
        print(f"Database Error fetching prescription details for patient {patient_id}: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        print(f"Unexpected Error fetching prescription details for patient {patient_id}: {e}")
        return False, f"Unexpected Error: {e}"


def get_all_services(conn):
    """Placeholder: Fetches all available services."""
    print("WARNING: get_all_services called but not implemented.")
    # In a real implementation, query the Services table
    try:
         with conn.cursor() as cursor:
             cursor.execute("SELECT ServiceID, ServiceName, ServiceCost FROM Services ORDER BY ServiceName")
             services = cursor.fetchall()
             return True, services
    except MySQLError as e:
         print(f"DB Error in get_all_services: {e}")
         return False, f"Database error: {e}"
    # return False, "Not Implemented" # Return failure until implemented
def get_doctor_dashboard_stats(conn, doctor_id):
    """
    Lấy các số liệu thống kê cho dashboard của bác sĩ.
    Ví dụ: số lịch hẹn hôm nay, số bệnh nhân gần đây, số đơn thuốc gần đây.
    """
    stats = {"appointments": 0, "patients": 0, "prescriptions": 0} # Giá trị mặc định
    today_str = datetime.now().strftime('%Y-%m-%d')

    try:
        with conn.cursor() as cursor:
            # Ví dụ: Đếm lịch hẹn hôm nay của bác sĩ này
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM Appointments
                WHERE DoctorID = %s AND AppointmentDate = %s AND Status = 'Scheduled'
            """, (doctor_id, today_str))
            result_appts = cursor.fetchone()
            if result_appts:
                stats["appointments"] = result_appts.get('count', 0)

            # Ví dụ: Đếm số bệnh nhân duy nhất có lịch hẹn với bác sĩ này trong 7 ngày qua
            # (Logic này có thể cần điều chỉnh tùy theo yêu cầu)
            cursor.execute("""
                SELECT COUNT(DISTINCT PatientID) as count
                FROM Appointments
                WHERE DoctorID = %s AND AppointmentDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()
            """, (doctor_id,))
            result_patients = cursor.fetchone()
            if result_patients:
                stats["patients"] = result_patients.get('count', 0)

            # Ví dụ: Đếm số đơn thuốc bác sĩ này tạo trong 7 ngày qua
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM Prescription
                WHERE DoctorID = %s AND PrescriptionDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()
            """, (doctor_id,))
            result_presc = cursor.fetchone()
            if result_presc:
                stats["prescriptions"] = result_presc.get('count', 0)

        return True, stats # Trả về thành công và dictionary chứa số liệu

    except MySQLError as e:
        print(f"Lỗi CSDL khi lấy dashboard stats cho bác sĩ {doctor_id}: {e}")
        return False, f"Lỗi CSDL: {e}"
    except Exception as e:
        print(f"Lỗi không mong đợi khi lấy dashboard stats cho bác sĩ {doctor_id}: {e}")
        return False, f"Lỗi không mong đợi: {e}"
def get_room_types_with_availability(conn):
     """Placeholder: Fetches room types and their availability."""
     print("WARNING: get_room_types_with_availability called but not implemented.")
     # In a real implementation, query RoomTypes and join with Rooms to count status
     try:
         with conn.cursor() as cursor:
             cursor.execute("""
                 SELECT
                     rt.RoomTypeID,
                     rt.TypeName,
                     rt.BaseCost,
                     COUNT(r.RoomID) AS TotalRooms,
                     SUM(CASE WHEN r.Status = 'Available' THEN 1 ELSE 0 END) AS AvailableCount
                 FROM RoomTypes rt
                 LEFT JOIN Rooms r ON rt.RoomTypeID = r.RoomTypeID
                 GROUP BY rt.RoomTypeID, rt.TypeName, rt.BaseCost
                 ORDER BY rt.TypeName;
             """)
             room_types_data = cursor.fetchall()
             # Ensure counts are integers
             for room in room_types_data:
                 room['TotalRooms'] = int(room.get('TotalRooms', 0))
                 room['AvailableCount'] = int(room.get('AvailableCount', 0))
             return True, room_types_data
     except MySQLError as e:
         print(f"DB Error in get_room_types_with_availability: {e}")
         return False, f"Database error: {e}"
     # return False, "Not Implemented" # Return failure until implemented
def get_admin_activity_overview_stats(conn):
    """Fetches data for the admin dashboard's activity overview section."""
    overview_data = {
        "active_users": "E",
        "disabled_users": "E",
        "expiring_medicines_30d": "E",
        "low_stock_inventory": "E",
        "pending_admissions": "E"
    }
    if not conn:
        print("Error: No database connection provided to get_admin_activity_overview_stats.")
        return overview_data

    try:
        with conn.cursor() as cursor:
            # User Status
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE IsActive = TRUE")
            active_users_result = cursor.fetchone()
            overview_data["active_users"] = str(active_users_result['count']) if active_users_result else "0"

            cursor.execute("SELECT COUNT(*) as count FROM users WHERE IsActive = FALSE")
            disabled_users_result = cursor.fetchone()
            overview_data["disabled_users"] = str(disabled_users_result['count']) if disabled_users_result else "0"

            # Expiring Medicine Batches (Active and expiring in next 30 days)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM MedicineBatch
                WHERE ExpiryDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
                  AND Status = 'Active'
            """)
            expiring_med_result = cursor.fetchone()
            overview_data["expiring_medicines_30d"] = str(expiring_med_result['count']) if expiring_med_result else "0"

            # Low Stock Inventory
            cursor.execute("SELECT COUNT(*) as count FROM Inventory WHERE Status IN ('Low Stock', 'Out of Stock')")
            low_stock_result = cursor.fetchone()
            overview_data["low_stock_inventory"] = str(low_stock_result['count']) if low_stock_result else "0"

            # Pending Admission Orders
            cursor.execute("SELECT COUNT(*) as count FROM AdmissionOrders WHERE Status = 'Pending'")
            pending_admissions_result = cursor.fetchone()
            overview_data["pending_admissions"] = str(pending_admissions_result['count']) if pending_admissions_result else "0"

    except MySQLError as e:
        print(f"Database error fetching admin overview stats: {e}")
        for key_item in overview_data: overview_data[key_item] = "E" # Reset on DB error
    except Exception as e:
        print(f"Unexpected error fetching admin overview stats: {e}")
        for key_item in overview_data: overview_data[key_item] = "E" # Reset on general error
    return overview_data

def get_departments_list(conn):
    """Fetches a list of departments (ID and Name) for dropdowns."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments ORDER BY DepartmentName")
            departments = cursor.fetchall()
            return True, departments
    except MySQLError as e:
        print(f"DB Error fetching departments list: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        print(f"Unexpected error fetching departments list: {e}")
        return False, f"Unexpected Error: {e}"

def create_admission_order(conn, patient_id, doctor_id, department_id, reason, notes=None):
    """Creates a new admission order record in the database."""
    if not all([patient_id, doctor_id, department_id, reason]):
        return False, "Patient ID, Doctor ID, Department ID, and Reason are required."
    try:
        with conn.cursor() as cursor:
            # Validate Patient ID
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s AND Status = 'active'", (patient_id,))
            if not cursor.fetchone():
                return False, f"Patient ID {patient_id} not found or inactive."

            # Validate Doctor ID (assuming Doctors table has DoctorID as PK)
            cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorID = %s AND status = 'active'", (doctor_id,))
            if not cursor.fetchone():
                return False, f"Doctor ID {doctor_id} not found or inactive."

            # Validate Department ID
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (department_id,))
            if not cursor.fetchone():
                return False, f"Department ID {department_id} not found."

            
            sql = """
                INSERT INTO AdmissionOrders
                (PatientID, DoctorID, DepartmentID, OrderDate, Reason, Notes, Status)
                VALUES (%s, %s, %s, CURDATE(), %s, %s, %s)
            """
            cursor.execute(sql, (patient_id, doctor_id, department_id, reason, notes, 'Pending'))
            conn.commit()
            return True, f"Admission order created successfully for Patient ID {patient_id}."

    except MySQLError as e:
        conn.rollback()
        print(f"DB error creating admission order: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error creating admission order: {e}")
        return False, f"Unexpected Error: {e}"
def get_pending_admission_orders(conn):
    """Retrieve all admission orders with 'Pending' status."""
    try:
        with conn.cursor() as cursor:
            # Join with Patients, Doctors, Departments to get names
            sql = """
                SELECT
                    ao.AdmissionOrderID as OrderID,
                    ao.PatientID,
                    p.PatientName,
                    ao.DoctorID,
                    d.DoctorName,
                    ao.DepartmentID,
                    dep.DepartmentName,
                    ao.OrderDate,
                    ao.Reason,
                    p.DateOfBirth,
                    p.Gender,
                    p.Address,
                    p.PhoneNumber
                FROM AdmissionOrders ao
                JOIN Patients p ON ao.PatientID = p.PatientID
                JOIN Doctors d ON ao.DoctorID = d.DoctorID
                JOIN Departments dep ON ao.DepartmentID = dep.DepartmentID
                WHERE ao.Status = 'Pending'
                ORDER BY ao.OrderDate ASC, ao.AdmissionOrderID ASC
            """
            cursor.execute(sql)
            pending_orders = cursor.fetchall()
            return True, pending_orders
    except MySQLError as e:
        print(f"DB error fetching pending admission orders: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        print(f"Unexpected error fetching pending admission orders: {e}")
        return False, f"Unexpected Error: {e}"

def get_admission_order_details(conn, order_id):
    """Get detailed information about a specific admission order."""
    try:
        with conn.cursor() as cursor:
            # Get basic order info
            sql = """
                SELECT
                    ao.AdmissionOrderID as OrderID,
                    ao.PatientID,
                    p.PatientName,
                    p.DateOfBirth,
                    p.Gender,
                    p.Address,
                    p.PhoneNumber,
                    ao.DoctorID,
                    d.DoctorName,
                    ao.DepartmentID,
                    dep.DepartmentName,
                    ao.OrderDate,
                    ao.Reason,
                    ao.Notes,
                    (SELECT InsuranceProvider FROM Insurance 
                     WHERE PatientID = ao.PatientID 
                     AND EffectiveDate <= CURDATE() 
                     AND EndDate >= CURDATE() 
                     LIMIT 1) as InsuranceProvider
                FROM AdmissionOrders ao
                JOIN Patients p ON ao.PatientID = p.PatientID
                JOIN Doctors d ON ao.DoctorID = d.DoctorID
                JOIN Departments dep ON ao.DepartmentID = dep.DepartmentID
                WHERE ao.AdmissionOrderID = %s
            """
            cursor.execute(sql, (order_id,))
            order_details = cursor.fetchone()
            
            if not order_details:
                return False, f"Admission order {order_id} not found"
                
            return True, order_details
    except MySQLError as e:
        print(f"DB error fetching admission order details: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        print(f"Unexpected error fetching admission order details: {e}")
        return False, f"Unexpected Error: {e}"

def process_admission_order(conn, order_id, patient_id, room_id, username):
    """Process an admission order by assigning a room and updating statuses."""
    try:
        with conn.cursor() as cursor:
            # 0. Get Receptionist User ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            receptionist = cursor.fetchone()
            if not receptionist:
                return False, f"Receptionist user '{username}' not found."
            receptionist_user_id = receptionist['id']

            # 1. Check Admission Order Status
            cursor.execute("SELECT PatientID, Status FROM AdmissionOrders WHERE AdmissionOrderID = %s", (order_id,))
            order = cursor.fetchone()
            if not order:
                return False, f"Admission Order ID {order_id} not found."
            if order['Status'] != 'Pending':
                return False, f"Admission Order {order_id} is not in 'Pending' status (Current: {order['Status']})."
            if str(order['PatientID']) != str(patient_id):
                return False, f"Patient ID mismatch (Order: {order['PatientID']}, Provided: {patient_id})."

            # 2. Check Room Status
            cursor.execute("SELECT Status FROM Rooms WHERE RoomID = %s", (room_id,))
            room = cursor.fetchone()
            if not room:
                return False, f"Room ID {room_id} not found."
            if room['Status'] != 'Available':
                return False, f"Room {room_id} is not 'Available' (Current: {room['Status']}). Cannot assign."

            # 3. Update Room: Set Status='Occupied', assign PatientID
            cursor.execute("UPDATE Rooms SET Status = 'Occupied', CurrentPatientID = %s WHERE RoomID = %s", 
                         (patient_id, room_id))

            # 4. Update Admission Order: Set Status='Processed', record processor and time, assigned room
            cursor.execute("""
                UPDATE AdmissionOrders
                SET Status = 'Processed',
                    ProcessedByUserID = %s,
                    ProcessedDate = NOW(),
                    AssignedRoomID = %s
                WHERE AdmissionOrderID = %s
            """, (receptionist_user_id, room_id, order_id))

            # 5. Update Patient Status to 'Inpatient'
            cursor.execute("UPDATE Patients SET Status = 'Inpatient' WHERE PatientID = %s", (patient_id,))

            conn.commit()
            return True, f"Admission Order {order_id} processed successfully. Patient {patient_id} assigned to Room {room_id}."

    except MySQLError as e:
        conn.rollback()
        print(f"DB error processing admission: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error processing admission: {e}")
        return False, f"Unexpected Error: {e}"

def get_available_rooms_by_department(conn, department_id):
    """Retrieve available rooms for a specific department."""
    if not department_id:
        return False, "Department ID is required."
    try:
        with conn.cursor() as cursor:
            # Join with RoomTypes to display type name and cost
            sql = """
                SELECT 
                    r.RoomID as id,
                    r.RoomNumber as number,
                    rt.TypeName as type,
                    rt.BaseCost as cost
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                WHERE r.DepartmentID = %s AND r.Status = 'Available'
                ORDER BY r.RoomNumber ASC
            """
            cursor.execute(sql, (department_id,))
            available_rooms = cursor.fetchall()
            return True, available_rooms
    except MySQLError as e:
        print(f"DB error fetching available rooms: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        print(f"Unexpected error fetching available rooms: {e}")
        return False, f"Unexpected Error: {e}"




def get_active_insurance_info(conn, patient_id):
    """Placeholder: Fetches active insurance info."""
    print(f"WARNING: get_active_insurance_info called for patient {patient_id} but not fully implemented.")
    # In a real implementation, query the Insurance table with date checks
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM Insurance
                WHERE PatientID = %s
                  AND EffectiveDate <= CURDATE()
                  AND EndDate >= CURDATE()
                ORDER BY EndDate DESC
                LIMIT 1
            """, (patient_id,))
            insurance = cursor.fetchone()
            return insurance # Returns dict or None
    except MySQLError as e:
        print(f"DB Error in get_active_insurance_info: {e}")
        return None # Indicate failure or no insurance found
    
def authenticate_user(username, password):
    """Authenticate user and return details or error message."""
    try:
        conn = get_db_connection()
        if not conn:
            # Return None for connection if it fails, plus an error message
            return None, None, None, None, "Database connection failed"

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id as user_db_id, u.username, u.password, u.role, u.IsActive,
                       CASE
                           WHEN u.role = 'doctor' THEN d.DoctorID
                           ELSE NULL
                       END as role_id
                FROM users u
                LEFT JOIN Doctors d ON u.username = d.DoctorUser AND d.status = 'active'
                WHERE BINARY u.username = %s
            """, (username,)) # BINARY ensures case-sensitive match

            user = cursor.fetchone()

            if user:
                # Check if account is active
                if not user.get('IsActive', True): # Default to True if column doesn't exist yet
                     conn.close()
                     return None, None, None, None, "User account is inactive."

                db_password_hash = user['password']
                # Check password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), db_password_hash.encode('utf-8')):
                    # Special check for doctors: ensure they have a linked, active DoctorID
                    if user['role'] == 'doctor' and user['role_id'] is None:
                        conn.close()
                        return None, None, None, None, "Doctor profile not linked or inactive."

                    # Return successful login details including the connection object
                    return user['username'], user['role'], conn, user['role_id'], None
                else:
                    conn.close()
                    return None, None, None, None, "Incorrect password"
            else:
                conn.close()
                return None, None, None, None, "User not found"

    except MySQLError as e:
        # Close connection if it was opened before the error
        if 'conn' in locals() and conn and conn.open:
             conn.close()
        print(f"DB Error in authenticate_user: {e}") # Log for debugging
        return None, None, None, None, f"Database error during login." # Generic error to user
    except Exception as e:
         # Catch other potential errors
         if 'conn' in locals() and conn and conn.open:
             conn.close()
         print(f"Unexpected Error in authenticate_user: {e}") # Log for debugging
         return None, None, None, None, "An unexpected error occurred during login."

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
    valid_roles = ["admin", "doctor", "receptionist", "accountant", "nurse", "director", "pharmacist", "inventory_manager"]

    if role.lower() not in valid_roles:
        return False, f"❌ Unsupported role: '{role}'. Allowed roles: {', '.join(valid_roles)}"

    if not is_valid_username(username)[0]:
        return False, is_valid_username(username)[1]
    
    if password != confirm_password:
        return False, "❌ Passwords do not match"
    
    if not is_strong_password(password)[0]:
        return False, "❌ Password must be at least 8 characters long and contain a mix of uppercase, lowercase, numbers, and special characters."

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
        # Validate new password strength first
        is_strong, msg = is_strong_password(new_password)
        if not is_strong:
            return False, msg # Return the strength error message

        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                return False, "❌ User not found."

            current_hashed_pw = user['password']
            if not bcrypt.checkpw(old_password.encode('utf-8'), current_hashed_pw.encode('utf-8')):
                return False, "❌ Current password is incorrect."

            # Check if new password is same as old
            if bcrypt.checkpw(new_password.encode('utf-8'), current_hashed_pw.encode('utf-8')):
                 return False, "❌ New password cannot be the same as the old password."

            # Hash and update the new password
            hashed_new_password = hash_password(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_new_password, username))
            conn.commit()
            return True, "✅ Password changed successfully."

    except MySQLError as e:
        conn.rollback() # Rollback on error
        print(f"DB Error in change_password: {e}") # Log detailed error
        return False, f"❌ Database error changing password." # Generic error to user
    except Exception as e:
        conn.rollback() # Rollback on unexpected error
        print(f"Unexpected Error in change_password: {e}") # Log detailed error
        return False, "❌ An unexpected error occurred." # Generic error to user


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
def add_doctor(conn, name, dept_id, specialization, username, phone_number=None, email=None):
    """Add new doctor with automatic account creation, including phone and email."""
    print("\n--- Add New Doctor ---")
    temp_password = generate_temp_password() # Đảm bảo hàm này đã được định nghĩa

    try:
        with conn.cursor() as cursor:
            # Kiểm tra các trường bắt buộc
            if not all([name, dept_id, specialization, username]):
                return False, "Doctor Name, Department, Specialty, and System Username are required."

            # Kiểm tra DepartmentID có tồn tại không
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (dept_id,))
            if not cursor.fetchone():
                return False, f"❌ Department ID '{dept_id}' does not exist."

            # Kiểm tra xem DoctorUser (username) đã tồn tại trong bảng Doctors chưa
            # Bảng Doctors đã có UNIQUE constraint cho DoctorUser, PhoneNumber, Email
            cursor.execute("SELECT DoctorUser FROM Doctors WHERE DoctorUser = %s", (username,))
            if cursor.fetchone():
                return False, f"❌ System Username '{username}' is already assigned to another doctor."

            # Kiểm tra xem username đã tồn tại trong bảng users chưa
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, f"❌ System Username '{username}' already exists in the users login table."
            
            # Kiểm tra PhoneNumber nếu được cung cấp và chưa có trong bảng Doctors
            if phone_number:
                cursor.execute("SELECT DoctorID FROM Doctors WHERE PhoneNumber = %s", (phone_number,))
                if cursor.fetchone():
                    return False, f"❌ Phone number '{phone_number}' already exists for another doctor."
            
            # Kiểm tra Email nếu được cung cấp và chưa có trong bảng Doctors
            if email:
                cursor.execute("SELECT DoctorID FROM Doctors WHERE Email = %s", (email,))
                if cursor.fetchone():
                    return False, f"❌ Email '{email}' already exists for another doctor."


            # Thêm thông tin vào bảng Doctors
            sql_insert_doctor = """
                INSERT INTO Doctors (DoctorName, DepartmentID, Specialty, DoctorUser, PhoneNumber, Email, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
            """
            # Thêm status='active' mặc định khi tạo bác sĩ mới
            cursor.execute(sql_insert_doctor, (name, dept_id, specialization, username, phone_number, email, 'active'))

            # Tạo tài khoản người dùng trong bảng users
            hashed_pw = hash_password(temp_password) # Đảm bảo hàm này đã được định nghĩa
            # Lưu FullName (tên bác sĩ) và Email (email bác sĩ) vào bảng users
            sql_insert_user = """
                INSERT INTO users (username, password, role, FullName, Email, IsActive)
                VALUES (%s, %s, 'doctor', %s, %s, TRUE) 
            """
            cursor.execute(sql_insert_user, (username, hashed_pw, name, email))

            conn.commit()
            return True, f"✅ Doctor '{name}' added successfully with username '{username}'.\nTemporary Password: {temp_password}\nPlease ask the doctor to change it immediately!"

    except MySQLError as e:
        conn.rollback()
        # Phân tích lỗi cụ thể hơn nếu là lỗi UNIQUE constraint từ database
        if e.args[0] == 1062: # Mã lỗi cho Duplicate entry
            error_message = str(e).lower()
            if 'doctoruser' in error_message:
                 return False, f"❌ Failed to add doctor: System Username '{username}' already exists."
            elif 'phonenumber' in error_message:
                 return False, f"❌ Failed to add doctor: Phone number '{phone_number}' already exists."
            elif 'email' in error_message and 'doctors' in error_message : # Email trong bảng Doctors
                 return False, f"❌ Failed to add doctor: Email '{email}' already exists for another doctor."
            elif 'username' in error_message and 'users' in error_message: # Username trong bảng Users
                 return False, f"❌ Failed to create user account: Username '{username}' already exists."
            elif 'email' in error_message and 'users' in error_message: # Email trong bảng Users
                 return False, f"❌ Failed to create user account: Email '{email}' already exists for another user."
        return False, f"❌ Failed to add doctor: Database error (Code: {e.args[0]}) - {e.args[1]}"
    except Exception as e_gen:
        conn.rollback()
        return False, f"❌ Failed to add doctor: An unexpected error occurred - {str(e_gen)}"

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
def update_invoice_payment_status(conn, invoice_id, new_status):
    """Updates the payment status of a specific invoice."""
    valid_statuses = ["Unpaid", "Partial", "Paid"]
    if new_status not in valid_statuses:
        return False, f"Invalid status: '{new_status}'. Allowed statuses are {', '.join(valid_statuses)}."
    if not invoice_id:
        return False, "Invoice ID is required."

    try:
        with conn.cursor() as cursor:
            # Kiểm tra hóa đơn tồn tại
            cursor.execute("SELECT InvoiceID FROM Invoices WHERE InvoiceID = %s", (invoice_id,))
            if not cursor.fetchone():
                return False, f"Invoice with ID {invoice_id} not found."

            cursor.execute("""
                UPDATE Invoices
                SET PaymentStatus = %s
                WHERE InvoiceID = %s
            """, (new_status, invoice_id))
            conn.commit()
            return True, f"Payment status for Invoice #{invoice_id} updated to '{new_status}' successfully."
    except MySQLError as e:
        conn.rollback()
        print(f"DB Error updating invoice status: {e}")
        return False, f"Database Error: {e}"
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error updating invoice status: {e}")
        return False, f"An unexpected error occurred: {e}"
    
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

def assign_doctor_user(conn, doctor_id, username, password=None):
    """Tạo user mới, băm mật khẩu và gán cho bác sĩ"""
    try:
        with conn.cursor() as cursor:
            # Check if doctor exists and doesn't have a username assigned
            cursor.execute("SELECT DoctorID, DoctorUser FROM Doctors WHERE DoctorID = %s", (doctor_id,))
            doctor = cursor.fetchone()
            if not doctor:
                return False, "❌ Doctor ID not found."
            if doctor['DoctorUser']:
                return False, f"❌ Doctor already has a username assigned: {doctor['DoctorUser']}."

            # Kiểm tra xem username đã tồn tại chưa
            cursor.execute("SELECT username FROM Users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "❌ Username already exists."

            # Validate username and password (if provided)
            valid_user, user_msg = is_valid_username(username)
            if not valid_user:
                 return False, user_msg

            if password:
                 strong_pass, pass_msg = is_strong_password(password)
                 if not strong_pass:
                     return False, pass_msg
                 raw_password_to_hash = password
                 password_info = f"Password set as provided."
            else:
                 raw_password_to_hash = generate_temp_password() # Generate if not provided
                 password_info = f"Temporary Password: {raw_password_to_hash}" # Include temp pass in message

            hashed_password = hash_password(raw_password_to_hash)

            # Tạo user mới với role 'doctor'
            cursor.execute(
                "INSERT INTO Users (username, password, role, IsActive) VALUES (%s, %s, 'doctor', TRUE)",
                (username, hashed_password)
            )

            # Gán user cho bác sĩ
            cursor.execute("UPDATE Doctors SET DoctorUser = %s WHERE doctorID = %s", (username, doctor_id))
            conn.commit()
            return True, f"✅ User '{username}' created and assigned.\n{password_info}"
    except MySQLError as e:
        conn.rollback()
        print(f"DB error in assign_doctor_user: {e}") # Log details
        return False, f"❌ Database error: Failed to assign user." # Generic error to user
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error in assign_doctor_user: {e}") # Log details
        return False, f"❌ Unexpected error assigning user." # Generic error to user

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
def view_patients(conn):
    """Retrieve all active patients from the system."""
    try:
        with conn.cursor() as cursor:
            # Select relevant patient details, filtering out disabled ones
            cursor.execute("""
                SELECT PatientID, PatientName, DateOfBirth, Gender, Address, PhoneNumber
                FROM Patients
                WHERE Status = 'active'
                ORDER BY PatientName
            """)
            patients = cursor.fetchall()
            if patients:
                return True, patients # Return the list of patient dictionaries
            else:
                return True, [] # Return an empty list if no active patients
    except MySQLError as e:
        print(f"❌ Database error in view_patients: {e}")
        return False, f"❌ Failed to retrieve patients: Database error."
    except Exception as e:
        print(f"❌ Unexpected error in view_patients: {e}")
        return False, "❌ An unexpected error occurred while fetching patients."


def view_appointments(conn, doctor_id=None):
    """
    Retrieve appointments.
    If doctor_id is provided, retrieve appointments only for that doctor.
    Otherwise, retrieve all appointments.
    """
    try:
        with conn.cursor() as cursor:
            if doctor_id:
                # View appointments for a specific doctor
                query = """
                    SELECT a.AppointmentID, p.PatientName, a.AppointmentDate, a.AppointmentTime, a.Status
                    FROM Appointments a
                    JOIN Patients p ON a.PatientID = p.PatientID
                    WHERE a.DoctorID = %s
                    ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC
                """
                cursor.execute(query, (doctor_id,))
                title = f"Appointments for Doctor ID {doctor_id}"
            else:
                # View all appointments (typically for admin/receptionist)
                query = """
                    SELECT a.AppointmentID, p.PatientName, d.DoctorName,
                           a.AppointmentDate, a.AppointmentTime, a.Status
                    FROM Appointments a
                    JOIN Patients p ON a.PatientID = p.PatientID
                    JOIN Doctors d ON a.DoctorID = d.DoctorID
                    ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC
                """
                cursor.execute(query)
                title = "All Appointments"

            appointments = cursor.fetchall()
            # Return the title along with the data for context
            return True, {"title": title, "data": appointments}
    except MySQLError as e:
        print(f"❌ Database error in view_appointments: {e}")
        return False, f"❌ Failed to retrieve appointments: Database error."
    except Exception as e:
        print(f"❌ Unexpected error in view_appointments: {e}")
        return False, "❌ An unexpected error occurred while fetching appointments."
    
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

def search_patients(conn, patient_id=None, name=None):
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
 
def add_department(conn, name):
    """Add a new department to the system"""
    try:
        with conn.cursor() as cursor:
            if name:
                cursor.execute("INSERT INTO Departments (DepartmentName) VALUES (%s)", (name,))
                conn.commit()
                return True, "✅ Department added successfully."
            else:
                return False, "❌ Department name cannot be empty."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to add department: {e}"

def view_departments(conn):
    """Fetch departments with doctor count"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT d.DepartmentID, d.DepartmentName, 
                    COUNT(doc.DoctorID) AS DoctorCount
                FROM Departments d
                LEFT JOIN Doctors doc ON d.DepartmentID = doc.DepartmentID
                GROUP BY d.DepartmentID
                ORDER BY d.DepartmentID
            """)
            return True, cursor.fetchall()
    except MySQLError as e:
        return False, f"❌ Failed to retrieve departments: {e}"

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
    Search appointments with optional filters.
    Admin/Receptionist/Accountant: All appointments.
    Doctor: Only appointments of the logged-in doctor.
    """
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT a.AppointmentID, a.DoctorID, d.DoctorName,
                       a.PatientID, p.PatientName,
                       a.AppointmentDate, a.AppointmentTime, a.Status
                FROM Appointments a
                LEFT JOIN Doctors d ON a.DoctorID = d.DoctorID
                LEFT JOIN Patients p ON a.PatientID = p.PatientID
                WHERE 1=1
            """
            params = []

            # Doctor role: filter by logged-in doctor's ID
            if role.lower() == 'doctor':
                cursor.execute("SELECT DoctorID FROM Doctors WHERE DoctorUser = %s", (username,))
                doctor = cursor.fetchone()
                if not doctor:
                    return False, "❌ Doctor profile not found for the given username."
                query += " AND a.DoctorID = %s"
                params.append(doctor["DoctorID"])

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
                valid_statuses = {"Scheduled", "Completed", "Cancelled"}
                if status not in valid_statuses:
                    return False, "❌ Invalid status selected."
                query += " AND a.Status = %s"
                params.append(status)

            query += " ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC"

            cursor.execute(query, params)
            return True, cursor.fetchall()

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
def get_all_available_rooms(conn):
    """
    Lấy danh sách tất cả các phòng trống trong bệnh viện (không phân biệt khoa)
    
    Args:
        conn: Kết nối database
        
    Returns:
        Tuple (success, data/error_message):
        - success: True nếu thành công, False nếu có lỗi
        - data: Danh sách phòng trống nếu thành công, error message nếu thất bại
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.RoomID, r.RoomNumber, rt.TypeName, d.DepartmentName, rt.BaseCost
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                WHERE r.Status = 'Available'
                ORDER BY d.DepartmentName, r.RoomNumber
            """)
            rooms = cursor.fetchall()
            return True, rooms
    except Exception as e:
        print(f"Error getting all available rooms: {str(e)}")
        return False, str(e)

def get_all_rooms_with_status(conn):
    """
    Lấy danh sách tất cả phòng với trạng thái chi tiết
    
    Returns:
        Tuple (success, data/error):
        - success: True/False
        - data: List of rooms or error message
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    r.RoomID, 
                    r.RoomNumber, 
                    rt.TypeName,
                    d.DepartmentName,
                    r.Status,
                    rt.BaseCost,
                    p.PatientName,
                    r.LastCleanedDate
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                LEFT JOIN Patients p ON r.CurrentPatientID = p.PatientID
                ORDER BY 
                    CASE r.Status
                        WHEN 'Available' THEN 1
                        WHEN 'Cleaning' THEN 2
                        WHEN 'Occupied' THEN 3
                        WHEN 'Maintenance' THEN 4
                        ELSE 5
                    END,
                    d.DepartmentName,
                    r.RoomNumber
            """)
            return True, cursor.fetchall()
    except Exception as e:
        print(f"Error getting rooms with status: {str(e)}")
        return False, str(e)   
def add_room(conn, room_number, room_type_id, department_id, status="Available"):
    """Add a new room to the system"""
    try:
        with conn.cursor() as cursor:
            if not all([room_number, room_type_id, department_id]):
                return False, "All categories are required."
            
            # Kiểm tra xem loại phòng có tồn tại không
            cursor.execute("SELECT RoomTypeID FROM RoomTypes WHERE RoomTypeID = %s", (room_type_id,))
            if not cursor.fetchone():
                return False, "Room type does not exist."

            # Kiểm tra xem khoa có tồn tại không
            cursor.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = %s", (department_id,))
            if not cursor.fetchone():
                return False, "Department does not exist."
            
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
    
def add_room_type(conn, type_name=None, base_cost=None, description=None): # Đổi tên 'des' thành 'description' cho rõ ràng
    """Add a new room type to the system"""
    try:
        with conn.cursor() as cursor:
            if not type_name or not base_cost: # TypeName và BaseCost là bắt buộc (NOT NULL)
                return False, "❌ Type name and base cost cannot be empty."
            
            # Kiểm tra base_cost có phải là số hợp lệ không
            try:
                base_cost_decimal = float(base_cost)
                if base_cost_decimal < 0:
                    return False, "❌ Base cost must be a non-negative number."
            except ValueError:
                return False, "❌ Base cost must be a valid number."

            # Câu lệnh INSERT giờ đây bao gồm cả 3 cột
            # Cột Description có thể NULL, nên nếu description là None hoặc chuỗi rỗng, nó vẫn hợp lệ
            sql_insert = "INSERT INTO RoomTypes (TypeName, BaseCost, Description) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (type_name, base_cost_decimal, description if description else None))
            
            conn.commit()
            return True, "✅ Room type added successfully."
    except MySQLError as e:
        conn.rollback()
        # Kiểm tra lỗi cụ thể hơn, ví dụ lỗi UNIQUE constraint cho TypeName
        if e.args[0] == 1062: # Mã lỗi cho Duplicate entry
             if 'TypeName' in str(e): # Kiểm tra nếu lỗi liên quan đến TypeName
                 return False, f"❌ Failed to add room type: TypeName '{type_name}' already exists."
        return False, f"❌ Failed to add room type: {e} (Error Code: {e.args[0]})"
    except Exception as ex: # Bắt các lỗi không mong muốn khác
        conn.rollback()
        return False, f"❌ An unexpected error occurred: {ex}"
    
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
        if not patient_id or not room_type_id:
            return False, "All fields are required."
        with conn.cursor() as cursor:
            # Check if patient exists
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "Patient not found."
            
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
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PatientServices (PatientID, ServiceID, DoctorID, ServiceDate, Quantity, CostAtTime, Notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, service_id, doctor_id, service_date, quantity, cost_at_time, notes)
        )
        conn.commit()
        return True, "Added"
    except Exception as e:
        return False, str(e)
        
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
    """Search for services used by a patient, filtered by ID or name."""
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT ps.PatientServiceID, p.PatientName, s.ServiceName, ps.ServiceDate, ps.Quantity, s.ServiceCost
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                JOIN Patients p ON ps.PatientID = p.PatientID
                WHERE 1=1
            """
            params = []

            if patient_id and patient_name:
                query += " AND p.PatientID = %s AND p.PatientName ILIKE %s"
                params.extend([patient_id, f"%{patient_name}%"])
            elif patient_id:
                query += " AND p.PatientID = %s"
                params.append(patient_id)
            elif patient_name:
                query += " AND p.PatientName ILIKE %s"
                params.append(f"%{patient_name}%")

            cursor.execute(query, tuple(params))
            return True, cursor.fetchall()

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

            # Kiểm tra xem dịch vụ của bệnh nhân có tồn tại không
            cursor.execute("SELECT PatientServiceID, InvoiceID FROM PatientServices WHERE PatientServiceID = %s", (patient_service_id,))
            service = cursor.fetchone()
            if not service:
                return False, "❌ Patient service record not found."
            if service['InvoiceID'] is not None:
                 return False, f"❌ Service already attached to Invoice ID: {service['InvoiceID']}."


            # Update PatientServices to link to the invoice
            cursor.execute("""
                UPDATE PatientServices
                SET InvoiceID = %s
                WHERE PatientServiceID = %s
            """, (invoice_id, patient_service_id))

            conn.commit()
            return True, "✅ Service attached to invoice successfully."
    except MySQLError as e:
        conn.rollback()
        print(f"DB error in attach_service_to_invoice: {e}")
        return False, f"❌ Failed to attach service to invoice: {e}"
    except Exception as e:
         conn.rollback()
         print(f"Unexpected error in attach_service_to_invoice: {e}")
         return False, f"❌ Unexpected error attaching service."

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
                INSERT INTO Prescription (PatientID, DoctorID, PrescriptionDate)
                VALUES (%s, %s, %s)
            """, (patient_id, doctor_id, prescription_date))

            conn.commit()
            return True, "✅ Prescription created successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to create prescription: {e}"
     
def delete_prescription_detail(conn, prescription_detail_id):
    """Delete a specific medicine entry from a prescription using its detail ID."""
    if not prescription_detail_id:
        return False, "❌ Prescription Detail ID is required."
    try:
        with conn.cursor() as cursor:
            # Check if the detail exists before deleting
            cursor.execute("SELECT PrescriptionDetailID FROM PrescriptionDetails WHERE PrescriptionDetailID = %s", (prescription_detail_id,))
            if not cursor.fetchone():
                 return False, f"❌ Prescription Detail ID {prescription_detail_id} not found."

            # Proceed with deletion
            cursor.execute("DELETE FROM PrescriptionDetails WHERE PrescriptionDetailID = %s", (prescription_detail_id,))
            affected_rows = cursor.rowcount # Check if a row was actually deleted
            conn.commit()

            if affected_rows > 0:
                return True, f"✅ Prescription detail ID {prescription_detail_id} deleted successfully."
            else:
                 # This case should ideally not happen due to the check above, but included for robustness
                 return False, f"❌ Prescription Detail ID {prescription_detail_id} found but could not be deleted."

    except MySQLError as e:
        conn.rollback()
        print(f"DB error in delete_prescription_detail: {e}")
        return False, f"❌ Failed to delete prescription detail: Database error."
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error in delete_prescription_detail: {e}")
        return False, "❌ Failed to delete prescription detail: Unexpected error."

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
                FROM Prescription p
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
                INSERT INTO EmergencyContact (PatientID, ContactName, Relationship, PhoneNumber, Address)
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
            cursor.execute("SELECT ContactID FROM EmergencyContact WHERE ContactID = %s", (contact_id,))
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
                UPDATE EmergencyContact SET {', '.join(update_fields)}
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
                INSERT INTO Medicine (MedicineName, Unit, Quantity, MedicineCost)
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
def add_medicine_batch(conn, medicine_id, batch_number, quantity,
                       import_date, expiry_date, supplier_name, medicine_cost):
    """
    Call stored procedure to add a new medicine batch.
    Validates quantity and cost before calling the stored procedure.
    """
    try:
        # ✅ Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 0:
                return False, "❌ Quantity cannot be negative."
        except (ValueError, TypeError):
            return False, "❌ Quantity must be a valid integer."

        # ✅ Validate medicine cost
        try:
            medicine_cost = float(medicine_cost)
            if medicine_cost < 0:
                return False, "❌ Cost cannot be negative."
        except (ValueError, TypeError):
            return False, "❌ Cost must be a valid number."

        # ✅ Validate dates (optional but good practice)
        if not import_date or not expiry_date:
            return False, "❌ Import date and expiry date are required."

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
        return False, f"❌ Failed to add medicine batch: {str(e)}"

def update_medicine_batch(conn, batch_id, medicine_id=None, batch_number=None,
                          expiry_date=None, quantity=None, cost=None):
    """
    Update selected fields of a medicine batch.
    Only non-None values will be updated.
    """
    try:
        if not batch_id:
            return False, "❌ Batch ID is required."

        with conn.cursor() as cursor:
            # Kiểm tra batch có tồn tại không
            cursor.execute("SELECT 1 FROM MedicineBatch WHERE BatchID = %s", (batch_id,))
            if not cursor.fetchone():
                return False, "❌ Medicine batch not found."

            # Danh sách trường cần cập nhật
            fields = []
            values = []

            if medicine_id is not None:
                fields.append("MedicineID = %s")
                values.append(medicine_id)
            if batch_number is not None:
                fields.append("BatchNumber = %s")
                values.append(batch_number)
            if expiry_date is not None:
                fields.append("ExpiryDate = %s")
                values.append(expiry_date)
            if quantity is not None:
                try:
                    quantity = int(quantity)
                    if quantity < 0:
                        return False, "❌ Quantity must be non-negative."
                    fields.append("Quantity = %s")
                    values.append(quantity)
                except ValueError:
                    return False, "❌ Quantity must be an integer."
            if cost is not None:
                try:
                    cost = float(cost)
                    if cost < 0:
                        return False, "❌ Cost must be non-negative."
                    fields.append("MedicineCost = %s")
                    values.append(cost)
                except ValueError:
                    return False, "❌ Cost must be a number."

            if not fields:
                return False, "❌ No valid fields provided for update."

            update_query = f"""
                UPDATE MedicineBatch
                SET {', '.join(fields)}
                WHERE BatchID = %s
            """
            values.append(batch_id)

            cursor.execute(update_query, tuple(values))
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
                SET Quantity = Quantity + %s 
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
            if not item_name or not quantity or not unit:
                return False, "Item name, unit and quantity are required."
            
            cursor.execute("""
            INSERT INTO Inventory (itemName, quantity, unit, status)
            VALUES (%s, %s, %s, %s)
            """, (item_name, quantity, unit, status))
            conn.commit()
            return True, "Inventory item added successfully."
    except MySQLError as e:
        conn.rollback()
        return False, f"Failed to add item: {e}"

# def update_inventory_item(conn, inventory_id, item_name, quantity, unit, status):
#     try:
#         if not inventory_id:
#             return False, "Please enter Inventory ID"
#         if not any([item_name, quantity, unit, status]):
#             return False, "At least one field except Inventory ID is required."
#         with conn.cursor() as cursor:
#             cursor.execute("""
#                 UPDATE Inventory
#                 SET itemName=%s, quantity=%s, unit=%s, status=%s
#                 WHERE inventoryID = %s
#             """, (item_name, quantity, unit, status, inventory_id))
#             conn.commit()
#             return True, "✅ Inventory item updated."
#     except MySQLError as e:
#         conn.rollback()
#         return False, f"❌ Update failed: {e}"

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
            cursor.execute("SELECT Quantity FROM Inventory WHERE InventoryID = %s", (inventoryID,))
            item = cursor.fetchone()
            if not item:
                return False, "❌ Inventory item not found."

            # Check if adjustment leads to negative stock if quantity is negative
            current_quantity = item['Quantity']
            if current_quantity + quantity < 0:
                 return False, f"❌ Adjustment leads to negative stock (Current: {current_quantity}, Adjust: {quantity})."


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
        print(f"DB error in adjust_inventory: {e}")
        return False, f"❌ Failed to adjust inventory item quantity: {e}"

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
    """Create an invoice for a patient with current date and update invoiceID in PatientServices."""
    try:
        with conn.cursor() as cursor:
            # Kiểm tra bệnh nhân tồn tại
            cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
            if not cursor.fetchone():
                return False, "❌ Patient not found."

            invoice_date = datetime.now().strftime("%Y-%m-%d")

            # Tạo hóa đơn
            cursor.execute("""
                INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount)
                VALUES (%s, %s, %s)
            """, (patient_id, invoice_date, total_amount))
            
            # Lấy invoiceID vừa tạo
            invoice_id = cursor.lastrowid

            # Cập nhật invoiceID vào PatientServices
            cursor.execute("""
                UPDATE PatientServices
                SET invoiceID = %s
                WHERE PatientID = %s
            """, (invoice_id, patient_id))

            conn.commit()
            return True, f"✅ Invoice created successfully with InvoiceID = {invoice_id}."
    except MySQLError as e:
        conn.rollback()
        return False, f"❌ Failed to create invoice: {e}"
   
def view_invoices(conn, patient_id=None):
    """View invoices (all or for specific patient)"""
    try:
        with conn.cursor() as cursor:  
            if patient_id:
                cursor.execute("""
                    SELECT InvoiceID, PatientID, InvoiceDate, TotalAmount,PaymentStatus
                    FROM Invoices WHERE PatientID = %s
                    ORDER BY InvoiceDate DESC
                """, (patient_id,))
            else:
                cursor.execute("""
                    SELECT InvoiceID, PatientID, InvoiceDate, TotalAmount,PaymentStatus
                    FROM Invoices
                    ORDER BY InvoiceDate DESC
                """)
            
            invoices = cursor.fetchall()  
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

def get_statistical_report_data(conn):
    """Fetch statistical data from the hospital database"""
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Tổng số bệnh nhân
            cursor.execute("SELECT COUNT(*) AS total FROM Patients")
            total_patients = cursor.fetchone()['total']

            # Tổng số bác sĩ
            cursor.execute("SELECT COUNT(*) AS total FROM Doctors")
            total_doctors = cursor.fetchone()['total']

            # Tổng số cuộc hẹn
            cursor.execute("SELECT COUNT(*) AS total FROM Appointments")
            total_appointments = cursor.fetchone()['total']

            # Tổng số toa thuốc
            cursor.execute("SELECT COUNT(*) AS total FROM Prescription")
            total_prescriptions = cursor.fetchone()['total']

            # Tổng số phòng bệnh
            cursor.execute("SELECT COUNT(*) AS total FROM Rooms")
            total_rooms = cursor.fetchone()['total']

            # Tổng số dịch vụ
            cursor.execute("SELECT COUNT(*) AS total FROM Services")
            total_services = cursor.fetchone()['total']

            # Phân bố bệnh nhân theo giới tính
            cursor.execute("""
                SELECT Gender, COUNT(*) AS count
                FROM Patients
                GROUP BY Gender
            """)
            gender_data = cursor.fetchall()
            patient_gender_dist = {row['Gender']: row['count'] for row in gender_data}

            # Số cuộc hẹn theo phòng ban
            cursor.execute("""
                SELECT d.DepartmentName, COUNT(*) AS appointment_count
                FROM Appointments a
                JOIN Doctors doc ON a.DoctorID = doc.DoctorID
                JOIN Departments d ON doc.DepartmentID = d.DepartmentID
                GROUP BY d.DepartmentName
                ORDER BY appointment_count DESC
            """)
            appointments_per_department = cursor.fetchall()

            return True, {
                'total_patients': total_patients,
                'total_doctors': total_doctors,
                'total_appointments': total_appointments,
                'total_prescriptions': total_prescriptions,
                'total_rooms': total_rooms,
                'total_services': total_services,
                'patient_gender_dist': patient_gender_dist,
                'appointments_per_department': appointments_per_department
            }

    except Exception as e:
        return False, f"❌ Failed to fetch statistical data: {e}"


def save_calculated_invoice(conn, patient_id, room_cost, med_cost, svc_cost, total_amount, notes, is_bhyt_applied):
    """Lưu hóa đơn đã được tính toán từ GUI vào cơ sở dữ liệu."""
    try:
        # Validate inputs
        p_id_int = int(patient_id)
        med_cost_f = float(med_cost)
        room_cost_f = float(room_cost)
        svc_cost_f = float(svc_cost)
        total_amount_f = float(total_amount)

        # Basic sanity check
        if total_amount_f < 0:
            print("Warning: Final amount is negative. Saving as 0.00")
            total_amount_f = 0.0

    except ValueError:
        return False, "Invalid numeric data for invoice amounts.", None

    try:
        with conn.cursor() as cursor:
            invoice_date = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO Invoices (
                    PatientID, InvoiceDate,
                    RoomCost, MedicineCost, ServiceCost, /* Original costs */
                    TotalAmount, /* Final amount due */
                    AmountPaid,
                    PaymentStatus, IsBHYTApplied, Notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p_id_int, invoice_date,
                room_cost_f, med_cost_f, svc_cost_f, total_amount_f,
                0, 'Unpaid', # Default status
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

from fpdf import FPDF
import os

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "INTERNATIONAL GENERAL HOSPITAL", 0, 0, "L")
        self.cell(0, 7, f"Patient ID: {self.patient_id}", 0, 1, "R")

        self.set_font("DejaVu", "", 11)
        self.cell(0, 7, "Department: Reception", 0, 0, "L")
        self.ln(5)
        self.set_font("DejaVu", "B", 16)
        self.cell(0, 10, "HOSPITAL INVOICE", 0, 1, "C")
        self.ln(2)

def generate_invoice_pdf(conn, invoice_id, output_path):
    try:
        # Register DejaVu font
        font_path='C:\\Users\\emily\\Downloads\\sql_final\\DejaVuSans.ttf'
        if not os.path.exists(font_path):
            return False, "DejaVu font not found. Please ensure DejaVuSans.ttf is available."
        
        pdf = InvoicePDF()
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        pdf.add_font("DejaVu", "I", font_path, uni=True)
        pdf.set_auto_page_break(auto=True, margin=15)

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.*, p.PatientName, p.Gender, p.DateOfBirth, p.PhoneNumber, p.Address
                FROM Invoices i
                JOIN Patients p ON i.PatientID = p.PatientID
                WHERE i.InvoiceID = %s
            """, (invoice_id,))
            invoice = cursor.fetchone()

        if not invoice:
            return False, "Invoice not found."

        pdf.patient_id = invoice["PatientID"]
        pdf.add_page()

        # I. Patient Information
        pdf.set_font("DejaVu", "B", 13)
        pdf.cell(0, 10, "I. Patient Information", 0, 1)
        pdf.set_font("DejaVu", "", 11)
        pdf.cell(0, 8, f"Full Name: {invoice['PatientName']}", 0, 1)
        pdf.cell(0, 8, f"Age: {calc_age(invoice['DateOfBirth'])}", 0, 1)
        pdf.cell(0, 8, f"Gender: {invoice['Gender']}", 0, 1)
        pdf.cell(0, 8, f"Address: {invoice['Address']}", 0, 1)
        pdf.cell(0, 8, f"Phone Number: {invoice['PhoneNumber']}", 0, 1)
        pdf.ln(5)

        # II. Cost Table
        pdf.set_font("DejaVu", "B", 13)
        pdf.cell(0, 10, "II. Medical Service Charges", 0, 1)
        # Truy vấn dịch vụ gắn với hóa đơn
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.Notes FROM Invoices i WHERE i.InvoiceID = %s
            """, (invoice_id,))
            result = cursor.fetchone()  # fetchone vì chỉ lấy 1 row
        invoice_note = result['Notes'] if result and result['Notes'] else 'No note available'

        pdf.set_font("DejaVu", "", 11)
        for line in invoice_note.strip().split('\n'):
            line_width = pdf.get_string_width(line)
            page_width = pdf.w - 2 * pdf.l_margin
            x_center = pdf.l_margin + (page_width - line_width) / 2
            pdf.set_x(x_center)
            pdf.cell(line_width, 8, line, ln=True)


        # Signature Section
        pdf.set_font("DejaVu", "", 11)

        # Date aligned to right
        date_text = f"Hanoi, {invoice['InvoiceDate'].strftime('%B %d, %Y')}"
        date_text_width = pdf.get_string_width(date_text)
        page_width = pdf.w - 2 * pdf.l_margin
        x_align = pdf.l_margin + page_width - date_text_width

        pdf.set_x(x_align)
        pdf.cell(date_text_width, 5, date_text, 0, 1, "C")
        pdf.ln()

        # Signature labels aligned left and right
        pdf.set_font("DejaVu", "B", 11)
        signature_width = page_width / 2

        pdf.cell(signature_width, 0, "Patient's Confirmation", 0, 0, "L")
        pdf.cell(signature_width, 0, "Cashier's Confirmation", 0, 1, "R")
        pdf.ln(30)

        # Italic note centered
        pdf.set_font("DejaVu", "I", 9)
        pdf.multi_cell(0, 8, 
            "Note: This receipt is only valid for issuing the invoice on the same day. "
            "The hospital will not resolve any issues after the due date.", 0
        )

        pdf.output(output_path)
        return True, f"Invoice PDF generated at {output_path}"

    except Exception as e:
        return False, f"Error generating invoice PDF: {e}"
    
# generate_prescription
from fpdf import FPDF

def calc_age(dob):
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def generate_prescription_pdf(conn, prescription_id, output_path):
    """Tạo PDF đơn thuốc hỗ trợ Unicode"""
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin đơn thuốc
            cursor.execute("""
                SELECT p.*, doc.DoctorName, pat.*
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
            pdf.add_font('DejaVu', '', 'C:\\Users\\emily\\Downloads\\sql_final\\DejaVuSans.ttf', uni=True)
            pdf.add_font('DejaVu', 'B', 'C:\\Users\\emily\\Downloads\\sql_final\\DejaVuSans-Bold.ttf', uni=True)
            pdf.set_font("DejaVu", "B", 16)

            # Tên bệnh viện, mã điều trị, mã bệnh nhân
            pdf.set_font("DejaVu", "B", 14)
            pdf.cell(0, 10, "INTERNATIONAL GENERAL HOSPITAL", 0, 1, "C")
            pdf.set_font("DejaVu", "", 11)
            pdf.cell(0, 7, f"Treatment Code: {prescription['PrescriptionID']}    Patient ID: {prescription['PatientID']}", 0, 1, "C")
            pdf.ln(5)

            # Tiêu đề lớn PRESCRIPTION
            pdf.set_font("DejaVu", "B", 22)
            pdf.cell(0, 15, "PRESCRIPTION", 0, 1, "C")
            pdf.ln(3)

            # Thông tin bệnh nhân
            age = calc_age(prescription['DateOfBirth'])
            gender = "Male" if prescription['Gender'] == "M" else "Female"
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(0, 10, f"Full name: {prescription['PatientName']}         Age: {age}         Gender: {gender}", 0, 1)
            pdf.set_font("DejaVu", "B", 11)
            pdf.cell(0, 7, f"Address: {prescription['Address']}", 0, 1)
            pdf.cell(0, 7, f"Diagnosis: {prescription.get('Diagnosis') or '-'}", 0, 1)
            pdf.ln(7)

            # Danh sách thuốc
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(0, 10, "Medications:", 0, 1)
            pdf.ln(1)

            # Tiêu đề bảng
            pdf.set_fill_color(200, 220, 255)
            add_col_widths = [50, 25, 90, 25]
            headers = ["Medicine", "Dosage", "Frequency", "Duration"]
            for i, header in enumerate(headers):
                pdf.cell(add_col_widths[i], 10, header, 1, 0, "C", 1)
            pdf.ln()

            pdf.set_font("DejaVu", "", 11)
            line_height = 8
            col_widths = {
                "Medicine": 50,
                "Dosage": 25,
                "Frequency": 90,
                "Duration": 25
            }
            for med in details:
                cell_texts = {
                    "Medicine": med.get("MedicineName") or "-",
                    "Dosage": med.get("Dosage") or "-",
                    "Frequency": med.get("Frequency") or "-",
                    "Duration": med.get("Duration") or "-"
                }


                # Tính số dòng thực sự cần dùng cho mỗi ô
                line_counts = []
                for key, col_width in col_widths.items():
                    text = cell_texts[key]
                    est_chars_per_line = col_width / 2.5
                    est_lines = int(len(text) / est_chars_per_line) + 1
                    line_counts.append(est_lines)

                row_height = max(line_counts) * line_height

                # Ghi nhớ vị trí đầu hàng
                x_start = pdf.get_x()
                y_start = pdf.get_y()

                # In từng ô
                x = x_start
                for key in col_widths:
                    text = cell_texts[key]
                    col_width = col_widths[key]

                    # Ước tính số dòng và chiều cao text trong ô này
                    est_chars_per_line = col_width / 2.5
                    num_lines = int(len(text) / est_chars_per_line) + 1
                    text_height = num_lines * line_height

                    # Tính offset để căn giữa theo chiều cao (vertical center)
                    y_offset = (row_height - text_height) / 2

                    # Vẽ khung ô
                    pdf.rect(x, y_start, col_width, row_height)

                    # Di chuyển con trỏ vào giữa ô (theo chiều dọc)
                    pdf.set_xy(x, y_start + y_offset)
                    pdf.multi_cell(col_width, line_height, text, border=0, align="C")

                    # Di chuyển sang cột tiếp theo
                    x += col_width

                # Xuống hàng mới
                pdf.set_y(y_start + row_height)
            
            pdf.ln(5)
            # Lời dặn của bác sĩ
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(0, 10, "Doctor's instructions:", 0, 1)
            pdf.set_font("DejaVu", "", 11)
            pdf.multi_cell(0, 7, prescription.get('Note', "-"))
            pdf.ln(10)

            # Địa điểm, ngày tháng, bác sĩ và ký tên
            pdf.set_font("DejaVu", "", 11)
            date_text = f"Hanoi, {prescription['PrescriptionDate'].strftime('%B %d, %Y')}"
            date_text_width = pdf.get_string_width(date_text)
            page_width = pdf.w - 2 * pdf.l_margin
            x_align = pdf.l_margin + page_width - date_text_width

            pdf.set_x(x_align)
            pdf.cell(date_text_width, 7, date_text, 0, 1,"C")

            pdf.ln()
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_x(x_align)
            pdf.cell(date_text_width, 7, "Doctor's Signature", 0, 1, "C")

            pdf.ln(15)
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_x(x_align)
            pdf.cell(date_text_width, 7, prescription['DoctorName'], 0, 1, "C")

            # # Trước khi thêm ghi chú cuối
            # if pdf.get_y() > 250:
            #     pdf.add_page()

            # # Nếu vừa add_page(), con trỏ ở đầu, ta nên tạo khoảng cách đẩy nó xuống gần cuối (nếu muốn footer cuối trang)
            # if pdf.get_y() < 200:  # Giả sử vừa add page
            #     pdf.set_y(250)  # Đặt footer ở vị trí cố định gần đáy

            # # Footer notes
            # pdf.set_font("DejaVu", "", 9)
            # pdf.ln(5)
            # pdf.multi_cell(0, 5, "- Follow the instructions carefully. If any unusual symptoms occur, please return to the hospital or call the phone number listed above (7 AM - 9 PM).")
            # pdf.multi_cell(0, 5, "- Bring this prescription with you if you come back for a follow-up.")
            # pdf.multi_cell(0, 5, "- Name of the child's father/mother or guardian:")
            
            pdf.output(output_path)
            return True, f"PDF đã được tạo tại {output_path}"

    except Exception as e:
        return False, f"Lỗi khi tạo PDF: {e}"
def get_financial_report_data(conn, start_date=None, end_date=None):
    """
    Get comprehensive financial report data including:
    - Total revenue by service type
    - Outstanding payments
    - Insurance claims
    - Daily/weekly/monthly trends
    
    Args:
        conn: Database connection
        start_date (str): YYYY-MM-DD format (optional)
        end_date (str): YYYY-MM-DD format (optional)
    
    Returns:
        tuple: (success: bool, data: dict/str)
    """
    try:
        with conn.cursor() as cursor:
            # Base query with optional date filtering
            date_condition = ""
            params = []
            if start_date and end_date:
                date_condition = "WHERE i.InvoiceDate BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            elif start_date:
                date_condition = "WHERE i.InvoiceDate >= %s"
                params.append(start_date)
            elif end_date:
                date_condition = "WHERE i.InvoiceDate <= %s"
                params.append(end_date)
            
            # 1. Overall financial summary
            cursor.execute(f"""
                SELECT 
                    SUM(i.TotalAmount) as total_revenue,
                    SUM(CASE WHEN i.PaymentStatus = 'Paid' THEN i.TotalAmount ELSE 0 END) as paid_amount,
                    SUM(CASE WHEN i.PaymentStatus = 'Pending' THEN i.TotalAmount ELSE 0 END) as pending_amount,
                    COUNT(DISTINCT i.InvoiceID) as invoice_count,
                    AVG(i.TotalAmount) as avg_invoice
                FROM Invoices i
                {date_condition}
            """, params)
            summary = cursor.fetchone()
            
            # 2. Revenue by service type
            cursor.execute(f"""
                SELECT 
                    s.ServiceName,
                    COUNT(ps.ServiceID) as service_count,
                    SUM(ps.CostAtTime * ps.Quantity) as total_revenue
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                JOIN Invoices i ON ps.InvoiceID = i.InvoiceID
                {date_condition}
                GROUP BY s.ServiceName
                ORDER BY total_revenue DESC
            """, params)
            service_revenue = cursor.fetchall()
            
            # 3. Insurance claims summary (nếu bảng InsuranceClaims tồn tại)
            insurance_data = None
            try:
                cursor.execute(f"""
                    SELECT 
                        COUNT(DISTINCT i.InsuranceID) as insurance_count,
                        SUM(i.CoveredAmount) as total_covered,
                        SUM(i.PatientResponsibility) as total_patient_responsibility
                    FROM InsuranceClaims i
                    JOIN Invoices inv ON i.InvoiceID = inv.InvoiceID
                    {date_condition}
                """, params)
                insurance_data = cursor.fetchone()
            except:
                insurance_data = {
                    'insurance_count': 0,
                    'total_covered': 0,
                    'total_patient_responsibility': 0
                }
            
            # 4. Daily revenue trend
            cursor.execute(f"""
                SELECT 
                    DATE(i.InvoiceDate) as day,
                    SUM(i.TotalAmount) as daily_revenue
                FROM Invoices i
                {date_condition}
                GROUP BY DATE(i.InvoiceDate)
                ORDER BY day
            """, params)
            daily_trend = cursor.fetchall()
            
            return True, {
                'summary': summary,
                'service_revenue': service_revenue,
                'insurance_data': insurance_data,
                'daily_trend': daily_trend,
                'date_range': {
                    'start': start_date or 'Earliest',
                    'end': end_date or 'Latest'
                }
            }
            
    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_room_utilization_stats(conn):
    """
    Get detailed room utilization statistics including:
    - Occupancy rates by department
    - Average stay duration
    - Revenue by room type
    
    Returns:
        tuple: (success: bool, data: dict/str)
    """
    try:
        with conn.cursor() as cursor:
            # 1. Overall room statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_rooms,
                    SUM(CASE WHEN Status = 'Occupied' THEN 1 ELSE 0 END) as occupied_rooms,
                    SUM(CASE WHEN Status = 'Available' THEN 1 ELSE 0 END) as available_rooms,
                    SUM(CASE WHEN Status = 'Maintenance' THEN 1 ELSE 0 END) as maintenance_rooms
                FROM Rooms
            """)
            room_stats = cursor.fetchone()
            
            # 2. Occupancy by department
            cursor.execute("""
                SELECT 
                    d.DepartmentName,
                    COUNT(r.RoomID) as total_rooms,
                    SUM(CASE WHEN r.Status = 'Occupied' THEN 1 ELSE 0 END) as occupied,
                    ROUND(SUM(CASE WHEN r.Status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(r.RoomID) * 100, 1) as occupancy_rate
                FROM Rooms r
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                GROUP BY d.DepartmentName
                ORDER BY occupancy_rate DESC
            """)
            dept_stats = cursor.fetchall()
            
            # 3. Revenue by room type
            cursor.execute("""
    SELECT 
        rt.TypeName,
        COUNT(r.RoomID)        AS room_count,
        rt.BaseCost * COUNT(r.RoomID) AS total_revenue
    FROM RoomTypes rt
    JOIN Rooms r
      ON rt.RoomTypeID = r.RoomTypeID
    GROUP BY rt.TypeName, rt.BaseCost
    ORDER BY total_revenue DESC
""")
            revenue_stats = cursor.fetchall()
            
            # 4. Average length of stay
            cursor.execute("""
                SELECT 
                    AVG(DATEDIFF(COALESCE(ProcessedDate, CURDATE()), OrderDate)) as avg_stay_days
                FROM Admissionorders
                WHERE OrderDate > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            """)
            stay_stats = cursor.fetchone()
            
            return True, {
                'overall': room_stats,
                'by_department': dept_stats,
                'revenue_by_type': revenue_stats,
                'stay_stats': stay_stats
            }
            
    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_hospital_statistics(conn):
    """
    Get comprehensive hospital statistics including:
    - Patient demographics
    - Doctor productivity
    - Service utilization
    - Appointment metrics
    
    Returns:
        tuple: (success: bool, data: dict/str)
    """
    try:
        with conn.cursor() as cursor:
            # 1. Patient demographics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_patients,
                    SUM(CASE WHEN Gender = 'M' THEN 1 ELSE 0 END) as male_patients,
                    SUM(CASE WHEN Gender = 'F' THEN 1 ELSE 0 END) as female_patients,
                    SUM(CASE WHEN Gender = 'O' THEN 1 ELSE 0 END) as other_patients,
                    AVG(YEAR(CURDATE()) - YEAR(DateOfBirth)) as avg_age
                FROM Patients
                WHERE Status = 'Active'
            """)
            patient_stats = cursor.fetchone()
            
            # 2. Doctor productivity
            cursor.execute("""
    SELECT 
        d.DoctorName,
        COUNT(DISTINCT a.AppointmentID)       AS appointment_count,
        COUNT(DISTINCT p.PrescriptionID)      AS prescription_count,
        COUNT(DISTINCT ad.AdmissionOrderID)   AS admission_count
    FROM Doctors d
    LEFT JOIN Appointments a 
      ON d.DoctorID = a.DoctorID
         AND a.AppointmentDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()
    LEFT JOIN Prescription p 
      ON d.DoctorID = p.DoctorID
         AND p.PrescriptionDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()
    LEFT JOIN AdmissionOrders ad 
      ON d.DoctorID = ad.DoctorID
         AND ad.OrderDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()
    GROUP BY d.DoctorName
    ORDER BY appointment_count DESC
    LIMIT 10
""")
            doctor_stats = cursor.fetchall()
            
            # 3. Service utilization
            cursor.execute("""
                SELECT 
    s.ServiceName,
    COUNT(ps.ServiceID)                   AS service_count,
    SUM(ps.CostAtTime * ps.Quantity)      AS total_revenue
FROM Services s
LEFT JOIN PatientServices ps 
  ON s.ServiceID = ps.ServiceID
WHERE ps.ServiceDate 
      BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) 
          AND CURDATE()
GROUP BY s.ServiceName
ORDER BY service_count DESC
LIMIT 10; """)
            service_stats = cursor.fetchall()
            
            # 4. Appointment metrics
            cursor.execute("""
                SELECT 
  COUNT(*) AS total_appointments,
  SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS completed,
  SUM(CASE WHEN Status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
  SUM(CASE WHEN Status = 'Scheduled' THEN 1 ELSE 0 END) AS scheduled,
  AVG(
    TIMESTAMPDIFF(
      MINUTE,
      CONCAT(AppointmentDate, ' ', AppointmentTime),
      NOW()
    )
  ) AS avg_duration_minutes
FROM Appointments
WHERE AppointmentDate 
      BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE(); """)
            appointment_stats = cursor.fetchone()
            
            return True, {
                'patient_demographics': patient_stats,
                'doctor_productivity': doctor_stats,
                'service_utilization': service_stats,
                'appointment_metrics': appointment_stats
            }
            
    except Exception as e:
        return False, f"Database error: {str(e)}"

def get_departments_list(conn):
    """Get list of all departments for dropdowns"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DepartmentID, DepartmentName 
                FROM Departments 
                ORDER BY DepartmentName
            """)
            return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_all_rooms_with_status(conn):
    """Get complete room list with status information"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    r.RoomID, 
                    r.RoomNumber, 
                    rt.TypeName,
                    d.DepartmentName,
                    r.Status,
                    rt.BaseCost
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                ORDER BY d.DepartmentName, r.RoomNumber
            """)
            return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {str(e)}"
def generate_financial_report(conn, start_date=None, end_date=None):
    """
    Generate a more detailed financial report including revenue breakdown.

    Args:
        conn: Database connection object.
        start_date (str, optional): Start date 'YYYY-MM-DD'. Defaults to None (no start limit).
        end_date (str, optional): End date 'YYYY-MM-DD'. Defaults to None (no end limit).

    Returns:
        tuple: (bool, dict/str):
               - True and a dictionary containing report data if successful.
                 Keys: 'title', 'period', 'total_revenue', 'room_revenue',
                       'medicine_revenue', 'service_revenue', 'monthly_summary' (optional)
               - False and an error message string if failed.
    """
    report_data = {
        'title': "Financial Summary Report",
        'period': "All Time",
        'total_revenue': 0.0,
        'room_revenue': 0.0,
        'medicine_revenue': 0.0,
        'service_revenue': 0.0,
        'monthly_summary': [] # Optional: For charting later
    }
    try:
        with conn.cursor() as cursor:
            # Base query to sum different cost types from *paid* invoices
            # Assuming 'Paid' is the status for completed payments
            query = """
                SELECT
                    SUM(RoomCost) as TotalRoomRevenue,
                    SUM(MedicineCost) as TotalMedicineRevenue,
                    SUM(ServiceCost) as TotalServiceRevenue,
                    SUM(TotalAmount) as GrandTotalRevenue -- This is the final amount paid
                FROM Invoices
                WHERE PaymentStatus = 'Paid'
            """
            params = []
            period_desc = []
            if start_date:
                query += " AND InvoiceDate >= %s"
                params.append(start_date)
                period_desc.append(f"From {start_date}")
            if end_date:
                query += " AND InvoiceDate <= %s"
                params.append(end_date)
                period_desc.append(f"To {end_date}")

            if period_desc:
                 report_data['period'] = " ".join(period_desc)

            cursor.execute(query, tuple(params))
            summary = cursor.fetchone()

            if summary:
                report_data['room_revenue'] = float(summary.get('TotalRoomRevenue', 0.0) or 0.0)
                report_data['medicine_revenue'] = float(summary.get('TotalMedicineRevenue', 0.0) or 0.0)
                report_data['service_revenue'] = float(summary.get('TotalServiceRevenue', 0.0) or 0.0)
                report_data['total_revenue'] = float(summary.get('GrandTotalRevenue', 0.0) or 0.0)
                # Note: GrandTotalRevenue might differ from sum of components if discounts exist but aren't stored separately

            # --- Optional: Add Monthly Summary for charting ---
            query_monthly = """
                 SELECT
                     DATE_FORMAT(InvoiceDate, '%Y-%m') as MonthYear,
                     SUM(TotalAmount) as MonthlyTotal
                 FROM Invoices
                 WHERE PaymentStatus = 'Paid'
            """
            params_monthly = []
            if start_date:
                 query_monthly += " AND InvoiceDate >= %s"
                 params_monthly.append(start_date)
            if end_date:
                 query_monthly += " AND InvoiceDate <= %s"
                 params_monthly.append(end_date)

            query_monthly += " GROUP BY MonthYear ORDER BY MonthYear ASC"
            cursor.execute(query_monthly, tuple(params_monthly))
            report_data['monthly_summary'] = cursor.fetchall()
            # --- End Optional Monthly Summary ---

            return True, report_data

    except MySQLError as e:
        print(f"DB Error generating financial report: {e}")
        return False, f"Database error generating financial report: {e}"
    except Exception as e:
        print(f"Unexpected error generating financial report: {e}")
        return False, f"An unexpected error occurred: {e}"

# --- New Room Report ---
def generate_room_report(conn, report_type='status'):
    """
    Generates reports related to rooms.

    Args:
        conn: Database connection object.
        report_type (str): 'status' for current occupancy/status counts,
                           'revenue' for total invoiced room revenue (simplified).

    Returns:
        tuple: (bool, dict/str):
               - True and dictionary with report data/title.
               - False and error message.
    """
    try:
        with conn.cursor() as cursor:
            if report_type == 'status':
                # Get current room status counts by type and department
                cursor.execute("""
                    SELECT
                        d.DepartmentName,
                        rt.TypeName,
                        r.Status,
                        COUNT(r.RoomID) as Count
                    FROM Rooms r
                    JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                    JOIN Departments d ON r.DepartmentID = d.DepartmentID
                    GROUP BY d.DepartmentName, rt.TypeName, r.Status
                    ORDER BY d.DepartmentName, rt.TypeName, r.Status;
                """)
                status_data = cursor.fetchall()
                return True, {'title': "Current Room Status Report", 'data': status_data, 'type': 'status'}

            elif report_type == 'revenue':
                 # Get total invoiced room revenue (based on Invoices table)
                 # Note: This assumes RoomCost in Invoices reflects actual billed amount.
                 cursor.execute("""
                    SELECT
                        DATE_FORMAT(InvoiceDate, '%Y-%m') as MonthYear,
                        SUM(RoomCost) as TotalRoomRevenue
                    FROM Invoices
                    WHERE RoomCost > 0 AND PaymentStatus = 'Paid' -- Only count paid invoices with room cost
                    GROUP BY MonthYear
                    ORDER BY MonthYear ASC;
                 """)
                 revenue_data = cursor.fetchall()
                 return True, {'title': "Monthly Invoiced Room Revenue", 'data': revenue_data, 'type': 'revenue'}
            else:
                return False, "Invalid room report type specified."

    except MySQLError as e:
        print(f"DB Error generating room report: {e}")
        return False, f"Database error generating room report: {e}"
    except Exception as e:
        print(f"Unexpected error generating room report: {e}")
        return False, f"An unexpected error occurred: {e}"


# --- Enhanced Statistics Report ---
def generate_statistics_report(conn, start_date=None, end_date=None):
    """
    Generate various operational statistics within a date range.

    Args:
        conn: Database connection object.
        start_date (str, optional): Start date 'YYYY-MM-DD'. Defaults to None.
        end_date (str, optional): End date 'YYYY-MM-DD'. Defaults to None.

    Returns:
        tuple: (bool, dict/str):
               - True and a dictionary containing different stats.
               - False and an error message.
    """
    stats = {
        'title': "Hospital Statistics Report",
        'period': "All Time",
        'patient_registrations': [],
        'appointment_summary': {},
        'top_services': [],
        'patient_demographics': {}
    }
    period_desc = []
    if start_date: period_desc.append(f"From {start_date}")
    if end_date: period_desc.append(f"To {end_date}")
    if period_desc: stats['period'] = " ".join(period_desc)

    try:
        with conn.cursor() as cursor:

            # 1. Patient Registrations (Example: Using created_at if Patients table lacks RegistrationDate)
            # Modify table/column names if your schema differs
            query_patients = """
                SELECT COUNT(*) as TotalPatients, DATE_FORMAT(created_at, '%Y-%m') as MonthYear
                FROM Patients -- Or 'users' if registration is tied to user creation
                WHERE 1=1
            """
            params_patients = []
            if start_date:
                query_patients += " AND DATE(created_at) >= %s"
                params_patients.append(start_date)
            if end_date:
                query_patients += " AND DATE(created_at) <= %s"
                params_patients.append(end_date)
            query_patients += " GROUP BY MonthYear ORDER BY MonthYear ASC"
            cursor.execute(query_patients, tuple(params_patients))
            stats['patient_registrations'] = cursor.fetchall()

            # 2. Appointment Status Summary
            query_appts = """
                SELECT Status, COUNT(*) as Count
                FROM Appointments
                WHERE 1=1
            """
            params_appts = []
            if start_date:
                query_appts += " AND AppointmentDate >= %s"
                params_appts.append(start_date)
            if end_date:
                query_appts += " AND AppointmentDate <= %s"
                params_appts.append(end_date)
            query_appts += " GROUP BY Status ORDER BY Status"
            cursor.execute(query_appts, tuple(params_appts))
            stats['appointment_summary'] = {row['Status']: row['Count'] for row in cursor.fetchall()}

            # 3. Top Services Used (Based on PatientServices)
            query_services = """
                SELECT s.ServiceName, COUNT(ps.PatientServiceID) as UsageCount
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                WHERE 1=1
            """
            params_services = []
            if start_date:
                query_services += " AND DATE(ps.ServiceDate) >= %s"
                params_services.append(start_date)
            if end_date:
                query_services += " AND DATE(ps.ServiceDate) <= %s"
                params_services.append(end_date)
            query_services += " GROUP BY s.ServiceName ORDER BY UsageCount DESC LIMIT 10" # Top 10
            cursor.execute(query_services, tuple(params_services))
            stats['top_services'] = cursor.fetchall()

            # 4. Patient Demographics (Example: Gender Distribution)
            query_demo = """
                 SELECT Gender, COUNT(*) as Count
                 FROM Patients
                 WHERE Status = 'active' -- Count only active patients
                 GROUP BY Gender;
            """
            cursor.execute(query_demo)
            stats['patient_demographics'] = {row['Gender']: row['Count'] for row in cursor.fetchall()}

            return True, stats

    except MySQLError as e:
        print(f"DB Error generating statistics report: {e}")
        return False, f"Database error generating statistics report: {e}"
    except Exception as e:
        print(f"Unexpected error generating statistics report: {e}")
        return False, f"An unexpected error occurred: {e}"
    
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
    """Generate service report based on services used (PatientServices)."""
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT s.ServiceName, SUM(ps.Quantity) as TotalUsed, SUM(ps.CostAtTime) as TotalRevenue
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                WHERE 1=1
            """
            params = []
            if start_date and end_date:
                query += " AND DATE(ps.ServiceDate) BETWEEN %s AND %s"
                params.extend([start_date, end_date])

            query += """
                GROUP BY s.ServiceName
                ORDER BY TotalRevenue DESC
            """
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            return True, ("SERVICE USAGE REPORT", results) # Return tuple (Title, Data)
    except MySQLError as e:
        print(f"DB Error in get_service_report: {e}")
        return False, f"❌ Failed to generate service report: {e}" # Return tuple (Status, Message)
    except Exception as e:
        print(f"Unexpected error in get_service_report: {e}")
        return False, f"❌ Unexpected error generating service report." # Return tuple (Status, Message)
    
# Reporting Functions
def generate_financial_report(conn, start_date=None, end_date=None):
    """
    Generate a more detailed financial report including revenue breakdown.

    Args:
        conn: Database connection object.
        start_date (str, optional): Start date 'YYYY-MM-DD'. Defaults to None (no start limit).
        end_date (str, optional): End date 'YYYY-MM-DD'. Defaults to None (no end limit).

    Returns:
        tuple: (bool, dict/str):
               - True and a dictionary containing report data if successful.
                 Keys: 'title', 'period', 'total_revenue', 'room_revenue',
                       'medicine_revenue', 'service_revenue', 'monthly_summary' (optional)
               - False and an error message string if failed.
    """
    report_data = {
        'title': "Financial Summary Report",
        'period': "All Time",
        'total_revenue': 0.0,
        'room_revenue': 0.0,
        'medicine_revenue': 0.0,
        'service_revenue': 0.0,
        'monthly_summary': [] # Optional: For charting later
    }
    try:
        with conn.cursor() as cursor:
            # Base query to sum different cost types from *paid* invoices
            # Assuming 'Paid' is the status for completed payments
            query = """
                SELECT
                    SUM(RoomCost) as TotalRoomRevenue,
                    SUM(MedicineCost) as TotalMedicineRevenue,
                    SUM(ServiceCost) as TotalServiceRevenue,
                    SUM(TotalAmount) as GrandTotalRevenue -- This is the final amount paid
                FROM Invoices
                WHERE PaymentStatus = 'Paid'
            """
            params = []
            period_desc = []
            if start_date:
                query += " AND InvoiceDate >= %s"
                params.append(start_date)
                period_desc.append(f"From {start_date}")
            if end_date:
                query += " AND InvoiceDate <= %s"
                params.append(end_date)
                period_desc.append(f"To {end_date}")

            if period_desc:
                 report_data['period'] = " ".join(period_desc)

            cursor.execute(query, tuple(params))
            summary = cursor.fetchone()

            if summary:
                report_data['room_revenue'] = float(summary.get('TotalRoomRevenue', 0.0) or 0.0)
                report_data['medicine_revenue'] = float(summary.get('TotalMedicineRevenue', 0.0) or 0.0)
                report_data['service_revenue'] = float(summary.get('TotalServiceRevenue', 0.0) or 0.0)
                report_data['total_revenue'] = float(summary.get('GrandTotalRevenue', 0.0) or 0.0)
                # Note: GrandTotalRevenue might differ from sum of components if discounts exist but aren't stored separately

            # --- Optional: Add Monthly Summary for charting ---
            query_monthly = """
                 SELECT
                     DATE_FORMAT(InvoiceDate, '%Y-%m') as MonthYear,
                     SUM(TotalAmount) as MonthlyTotal
                 FROM Invoices
                 WHERE PaymentStatus = 'Paid'
            """
            params_monthly = []
            if start_date:
                 query_monthly += " AND InvoiceDate >= %s"
                 params_monthly.append(start_date)
            if end_date:
                 query_monthly += " AND InvoiceDate <= %s"
                 params_monthly.append(end_date)

            query_monthly += " GROUP BY MonthYear ORDER BY MonthYear ASC"
            cursor.execute(query_monthly, tuple(params_monthly))
            report_data['monthly_summary'] = cursor.fetchall()
            # --- End Optional Monthly Summary ---

            return True, report_data

    except MySQLError as e:
        print(f"DB Error generating financial report: {e}")
        return False, f"Database error generating financial report: {e}"
    except Exception as e:
        print(f"Unexpected error generating financial report: {e}")
        return False, f"An unexpected error occurred: {e}"

def generate_room_report(conn, report_type='status'):
    """
    Generates reports related to rooms.

    Args:
        conn: Database connection object.
        report_type (str): 'status' for current occupancy/status counts,
                           'revenue' for total invoiced room revenue (simplified).

    Returns:
        tuple: (bool, dict/str):
               - True and dictionary with report data/title.
               - False and error message.
    """
    try:
        with conn.cursor() as cursor:
            if report_type == 'status':
                # Get current room status counts by type and department
                cursor.execute("""
                    SELECT
                        d.DepartmentName,
                        rt.TypeName,
                        r.Status,
                        COUNT(r.RoomID) as Count
                    FROM Rooms r
                    JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                    JOIN Departments d ON r.DepartmentID = d.DepartmentID
                    GROUP BY d.DepartmentName, rt.TypeName, r.Status
                    ORDER BY d.DepartmentName, rt.TypeName, r.Status;
                """)
                status_data = cursor.fetchall()
                return True, {'title': "Current Room Status Report", 'data': status_data, 'type': 'status'}

            elif report_type == 'revenue':
                 # Get total invoiced room revenue (based on Invoices table)
                 # Note: This assumes RoomCost in Invoices reflects actual billed amount.
                 cursor.execute("""
                    SELECT
                        DATE_FORMAT(InvoiceDate, '%Y-%m') as MonthYear,
                        SUM(RoomCost) as TotalRoomRevenue
                    FROM Invoices
                    WHERE RoomCost > 0 AND PaymentStatus = 'Paid' -- Only count paid invoices with room cost
                    GROUP BY MonthYear
                    ORDER BY MonthYear ASC;
                 """)
                 revenue_data = cursor.fetchall()
                 return True, {'title': "Monthly Invoiced Room Revenue", 'data': revenue_data, 'type': 'revenue'}
            else:
                return False, "Invalid room report type specified."

    except MySQLError as e:
        print(f"DB Error generating room report: {e}")
        return False, f"Database error generating room report: {e}"
    except Exception as e:
        print(f"Unexpected error generating room report: {e}")
        return False, f"An unexpected error occurred: {e}"

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
            username = input("Enter Username: ")
            password = input("Enter Password: ")
            confirm_password = input("Enter Confirm Password: ")
            role = input("Enter role: ")
            success, message = register_user(conn, username, password, confirm_password, role)
            print(message)
        elif choice == '2':
            username = input("Enter Username: ")
            success, message = delete_user(conn, username)
            print(message)
        elif choice == '3':
            name = input("Enter Doctor Name: ")
            dept_id = input("Enter Department ID: ")
            specialization = input("Enter Specialization: ")
            username = input("Enter Username: ")
            success, message = add_doctor(conn, name, dept_id, specialization, username)
            print(message)
        elif choice == '4':
            doctor_id = input("Enter Doctor ID: ")
            success, message = delete_doctor(conn, doctor_id)
            print(message)
        elif choice == '5':
            name = input("Enter Patient Name: ")
            dob = input("Enter Date of Birth (YYYY-MM-DD): ")
            gender = input("Enter Gender (M/F/O): ")
            address = input("Enter Address: ")
            phone = input("Enter Phone Number: ")
            success, message = add_patient(conn, name, dob, gender, address, phone)
            print(message)
        elif choice == '6':
            patient_id = input("Enter Patient ID: ")
            success, message = delete_patient(conn, patient_id)
            print(message)
        elif choice == '7':
            success, patients = view_patients(conn)
            if success:
                print("\n--- Patient List ---")
                for p in patients:
                    print(f"ID: {p['PatientID']}, Name: {p['PatientName']}, DOB: {p['DateOfBirth']}, Gender: {p['Gender']}, Address: {p['Address']}, Phone: {p['PhoneNumber']}")
            else:
                print(patients)
        elif choice == '8':
            patient_id = input("Enter Patient ID: ")
            doctor_id = input("Enter Doctor ID: ")
            appointment_date = input("Enter Appointment Date (YYYY-MM-DD): ")
            appointment_time = input("Enter Appointment Time (HH:MM): ")
            success, message = schedule_appointment(conn, patient_id, doctor_id, appointment_date, appointment_time)
            print(message)
        elif choice == '9':
            success, result = view_appointments(conn)
            if success:
                print(f"\n--- {result['title']} ---")
                for appt in result['data']:
                    print(appt)
            else:
                print(result)
        elif choice == '10':
            patient_id = input("Enter Patient ID: ")
            total_amount = input("Enter Total Amount: ")
            success, message = create_invoice(conn, patient_id, total_amount)
            print(message)
        elif choice == '11':
            success, invoices = view_invoices(conn)
            if success:
                print("\n--- Invoice List ---")
                for inv in invoices:
                    print(inv)
            else:
                print(invoices)
        elif choice == '12':
            success, departments = view_departments(conn)
            if success:
                print("\n--- Department List ---")
                for d in departments:
                    print(d)
            else:
                print(departments)
        elif choice == '13':
            success, report = generate_financial_report(conn)
            if success:
                print("\n--- Financial Report ---")
                for k, v in report.items():
                    print(f"{k}: {v}")
            else:
                print(report)
        elif choice == '14':
            old_pw = getpass.getpass("Enter current password: ")
            new_pw = getpass.getpass("Enter new password: ")
            success, message = change_password(conn, username, old_pw, new_pw)
            print(message)
        elif choice == '15':
            print("Logging out...")
            return
        else:
            print("❌ Invalid option")
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
    # Consider moving DB connection for initialization outside the main loop if needed only once
    try:
        initialize_admin()
    except Exception as init_e:
        print(f"❌ CRITICAL: Failed to initialize admin: {init_e}")
        # Decide if the application should exit if admin init fails
        # return

    while True:
        # Authentication moved inside the loop for retries
        print("\n--- LOGIN ---")
        input_username = input("Username: ")
        input_password = getpass.getpass("Password: ")

        # Authenticate user
        username, role, conn, role_id, error_message = authenticate_user(input_username, input_password)

        # Check for authentication errors
        if error_message:
            print(f"\n❌ Login Failed: {error_message}")
            # Optional: Add delay or attempt limit here
            continue # Go back to the start of the loop to retry login

        # Authentication successful
        print(f"\n🔑 Logged in as {username} (Role: {role}).")
        if role == 'doctor':
             print(f"   Doctor ID: {role_id}")


        active_connection = conn # Store the active connection

        try:
            # Launch appropriate menu based on role
            if role == 'admin':
                admin_menu(active_connection, username)
            elif role == 'doctor':
                 # Ensure doctor_id (role_id) is valid before calling menu
                 if role_id is not None:
                     doctor_menu(active_connection, role_id, username)
                 else:
                      # This case should be caught by authenticate_user, but double-check
                      print("❌ Error: Doctor logged in but DoctorID is missing. Logging out.")
            elif role == 'receptionist':
                receptionist_menu(active_connection, username)
            elif role == 'accountant':
                accountant_menu(active_connection, username)
            else:
                 print(f"❌ Role '{role}' does not have an associated menu.")

        except Exception as menu_e:
             print(f"\n❌ An error occurred during operation: {menu_e}")
        finally:
            if active_connection and active_connection.open:
                active_connection.close()
                print("🔒 Database connection closed. Session ended.")
            else:
                 print("🔒 Session ended (Connection was already closed or invalid).")
            print("Returning to login...\n")


if __name__ == "__main__":
    main()