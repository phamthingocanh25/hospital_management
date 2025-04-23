from datetime import datetime
import pymysql
from pymysql.err import MySQLError

# 1. Kết nối CSDL
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='MaiAnh<3',
        database='HospitalManagementSystem',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 2. Thêm bệnh nhân
def add_patient(name, dob, gender, phone):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO Patients (PatientName, DateOfBirth, Gender, PhoneNumber) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, dob, gender, phone))
        conn.commit()
        print("✅ Patient added successfully.")
    finally:
        conn.close()

# 3. Thêm bác sĩ
def add_doctor(name, department_id, specialty):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO Doctors (DoctorName, DepartmentID, Specialty) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, department_id, specialty))
        conn.commit()
        print("✅ Doctor added successfully.")
    finally:
        conn.close()

# 4. Đặt lịch hẹn
def schedule_appointment(patient_id, doctor_id, date, time):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (patient_id, doctor_id, date, time))
        conn.commit()
        print("📅 Appointment scheduled.")
    finally:
        conn.close()

# 5. Tạo hóa đơn
def create_invoice(patient_id, date, amount):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount) VALUES (%s, %s, %s)"
            cursor.execute(sql, (patient_id, date, amount))
        conn.commit()
        print("🧾 Invoice created.")
    finally:
        conn.close()

# 6. Báo cáo: số lịch hẹn theo ngày
def report_appointments_by_day():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT AppointmentDate, COUNT(*) AS TotalAppointments
                FROM Appointments
                GROUP BY AppointmentDate
                ORDER BY AppointmentDate
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            print("\n📅 Appointment Report:")
            for row in results:
                print(f"{row['AppointmentDate']}: {row['TotalAppointments']} appointments")
    finally:
        conn.close()

# 7. Báo cáo: doanh thu theo tháng
def financial_report_by_month():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT MONTH(InvoiceDate) AS Month, SUM(TotalAmount) AS Revenue
                FROM Invoices
                GROUP BY MONTH(InvoiceDate)
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            print("\n💰 Financial Report:")
            for row in results:
                print(f"Month {row['Month']}: {row['Revenue']} VND")
    finally:
        conn.close()

# 8. Giao diện dòng lệnh
def main_menu():
    while True:
        print("\n--- Hospital Management System ---")
        print("1. Add Patient")
        print("2. Add Doctor")
        print("3. Schedule Appointment")
        print("4. Create Invoice")
        print("5. Report: Appointments per Day")
        print("6. Report: Revenue per Month")
        print("7. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Name: ")
            dob = input("Date of Birth (YYYY-MM-DD): ")
            gender = input("Gender (M/F): ")
            phone = input("Phone Number: ")
            add_patient(name, dob, gender, phone)

        elif choice == "2":
            name = input("Doctor Name: ")
            dept_id = int(input("Department ID: "))
            specialty = input("Specialty: ")
            add_doctor(name, dept_id, specialty)

        elif choice == "3":
            pid = int(input("Patient ID: "))
            did = int(input("Doctor ID: "))
            date = input("Appointment Date (YYYY-MM-DD): ")
            time = input("Time (HH:MM:SS): ")
            schedule_appointment(pid, did, date, time)

        elif choice == "4":
            pid = int(input("Patient ID: "))
            date = input("Invoice Date (YYYY-MM-DD): ")
            amount = float(input("Total Amount (VND): "))
            create_invoice(pid, date, amount)

        elif choice == "5":
            report_appointments_by_day()

        elif choice == "6":
            financial_report_by_month()

        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

# Chạy chương trình
if __name__ == "__main__":
    main_menu()
