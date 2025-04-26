from 7.core_logic import *
import tkinter as tk
from tkinter import messagebox

def open_login_window(root):
    root.destroy()
    def authenticate_user_action():
        """Handles authentication for the login window"""
        username = username_entry.get()  # Assuming username_entry is a Tkinter entry widget
        password = password_entry.get()  # Assuming password_entry is a Tkinter entry widget
        
        user, role, conn, role_id, error = authenticate_user(username, password)
        
        if error:
            messagebox.showerror("Login Failed", error)
            return
        
        login_window.destroy()

        # Proceed based on the role
        if role == "admin":
            messagebox.showinfo("Login Successful", "Welcome Admin!")
            open_admin_menu(conn, username)
        elif role == "doctor":
            messagebox.showinfo("Login Successful", "Welcome Doctor!")
            open_doctor_menu(conn, role_id, username)
        elif role == "receptionist":
            messagebox.showinfo("Login Successful", "Welcome Receptionist!")
            open_receptionist_menu(conn, username)
        elif role == "accountant":
            messagebox.showinfo("Login Successful", "Welcome Accountant!")
            open_accountant_menu(conn, username)
        else:
            messagebox.showerror("Login Failed", "Unknown role")
            return


    login_window = tk.Tk()
    login_window.title("Hospital Management System - Login")
    login_window.geometry("350x200")

    tk.Label(login_window, text="Username").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    tk.Label(login_window, text="Password").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    tk.Button(login_window, text="Login", command=authenticate_user_action).pack(pady=15)

    login_window.mainloop()

def open_admin_menu(conn, username):
    admin_window = tk.Tk()
    admin_window.title("Admin Menu")

    # Create buttons for each action
    tk.Button(admin_window, text="Register New User", command=register_user_action).pack(pady=10)
    tk.Button(admin_window, text="Delete User", command=delete_user_action).pack(pady=10)
    tk.Button(admin_window, text="Add Doctor", command=add_doctor_action).pack(pady=10)
    tk.Button(admin_window, text="Delete Doctor", command=delete_doctor_action).pack(pady=10)
    tk.Button(admin_window, text="Add Patient", command=add_patient_action).pack(pady=10)
    tk.Button(admin_window, text="Delete Patient", command=delete_patient_action).pack(pady=10)
    tk.Button(admin_window, text="Seach Patient", command=search_patient_action).pack(pady=10)
    tk.Button(admin_window, text="Schedule Appointment", command=schedule_appointment_action).pack(pady=10)
    tk.Button(admin_window, text="View Appointments", command=lambda: view_appointments_action(conn, 'admin')).pack(pady=10)
    tk.Button(admin_window, text="Update Appointment Status", command=lambda: update_appointment_status_action(conn)).pack(pady=10)
    tk.Button(admin_window, text="Create Invoice", command=create_invoice_action).pack(pady=10)
    tk.Button(admin_window, text="View Invoices", command=view_invoices_action).pack(pady=10)
    tk.Button(admin_window, text="View Departments", command=view_departments_action).pack(pady=10)
    tk.Button(admin_window, text="Financial Report", command=generate_financial_report_action).pack(pady=10)
    tk.Button(admin_window, text="Change Password", command=lambda: change_password_action(conn, username)).pack(pady=10)
    tk.Button(admin_window, text="Logout", command= lambda: logout_action(admin_window)).pack(pady=10)

    admin_window.mainloop()

def open_doctor_menu(conn, role_id, username):
    doctor_window = tk.Tk()
    doctor_window.title("Doctor Menu")

    # Create buttons for each action
    tk.Button(doctor_window, text="Search Patient Information", command=search_patient_action).pack(pady=10)
    tk.Button(doctor_window, text="View My Appointments", command= lambda: view_appointments_action(conn,'doctor',username)).pack(pady=10)
    tk.Button(doctor_window, text="Update Appointment Status", command=lambda: update_appointment_status_action(conn)).pack(pady=10)
    tk.Button(doctor_window, text="Change Password", command=lambda: change_password_action(conn, username)).pack(pady=10)
    tk.Button(doctor_window, text="Logout", command=doctor_window.destroy).pack(pady=10)

    doctor_window.mainloop()

def open_receptionist_menu(conn, username):
    receptionist_window = tk.Tk()
    receptionist_window.title("Receptionist Menu")

    # Create buttons for each action

    tk.Button(receptionist_window, text="Add Patient", command=add_patient_action).pack(pady=10)
    tk.Button(receptionist_window, text="Delete Patient", command=delete_patient_action).pack(pady=10)
    tk.Button(receptionist_window, text="Seach Patient", command=search_patient_action).pack(pady=10)
    tk.Button(receptionist_window, text="Schedule Appointment", command=schedule_appointment_action).pack(pady=10)
    tk.Button(receptionist_window, text="View Appointments", command=lambda: view_appointments_action(conn, 'receptionist')).pack(pady=10)
    tk.Button(receptionist_window, text="Create Invoice", command=create_invoice_action).pack(pady=10)
    tk.Button(receptionist_window, text="View Invoices", command=view_invoices_action).pack(pady=10)
    tk.Button(receptionist_window, text="View Departments", command=view_departments_action).pack(pady=10)
    tk.Button(receptionist_window, text="Change Password", command=lambda: change_password_action(conn, username)).pack(pady=10)
    tk.Button(receptionist_window, text="Logout", command= lambda: logout_action(receptionist_window)).pack(pady=10)

    receptionist_window.mainloop()

def open_accountant_menu(conn, username):
    accountant_window = tk.Tk()
    accountant_window.title("Accountant Menu")

    # Create buttons for each action
    tk.Button(accountant_window, text="View Invoices", command=view_invoices_action).pack(pady=10)
    tk.Button(accountant_window, text="Financial Report", command=generate_financial_report_action).pack(pady=10)
    tk.Button(accountant_window, text="Change Password", command=lambda: change_password_action(conn, username)).pack(pady=10)
    tk.Button(accountant_window, text="Logout", command=lambda: logout_action(accountant_window)).pack(pady=10)

    accountant_window.mainloop()

def register_user_action():
    reg_window = tk.Toplevel()
    reg_window.title("Register New User")

    tk.Label(reg_window, text="Username").pack()
    entry_username = tk.Entry(reg_window)
    entry_username.pack()

    tk.Label(reg_window, text="Password").pack()
    entry_password = tk.Entry(reg_window, show="*")
    entry_password.pack()

    tk.Label(reg_window, text="Confirm Password").pack()
    entry_confirm = tk.Entry(reg_window, show="*")
    entry_confirm.pack()

    tk.Label(reg_window, text="Role").pack()
    role_var = tk.StringVar()
    role_var.set("receptionist")
    tk.OptionMenu(reg_window, role_var, "admin", "accountant", "receptionist").pack()

    def submit_registration():
        username = entry_username.get()
        password = entry_password.get()
        confirm_password = entry_confirm.get()
        role = role_var.get()

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        success, message = register_user(conn, username, password, confirm_password, role)
        if success:
            messagebox.showinfo("Success", message)
            reg_window.destroy()
        else:
            messagebox.showerror("Error", message)

    tk.Button(reg_window, text="Register", command=submit_registration).pack(pady=10)

def delete_user_action():
    delete_window = tk.Toplevel()
    delete_window.title("Delete User")

    tk.Label(delete_window, text="Username").pack()
    entry_username = tk.Entry(delete_window)
    entry_username.pack()

    def submit_deletion():
        username = entry_username.get()
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        success, message = delete_user(conn, username)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)

    tk.Button(delete_window, text="Delete User", command=submit_deletion).pack(pady=10)

def add_doctor_action():
    add_doctor_window = tk.Toplevel()
    add_doctor_window.title("Add Doctor")

    # Doctor Name
    tk.Label(add_doctor_window, text="Doctor Name").pack()
    entry_name = tk.Entry(add_doctor_window)
    entry_name.pack()

    # Department ID
    tk.Label(add_doctor_window, text="Department ID").pack()
    entry_dept = tk.Entry(add_doctor_window)
    entry_dept.pack()

    # Specialization
    tk.Label(add_doctor_window, text="Specialization").pack()
    entry_specialization = tk.Entry(add_doctor_window)
    entry_specialization.pack()

    # Username
    tk.Label(add_doctor_window, text="Username").pack()
    entry_username = tk.Entry(add_doctor_window)
    entry_username.pack()

    def submit_add_doctor():
        name = entry_name.get()
        dept_id = entry_dept.get()  # Giả sử bạn đã có entry cho Dept ID
        specialization = entry_specialization.get()
        username = entry_username.get()  # Giả sử bạn đã có entry cho Username
        
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        success, message = add_doctor(conn, name, dept_id, specialization, username)
        if success:
            messagebox.showinfo("Success", message)
            add_doctor_window.destroy()
        else:
            messagebox.showerror("Error", message)

    tk.Button(add_doctor_window, text="Add Doctor", command=submit_add_doctor).pack(pady=10)

def delete_doctor_action():
    delete_doctor_window = tk.Toplevel()
    delete_doctor_window.title("Delete Doctor")

    tk.Label(delete_doctor_window, text="Doctor ID").pack()
    entry_id = tk.Entry(delete_doctor_window)
    entry_id.pack()

    def submit_delete_doctor():
        doctor_id = entry_id.get()  # Giả sử bạn có entry để nhập Doctor ID
        
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        # Gọi hàm delete_doctor và truyền các tham số vào
        success, message = delete_doctor(conn, doctor_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_doctor_window.destroy()
        else:
            messagebox.showerror("Error", message)


    tk.Button(delete_doctor_window, text="Delete Doctor", command=submit_delete_doctor).pack(pady=10)

def add_patient_action():
    add_patient_window = tk.Toplevel()
    add_patient_window.title("Add New Patient")

    # Tạo các label và entry cho các trường thông tin bệnh nhân
    tk.Label(add_patient_window, text="Patient Name").pack()
    entry_name = tk.Entry(add_patient_window)
    entry_name.pack()

    tk.Label(add_patient_window, text="Date of Birth (yyyy-mm-dd)").pack()
    entry_dob = tk.Entry(add_patient_window)
    entry_dob.pack()

    tk.Label(add_patient_window, text="Gender (Required)").pack()
    entry_gender = tk.Entry(add_patient_window)
    entry_gender.pack()

    tk.Label(add_patient_window, text="Phone Number (Required)").pack()
    entry_phone_number = tk.Entry(add_patient_window)
    entry_phone_number.pack()

    tk.Label(add_patient_window, text="Address (Optional)").pack()
    entry_address = tk.Entry(add_patient_window)
    entry_address.pack()

    def submit_add_patient():
        name = entry_name.get()
        date_of_birth = entry_dob.get()
        gender = entry_gender.get()  # Giới tính là bắt buộc
        phone_number = entry_phone_number.get()  # Số điện thoại là bắt buộc
        address = entry_address.get() or None  # Địa chỉ là không bắt buộc

        # Kiểm tra xem giới tính và số điện thoại đã nhập chưa
        if not gender or not phone_number:
            messagebox.showerror("Error", "Gender and Phone Number are required fields.")
            return

        conn = get_db_connection()  # Lấy kết nối DB
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        # Gọi hàm add_patient để thêm bệnh nhân vào cơ sở dữ liệu
        success, message = add_patient(conn, name, date_of_birth, gender, address, phone_number)
        if success:
            messagebox.showinfo("Success", message)
            add_patient_window.destroy()  # Đóng cửa sổ khi thành công
        else:
            messagebox.showerror("Error", message)  # Hiển thị lỗi nếu không thành công

    # Tạo nút để thêm bệnh nhân
    tk.Button(add_patient_window, text="Add Patient", command=submit_add_patient).pack(pady=10)

def delete_patient_action():
    delete_patient_window = tk.Toplevel()
    delete_patient_window.title("Delete Patient")

    tk.Label(delete_patient_window, text="Patient ID").pack()
    entry_id = tk.Entry(delete_patient_window)
    entry_id.pack()

    def submit_delete_patient():
        patient_id = entry_id.get()
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        success, message = delete_patient(conn, patient_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_patient_window.destroy()
        else:
            messagebox.showerror("Error", message)

    tk.Button(delete_patient_window, text="Delete Patient", command=submit_delete_patient).pack(pady=10)

def search_patient_action():
    search_patient_window = tk.Toplevel()
    search_patient_window.title("Search Patient Information")

    tk.Label(search_patient_window, text="Search by Patient Name or ID").pack(pady=10)

    tk.Label(search_patient_window, text="Patient Name (Optional)").pack()
    entry_name = tk.Entry(search_patient_window)
    entry_name.pack()

    tk.Label(search_patient_window, text="Patient ID (Optional)").pack()
    entry_patient_id = tk.Entry(search_patient_window)
    entry_patient_id.pack()

    text_area = tk.Text(search_patient_window, height=20, width=70)
    text_area.pack(pady=10)

    def submit_search_patient():
        name = entry_name.get()
        patient_id = entry_patient_id.get()

        # Kiểm tra nếu người dùng không nhập gì thì yêu cầu nhập lại
        if not name and not patient_id:
            messagebox.showerror("Error", "Please enter either a Patient Name or Patient ID to search.")
            return

        conn = get_db_connection()  # Lấy kết nối DB
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        # Gọi hàm search_patient để tìm kiếm bệnh nhân
        success, result = search_patient(conn, patient_id if patient_id else None, name if name else None)

        if success:
            text_area.delete(1.0, tk.END)
            
            if result:
                for patient in result:
                    text_area.insert(tk.END, f"Patient ID: {patient['PatientID']}\n")
                    text_area.insert(tk.END, f"Patient Name: {patient['PatientName']}\n")
                    text_area.insert(tk.END, f"Date Of Birth: {patient['DateOfBirth']}\n")
                    text_area.insert(tk.END, f"Gender: {patient['Gender']}\n")
                    text_area.insert(tk.END, f"Address: {patient['Address']}\n")
                    text_area.insert(tk.END, f"Phone Number: {patient['PhoneNumber']}\n")
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No patients found.\n")
        else:
            messagebox.showerror("Error", result)

    # Tạo nút tìm kiếm bệnh nhân
    tk.Button(search_patient_window, text="Search Patient Information", command=submit_search_patient).pack(pady=10)

def schedule_appointment_action():
    """Open the Schedule Appointment window"""
    schedule_window = tk.Toplevel()
    schedule_window.title("Schedule Appointment")

    # Nhập thông tin bệnh nhân
    tk.Label(schedule_window, text="Patient ID").pack()
    entry_patient_id = tk.Entry(schedule_window)
    entry_patient_id.pack()

    # Nhập thông tin bác sĩ
    tk.Label(schedule_window, text="Doctor ID").pack()
    entry_doctor_id = tk.Entry(schedule_window)
    entry_doctor_id.pack()

    # Nhập ngày cuộc hẹn
    tk.Label(schedule_window, text="Appointment Date (YYYY-MM-DD)").pack()
    entry_appointment_date = tk.Entry(schedule_window)
    entry_appointment_date.pack()

    # Nhập giờ cuộc hẹn
    tk.Label(schedule_window, text="Appointment Time (HH:MM)").pack()
    entry_appointment_time = tk.Entry(schedule_window)
    entry_appointment_time.pack()

    def submit_schedule_appointment():
        patient_id = entry_patient_id.get()
        doctor_id = entry_doctor_id.get()
        appointment_date = entry_appointment_date.get()
        appointment_time = entry_appointment_time.get()

        # Kiểm tra các trường đã được nhập chưa
        if not patient_id or not doctor_id or not appointment_date or not appointment_time:
            messagebox.showerror("Error", "All fields are required.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        # Gọi hàm schedule_appointment từ core_logic.py
        success, message = schedule_appointment(conn, patient_id, doctor_id, appointment_date, appointment_time)
        if success:
            messagebox.showinfo("Success", message)
            schedule_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Thêm nút để gửi thông tin lịch hẹn
    tk.Button(schedule_window, text="Schedule Appointment", command=submit_schedule_appointment).pack(pady=10)

def view_appointments_action(conn, role, username=None):
    window = tk.Toplevel()
    window.title("View Appointments")

    tk.Label(window, text="Year (optional):").pack()
    entry_year = tk.Entry(window)
    entry_year.pack()

    tk.Label(window, text="Month (optional):").pack()
    entry_month = tk.Entry(window)
    entry_month.pack()

    tk.Label(window, text="Day (optional):").pack()
    entry_day = tk.Entry(window)
    entry_day.pack()

    text_area = tk.Text(window, height=20, width=80)
    text_area.pack(pady=10)

    def fetch_appointments():
        year = entry_year.get()
        month = entry_month.get()
        day = entry_day.get()

        year = int(year) if year else None
        month = int(month) if month else None
        day = int(day) if day else None

        success, result = view_appointments(conn, role, username, year, month, day)
        text_area.delete(1.0, tk.END)

        if success:
            if result:
                for row in result:
                    text_area.insert(tk.END, f"Appointment ID: {row['AppointmentID']}\n")
                    text_area.insert(tk.END, f"Doctor ID: {row['DoctorID']}\n")
                    text_area.insert(tk.END, f"Patient ID: {row['PatientID']}\n")
                    text_area.insert(tk.END, f"Appointment Date: {row['AppointmentDate']}\n")
                    text_area.insert(tk.END, f"Appointment Time: {row['AppointmentTime']}\n")
                    text_area.insert(tk.END, "-" * 40 + "\n")
            else:
                text_area.insert(tk.END, "No appointments found.\n")
        else:
            messagebox.showerror("Error", result)

    tk.Button(window, text="Fetch Appointments", command=fetch_appointments).pack(pady=10)

def update_appointment_status_action(conn):
    window = tk.Toplevel()
    window.title("Update Appointment Status")

    # Nhập Appointment ID
    tk.Label(window, text="Appointment ID:").pack()
    entry_id = tk.Entry(window)
    entry_id.pack()

    # Chọn trạng thái mới
    tk.Label(window, text="New Status:").pack()
    status_var = tk.StringVar(window)
    status_var.set("Scheduled")  # Giá trị mặc định

    status_options = ["Scheduled", "Completed", "Cancelled"]
    tk.OptionMenu(window, status_var, *status_options).pack()

    def submit_update():
        appointment_id = entry_id.get().strip()
        new_status = status_var.get()

        if not appointment_id:
            messagebox.showerror("Error", "Please enter an Appointment ID.")
            return

        success, message = update_appointment_status(conn, appointment_id, new_status)
        if success:
            messagebox.showinfo("Success", message)
            window.destroy()
        else:
            messagebox.showerror("Error", message)

    tk.Button(window, text="Update Status", command=submit_update).pack(pady=10)

def create_invoice_action():
    window = tk.Toplevel()
    window.title("Create Invoice")

    tk.Label(window, text="Patient ID").pack()
    entry_patient_id = tk.Entry(window)
    entry_patient_id.pack()

    tk.Label(window, text="Total Amount").pack()
    entry_amount = tk.Entry(window)
    entry_amount.pack()

    def submit_invoice():
        patient_id = entry_patient_id.get().strip()
        amount_str = entry_amount.get().strip()

        try:
            total_amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        success, msg = create_invoice(conn, patient_id, total_amount)
        if success:
            messagebox.showinfo("Success", msg)
            window.destroy()
        else:
            messagebox.showerror("Error", msg)

    tk.Button(window, text="Create Invoice", command=submit_invoice).pack(pady=10)

def view_invoices_action():
    window = tk.Toplevel()
    window.title("View Invoices")

    tk.Label(window, text="Enter Patient ID (leave empty to view all)").pack()
    entry_patient_id = tk.Entry(window)
    entry_patient_id.pack()

    text_area = tk.Text(window, height=20, width=70)
    text_area.pack(pady=10)

    def fetch_invoices():
        # Tạo kết nối với cơ sở dữ liệu
        conn = get_db_connection()  # Giả sử bạn đã có hàm get_db_connection để lấy kết nối cơ sở dữ liệu
        
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        patient_id = entry_patient_id.get()  # Lấy patient_id từ entry
        success, result = view_invoices(conn, patient_id if patient_id else None)
        
        if success:
            text_area.delete(1.0, tk.END)  # Clear previous text
            if result:  # Nếu có dữ liệu
                for invoice in result:
                    # Truy cập dữ liệu từ dictionary thay vì tuple
                    text_area.insert(tk.END, f"Invoice ID: {invoice['InvoiceID']}\n")  # invoice['InvoiceID']
                    text_area.insert(tk.END, f"Patient ID: {invoice['PatientID']}\n")  # invoice['PatientID']
                    text_area.insert(tk.END, f"Date: {invoice['InvoiceDate']}\n")  # invoice['InvoiceDate']
                    text_area.insert(tk.END, f"Total Amount: {invoice['TotalAmount']} VND\n")  # invoice['TotalAmount']
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No invoices found.\n")
        else:
            messagebox.showerror("Error", result)  # Nếu không thành công

    tk.Button(window, text="Search", command=fetch_invoices).pack()

def view_departments_action():
    """View all departments from the GUI"""
    window = tk.Toplevel()
    window.title("View Departments")

    text_area = tk.Text(window, height=20, width=70)
    text_area.pack(pady=10)

    def fetch_departments():
        # Tạo kết nối với cơ sở dữ liệu
        conn = get_db_connection()  # Giả sử bạn đã có hàm get_db_connection để lấy kết nối cơ sở dữ liệu
        
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        success, result = view_departments(conn)  # Lấy danh sách phòng ban

        if success:
            text_area.delete(1.0, tk.END)  # Clear previous text
            if result:  # Nếu có dữ liệu
                for dept in result:
                    text_area.insert(tk.END, f"Invoice ID: {dept['DepartmentID']}\n") 
                    text_area.insert(tk.END, f"Department Name: {dept['DepartmentName']}\n")
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No departments found.\n")
        else:
            messagebox.showerror("Error", result)  # Nếu không thành công

    fetch_departments()

def generate_financial_report_action():
    window = tk.Toplevel()
    window.title("Generate Financial Report")

    tk.Label(window, text="Select Report Type").pack()
    report_type = tk.StringVar(value="month")
    tk.Radiobutton(window, text="By Month", variable=report_type, value="month").pack()
    tk.Radiobutton(window, text="By Year", variable=report_type, value="year").pack()

    tk.Label(window, text="Enter Year (for monthly report)").pack()
    year_entry = tk.Entry(window)
    year_entry.pack()

    text_area = tk.Text(window, height=20, width=70)
    text_area.pack(pady=10)

    def fetch_report():
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        selected_type = report_type.get()
        year = year_entry.get() if selected_type == 'month' else None
        success, result = generate_financial_report(conn, selected_type, year)

        text_area.delete(1.0, tk.END)

        if success:
            title, rows = result
            text_area.insert(tk.END, title + "\n" + "-" * 40 + "\n")
            total = 0
            for row in rows:
                if selected_type == 'month':
                    text_area.insert(tk.END, f"Month {row['Month']}: {row['Total']:,.2f} VND\n")
                else:
                    text_area.insert(tk.END, f"Year {row['Year']}: {row['Total']:,.2f} VND\n")
                total += row['Total']
            text_area.insert(tk.END, "-" * 40 + "\n")
            text_area.insert(tk.END, f"GRAND TOTAL: {total:,.2f} VND\n")
        else:
            messagebox.showerror("Error", result)

    tk.Button(window, text="Generate Report", command=fetch_report).pack(pady=5)

import tkinter as tk
from tkinter import messagebox

def change_password_action(conn, username):
    """Change password GUI"""
    change_password_window = tk.Toplevel()
    change_password_window.title("Change Password")

    # Nhập mật khẩu cũ
    tk.Label(change_password_window, text="Old Password").pack()
    entry_old_password = tk.Entry(change_password_window, show="*")
    entry_old_password.pack()

    # Nhập mật khẩu mới
    tk.Label(change_password_window, text="New Password").pack()
    entry_new_password = tk.Entry(change_password_window, show="*")
    entry_new_password.pack()

    # Nhập lại mật khẩu mới
    tk.Label(change_password_window, text="Confirm New Password").pack()
    entry_confirm_password = tk.Entry(change_password_window, show="*")
    entry_confirm_password.pack()

    def submit_change_password():
        old_password = entry_old_password.get()
        new_password = entry_new_password.get()
        confirm_password = entry_confirm_password.get()

        # Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Gọi hàm change_password để thay đổi mật khẩu
        success, message = change_password(conn, username, old_password, new_password)
        
        if success:
            messagebox.showinfo("Success", message)
            change_password_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Nút để xác nhận thay đổi mật khẩu
    tk.Button(change_password_window, text="Change Password", command=submit_change_password).pack(pady=10)

def logout_action(current_window):
    current_window.destroy()
    messagebox.showinfo("Logout", "You have been logged out.")
    main()

def main():
    global root
    root = tk.Tk()
    root.title("Hospital Management System")
    root.geometry("400x300")

    tk.Label(root, text="Welcome to the Hospital Management System").pack(pady=20)
    tk.Button(root, text="Login", command=lambda: open_login_window(root)).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
