from core_logic import *
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from tkinter import simpledialog
from tkinter import scrolledtext
from tkcalendar import DateEntry




# Custom color scheme
BG_COLOR = "#f0f8ff"
BUTTON_COLOR = "#4682b4"
BUTTON_HOVER = "#5f9ea0"
TEXT_COLOR = "#2f4f4f"
ACCENT_COLOR = "#008080"
ENTRY_BG = "#ffffff"
TITLE_FONT = ("Helvetica", 12, "bold") # Giảm cỡ chữ một chút
LABEL_FONT = ("Helvetica", 10)
BUTTON_FONT = ("Helvetica", 10, "bold")
TREEVIEW_FONT = ("Helvetica", 9) # Font cho treeview có thể nhỏ hơn

# Font settings
TITLE_FONT = ("Helvetica", 14, "bold")
LABEL_FONT = ("Helvetica", 10)
BUTTON_FONT = ("Helvetica", 10, "bold")

def apply_styles(widget):
    # (Giữ nguyên hàm apply_styles của bạn)
    if isinstance(widget, tk.Button):
        widget.config(bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, relief=tk.RAISED, borderwidth=2, padx=8, pady=4) # Giảm padding/border
        widget.bind("<Enter>", lambda e: widget.config(bg=BUTTON_HOVER))
        widget.bind("<Leave>", lambda e: widget.config(bg=BUTTON_COLOR))
    elif isinstance(widget, tk.Entry):
         widget.config(bg=ENTRY_BG, relief=tk.SUNKEN, borderwidth=1, font=LABEL_FONT)
    elif isinstance(widget, tk.Label) and widget.cget('relief') == tk.SUNKEN: # Style cho label hiển thị giá trị
         widget.config(bg=ENTRY_BG, fg=TEXT_COLOR, font=LABEL_FONT, anchor='e', padx=3)

def create_scrollable_text(window, height=15, width=60):
    """Tạo vùng text có thể cuộn"""
    frame = tk.Frame(window)
    frame.pack(pady=10)
    
    text_area = tk.Text(
        frame,
        height=height,
        width=width,
        wrap=tk.WORD,
        bg=ENTRY_BG,
        font=LABEL_FONT,
        padx=5,
        pady=5
    )
    
    # Thêm tag cho định dạng
    text_area.tag_config("title", font=("Helvetica", 14, "bold"))
    text_area.tag_config("subtitle", font=("Helvetica", 12, "bold"))
    
    scrollbar = ttk.Scrollbar(frame, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    return text_area

def center_window(window, width=None, height=None):
    """Center the window on screen"""
    window.update_idletasks()
    if width and height:
        window.geometry(f"{width}x{height}")
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - window.winfo_reqwidth()) // 2
    y = (screen_height - window.winfo_reqheight()) // 2
    
    window.geometry(f"+{x}+{y}")

def open_login_window(root):
    root.destroy()
    
    def authenticate_user_action():
        """Handles authentication for the login window"""
        username = username_entry.get()
        password = password_entry.get()
    
        user, role, conn, role_id, error = authenticate_user(username, password)
    
        if error:
           messagebox.showerror("Login Failed", error)
           return
    
        login_window.destroy()

    # Proceed based on the role
        welcome_messages = {
        "admin": "Welcome Admin!",
        "doctor": "Welcome Doctor!",
        "receptionist": "Welcome Receptionist!",
        "accountant": "Welcome Accountant!"
        }
    
        if role in welcome_messages:
        # Hiển thị thông báo và sau đó mở menu tương ứng
           def open_role_menu():
               if role == "admin":
                  open_admin_menu(conn, username)
               elif role == "doctor":
                  open_doctor_menu(conn, role_id, username)
               elif role == "receptionist":
                  open_receptionist_menu(conn, username)
               elif role == "accountant":
                  open_accountant_menu(conn, username)
        
        # Hiển thị thông báo và sau khi đóng sẽ gọi open_role_menu
           messagebox.showinfo("Login Successful", welcome_messages[role])
           open_role_menu()
        else:
           messagebox.showerror("Login Failed", "Unknown role")
           return
    login_window = tk.Tk()
    login_window.title("Hospital Management System - Login")
    login_window.geometry("400x300")
    login_window.config(bg=BG_COLOR)
    center_window(login_window)
    
    # Main frame
    main_frame = tk.Frame(login_window, bg=BG_COLOR)
    main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Hospital Management System",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Login form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(pady=10)
    
    # Username
    tk.Label(form_frame, text="Username:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    username_entry = tk.Entry(form_frame)
    username_entry.grid(row=0, column=1, pady=5, padx=5)
    apply_styles(username_entry)
    
    # Password
    tk.Label(form_frame, text="Password:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    password_entry = tk.Entry(form_frame, show="*")
    password_entry.grid(row=1, column=1, pady=5, padx=5)
    apply_styles(password_entry)
    
    # Login button
    login_button = tk.Button(
        main_frame,
        text="Login",
        command=authenticate_user_action
    )
    apply_styles(login_button)
    login_button.pack(pady=20)
    
    login_window.mainloop()

def open_admin_menu(conn, username):
    admin_window = tk.Tk()
    admin_window.title(f"Admin Menu - {username}")
    admin_window.geometry("900x650")
    admin_window.config(bg=BG_COLOR)
    center_window(admin_window)
    admin_window.lift()
    admin_window.attributes('-topmost',True)
    admin_window.after(100, lambda: admin_window.attributes('-topmost',False))

    # Main frame with scrollbar
    main_frame = tk.Frame(admin_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Administrator Dashboard",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(fill=tk.X)
    
    # Create buttons in two columns
    buttons = [
        ("Register New User", lambda: register_user_gui(conn)),
        ("Delete User", lambda: delete_user_gui(conn)),
        ("Add Doctor", lambda: add_doctor_gui(conn)),
        ("Delete Doctor", lambda: delete_doctor_gui(conn)),
        ("Add Patient", lambda: add_patient_gui(conn)),
        ("Delete Patient", lambda: delete_patient_gui(conn)),
        ("Search Patient", lambda: search_patient_gui(conn)),
        ("Create Insurance Record", lambda: create_insurance_gui(conn)),
        ("View Insurance", lambda: view_insurance_gui(conn)),
        ("View Prescriptions", lambda: view_prescriptions_gui(conn)),  
        ("Room Status", lambda: view_room_status_gui(conn)), 
        ("Schedule Appointment", lambda: schedule_appointment_gui(conn)),
        ("View Appointments", lambda: view_appointments_gui(conn, 'admin')),
        ("Update Appointment Status", lambda: update_appointment_status_gui(conn)),
        ("Create Invoice", lambda: create_invoice_gui(conn)),
        ("View Invoices", lambda: view_invoices_gui(conn)),
        ("View Departments", lambda: view_departments_gui(conn)),
        ("Financial Report", lambda: generate_financial_report_gui(conn)),
        ("Change Password", lambda: change_password_gui(conn, username)),
        ("Logout", lambda: logout_action(admin_window))
    ]
    
    # Organize buttons in two columns
    for i, (text, command) in enumerate(buttons):
        row = i // 2
        col = i % 2
        btn = tk.Button(
            button_frame,
            text=text,
            command=command,
            width=25
        )
        apply_styles(btn)
        btn.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
    
    # Configure grid weights
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    
    admin_window.mainloop()

def open_doctor_menu(conn, role_id, username):
    doctor_window = tk.Tk()
    doctor_window.title(f"Doctor Menu - {username}")
    doctor_window.geometry("700x500")
    doctor_window.config(bg=BG_COLOR)
    center_window(doctor_window)
    
    # Main frame
    main_frame = tk.Frame(doctor_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Doctor Dashboard",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Buttons
    buttons = [
        ("Search Patient Information", lambda: search_patient_gui(conn)),
        ("View Patient Prescriptions", lambda: view_patient_prescriptions_gui(conn)),  # Thêm nút mới
        ("View Patient Insurance", lambda: view_patient_insurance_gui(conn)),  # Thêm nút mới
        ("Create Prescription", lambda: create_prescription_gui(conn, role_id)),  # Thêm nút mới
        ("View My Appointments", lambda: view_appointments_gui(conn, 'doctor', username)),
        ("Update Appointment Status", lambda: update_appointment_status_gui(conn)),
        ("Change Password", lambda: change_password_gui(conn, username)),
        ("Logout", doctor_window.destroy)
    ]
    
    for text, command in buttons:
        btn = tk.Button(
            main_frame,
            text=text,
            command=command,
            width=30
        )
        apply_styles(btn)
        btn.pack(pady=5, fill=tk.X)
    
    doctor_window.mainloop()

def open_receptionist_menu(conn, username):
    receptionist_window = tk.Tk()
    receptionist_window.title(f"Receptionist Menu - {username}")
    receptionist_window.geometry("800x600")
    receptionist_window.config(bg=BG_COLOR)
    center_window(receptionist_window)
    
    # Main frame
    main_frame = tk.Frame(receptionist_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Receptionist Dashboard",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(fill=tk.X)
    
    # Create buttons in two columns
    buttons = [
        ("Add Patient", lambda: add_patient_gui(conn)),
        ("Delete Patient", lambda: delete_patient_gui(conn)),
        ("Search Patient", lambda: search_patient_gui(conn)),
        ("View Patient Insurance", lambda: view_patient_insurance_gui(conn)),
         ("Create Insurance Record", lambda: create_insurance_gui(conn)),  
        ("Room Management", lambda: room_management_gui(conn)), 
        ("Available Rooms", lambda: view_available_rooms_gui(conn)),
        ("Schedule Appointment", lambda: schedule_appointment_gui(conn)),
        ("View Appointments", lambda: view_appointments_gui(conn, 'receptionist')),
        ("Create Invoice", lambda: create_invoice_gui(conn)),
        ("View Invoices", lambda: view_invoices_gui(conn)),
        ("View Departments", lambda: view_departments_gui(conn)),
        ("Change Password", lambda: change_password_gui(conn, username)),
        ("Logout", lambda: logout_action(receptionist_window))
    ]
    
    # Organize buttons in two columns
    for i, (text, command) in enumerate(buttons):
        row = i // 2
        col = i % 2
        btn = tk.Button(
            button_frame,
            text=text,
            command=command,
            width=25
        )
        apply_styles(btn)
        btn.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
    
    # Configure grid weights
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    
    receptionist_window.mainloop()

def open_accountant_menu(conn, username):
    accountant_window = tk.Tk()
    accountant_window.title(f"Accountant Menu - {username}")
    accountant_window.geometry("500x300")
    accountant_window.config(bg=BG_COLOR)
    center_window(accountant_window)
    
    # Main frame
    main_frame = tk.Frame(accountant_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Accountant Dashboard",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Buttons
    buttons = [
        ("View Invoices", lambda: view_invoices_gui(conn)),
        ("Financial Report", lambda: generate_financial_report_gui(conn)),
        ("Change Password", lambda: change_password_gui(conn, username)),
        ("Logout", lambda: logout_action(accountant_window))
    ]
    
    for text, command in buttons:
        btn = tk.Button(
            main_frame,
            text=text,
            command=command,
            width=30
        )
        apply_styles(btn)
        btn.pack(pady=5, fill=tk.X)
    
    accountant_window.mainloop()

# GUI Wrapper Functions for Core Logic
def register_user_gui(conn):
    """GUI for registering a new user"""
    reg_window = tk.Toplevel()
    reg_window.title("Register New User")
    reg_window.geometry("400x300")
    reg_window.config(bg=BG_COLOR)
    center_window(reg_window)
    
    # Main frame
    main_frame = tk.Frame(reg_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Register New User",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Username
    tk.Label(form_frame, text="Username:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_username = tk.Entry(form_frame)
    entry_username.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_username)
    
    # Password
    tk.Label(form_frame, text="Password:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_password = tk.Entry(form_frame, show="*")
    entry_password.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_password)
    
    # Confirm Password
    tk.Label(form_frame, text="Confirm Password:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_confirm = tk.Entry(form_frame, show="*")
    entry_confirm.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_confirm)
    
    # Role
    tk.Label(form_frame, text="Role:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    role_var = tk.StringVar()
    role_var.set("receptionist")
    role_menu = ttk.OptionMenu(form_frame, role_var, "receptionist", "admin", "accountant", "receptionist")
    role_menu.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    
    def submit():
        username = entry_username.get()
        password = entry_password.get()
        confirm_password = entry_confirm.get()
        role = role_var.get()

        success, message = register_user(conn, username, password, confirm_password, role)
        if success:
            messagebox.showinfo("Success", message)
            reg_window.destroy()
        else:
            messagebox.showerror("Error", message)
            reg_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Register",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def delete_user_gui(conn):
    """GUI for deleting a user"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete User")
    delete_window.geometry("300x150")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    
    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Username
    tk.Label(main_frame, text="Username:", bg=BG_COLOR).pack()
    entry_username = tk.Entry(main_frame)
    entry_username.pack(pady=5)
    apply_styles(entry_username)
    
    def submit():
        username = entry_username.get()
        success, message = delete_user(conn, username)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Delete User",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def add_doctor_gui(conn):
    """GUI for adding a doctor"""
    add_window = tk.Toplevel()
    add_window.title("Add Doctor")
    add_window.geometry("400x350")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    
    # Main frame
    main_frame = tk.Frame(add_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Doctor Name
    tk.Label(form_frame, text="Doctor Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)
    
    # Department ID
    tk.Label(form_frame, text="Department ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_dept = tk.Entry(form_frame)
    entry_dept.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_dept)
    
    # Specialization
    tk.Label(form_frame, text="Specialization:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_specialization = tk.Entry(form_frame)
    entry_specialization.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_specialization)
    
    # Username
    tk.Label(form_frame, text="Username:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_username = tk.Entry(form_frame)
    entry_username.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_username)
    
    def submit():
        name = entry_name.get()
        dept_id = entry_dept.get()
        specialization = entry_specialization.get()
        username = entry_username.get()
        
        success, message = add_doctor(conn, name, dept_id, specialization, username)
        if success:
            messagebox.showinfo("Success", message)
            add_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Add Doctor",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def delete_doctor_gui(conn):
    """GUI for deleting a doctor"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Doctor")
    delete_window.geometry("300x150")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    
    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Doctor ID
    tk.Label(main_frame, text="Doctor ID:", bg=BG_COLOR).pack()
    entry_id = tk.Entry(main_frame)
    entry_id.pack(pady=5)
    apply_styles(entry_id)
    
    def submit():
        doctor_id = entry_id.get()
        success, message = delete_doctor(conn, doctor_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Delete Doctor",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def add_patient_gui(conn):
    """GUI for adding a patient"""
    add_window = tk.Toplevel()
    add_window.title("Add Patient")
    add_window.geometry("400x400")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    
    # Main frame
    main_frame = tk.Frame(add_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Patient Name
    tk.Label(form_frame, text="Patient Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)
    
    # Date of Birth
    tk.Label(form_frame, text="Date of Birth (YYYY-MM-DD):", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_dob = tk.Entry(form_frame)
    entry_dob.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_dob)
    
    # Gender
    tk.Label(form_frame, text="Gender:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_gender = tk.Entry(form_frame)
    entry_gender.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_gender)
    
    # Phone Number
    tk.Label(form_frame, text="Phone Number:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_phone = tk.Entry(form_frame)
    entry_phone.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_phone)
    
    # Address
    tk.Label(form_frame, text="Address:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    entry_address = tk.Entry(form_frame)
    entry_address.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_address)
    
    def submit():
        name = entry_name.get()
        dob = entry_dob.get()
        gender = entry_gender.get()
        phone = entry_phone.get()
        address = entry_address.get() or None
        
        success, message = add_patient(conn, name, dob, gender, address, phone)
        if success:
            messagebox.showinfo("Success", message)
            add_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Add Patient",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def delete_patient_gui(conn):
    """GUI for deleting a patient"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Patient")
    delete_window.geometry("300x150")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    
    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).pack()
    entry_id = tk.Entry(main_frame)
    entry_id.pack(pady=5)
    apply_styles(entry_id)
    
    def submit():
        patient_id = entry_id.get()
        success, message = delete_patient(conn, patient_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Delete Patient",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
def view_available_rooms_gui(conn):
    """GUI để xem các phòng đang trống."""
    avail_window = tk.Toplevel()
    avail_window.title("Available Rooms")
    avail_window.geometry("800x500")
    avail_window.config(bg=BG_COLOR)
    center_window(avail_window, 800, 500)
    avail_window.grab_set()

    # Main frame
    main_frame = tk.Frame(avail_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Title
    title_label = tk.Label(
        main_frame,
        text="Available Rooms List",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 15))

    # Treeview frame
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    # Treeview scrollbar
    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Treeview definition
    cols = ("room_number", "type", "department", "cost")
    tree = ttk.Treeview(
        tree_frame,
        columns=cols,
        show="headings",
        yscrollcommand=tree_scroll.set,
        style="Custom.Treeview" # Use the custom style defined earlier
    )
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    tree_scroll.config(command=tree.yview)

    # Define headings
    tree.heading("room_number", text="Room Number", anchor=tk.CENTER)
    tree.heading("type", text="Room Type")
    tree.heading("department", text="Department")
    tree.heading("cost", text="Cost/Day (VND)", anchor=tk.E)

    # Define column properties
    tree.column("room_number", width=100, anchor=tk.CENTER)
    tree.column("type", width=200)
    tree.column("department", width=200)
    tree.column("cost", width=150, anchor=tk.E)

    # --- Helper function to refresh data ---
    def refresh_available_rooms():
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        try:
            # Call the core logic function to get available rooms
            # *** IMPORTANT: Ensure get_available_rooms(conn) exists in core_logic.py ***
            # It should return success_flag, list_of_room_dicts
            # Each dict should have keys like 'RoomNumber', 'TypeName', 'DepartmentName', 'BaseCost'
            success, rooms_data = get_available_rooms(conn)

            if success:
                if rooms_data:
                    for room in rooms_data:
                        tree.insert("", tk.END, values=(
                            room.get('RoomNumber', 'N/A'),
                            room.get('TypeName', 'N/A'),
                            room.get('DepartmentName', 'N/A'),
                            format_currency(room.get('BaseCost', 0.0)) # Format cost
                        ))
                else:
                    # Optionally display a message in the tree or a label
                    tree.insert("", tk.END, values=("No available rooms found.", "", "", ""))
            else:
                messagebox.showerror("Error", f"Failed to fetch available rooms:\n{rooms_data}", parent=avail_window)

        except NameError:
             messagebox.showerror("Code Error", "Function 'get_available_rooms' not found in core_logic.py.", parent=avail_window)
        except MySQLError as db_err:
             messagebox.showerror("Database Error", f"Error fetching rooms: {db_err}", parent=avail_window)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}", parent=avail_window)
    # --- End Helper function ---

    # Button frame
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(pady=10)

    # Refresh Button
    refresh_btn = tk.Button(
        button_frame,
        text="Refresh List",
        command=refresh_available_rooms
    )
    apply_styles(refresh_btn)
    refresh_btn.pack(side=tk.LEFT, padx=10)

    # Close Button
    close_btn = tk.Button(
        button_frame,
        text="Close",
        command=avail_window.destroy
    )
    apply_styles(close_btn)
    close_btn.pack(side=tk.LEFT, padx=10)

    # Load initial data
    refresh_available_rooms()

    avail_window.focus_set()
def create_invoice_gui(conn):
    """GUI Tạo Hóa Đơn Chi Tiết có Scrollbar và nhập % BH thủ công"""
    invoice_window = tk.Toplevel()
    invoice_window.title("Create Detailed Invoice - Manual Discount")
    invoice_window.geometry("980x800")
    invoice_window.config(bg=BG_COLOR)

    # --- Setup Canvas và Scrollbar ---
    container = tk.Frame(invoice_window, bg=BG_COLOR)
    container.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    main_frame = tk.Frame(canvas, bg=BG_COLOR, padx=15, pady=15)
    main_frame_window_id = canvas.create_window((0, 0), window=main_frame, anchor="nw")

    def configure_scroll_region(event=None): canvas.configure(scrollregion=canvas.bbox("all"))
    def configure_frame_width(event): canvas.itemconfig(main_frame_window_id, width=event.width)
    main_frame.bind("<Configure>", configure_scroll_region)
    canvas.bind("<Configure>", configure_frame_width)
    def _on_mousewheel(event):
        scroll_amount = 0; delta = getattr(event, 'delta', 0); num = getattr(event, 'num', 0)
        if delta: scroll_amount = -1 * int(delta / 60)
        elif num in (4, 5): scroll_amount = -1 if num == 4 else 1
        if scroll_amount: canvas.yview_scroll(scroll_amount, "units")
    # Bind mousewheel primarily to the canvas
    canvas.bind("<MouseWheel>", _on_mousewheel)
    canvas.bind("<Button-4>", _on_mousewheel) # For Linux scroll up
    canvas.bind("<Button-5>", _on_mousewheel) # For Linux scroll down


    # --- Biến trạng thái ---
    current_patient_id = tk.StringVar(value="")
    patient_info_var = tk.StringVar(value="No patient selected")
    selected_room_info = {'id': None, 'name': 'N/A', 'rate': 0.0}
    # Initialize original_costs with floats
    original_costs = {'prescription': 0.0, 'room': 0.0, 'service': 0.0}
    calculated_costs = {'discount': 0.0, 'final_amount': 0.0, 'notes': ""}
    all_services_list = []
    room_availability_data = []

    # --- Style cho Treeview ---
    style = ttk.Style()
    style.configure("Custom.Treeview", font=TREEVIEW_FONT, rowheight=int(TREEVIEW_FONT[1]*2.5))
    style.configure("Custom.Treeview.Heading", font=(TREEVIEW_FONT[0], TREEVIEW_FONT[1], 'bold'))

    # --- 1. Patient Search Section ---
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=(0, 10))
    tk.Label(search_frame, text="Patient Name/ID:", bg=BG_COLOR, font=LABEL_FONT).pack(side=tk.LEFT, padx=5)
    patient_search_entry = tk.Entry(search_frame, width=30, font=LABEL_FONT)
    patient_search_entry.pack(side=tk.LEFT, padx=5, ipady=2)
    apply_styles(patient_search_entry)
    search_btn = tk.Button(search_frame, text="Search") # Command gán sau
    search_btn.pack(side=tk.LEFT, padx=5)
    apply_styles(search_btn)
    patient_info_label = tk.Label(main_frame, textvariable=patient_info_var, bg=ENTRY_BG, fg=TEXT_COLOR, font=LABEL_FONT, relief=tk.SUNKEN, anchor='w', padx=5, wraplength=900)
    patient_info_label.pack(fill=tk.X, pady=(0, 10), ipady=3)

    # --- 2. Prescription Details Section ---
    pres_frame = tk.LabelFrame(main_frame, text="Prescription Details", bg=BG_COLOR, fg=TEXT_COLOR, padx=5, pady=5, font=LABEL_FONT)
    pres_frame.pack(fill=tk.X, pady=(0, 10))
    pres_tree_scroll = ttk.Scrollbar(pres_frame)
    pres_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # Add a hidden column to store the raw numeric total
    pres_cols = ("med", "dose", "qty", "price", "total_display", "raw_total")
    pres_tree = ttk.Treeview(pres_frame, columns=pres_cols, displaycolumns=("med", "dose", "qty", "price", "total_display"), show="headings", height=5, yscrollcommand=pres_tree_scroll.set, style="Custom.Treeview")
    pres_tree.pack(fill=tk.BOTH, expand=True)
    pres_tree_scroll.config(command=pres_tree.yview)
    pres_tree.heading("med", text="Medicine"); pres_tree.heading("dose", text="Dosage"); pres_tree.heading("qty", text="Quantity", anchor=tk.E); pres_tree.heading("price", text="Price (VND)", anchor=tk.E); pres_tree.heading("total_display", text="Total (VND)", anchor=tk.E)
    pres_tree.column("med", width=250); pres_tree.column("dose", width=150); pres_tree.column("qty", width=80, anchor=tk.E); pres_tree.column("price", width=120, anchor=tk.E); pres_tree.column("total_display", width=120, anchor=tk.E)
    # Hide the raw_total column
    pres_tree.column("raw_total", width=0, stretch=tk.NO)


    # --- 3. Room Charges Section ---
    room_frame_outer = tk.LabelFrame(main_frame, text="Room Selection & Charges", bg=BG_COLOR, fg=TEXT_COLOR, padx=5, pady=5, font=LABEL_FONT)
    room_frame_outer.pack(fill=tk.X, pady=(0, 10))
    room_selection_frame = tk.Frame(room_frame_outer, bg=BG_COLOR); room_selection_frame.pack(fill=tk.X)
    room_avail_cols = ("type", "cost", "available", "total_r"); room_avail_tree = ttk.Treeview(room_selection_frame, columns=room_avail_cols, show="headings", height=4, style="Custom.Treeview"); room_avail_tree.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    room_avail_tree.heading("type", text="Room Type"); room_avail_tree.heading("cost", text="Cost/Day (VND)", anchor=tk.E); room_avail_tree.heading("available", text="Available", anchor=tk.CENTER); room_avail_tree.heading("total_r", text="Total Rooms", anchor=tk.CENTER)
    room_avail_tree.column("type", width=180); room_avail_tree.column("cost", width=120, anchor=tk.E); room_avail_tree.column("available", width=70, anchor=tk.CENTER); room_avail_tree.column("total_r", width=70, anchor=tk.CENTER)
    room_action_frame = tk.Frame(room_selection_frame, bg=BG_COLOR); room_action_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
    select_room_btn = tk.Button(room_action_frame, text="Select Type"); select_room_btn.pack(pady=5); apply_styles(select_room_btn)
    tk.Label(room_action_frame, text="Days:", bg=BG_COLOR, font=LABEL_FONT).pack(); days_entry = tk.Entry(room_action_frame, width=5, font=LABEL_FONT); days_entry.pack(); days_entry.insert(0,"1"); apply_styles(days_entry)
    room_display_frame = tk.Frame(room_frame_outer, bg=BG_COLOR, pady=5); room_display_frame.pack(fill=tk.X); room_display_frame.columnconfigure(1, weight=1); room_display_frame.columnconfigure(3, weight=1)
    tk.Label(room_display_frame, text="Selected Room:", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=0, padx=5, sticky='w'); selected_room_label = tk.Label(room_display_frame, text="N/A", bg=ENTRY_BG, font=LABEL_FONT, width=30, anchor='w', relief=tk.SUNKEN); selected_room_label.grid(row=0, column=1, padx=5, sticky='ew')
    tk.Label(room_display_frame, text="Room Subtotal:", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=2, padx=15, sticky='e'); room_subtotal_label = tk.Label(room_display_frame, text="0.00 VND", bg=ENTRY_BG, font=LABEL_FONT, width=20, anchor='e', relief=tk.SUNKEN); room_subtotal_label.grid(row=0, column=3, padx=5, sticky='ew'); apply_styles(room_subtotal_label)


    # --- 4. Service Charges Section ---
    svc_frame_outer = tk.LabelFrame(main_frame, text="Service Charges", bg=BG_COLOR, fg=TEXT_COLOR, padx=5, pady=5, font=LABEL_FONT)
    svc_frame_outer.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    svc_left_frame = tk.Frame(svc_frame_outer, bg=BG_COLOR); svc_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); svc_right_frame = tk.Frame(svc_frame_outer, bg=BG_COLOR, padx=10); svc_right_frame.pack(side=tk.RIGHT, fill=tk.Y)
    svc_tree_scroll = ttk.Scrollbar(svc_left_frame); svc_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # Add a hidden column to store the raw numeric total
    svc_cols = ("svc", "price_display", "qty", "total_display", "raw_total", "raw_price")
    svc_tree = ttk.Treeview(svc_left_frame, columns=svc_cols, displaycolumns=("svc", "price_display", "qty", "total_display"), show="headings", height=6, yscrollcommand=svc_tree_scroll.set, style="Custom.Treeview")
    svc_tree.pack(fill=tk.BOTH, expand=True); svc_tree_scroll.config(command=svc_tree.yview)
    svc_tree.heading("svc", text="Service"); svc_tree.heading("price_display", text="Price (VND)", anchor=tk.E); svc_tree.heading("qty", text="Quantity", anchor=tk.E); svc_tree.heading("total_display", text="Total (VND)", anchor=tk.E)
    svc_tree.column("svc", width=200); svc_tree.column("price_display", width=120, anchor=tk.E); svc_tree.column("qty", width=80, anchor=tk.E); svc_tree.column("total_display", width=120, anchor=tk.E)
    # Hide raw columns
    svc_tree.column("raw_total", width=0, stretch=tk.NO)
    svc_tree.column("raw_price", width=0, stretch=tk.NO)

    tk.Label(svc_right_frame, text="Service:", bg=BG_COLOR, font=LABEL_FONT).pack(anchor='w'); service_var = tk.StringVar(); service_combo = ttk.Combobox(svc_right_frame, textvariable=service_var, state="readonly", width=25, font=LABEL_FONT); service_combo.pack(pady=5)
    tk.Label(svc_right_frame, text="Qty:", bg=BG_COLOR, font=LABEL_FONT).pack(anchor='w'); service_qty_entry = tk.Entry(svc_right_frame, width=10, font=LABEL_FONT); service_qty_entry.pack(pady=5); service_qty_entry.insert(0, "1"); apply_styles(service_qty_entry)
    add_svc_btn = tk.Button(svc_right_frame, text="Add Service"); add_svc_btn.pack(pady=10); apply_styles(add_svc_btn)
    remove_svc_btn = tk.Button(svc_right_frame, text="Remove Selected"); remove_svc_btn.pack(pady=5); apply_styles(remove_svc_btn)

    # --- 5. Insurance Information Display ---
    insurance_display_frame = tk.LabelFrame(main_frame, text="Active Insurance Policy", bg=BG_COLOR, fg=TEXT_COLOR, padx=5, pady=5, font=LABEL_FONT)
    insurance_display_frame.pack(fill=tk.X, pady=(0, 10))
    insurance_text = scrolledtext.ScrolledText(insurance_display_frame, height=5, wrap=tk.WORD, font=LABEL_FONT, state=tk.DISABLED, bg=ENTRY_BG)
    insurance_text.pack(fill=tk.X, expand=True, padx=5, pady=5)
    insurance_text.insert(tk.END, "Search for a patient to view insurance information and coverage details.")


    # --- 6. Manual Discount Application Section ---
    discount_frame = tk.LabelFrame(main_frame, text="Apply Manual Discount (%) - Enter percentage (0-100)", bg=BG_COLOR, fg=TEXT_COLOR, padx=10, pady=10, font=LABEL_FONT)
    discount_frame.pack(fill=tk.X, pady=(0,10))
    discount_frame.columnconfigure(1, weight=1); discount_frame.columnconfigure(3, weight=1)
    tk.Label(discount_frame, text="Cost Type", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=0, padx=5, sticky='w'); tk.Label(discount_frame, text="Discount %", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=1, padx=5, sticky='ew'); tk.Label(discount_frame, text="Discount Amount", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=2, padx=5, sticky='e'); tk.Label(discount_frame, text="Amount After Disc.", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=3, padx=5, sticky='e')
    tk.Label(discount_frame, text="Medicine:", bg=BG_COLOR, font=LABEL_FONT).grid(row=1, column=0, padx=5, pady=2, sticky='w'); med_discount_percent_entry = tk.Entry(discount_frame, width=6, font=LABEL_FONT, justify='right'); med_discount_percent_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew'); med_discount_percent_entry.insert(0,"0"); apply_styles(med_discount_percent_entry); med_discount_amount_label = tk.Label(discount_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', width=15); med_discount_amount_label.grid(row=1, column=2, padx=5, pady=2, sticky='ew'); med_after_discount_label = tk.Label(discount_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', width=15); med_after_discount_label.grid(row=1, column=3, padx=5, pady=2, sticky='ew')
    tk.Label(discount_frame, text="Room:", bg=BG_COLOR, font=LABEL_FONT).grid(row=2, column=0, padx=5, pady=2, sticky='w'); room_discount_percent_entry = tk.Entry(discount_frame, width=6, font=LABEL_FONT, justify='right'); room_discount_percent_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew'); room_discount_percent_entry.insert(0,"0"); apply_styles(room_discount_percent_entry); room_discount_amount_label = tk.Label(discount_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', width=15); room_discount_amount_label.grid(row=2, column=2, padx=5, pady=2, sticky='ew'); room_after_discount_label = tk.Label(discount_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', width=15); room_after_discount_label.grid(row=2, column=3, padx=5, pady=2, sticky='ew')
    tk.Label(discount_frame, text="Services:", bg=BG_COLOR, font=LABEL_FONT).grid(row=3, column=0, padx=5, pady=2, sticky='w'); svc_discount_percent_entry = tk.Entry(discount_frame, width=6, font=LABEL_FONT, justify='right'); svc_discount_percent_entry.grid(row=3, column=1, padx=5, pady=2, sticky='ew'); svc_discount_percent_entry.insert(0,"0"); apply_styles(svc_discount_percent_entry); svc_discount_amount_label = tk.Label(discount_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', width=15); svc_discount_amount_label.grid(row=3, column=2, padx=5, pady=2, sticky='ew'); svc_after_discount_label = tk.Label(discount_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', width=15); svc_after_discount_label.grid(row=3, column=3, padx=5, pady=2, sticky='ew')

    # --- 7. Calculation Summary Section ---
    summary_frame = tk.LabelFrame(main_frame, text="Invoice Summary", bg=BG_COLOR, fg=TEXT_COLOR, padx=10, pady=10, font=LABEL_FONT)
    summary_frame.pack(fill=tk.X, pady=(0, 10))
    summary_frame.columnconfigure(1, weight=1)
    tk.Label(summary_frame, text="Subtotal (Original):", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=0, padx=5, sticky='e'); subtotal_val_label = tk.Label(summary_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', relief=tk.SUNKEN, width=25); subtotal_val_label.grid(row=0, column=1, padx=5, sticky='ew'); apply_styles(subtotal_val_label)
    tk.Label(summary_frame, text="Total Manual Discount:", bg=BG_COLOR, font=LABEL_FONT).grid(row=1, column=0, padx=5, sticky='e'); discount_val_label = tk.Label(summary_frame, text="0.00 VND", font=LABEL_FONT, anchor='e', relief=tk.SUNKEN, width=25); discount_val_label.grid(row=1, column=1, padx=5, sticky='ew'); apply_styles(discount_val_label)
    tk.Label(summary_frame, text="FINAL AMOUNT DUE:", bg=BG_COLOR, font=TITLE_FONT).grid(row=2, column=0, padx=5, pady=5, sticky='e'); final_amount_val_label = tk.Label(summary_frame, text="0.00 VND", fg=ACCENT_COLOR, font=TITLE_FONT, anchor='e', relief=tk.SUNKEN, width=25); final_amount_val_label.grid(row=2, column=1, padx=5, pady=5, sticky='ew'); apply_styles(final_amount_val_label)

    # --- 8. Action Buttons Section ---
    action_frame = tk.Frame(main_frame, bg=BG_COLOR)
    action_frame.pack(pady=(10, 20)) # Tăng pady dưới
    calc_subtotals_btn = tk.Button(action_frame, text="Calculate Subtotals")
    calc_subtotals_btn.pack(side=tk.LEFT, padx=10)
    apply_styles(calc_subtotals_btn)
    create_invoice_btn = tk.Button(action_frame, text="Create Invoice", state=tk.DISABLED)
    create_invoice_btn.pack(side=tk.LEFT, padx=10)
    apply_styles(create_invoice_btn)
    close_btn = tk.Button(action_frame, text="Close", command=invoice_window.destroy)
    close_btn.pack(side=tk.LEFT, padx=10)
    apply_styles(close_btn)

    # --- Helper and Action Functions ---

    def format_currency(value):
        try: return f"{float(value):,.0f} VND" # Format as integer VND
        except: return "0 VND"

    # --- MODIFIED: get_total_from_tree ---
    def get_total_from_tree(tree, raw_total_col_id):
        """Gets the sum of raw numeric totals from a specified column ID."""
        total = 0.0
        try:
            # Get the integer index of the column identifier
            # This might raise ValueError if raw_total_col_id is not in tree['columns']
            col_index = tree['columns'].index(raw_total_col_id)
        except ValueError:
            print(f"Error: Column '{raw_total_col_id}' not found in treeview columns: {tree['columns']}")
            # Return 0 or raise an error, depending on desired behavior
            return 0.0 # Return 0 for now

        for item_id in tree.get_children():
            try:
                # Retrieve the list of values for the current item
                item_values = tree.item(item_id, 'values')
                # Access the raw numeric value using the determined integer index
                raw_total_val = item_values[col_index]
                total += float(raw_total_val) # Ensure it's float for calculation
            except (ValueError, IndexError, TypeError) as e:
                 # Log error for the specific item and continue
                 print(f"Error processing item {item_id}, column index {col_index}: {e}. Values: {item_values}")
                 continue # Skip problematic rows
        return total
    # --- END MODIFIED: get_total_from_tree ---

    def clear_all_details():
        patient_info_var.set("No patient selected"); current_patient_id.set("")
        for item in pres_tree.get_children(): pres_tree.delete(item)
        selected_room_info.update({'id': None, 'name': 'N/A', 'rate': 0.0}); selected_room_label.config(text="N/A"); days_entry.delete(0, tk.END); days_entry.insert(0,"1"); update_room_subtotal()
        for item in svc_tree.get_children(): svc_tree.delete(item)
        insurance_text.config(state=tk.NORMAL); insurance_text.delete(1.0, tk.END); insurance_text.insert(tk.END, "Search patient..."); insurance_text.config(state=tk.DISABLED)
        subtotal_val_label.config(text=format_currency(0.0)); discount_val_label.config(text=format_currency(0.0)); final_amount_val_label.config(text=format_currency(0.0))
        med_discount_percent_entry.delete(0,tk.END); med_discount_percent_entry.insert(0,"0"); med_discount_amount_label.config(text="0.00 VND"); med_after_discount_label.config(text="0.00 VND")
        room_discount_percent_entry.delete(0,tk.END); room_discount_percent_entry.insert(0,"0"); room_discount_amount_label.config(text="0.00 VND"); room_after_discount_label.config(text="0.00 VND")
        svc_discount_percent_entry.delete(0,tk.END); svc_discount_percent_entry.insert(0,"0"); svc_discount_amount_label.config(text="0.00 VND"); svc_after_discount_label.config(text="0.00 VND")
        # Reset original costs to floats
        original_costs.update({'prescription': 0.0, 'room': 0.0, 'service': 0.0})
        calculated_costs.update({'discount': 0.0, 'final_amount': 0.0, 'notes': ""})
        create_invoice_btn.config(state=tk.DISABLED)
        main_frame.update_idletasks(); canvas.config(scrollregion=canvas.bbox("all")); canvas.yview_moveto(0)

    def search_patient_action():
        search_term = patient_search_entry.get().strip();
        if not search_term: return messagebox.showwarning("Input Required", "Enter Patient Name/ID.")
        clear_all_details()
        try:
            p_id = int(search_term) if search_term.isdigit() else None
            success, result = search_patient(conn, patient_id=p_id, name=None if p_id else search_term)
            if not success or not result: return messagebox.showinfo("Not Found", f"Patient not found: '{search_term}'.")
            patient_data = result[0]
            if len(result) > 1: messagebox.showinfo("Multiple Found", "Using first result.")
            p_id = patient_data['PatientID']; p_name = patient_data['PatientName']; p_dob = patient_data['DateOfBirth']; p_phone = patient_data.get('PhoneNumber', 'N/A')
            current_patient_id.set(str(p_id)); patient_info_var.set(f"ID: {p_id} | Name: {p_name} | DoB: {p_dob} | Phone: {p_phone}")
            load_prescription_details(p_id); display_insurance_info(p_id)
            calculate_subtotals_action() # Calculate initial subtotals and update summary
            main_frame.update_idletasks(); canvas.config(scrollregion=canvas.bbox("all"))
        except Exception as e: messagebox.showerror("Search Error", f"Error: {str(e)}"); clear_all_details()
    search_btn.config(command=search_patient_action)

    def load_prescription_details(p_id):
        for item in pres_tree.get_children(): pres_tree.delete(item)
        try:
            success, prescriptions = get_patient_prescriptions(conn, p_id)
            if success and prescriptions:
                for pres in prescriptions:
                    price = float(pres.get('MedicineCost', 0.0)) # Ensure float
                    qty = int(pres.get('QuantityPrescribed', 0)) # Ensure int
                    raw_total = qty * price
                    # Store raw total in the hidden column 'raw_total'
                    pres_tree.insert("", tk.END, values=(
                        pres.get('MedicineName', 'N/A'),
                        pres.get('Dosage', ''),
                        qty,
                        format_currency(price),
                        format_currency(raw_total), # Display formatted total
                        raw_total                     # Store raw total
                    ))
            # After loading, recalculate subtotals
            calculate_subtotals_action()
        except Exception as e:
            print(f"Error loading prescriptions: {e}")
            messagebox.showerror("Prescription Load Error", f"Could not load prescriptions: {e}")

    def load_room_availability():
        for item in room_avail_tree.get_children(): room_avail_tree.delete(item)
        try:
            success, rooms_data = get_room_types_with_availability(conn)
            if success and rooms_data:
                room_availability_data[:] = rooms_data
                for room in rooms_data:
                    ravail = room.get('AvailableCount', 0); tag = ('unavailable',) if ravail <= 0 else ()
                    room_avail_tree.insert("", tk.END, values=(room.get('TypeName', 'N/A'), format_currency(room.get('BaseCost', 0.0)), ravail, room.get('TotalRooms', 0)), tags=tag)
                room_avail_tree.tag_configure('unavailable', foreground='red', font=(TREEVIEW_FONT[0], TREEVIEW_FONT[1], 'italic'))
        except Exception as e: print(f"Error loading rooms: {e}")
    load_room_availability()

    def select_room_type_action():
        selected_item = room_avail_tree.selection();
        if not selected_item: return messagebox.showwarning("Selection Required", "Select room type.")
        item_values = room_avail_tree.item(selected_item[0], 'values'); item_tags = room_avail_tree.item(selected_item[0], 'tags')
        if 'unavailable' in item_tags: return messagebox.showerror("Room Unavailable", f"'{item_values[0]}' unavailable.")
        try:
            room_name = item_values[0]; room_rate = 0.0; room_type_id = None
            # Find the room details from the stored data
            for r_info in room_availability_data:
                 if r_info['TypeName'] == room_name:
                     room_type_id = r_info['RoomTypeID']
                     # Ensure BaseCost is fetched as float
                     room_rate = float(r_info.get('BaseCost', 0.0))
                     break
            if room_type_id is None: return messagebox.showerror("Error", "Could not retrieve room rate.")
            selected_room_info.update({'id': room_type_id, 'name': room_name, 'rate': room_rate})
            selected_room_label.config(text=f"{room_name} ({format_currency(room_rate)}/day)")
            # Update room subtotal and then recalculate all subtotals/summary
            update_room_subtotal()
            calculate_subtotals_action()
        except Exception as e: messagebox.showerror("Error Selecting Room", f"Error: {str(e)}"); selected_room_info.update({'id': None, 'name': 'N/A', 'rate': 0.0}); selected_room_label.config(text="N/A"); update_room_subtotal()
    select_room_btn.config(command=select_room_type_action)
    # Bind KeyRelease on days_entry to recalculate everything
    days_entry.bind("<KeyRelease>", lambda e: calculate_subtotals_action())

    def update_room_subtotal():
        """Updates the room subtotal label and original_costs['room']. Returns the calculated total."""
        try:
            rate = float(selected_room_info.get('rate', 0.0)) # Ensure float
            days_str = days_entry.get()
            if not days_str.isdigit() or int(days_str) < 0:
                days = 0
            else:
                days = int(days_str)
            total = rate * days
            original_costs['room'] = total # Update original_costs
            room_subtotal_label.config(text=format_currency(total))
            return total
        except ValueError as ve:
            print(f"Error in update_room_subtotal (ValueError): {ve}")
            original_costs['room'] = 0.0
            room_subtotal_label.config(text="Error")
            return 0.0
        except Exception as e:
            print(f"Unexpected error in update_room_subtotal: {e}")
            original_costs['room'] = 0.0
            room_subtotal_label.config(text="Error")
            return 0.0

    def load_services_list():
        try:
            success, services = get_all_services(conn)
            if success and services:
                all_services_list[:] = services
                # Store service info along with display text
                service_display_list = []
                for s in services:
                    cost = float(s.get('ServiceCost', 0.0)) # Ensure float
                    display_text = f"{s['ServiceName']} ({format_currency(cost)})"
                    service_display_list.append(display_text)
                service_combo['values'] = service_display_list
            else:
                 messagebox.showerror("Service Load Error", "Could not load services list.")
        except Exception as e:
            print(f"Error loading services: {e}")
            messagebox.showerror("Service Load Error", f"Error loading services: {e}")
    load_services_list()

    def add_service_action():
        selected_text = service_var.get(); qty_str = service_qty_entry.get().strip()
        if not selected_text: return messagebox.showwarning("Input Required", "Select service.")
        if not current_patient_id.get(): return messagebox.showwarning("Patient Required", "Search patient first.")
        try: qty = int(qty_str); assert qty > 0
        except: return messagebox.showwarning("Input Error", "Quantity must be positive integer.")
        try:
            # Find the service details from the stored list based on display text
            s_info = None
            for s in all_services_list:
                cost = float(s.get('ServiceCost', 0.0))
                display_text = f"{s['ServiceName']} ({format_currency(cost)})"
                if display_text == selected_text:
                    s_info = s
                    break

            if s_info:
                raw_price = float(s_info.get('ServiceCost', 0.0)) # Ensure float
                raw_total = raw_price * qty
                # Store raw price and raw total in hidden columns
                svc_tree.insert("", tk.END, values=(
                    s_info['ServiceName'],
                    format_currency(raw_price), # Display formatted price
                    qty,
                    format_currency(raw_total), # Display formatted total
                    raw_total,                  # Store raw total
                    raw_price                   # Store raw price
                ))
                service_var.set(""); service_qty_entry.delete(0, tk.END); service_qty_entry.insert(0, "1")
                calculate_subtotals_action() # Recalculate totals and summary
            else: messagebox.showerror("Error", "Could not find service details for the selected item.")
        except Exception as e: messagebox.showerror("Error Adding Service", f"Error: {str(e)}")
    add_svc_btn.config(command=add_service_action)

    def remove_service_action():
        selected = svc_tree.selection();
        if not selected: return messagebox.showwarning("Selection Required", "Select service to remove.")
        if messagebox.askyesno("Confirm Removal", "Remove selected service(s)?"):
            for item_id in selected: svc_tree.delete(item_id)
            calculate_subtotals_action() # Recalculate totals and summary
    remove_svc_btn.config(command=remove_service_action)

    def display_insurance_info(p_id):
        """Hiển thị thông tin bảo hiểm và CoverageDetails."""
        insurance_text.config(state=tk.NORMAL); insurance_text.delete(1.0, tk.END)
        try:
            ins_info = get_active_insurance_info(conn, p_id) # Chỉ lấy các cột có trong DB
            if ins_info:
                details = f"Provider: {ins_info.get('InsuranceProvider', 'N/A')}\n"
                details += f"Policy: {ins_info.get('PolicyNumber', 'N/A')}\n"
                details += f"BHYT No: {ins_info.get('BHYTCardNumber', 'N/A')}\n"
                details += f"Valid: {ins_info.get('EffectiveDate', 'N/A')} to {ins_info.get('EndDate', 'N/A')}\n"
                coverage_db = ins_info.get('CoverageDetails', '') # Là TEXT
                details += f"Coverage Details (from DB): {coverage_db if coverage_db else '(No specific details provided)'}"
                insurance_text.insert(tk.END, details)
            else: insurance_text.insert(tk.END, "No active insurance found.")
        except Exception as e: insurance_text.insert(tk.END, f"Error loading insurance: {str(e)}")
        finally: insurance_text.config(state=tk.DISABLED)

    # --- MODIFIED: update_final_summary ---
    def update_final_summary():
        """Tính toán tổng chiết khấu và tổng cuối cùng dựa trên % nhập thủ công."""
        try:
            # Ensure original costs are floats
            med_orig = float(original_costs.get('prescription', 0.0))
            room_orig = float(original_costs.get('room', 0.0))
            svc_orig = float(original_costs.get('service', 0.0))

            # Get discount percentages, default to 0.0 if empty or invalid
            try: med_perc = float(med_discount_percent_entry.get())
            except ValueError: med_perc = 0.0
            try: room_perc = float(room_discount_percent_entry.get())
            except ValueError: room_perc = 0.0
            try: svc_perc = float(svc_discount_percent_entry.get())
            except ValueError: svc_perc = 0.0

            # Clamp percentages between 0 and 100
            med_perc = max(0.0, min(100.0, med_perc))
            room_perc = max(0.0, min(100.0, room_perc))
            svc_perc = max(0.0, min(100.0, svc_perc))

            # Calculate discounts and final amounts for each category
            med_after, med_disc_amt = calculate_discount_from_percentage(med_orig, med_perc)
            room_after, room_disc_amt = calculate_discount_from_percentage(room_orig, room_perc)
            svc_after, svc_disc_amt = calculate_discount_from_percentage(svc_orig, svc_perc)

            # Update discount labels
            med_discount_amount_label.config(text=format_currency(med_disc_amt))
            med_after_discount_label.config(text=format_currency(med_after))
            room_discount_amount_label.config(text=format_currency(room_disc_amt))
            room_after_discount_label.config(text=format_currency(room_after))
            svc_discount_amount_label.config(text=format_currency(svc_disc_amt))
            svc_after_discount_label.config(text=format_currency(svc_after))

            # Calculate overall totals (ensure all operands are floats)
            total_discount = float(med_disc_amt) + float(room_disc_amt) + float(svc_disc_amt)
            final_amount = (med_orig + room_orig + svc_orig) - total_discount
            final_amount = max(0.0, final_amount) # Ensure final amount is not negative

            # Store calculated values
            calculated_costs['discount'] = total_discount
            calculated_costs['final_amount'] = final_amount

            # Update summary labels
            discount_val_label.config(text=format_currency(total_discount))
            final_amount_val_label.config(text=format_currency(final_amount))

            # Enable/disable create invoice button based on whether there's a cost
            if med_orig > 0 or room_orig > 0 or svc_orig > 0:
                create_invoice_btn.config(state=tk.NORMAL)
            else:
                create_invoice_btn.config(state=tk.DISABLED)

        except ValueError:
             # This block might not be strictly necessary now with the try-except for float conversion above
             # but kept for safety to reset invalid entries.
             if not med_discount_percent_entry.get().replace('.', '', 1).isdigit():
                 med_discount_percent_entry.delete(0,tk.END); med_discount_percent_entry.insert(0,"0")
             if not room_discount_percent_entry.get().replace('.', '', 1).isdigit():
                 room_discount_percent_entry.delete(0,tk.END); room_discount_percent_entry.insert(0,"0")
             if not svc_discount_percent_entry.get().replace('.', '', 1).isdigit():
                 svc_discount_percent_entry.delete(0,tk.END); svc_discount_percent_entry.insert(0,"0")
             # If an entry was invalid and reset, recalculate the summary with 0%
             update_final_summary()
        except Exception as e:
            print(f"Error in update_final_summary: {e}")
            messagebox.showerror("Calculation Error", f"Error updating summary: {e}")
            create_invoice_btn.config(state=tk.DISABLED)
    # --- END MODIFIED: update_final_summary ---


    # --- MODIFIED: calculate_subtotals_action ---
    def calculate_subtotals_action():
        """Tính tổng gốc và gọi cập nhật summary."""
        # No need to check for patient here, as it's called after patient search or item add/remove
        # if not current_patient_id.get(): return messagebox.showwarning("Patient Required", "Search patient first.")
        try:
            # Get subtotals using the raw numeric values stored in the treeviews
            med_sub = get_total_from_tree(pres_tree, "raw_total") # Use the ID of the raw total column
            room_sub = update_room_subtotal() # This already updates original_costs['room']
            svc_sub = get_total_from_tree(svc_tree, "raw_total") # Use the ID of the raw total column

            # Update original_costs dictionary with the latest subtotals (as floats)
            original_costs['prescription'] = float(med_sub)
            # original_costs['room'] is updated in update_room_subtotal()
            original_costs['service'] = float(svc_sub)

            # Calculate the overall subtotal (sum of floats)
            overall_subtotal = original_costs['prescription'] + original_costs['room'] + original_costs['service']

            # Update the display label for the original subtotal
            subtotal_val_label.config(text=format_currency(overall_subtotal))

            # CRITICAL: Call update_final_summary AFTER calculating and storing the latest original costs
            update_final_summary()

        except Exception as e:
            # Display the specific error in a message box
            messagebox.showerror("Subtotal Error", f"Error calculating subtotals: {str(e)}")
            # Disable button if calculation fails
            create_invoice_btn.config(state=tk.DISABLED)
            # Reset costs if error occurs
            original_costs.update({'prescription': 0.0, 'room': 0.0, 'service': 0.0})
            update_final_summary() # Try to update summary with zero costs
    # --- END MODIFIED: calculate_subtotals_action ---

    # --- MODIFIED: Event Bindings ---
    calc_subtotals_btn.config(command=calculate_subtotals_action)
    # Bind KeyRelease on discount entries to calculate_subtotals_action
    # This ensures original costs are updated before the final summary calculation
    med_discount_percent_entry.bind("<KeyRelease>", lambda e: calculate_subtotals_action())
    room_discount_percent_entry.bind("<KeyRelease>", lambda e: calculate_subtotals_action())
    svc_discount_percent_entry.bind("<KeyRelease>", lambda e: calculate_subtotals_action())
    # --- END MODIFIED: Event Bindings ---

    def save_invoice_action():
        """Lưu hóa đơn cuối cùng vào DB."""
        if not current_patient_id.get(): return messagebox.showerror("Error", "No patient selected.")
        if create_invoice_btn['state'] == tk.DISABLED: return messagebox.showwarning("Calculate First", "Calculate subtotals first or add items.")

        # Ensure costs are floats before saving
        p_id = int(current_patient_id.get())
        med_cost_orig = float(original_costs.get('prescription', 0.0))
        room_cost_orig = float(original_costs.get('room', 0.0))
        svc_cost_orig = float(original_costs.get('service', 0.0))
        discount = float(calculated_costs.get('discount', 0.0))
        final_amount = float(calculated_costs.get('final_amount', 0.0))

        # Tạo notes chi tiết (bao gồm cả % đã áp dụng)
        notes = f"--- INVOICE DETAILS (Patient ID: {p_id}) ---\n\n"
        notes += f"** Prescription Details (Original: {format_currency(med_cost_orig)}, Discount Applied: {med_discount_percent_entry.get()}%) **\n"
        if pres_tree.get_children():
            for i in pres_tree.get_children():
                 # Display name and formatted original total for the item
                 vals = pres_tree.item(i,'values')
                 notes += f"- {vals[0]}: {vals[4]}\n" # vals[4] is total_display
        else: notes += "- None\n"

        notes += f"\n** Room Charges (Original: {format_currency(room_cost_orig)}, Discount Applied: {room_discount_percent_entry.get()}%) **\n"
        notes += f"- {selected_room_info['name']} ({days_entry.get()} days): {format_currency(room_cost_orig)}\n" if room_cost_orig > 0 else "- None\n"

        notes += f"\n** Service Charges (Original: {format_currency(svc_cost_orig)}, Discount Applied: {svc_discount_percent_entry.get()}%) **\n"
        if svc_tree.get_children():
            for i in svc_tree.get_children():
                 # Display name and formatted original total for the item
                 vals = svc_tree.item(i,'values')
                 notes += f"- {vals[0]}: {vals[3]}\n" # vals[3] is total_display
        else: notes += "- None\n"

        notes += f"\n--- SUMMARY ---\nSubtotal (Original): {format_currency(med_cost_orig + room_cost_orig + svc_cost_orig)}\n"
        notes += f"Total Manual Discount: {format_currency(discount)}\n"
        notes += f"FINAL AMOUNT DUE: {format_currency(final_amount)}\n"
        calculated_costs['notes'] = notes

        # Gọi hàm lưu từ core_logic (Pass original costs and final calculated amounts)
        success, message, new_invoice_id = save_calculated_invoice(
            conn, p_id,
            med_cost_orig, room_cost_orig, svc_cost_orig, # Pass original costs
            discount, final_amount, # Pass calculated discount and final amount
            notes
        )
        if success: messagebox.showinfo("Success", f"Invoice #{new_invoice_id} created!"); invoice_window.destroy()
        else: messagebox.showerror("Save Error", f"Failed to save invoice: {message}")

    create_invoice_btn.config(command=save_invoice_action)

    # --- Final Setup ---
    center_window(invoice_window, 980, 800)
    main_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0) # Đảm bảo scroll lên đầu khi mở

    # Initial calculation after window setup
    calculate_subtotals_action()

    invoice_window.mainloop()
def create_insurance_gui(conn):
    """GUI for creating insurance records"""
    insurance_window = tk.Toplevel()
    insurance_window.title("Create Insurance Record")
    insurance_window.geometry("500x400")
    insurance_window.config(bg=BG_COLOR)
    center_window(insurance_window)
    
    # Main frame
    main_frame = tk.Frame(insurance_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    patient_id_entry = tk.Entry(form_frame)
    patient_id_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(patient_id_entry)
    
    # Insurance Provider
    tk.Label(form_frame, text="Insurance Provider:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    provider_entry = tk.Entry(form_frame)
    provider_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(provider_entry)
    
    # Policy Number
    tk.Label(form_frame, text="Policy Number:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    policy_entry = tk.Entry(form_frame)
    policy_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(policy_entry)
    
    # BHYT Card Number (optional)
    tk.Label(form_frame, text="BHYT Card Number (optional):", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    bhyt_entry = tk.Entry(form_frame)
    bhyt_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(bhyt_entry)
    
    # Effective Date
    tk.Label(form_frame, text="Effective Date (YYYY-MM-DD):", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    eff_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
    eff_date_entry.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    
    # End Date
    tk.Label(form_frame, text="End Date (YYYY-MM-DD):", bg=BG_COLOR).grid(row=5, column=0, sticky="e", pady=5)
    end_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
    end_date_entry.grid(row=5, column=1, pady=5, padx=5, sticky="ew")
    
    # Coverage Details
    tk.Label(form_frame, text="Coverage Details:", bg=BG_COLOR).grid(row=6, column=0, sticky="e", pady=5)
    coverage_entry = tk.Text(form_frame, height=4, width=30)
    coverage_entry.grid(row=6, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(coverage_entry)
    
    def submit():
        patient_id = patient_id_entry.get()
        provider = provider_entry.get()
        policy_no = policy_entry.get()
        bhyt_no = bhyt_entry.get()
        eff_date = eff_date_entry.get()
        end_date = end_date_entry.get()
        coverage = coverage_entry.get("1.0", tk.END).strip()
        
        if not all([patient_id, provider, policy_no, eff_date, end_date]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        success, message = create_insurance(
            conn, patient_id, provider, policy_no, bhyt_no, 
            eff_date, end_date, coverage
        )
        
        if success:
            messagebox.showinfo("Success", message)
            insurance_window.destroy()
        else:
            messagebox.showerror("Error", message)
    
    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Create Insurance Record",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)
def search_patient_gui(conn):
    """GUI for searching patients"""
    search_window = tk.Toplevel()
    search_window.title("Search Patient")
    search_window.geometry("500x500")
    search_window.config(bg=BG_COLOR)
    center_window(search_window)
    
    # Main frame
    main_frame = tk.Frame(search_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Search options
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X)
    
    # Search by ID
    tk.Label(search_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(search_frame)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)
    
    # Search by Name
    tk.Label(search_frame, text="Patient Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(search_frame)
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)
    
    # Results area
    text_area = create_scrollable_text(main_frame)
    
    def search():
        patient_id = entry_id.get()
        name = entry_name.get()
        
        if not patient_id and not name:
            messagebox.showerror("Error", "Please enter either ID or name")
            search_window.focus_force()
            return
        
        success, result = search_patient(conn, patient_id if patient_id else None, name if name else None)
        
        text_area.delete(1.0, tk.END)
        
        if success:
            if result:
                for patient in result:
                    text_area.insert(tk.END, f"Patient ID: {patient['PatientID']}\n")
                    text_area.insert(tk.END, f"Name: {patient['PatientName']}\n")
                    text_area.insert(tk.END, f"DOB: {patient['DateOfBirth']}\n")
                    text_area.insert(tk.END, f"Gender: {patient['Gender']}\n")
                    text_area.insert(tk.END, f"Phone: {patient['PhoneNumber']}\n")
                    if patient['Address']:
                        text_area.insert(tk.END, f"Address: {patient['Address']}\n")
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No patients found\n")
        else:
            messagebox.showerror("Error", result)

    # Search button
    search_btn = tk.Button(
        main_frame,
        text="Search",
        command=search
    )
    apply_styles(search_btn)
    search_btn.pack(pady=10)
    
    # Configure grid weights
    search_frame.grid_columnconfigure(1, weight=1)

def schedule_appointment_gui(conn):
    """GUI for scheduling appointments"""
    appt_window = tk.Toplevel()
    appt_window.title("Schedule Appointment")
    appt_window.geometry("400x350")
    appt_window.config(bg=BG_COLOR)
    center_window(appt_window)
    
    # Main frame
    main_frame = tk.Frame(appt_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient = tk.Entry(form_frame)
    entry_patient.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient)
    
    # Doctor ID
    tk.Label(form_frame, text="Doctor ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_doctor = tk.Entry(form_frame)
    entry_doctor.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_doctor)
    
    # Date
    tk.Label(form_frame, text="Date (YYYY-MM-DD):", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_date = tk.Entry(form_frame)
    entry_date.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_date)
    
    # Time
    tk.Label(form_frame, text="Time (HH:MM):", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_time = tk.Entry(form_frame)
    entry_time.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_time)
    
    def submit():
        patient_id = entry_patient.get()
        doctor_id = entry_doctor.get()
        date = entry_date.get()
        time = entry_time.get()
        
        success, message = schedule_appointment(conn, patient_id, doctor_id, date, time)
        if success:
            messagebox.showinfo("Success", message)
            appt_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Schedule Appointment",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def view_appointments_gui(conn, role, user_id=None):
    """GUI for viewing appointments with filtering options"""
    view_window = tk.Toplevel()
    view_window.title("View Appointments")
    view_window.geometry("900x700")  # Increased size for better display
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    
    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Filter frame
    filter_frame = tk.Frame(main_frame, bg=BG_COLOR)
    filter_frame.pack(fill=tk.X, pady=10)
    
    # Date filters
    date_frame = tk.Frame(filter_frame, bg=BG_COLOR)
    date_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    
    # Year
    tk.Label(date_frame, text="Year:", bg=BG_COLOR).grid(row=0, column=0, padx=5)
    entry_year = tk.Entry(date_frame, width=10)
    entry_year.grid(row=0, column=1, padx=5)
    apply_styles(entry_year)
    
    # Month
    tk.Label(date_frame, text="Month:", bg=BG_COLOR).grid(row=0, column=2, padx=5)
    entry_month = tk.Entry(date_frame, width=10)
    entry_month.grid(row=0, column=3, padx=5)
    apply_styles(entry_month)
    
    # Day
    tk.Label(date_frame, text="Day:", bg=BG_COLOR).grid(row=0, column=4, padx=5)
    entry_day = tk.Entry(date_frame, width=10)
    entry_day.grid(row=0, column=5, padx=5)
    apply_styles(entry_day)
    
    # Status filter
    status_frame = tk.Frame(filter_frame, bg=BG_COLOR)
    status_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
    
    tk.Label(status_frame, text="Status:", bg=BG_COLOR).grid(row=0, column=0, padx=5)
    status_var = tk.StringVar(value="All")
    status_options = ["All", "Scheduled", "Completed", "Cancelled"]
    status_menu = tk.OptionMenu(status_frame, status_var, *status_options)
    status_menu.config(bg=BG_COLOR, width=15)
    status_menu.grid(row=0, column=1, padx=5)
    
    # Results area with improved formatting
    text_frame = tk.Frame(main_frame, bg=BG_COLOR)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    text_area = scrolledtext.ScrolledText(
        text_frame,
        wrap=tk.WORD,
        width=100,
        height=25,
        font=('Consolas', 10)
    )
    text_area.pack(fill=tk.BOTH, expand=True)
    
    def fetch_appointments():
        """Fetch and display appointments based on filters"""
        try:
            # Get filter values
            year = entry_year.get().strip()
            month = entry_month.get().strip()
            day = entry_day.get().strip()
            status = status_var.get() if status_var.get() != "All" else None
            
            # Convert to integers if provided
            year = int(year) if year else None
            month = int(month) if month else None
            day = int(day) if day else None
            
            # Fetch appointments
            success, result = view_appointments(
                conn, role, user_id, 
                year, month, day, status
            )
            
            # Clear previous results
            text_area.delete(1.0, tk.END)
            
            if not success:
                messagebox.showerror("Error", result)
                return
            
            if not result:
                text_area.insert(tk.END, "No appointments found matching the criteria.\n")
                return
            
            # Display appointments in a formatted way
            for appt in result:
                text_area.insert(tk.END, f"Appointment ID: {appt['AppointmentID']}\n")
                text_area.insert(tk.END, f"Date:       {appt['AppointmentDate']}\n")
                text_area.insert(tk.END, f"Time:       {appt['AppointmentTime']}\n")
                text_area.insert(tk.END, f"Status:     {appt['Status']}\n")
                text_area.insert(tk.END, f"Doctor:     {appt['DoctorName']} (ID: {appt['DoctorID']})\n")
                text_area.insert(tk.END, f"Patient:    {appt['PatientName']} (ID: {appt['PatientID']})\n")
                text_area.insert(tk.END, "-"*70 + "\n\n")
            
            text_area.insert(tk.END, f"\nTotal appointments found: {len(result)}\n")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for year/month/day")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(pady=10)
    
    # Fetch button
    fetch_btn = tk.Button(
        button_frame,
        text="Fetch Appointments",
        command=fetch_appointments,
        width=20
    )
    apply_styles(fetch_btn)
    fetch_btn.pack(side=tk.LEFT, padx=10)
    
    # Close button
    close_btn = tk.Button(
        button_frame,
        text="Close",
        command=view_window.destroy,
        width=20
    )
    apply_styles(close_btn)
    close_btn.pack(side=tk.LEFT, padx=10)
    
    # Configure grid weights
    filter_frame.grid_columnconfigure(0, weight=1)
    date_frame.grid_columnconfigure(6, weight=1)
    status_frame.grid_columnconfigure(2, weight=1)
    
    # Focus on window
    view_window.focus_set()

def update_appointment_status_gui(conn):
    """GUI for updating appointment status"""
    update_window = tk.Toplevel()
    update_window.title("Update Appointment Status")
    update_window.geometry("400x250")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    
    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Appointment ID
    tk.Label(form_frame, text="Appointment ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(form_frame)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)
    
    # Status
    tk.Label(form_frame, text="New Status:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    status_var = tk.StringVar()
    status_var.set("Scheduled")
    status_menu = ttk.OptionMenu(form_frame, status_var, "Scheduled", "Scheduled", "Completed", "Cancelled")
    status_menu.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    
    def submit():
        appt_id = entry_id.get()
        new_status = status_var.get()
        
        success, message = update_appointment_status(conn, appt_id, new_status)
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Update Status",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def create_prescription_gui(conn, doctor_id):
    """GUI tạo đơn thuốc mới (cho bác sĩ)"""
    pres_window = tk.Toplevel()
    pres_window.title("Create New Prescription")
    pres_window.geometry("1000x750")
    pres_window.config(bg=BG_COLOR)
    center_window(pres_window)
    
    # Main frame
    main_frame = tk.Frame(pres_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="New Prescription",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X, pady=(0, 15))
    form_frame.columnconfigure(1, weight=1)
    
    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR, anchor='e').grid(row=0, column=0, sticky="ew", pady=5, padx=(0,5))
    patient_id_entry = tk.Entry(form_frame)
    patient_id_entry.grid(row=0, column=1, pady=5, sticky="ew")
    apply_styles(patient_id_entry)
    
    # Appointment ID (optional)
    tk.Label(form_frame, text="Appointment ID (optional):", bg=BG_COLOR, anchor='e').grid(row=1, column=0, sticky="ew", pady=5, padx=(0,5))
    appointment_id_entry = tk.Entry(form_frame)
    appointment_id_entry.grid(row=1, column=1, pady=5, sticky="ew")
    apply_styles(appointment_id_entry)
    
    # Diagnosis
    tk.Label(form_frame, text="Diagnosis:", bg=BG_COLOR, anchor='e').grid(row=2, column=0, sticky="ew", pady=5, padx=(0,5))
    diagnosis_entry = tk.Entry(form_frame)
    diagnosis_entry.grid(row=2, column=1, pady=5, sticky="ew")
    apply_styles(diagnosis_entry)
    
    # Notes
    tk.Label(form_frame, text="Notes:", bg=BG_COLOR, anchor='ne').grid(row=3, column=0, sticky="nsew", pady=5, padx=(0,5))
    notes_entry = tk.Text(form_frame, height=4, width=40)
    notes_entry.grid(row=3, column=1, pady=5, sticky="ew")
    apply_styles(notes_entry)
    notes_scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=notes_entry.yview)
    notes_scrollbar.grid(row=3, column=2, sticky='ns')
    notes_entry['yscrollcommand'] = notes_scrollbar.set
    
    # Medicine frame
    med_frame = tk.LabelFrame(main_frame, text="Medicines", bg=BG_COLOR, fg=TEXT_COLOR, padx=10, pady=10)
    med_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Treeview for medicines
    columns = ("Medicine", "Dosage", "Frequency", "Duration", "Instruction", "Quantity")
    med_tree = ttk.Treeview(med_frame, columns=columns, show="headings")
    
    # Configure columns
    med_tree.heading("Medicine", text="Medicine")
    med_tree.heading("Dosage", text="Dosage")
    med_tree.heading("Frequency", text="Frequency")
    med_tree.heading("Duration", text="Duration")
    med_tree.heading("Instruction", text="Instruction")
    med_tree.heading("Quantity", text="Quantity")
    
    med_tree.column("Medicine", width=200)
    med_tree.column("Dosage", width=100)
    med_tree.column("Frequency", width=120)
    med_tree.column("Duration", width=100)
    med_tree.column("Instruction", width=200)
    med_tree.column("Quantity", width=80, anchor="center")
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(med_frame, orient="vertical", command=med_tree.yview)
    med_tree.configure(yscrollcommand=scrollbar.set)
    
    med_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Medicine input controls frame
    med_controls_frame = tk.Frame(med_frame, bg=BG_COLOR)
    med_controls_frame.pack(fill=tk.X, pady=5)
    
    # Medicine selection
    tk.Label(med_controls_frame, text="Medicine:", bg=BG_COLOR).grid(row=0, column=0, padx=5, sticky='e')
    med_var = tk.StringVar()
    med_dropdown = ttk.Combobox(med_controls_frame, textvariable=med_var, width=15)
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MedicineID, MedicineName FROM Medicine")
            medicines = cursor.fetchall()
            med_dropdown['values'] = [f"{m['MedicineID']} - {m['MedicineName']}" for m in medicines]
    except MySQLError as e:
        messagebox.showerror("Error", f"Failed to load medicines: {e}")
    
    med_dropdown.grid(row=0, column=1, padx=5, sticky='ew')
    
    # Dosage
    tk.Label(med_controls_frame, text="Dosage:", bg=BG_COLOR).grid(row=0, column=2, padx=5, sticky='e')
    dosage_entry = tk.Entry(med_controls_frame, width=10)
    dosage_entry.grid(row=0, column=3, padx=5, sticky='ew')
    
    # Frequency
    tk.Label(med_controls_frame, text="Frequency:", bg=BG_COLOR).grid(row=0, column=4, padx=5, sticky='e')
    freq_entry = tk.Entry(med_controls_frame, width=10)
    freq_entry.grid(row=0, column=5, padx=5, sticky='ew')
    
    # Duration
    tk.Label(med_controls_frame, text="Duration:", bg=BG_COLOR).grid(row=1, column=0, padx=5, sticky='e')
    duration_entry = tk.Entry(med_controls_frame, width=10)
    duration_entry.grid(row=1, column=1, padx=5, sticky='ew')
    
    # Instructions
    tk.Label(med_controls_frame, text="Instruction:", bg=BG_COLOR).grid(row=1, column=2, padx=5, sticky='e')
    instruction_entry = tk.Entry(med_controls_frame, width=10)
    instruction_entry.grid(row=1, column=3, columnspan=3, padx=5, sticky='ew')
    
    # Quantity
    tk.Label(med_controls_frame, text="Quantity:", bg=BG_COLOR).grid(row=1, column=6, padx=5, sticky='e')
    quantity_entry = tk.Entry(med_controls_frame, width=10)
    quantity_entry.grid(row=1, column=7, padx=5, sticky='ew')
    
    # Button frame
    btn_frame = tk.Frame(med_controls_frame, bg=BG_COLOR)
    btn_frame.grid(row=2, column=0, columnspan=8, pady=5, sticky='ew')
    
    # Configure grid weights for button frame
    for i in range(8):
        btn_frame.columnconfigure(i, weight=1)
    
    # Add button (larger)
    add_btn = tk.Button(
        btn_frame,
        text="Add Medicine",
        command=lambda: add_medicine(),
        width=8
    )
    apply_styles(add_btn)
    add_btn.grid(row=0, column=0, columnspan=3, padx=5, sticky='ew')
    
    # Remove button (larger)
    remove_btn = tk.Button(
        btn_frame,
        text="Remove Selected",
        command=lambda: remove_medicine(),
        width=8
    )
    apply_styles(remove_btn)
    remove_btn.grid(row=0, column=3, columnspan=3, padx=5, sticky='ew')
    
    # Clear button
    clear_btn = tk.Button(
        btn_frame,
        text="Clear Fields",
        command=lambda: clear_medicine_fields(),
        width=8
    )
    apply_styles(clear_btn)
    clear_btn.grid(row=0, column=6, padx=5, sticky='ew')
    
    # Move Up button
    up_btn = tk.Button(
        btn_frame,
        text="↑ Move Up",
        command=lambda: move_medicine_up(),
        width=8
    )
    apply_styles(up_btn)
    up_btn.grid(row=0, column=7, padx=5, sticky='ew')
    
    def add_medicine():
        med = med_var.get()
        dosage = dosage_entry.get()
        freq = freq_entry.get()
        duration = duration_entry.get()
        instruction = instruction_entry.get()
        quantity = quantity_entry.get()
        
        if not all([med, dosage, freq, quantity]):
            messagebox.showerror("Error", "Please fill all required fields (Medicine, Dosage, Frequency, Quantity)")
            return
            
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be a positive number")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return
            
        med_tree.insert("", "end", values=(med, dosage, freq, duration or "", instruction or "", quantity))
        clear_medicine_fields()
    
    def remove_medicine():
        selected = med_tree.selection()
        if selected:
            med_tree.delete(selected)
    
    def clear_medicine_fields():
        med_var.set("")
        dosage_entry.delete(0, tk.END)
        freq_entry.delete(0, tk.END)
        duration_entry.delete(0, tk.END)
        instruction_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
    
    def move_medicine_up():
        selected = med_tree.selection()
        if not selected:
            return
            
        selected_item = selected[0]
        prev_item = med_tree.prev(selected_item)
        
        if prev_item:
            # Get values
            values = med_tree.item(selected_item, 'values')
            prev_values = med_tree.item(prev_item, 'values')
            
            # Swap values
            med_tree.item(prev_item, values=values)
            med_tree.item(selected_item, values=prev_values)
            
            # Reselect the item
            med_tree.selection_set(selected_item)
    
    # Submit button frame
    submit_frame = tk.Frame(main_frame, bg=BG_COLOR)
    submit_frame.pack(fill=tk.X, pady=10)
    
    def submit_prescription():
        patient_id = patient_id_entry.get()
        appointment_id = appointment_id_entry.get()
        diagnosis = diagnosis_entry.get()
        notes = notes_entry.get("1.0", tk.END).strip()
        
        if not patient_id:
            messagebox.showerror("Error", "Patient ID is required")
            return
            
        if not med_tree.get_children():
            messagebox.showerror("Error", "Please add at least one medicine")
            return
            
        try:
            with conn.cursor() as cursor:
                # Check if appointment exists and belongs to this doctor and patient
                if appointment_id:
                    cursor.execute("""
                        SELECT AppointmentID FROM Appointments 
                        WHERE AppointmentID = %s 
                        AND DoctorID = %s 
                        AND PatientID = %s
                    """, (appointment_id, doctor_id, patient_id))
                    
                    if not cursor.fetchone():
                        messagebox.showerror("Error", "Appointment not found or doesn't match patient/doctor")
                        return
                
                # Create prescription
                cursor.execute("""
                    INSERT INTO Prescription (
                        AppointmentID, 
                        PatientID, 
                        DoctorID, 
                        PrescriptionDate, 
                        Diagnosis, 
                        Notes
                    )
                    VALUES (%s, %s, %s, CURDATE(), %s, %s)
                """, (
                    appointment_id if appointment_id else None,
                    patient_id,
                    doctor_id,
                    diagnosis or None,
                    notes or None
                ))
                
                pres_id = cursor.lastrowid
                
                # Add prescription details
                for item in med_tree.get_children():
                    med, dosage, freq, duration, instruction, quantity = med_tree.item(item)['values']
                    med_id = med.split(" - ")[0]  # Extract medicine ID
                    
                    cursor.execute("""
                        INSERT INTO PrescriptionDetails (
                            PrescriptionID, 
                            MedicineID, 
                            Dosage, 
                            Frequency, 
                            Duration, 
                            Instruction, 
                            QuantityPrescribed
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (pres_id, med_id, dosage, freq, duration or None, instruction or None, quantity))
                
                conn.commit()
                messagebox.showinfo("Success", f"Prescription #{pres_id} created successfully")
                
                # Offer to print prescription
                if messagebox.askyesno("Print Prescription", "Would you like to print this prescription?"):
                    export_prescription_pdf(conn, pres_id)
                
                pres_window.destroy()
                
        except MySQLError as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to create prescription: {e}")
    
    submit_btn = tk.Button(
        submit_frame,
        text="Submit Prescription",
        command=submit_prescription,
        width=20
    )
    apply_styles(submit_btn)
    submit_btn.pack()
# Thêm hàm generate_invoice_pdf vào core_logic.py
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
            
            # Invoice items
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



def view_invoices_gui(conn):
    """GUI for viewing invoices"""
    view_window = tk.Toplevel()
    view_window.title("View Invoices")
    view_window.geometry("700x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    
    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Filter frame
    filter_frame = tk.Frame(main_frame, bg=BG_COLOR)
    filter_frame.pack(fill=tk.X)
    
    # Patient ID (optional)
    tk.Label(filter_frame, text="Patient ID (leave empty for all):", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient = tk.Entry(filter_frame)
    entry_patient.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient)
    
    # Results area
    text_area = create_scrollable_text(main_frame, height=20, width=80)
    
    def fetch():
        patient_id = entry_patient.get()
        
        success, result = view_invoices(conn, patient_id if patient_id else None)
        
        text_area.delete(1.0, tk.END)
        
        if success:
            if result:
                for invoice in result:
                    text_area.insert(tk.END, f"Invoice ID: {invoice['InvoiceID']}\n")
                    text_area.insert(tk.END, f"Patient ID: {invoice['PatientID']}\n")
                    text_area.insert(tk.END, f"Date: {invoice['InvoiceDate']}\n")
                    text_area.insert(tk.END, f"Amount: {invoice['TotalAmount']:.2f} VND\n")
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No invoices found\n")
        else:
            messagebox.showerror("Error", result)

    # Fetch button
    fetch_btn = tk.Button(
        main_frame,
        text="Fetch Invoices",
        command=fetch
    )
    apply_styles(fetch_btn)
    fetch_btn.pack(pady=10)
    
    # Configure grid weights
    filter_frame.grid_columnconfigure(1, weight=1)

def view_room_statistics_gui(conn):
    """Hiển thị thống kê phòng"""
    stats_window = tk.Toplevel()
    stats_window.title("Room Statistics")
    stats_window.geometry("800x600")
    stats_window.config(bg=BG_COLOR)
    center_window(stats_window)
    
    # Main frame
    main_frame = tk.Frame(stats_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Room Statistics by Department",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Treeview for displaying data
    tree = ttk.Treeview(main_frame, columns=("Department", "Type", "Total", "Available", "Occupied"), show="headings")
    
    tree.heading("Department", text="Department")
    tree.heading("Type", text="Room Type")
    tree.heading("Total", text="Total Rooms")
    tree.heading("Available", text="Available")
    tree.heading("Occupied", text="Occupied")
    
    tree.column("Department", width=150)
    tree.column("Type", width=150)
    tree.column("Total", width=100, anchor="center")
    tree.column("Available", width=100, anchor="center")
    tree.column("Occupied", width=100, anchor="center")
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Fetch data
    success, result = get_room_statistics(conn)
    
    if success:
        for row in result:
            tree.insert("", "end", values=(
                row["DepartmentName"],
                row["TypeName"],
                row["TotalRooms"],
                row["AvailableRooms"],
                row["OccupiedRooms"]
            ))
    else:
        messagebox.showerror("Error", result)

def view_prescription_gui(conn, prescription_id):
    """GUI xem và xuất đơn thuốc"""
    view_window = tk.Toplevel()
    view_window.title(f"Prescription #{prescription_id}")
    view_window.geometry("800x600")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    
    # Main frame với scrollbar
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Frame chứa nội dung
    content_frame = tk.Frame(main_frame, bg=BG_COLOR)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(content_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Text widget để hiển thị thông tin
    text_area = tk.Text(
        content_frame,
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        bg=ENTRY_BG,
        font=LABEL_FONT,
        padx=10,
        pady=10
    )
    text_area.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_area.yview)
    
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin chính của đơn thuốc
            cursor.execute("""
                SELECT p.*, d.DoctorName, pt.PatientName, pt.DateOfBirth, pt.Gender
                FROM Prescription p
                JOIN Doctors d ON p.DoctorID = d.DoctorID
                JOIN Patients pt ON p.PatientID = pt.PatientID
                WHERE p.PrescriptionID = %s
            """, (prescription_id,))
            prescription = cursor.fetchone()
            
            if not prescription:
                messagebox.showerror("Error", "Prescription not found")
                view_window.destroy()
                return
            
            # Lấy chi tiết đơn thuốc
            cursor.execute("""
                SELECT pd.*, m.MedicineName, m.Unit
                FROM PrescriptionDetails pd
                JOIN Medicine m ON pd.MedicineID = m.MedicineID
                WHERE pd.PrescriptionID = %s
            """, (prescription_id,))
            details = cursor.fetchall()
            
            # Hiển thị thông tin
            text_area.insert(tk.END, "=== PRESCRIPTION DETAILS ===\n\n", "title")
            text_area.insert(tk.END, f"Prescription ID: {prescription_id}\n")
            text_area.insert(tk.END, f"Date: {prescription['PrescriptionDate']}\n\n")
            
            text_area.insert(tk.END, "=== PATIENT INFORMATION ===\n", "subtitle")
            text_area.insert(tk.END, f"Name: {prescription['PatientName']}\n")
            text_area.insert(tk.END, f"DOB: {prescription['DateOfBirth']}\n")
            text_area.insert(tk.END, f"Gender: {prescription['Gender']}\n\n")
            
            text_area.insert(tk.END, "=== DOCTOR INFORMATION ===\n", "subtitle")
            text_area.insert(tk.END, f"Doctor: {prescription['DoctorName']}\n\n")
            
            text_area.insert(tk.END, "=== DIAGNOSIS ===\n", "subtitle")
            text_area.insert(tk.END, f"{prescription['Diagnosis'] or 'Not specified'}\n\n")
            
            text_area.insert(tk.END, "=== PRESCRIBED MEDICINES ===\n", "subtitle")
            for med in details:
                text_area.insert(tk.END, f"\nMedicine: {med['MedicineName']}\n")
                text_area.insert(tk.END, f"Dosage: {med['Dosage']}\n")
                text_area.insert(tk.END, f"Frequency: {med['Frequency']}\n")
                text_area.insert(tk.END, f"Duration: {med['Duration'] or 'Not specified'}\n")
                text_area.insert(tk.END, f"Quantity: {med['QuantityPrescribed']} {med['Unit']}\n")
                text_area.insert(tk.END, "-"*50 + "\n")
            
            if prescription['Notes']:
                text_area.insert(tk.END, "\n=== ADDITIONAL NOTES ===\n", "subtitle")
                text_area.insert(tk.END, f"{prescription['Notes']}\n")
            
            # Định dạng text
            text_area.tag_config("title", font=("Helvetica", 14, "bold"))
            text_area.tag_config("subtitle", font=("Helvetica", 12, "bold"))
            
            # Không cho chỉnh sửa
            text_area.config(state=tk.DISABLED)
            
    except MySQLError as e:
        messagebox.showerror("Database Error", f"Failed to fetch prescription: {e}")
        view_window.destroy()
        return
    
    # Frame cho các nút
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(fill=tk.X, pady=10)
    
    # Thêm nút xuất PDF
    export_btn = tk.Button(
        button_frame,
        text="Export to PDF",
        command=lambda: export_prescription_pdf(conn, prescription_id),
        width=15
    )
    apply_styles(export_btn)
    export_btn.pack(side=tk.LEFT, padx=10)
    
    # Thêm nút đóng
    close_btn = tk.Button(
        button_frame,
        text="Close",
        command=view_window.destroy,
        width=15
    )
    apply_styles(close_btn)
    close_btn.pack(side=tk.RIGHT, padx=10)
def view_insurance_gui(conn):
    """GUI xem danh sách bảo hiểm"""
    insurance_window = tk.Toplevel()
    insurance_window.title("Insurance Records")
    insurance_window.geometry("900x600")
    insurance_window.config(bg=BG_COLOR)
    center_window(insurance_window)
    
    # Main frame
    main_frame = tk.Frame(insurance_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Search frame
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(search_frame, text="Patient ID:", bg=BG_COLOR).pack(side=tk.LEFT)
    patient_id_entry = tk.Entry(search_frame)
    patient_id_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(patient_id_entry)
    
    search_btn = tk.Button(
        search_frame,
        text="Search",
        command=lambda: search_insurance(conn, patient_id_entry.get(), text_area),
        width=10
    )
    apply_styles(search_btn)
    search_btn.pack(side=tk.LEFT, padx=5)
    
    # Results area
    text_area = create_scrollable_text(main_frame, height=25, width=100)
    
    # Search all initially
    search_insurance(conn, None, text_area)
    
    insurance_window.mainloop()

def search_insurance(conn, patient_id=None, text_area=None):
    """Tìm kiếm thông tin bảo hiểm"""
    try:
        with conn.cursor() as cursor:
            if patient_id:
                cursor.execute("""
                    SELECT i.*, p.PatientName
                    FROM Insurance i
                    JOIN Patients p ON i.PatientID = p.PatientID
                    WHERE i.PatientID = %s
                    ORDER BY i.EndDate DESC
                """, (patient_id,))
            else:
                cursor.execute("""
                    SELECT i.*, p.PatientName
                    FROM Insurance i
                    JOIN Patients p ON i.PatientID = p.PatientID
                    ORDER BY i.EndDate DESC
                """)
            
            insurances = cursor.fetchall()
            
            if text_area:
                text_area.delete(1.0, tk.END)
                
                if not insurances:
                    text_area.insert(tk.END, "No insurance records found\n")
                    return
                
                for ins in insurances:
                    text_area.insert(tk.END, f"Patient: {ins['PatientName']} (ID: {ins['PatientID']})\n")
                    text_area.insert(tk.END, f"Provider: {ins['InsuranceProvider']}\n")
                    text_area.insert(tk.END, f"Policy Number: {ins['PolicyNumber']}\n")
                    text_area.insert(tk.END, f"BHYT Card: {ins['BHYTCardNumber'] or 'N/A'}\n")
                    text_area.insert(tk.END, f"Valid: {ins['EffectiveDate']} to {ins['EndDate']}\n")
                    text_area.insert(tk.END, "-"*50 + "\n\n")
    
    except MySQLError as e:
        if text_area:
            text_area.insert(tk.END, f"Error: {str(e)}\n")

def view_prescriptions_gui(conn):
    """GUI xem danh sách đơn thuốc"""
    prescriptions_window = tk.Toplevel()
    prescriptions_window.title("Prescriptions")
    prescriptions_window.geometry("900x600")
    prescriptions_window.config(bg=BG_COLOR)
    center_window(prescriptions_window)
    
    # Main frame
    main_frame = tk.Frame(prescriptions_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Search frame
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(search_frame, text="Patient ID:", bg=BG_COLOR).pack(side=tk.LEFT)
    patient_id_entry = tk.Entry(search_frame)
    patient_id_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(patient_id_entry)
    
    search_btn = tk.Button(
        search_frame,
        text="Search",
        command=lambda: search_prescriptions(conn, patient_id_entry.get(), text_area),
        width=10
    )
    apply_styles(search_btn)
    search_btn.pack(side=tk.LEFT, padx=5)
    
    # Results area
    text_area = create_scrollable_text(main_frame, height=25, width=100)
    
    # View all initially
    search_prescriptions(conn, None, text_area)
    
    prescriptions_window.mainloop()

def search_prescriptions(conn, patient_id=None, text_area=None):
    """Tìm kiếm đơn thuốc"""
    try:
        with conn.cursor() as cursor:
            if patient_id:
                cursor.execute("""
                    SELECT pr.*, p.PatientName, d.DoctorName
                    FROM Prescription pr
                    JOIN Patients p ON pr.PatientID = p.PatientID
                    JOIN Doctors d ON pr.DoctorID = d.DoctorID
                    WHERE pr.PatientID = %s
                    ORDER BY pr.PrescriptionDate DESC
                """, (patient_id,))
            else:
                cursor.execute("""
                    SELECT pr.*, p.PatientName, d.DoctorName
                    FROM Prescription pr
                    JOIN Patients p ON pr.PatientID = p.PatientID
                    JOIN Doctors d ON pr.DoctorID = d.DoctorID
                    ORDER BY pr.PrescriptionDate DESC
                """)
            
            prescriptions = cursor.fetchall()
            
            if text_area:
                text_area.delete(1.0, tk.END)
                
                if not prescriptions:
                    text_area.insert(tk.END, "No prescriptions found\n")
                    return
                
                for pres in prescriptions:
                    text_area.insert(tk.END, f"Prescription ID: {pres['PrescriptionID']}\n")
                    text_area.insert(tk.END, f"Patient: {pres['PatientName']} (ID: {pres['PatientID']})\n")
                    text_area.insert(tk.END, f"Doctor: {pres['DoctorName']}\n")
                    text_area.insert(tk.END, f"Date: {pres['PrescriptionDate']}\n")
                    text_area.insert(tk.END, f"Diagnosis: {pres['Diagnosis'] or 'Not specified'}\n")
                    
                    # Get prescription details
                    cursor.execute("""
                        SELECT pd.*, m.MedicineName
                        FROM PrescriptionDetails pd
                        JOIN Medicine m ON pd.MedicineID = m.MedicineID
                        WHERE pd.PrescriptionID = %s
                    """, (pres['PrescriptionID'],))
                    details = cursor.fetchall()
                    
                    text_area.insert(tk.END, "\nMedicines:\n")
                    for med in details:
                        text_area.insert(tk.END, f"  - {med['MedicineName']}: {med['Dosage']} ({med['Frequency']})\n")
                    
                    text_area.insert(tk.END, "\n" + "="*50 + "\n\n")
    
    except MySQLError as e:
        if text_area:
            text_area.insert(tk.END, f"Error: {str(e)}\n")

def view_room_status_gui(conn):
    """GUI xem trạng thái phòng"""
    status_window = tk.Toplevel()
    status_window.title("Room Status")
    status_window.geometry("900x600")
    status_window.config(bg=BG_COLOR)
    center_window(status_window)
    
    # Main frame
    main_frame = tk.Frame(status_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Treeview để hiển thị dạng bảng
    tree = ttk.Treeview(main_frame, columns=("RoomID", "RoomNumber", "Type", "Department", "Status", "Patient"), show="headings")
    
    # Định nghĩa các cột
    tree.heading("RoomID", text="Room ID")
    tree.heading("RoomNumber", text="Room Number")
    tree.heading("Type", text="Room Type")
    tree.heading("Department", text="Department")
    tree.heading("Status", text="Status")
    tree.heading("Patient", text="Current Patient")
    
    tree.column("RoomID", width=80, anchor="center")
    tree.column("RoomNumber", width=100, anchor="center")
    tree.column("Type", width=150)
    tree.column("Department", width=150)
    tree.column("Status", width=100, anchor="center")
    tree.column("Patient", width=150)
    
    # Thêm scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Nút làm mới
    refresh_btn = tk.Button(
        main_frame,
        text="Refresh",
        command=lambda: refresh_room_status(conn, tree),
        width=15
    )
    apply_styles(refresh_btn)
    refresh_btn.pack(pady=10)
    
    # Load dữ liệu ban đầu
    refresh_room_status(conn, tree)
    
    status_window.mainloop()

def refresh_room_status(conn, tree):
    """Làm mới trạng thái phòng"""
    try:
        # Xóa dữ liệu cũ
        tree.delete(*tree.get_children())
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.RoomID, r.RoomNumber, rt.TypeName, d.DepartmentName, 
                       r.Status, p.PatientName
                FROM Rooms r
                JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Departments d ON r.DepartmentID = d.DepartmentID
                LEFT JOIN Patients p ON r.CurrentPatientID = p.PatientID
                ORDER BY d.DepartmentName, r.RoomNumber
            """)
            
            rooms = cursor.fetchall()
            
            for room in rooms:
                tree.insert("", "end", values=(
                    room["RoomID"],
                    room["RoomNumber"],
                    room["TypeName"],
                    room["DepartmentName"],
                    room["Status"],
                    room["PatientName"] or "None"
                ))
    
    except MySQLError as e:
        messagebox.showerror("Error", f"Failed to load room status: {str(e)}")
def export_prescription_pdf(conn, prescription_id):
    """Xuất đơn thuốc ra PDF"""
    from tkinter import filedialog
    
    # Chọn nơi lưu file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save Prescription As"
    )
    
    if not file_path:
        return
        
    success, message = generate_prescription_pdf(conn, prescription_id, file_path)
    
    if success:
        messagebox.showinfo("Success", f"Prescription exported to:\n{file_path}")
    else:
        messagebox.showerror("Error", message)

def view_patient_prescriptions_gui(conn):
    """GUI xem đơn thuốc của bệnh nhân (cho bác sĩ)"""
    patient_id = simpledialog.askstring("Patient ID", "Enter Patient ID:")
    if not patient_id:
        return
    
    view_prescriptions_gui(conn, patient_id)

def view_patient_insurance_gui(conn):
    """GUI xem bảo hiểm của bệnh nhân"""
    patient_id = simpledialog.askstring("Patient ID", "Enter Patient ID:")
    if not patient_id:
        return
    
    insurance_window = tk.Toplevel()
    insurance_window.title(f"Insurance for Patient {patient_id}")
    insurance_window.geometry("800x500")
    insurance_window.config(bg=BG_COLOR)
    center_window(insurance_window)
    
    # Main frame
    main_frame = tk.Frame(insurance_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Text area
    text_area = create_scrollable_text(main_frame)
    
    try:
        with conn.cursor() as cursor:
            # Lấy thông tin bệnh nhân
            cursor.execute("SELECT PatientName FROM Patients WHERE PatientID = %s", (patient_id,))
            patient = cursor.fetchone()
            
            if not patient:
                text_area.insert(tk.END, "Patient not found\n")
                return
            
            text_area.insert(tk.END, f"Insurance for: {patient['PatientName']} (ID: {patient_id})\n\n")
            
            # Lấy thông tin bảo hiểm
            cursor.execute("""
                SELECT * FROM Insurance 
                WHERE PatientID = %s
                ORDER BY EndDate DESC
            """, (patient_id,))
            
            insurances = cursor.fetchall()
            
            if not insurances:
                text_area.insert(tk.END, "No insurance records found\n")
                return
            
            for ins in insurances:
                text_area.insert(tk.END, f"Provider: {ins['InsuranceProvider']}\n")
                text_area.insert(tk.END, f"Policy Number: {ins['PolicyNumber']}\n")
                text_area.insert(tk.END, f"BHYT Card: {ins['BHYTCardNumber'] or 'N/A'}\n")
                text_area.insert(tk.END, f"Valid: {ins['EffectiveDate']} to {ins['EndDate']}\n")
                text_area.insert(tk.END, f"Coverage: {ins['CoverageDetails'] or 'Not specified'}\n")
                text_area.insert(tk.END, "-"*50 + "\n\n")
    
    except MySQLError as e:
        text_area.insert(tk.END, f"Error: {str(e)}\n")

def view_departments_gui(conn):
    """GUI for viewing departments"""
    view_window = tk.Toplevel()
    view_window.title("View Departments")
    view_window.geometry("600x400")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    
    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Results area
    text_area = create_scrollable_text(main_frame, height=15, width=70)
    
    def fetch():
        success, result = view_departments(conn)
        
        text_area.delete(1.0, tk.END)
        
        if success:
            if result:
                for dept in result:
                    text_area.insert(tk.END, f"Department ID: {dept['DepartmentID']}\n")
                    text_area.insert(tk.END, f"Name: {dept['DepartmentName']}\n")
                    text_area.insert(tk.END, f"Doctor Count: {dept['DoctorCount']}\n")
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No departments found\n")
        else:
            messagebox.showerror("Error", result)

    # Fetch button (though we'll call it immediately)
    fetch_btn = tk.Button(
        main_frame,
        text="Refresh",
        command=fetch
    )
    apply_styles(fetch_btn)
    fetch_btn.pack(pady=10)
    
    # Fetch data immediately when window opens
    fetch()

def room_management_gui(conn):
    """GUI quản lý phòng (cho receptionist)"""
    room_window = tk.Toplevel()
    room_window.title("Room Management")
    room_window.geometry("1000x700")
    room_window.config(bg=BG_COLOR)
    center_window(room_window)
    
    # Main frame
    main_frame = tk.Frame(room_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Room Management",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Filter frame
    filter_frame = tk.Frame(main_frame, bg=BG_COLOR)
    filter_frame.pack(fill=tk.X, pady=10)
    
    # Department filter
    tk.Label(filter_frame, text="Department:", bg=BG_COLOR).pack(side=tk.LEFT)
    dept_var = tk.StringVar()
    dept_dropdown = ttk.Combobox(filter_frame, textvariable=dept_var)
    
    # Room type filter
    tk.Label(filter_frame, text="Room Type:", bg=BG_COLOR).pack(side=tk.LEFT, padx=10)
    type_var = tk.StringVar()
    type_dropdown = ttk.Combobox(filter_filter, textvariable=type_var)
    
    # Status filter
    tk.Label(filter_frame, text="Status:", bg=BG_COLOR).pack(side=tk.LEFT, padx=10)
    status_var = tk.StringVar()
    status_dropdown = ttk.Combobox(filter_frame, textvariable=status_var, 
                                 values=["All", "Available", "Occupied", "Maintenance"])
    status_dropdown.current(0)
    
    # Load filter options
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DepartmentName FROM Departments")
            dept_dropdown['values'] = [d['DepartmentName'] for d in cursor.fetchall()]
            
            cursor.execute("SELECT TypeName FROM RoomTypes")
            type_dropdown['values'] = [t['TypeName'] for t in cursor.fetchall()]
    except MySQLError as e:
        messagebox.showerror("Error", f"Failed to load filter options: {e}")
    
    dept_dropdown.pack(side=tk.LEFT)
    type_dropdown.pack(side=tk.LEFT, padx=5)
    status_dropdown.pack(side=tk.LEFT, padx=5)
    
    # Treeview for rooms
    tree = ttk.Treeview(main_frame, columns=("ID", "Number", "Type", "Department", "Status", "Patient"), show="headings")
    
    tree.heading("ID", text="Room ID")
    tree.heading("Number", text="Room Number")
    tree.heading("Type", text="Room Type")
    tree.heading("Department", text="Department")
    tree.heading("Status", text="Status")
    tree.heading("Patient", text="Current Patient")
    
    tree.column("ID", width=80, anchor="center")
    tree.column("Number", width=100, anchor="center")
    tree.column("Type", width=150)
    tree.column("Department", width=150)
    tree.column("Status", width=100, anchor="center")
    tree.column("Patient", width=150)
    
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Action buttons frame
    action_frame = tk.Frame(main_frame, bg=BG_COLOR)
    action_frame.pack(fill=tk.X, pady=10)
    
    def refresh_rooms():
        dept = dept_var.get()
        room_type = type_var.get()
        status = status_var.get() if status_var.get() != "All" else None
        
        try:
            tree.delete(*tree.get_children())
            
            with conn.cursor() as cursor:
                query = """
                    SELECT r.RoomID, r.RoomNumber, rt.TypeName, d.DepartmentName, 
                           r.Status, p.PatientName
                    FROM Rooms r
                    JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
                    JOIN Departments d ON r.DepartmentID = d.DepartmentID
                    LEFT JOIN Patients p ON r.CurrentPatientID = p.PatientID
                    WHERE 1=1
                """
                params = []
                
                if dept:
                    query += " AND d.DepartmentName = %s"
                    params.append(dept)
                
                if room_type:
                    query += " AND rt.TypeName = %s"
                    params.append(room_type)
                
                if status:
                    query += " AND r.Status = %s"
                    params.append(status)
                
                query += " ORDER BY d.DepartmentName, r.RoomNumber"
                
                cursor.execute(query, params)
                rooms = cursor.fetchall()
                
                for room in rooms:
                    tree.insert("", "end", values=(
                        room["RoomID"],
                        room["RoomNumber"],
                        room["TypeName"],
                        room["DepartmentName"],
                        room["Status"],
                        room["PatientName"] or "None"
                    ))
                    
        except MySQLError as e:
            messagebox.showerror("Error", f"Failed to load rooms: {e}")
    
    refresh_btn = tk.Button(
        action_frame,
        text="Refresh",
        command=refresh_rooms,
        width=15
    )
    apply_styles(refresh_btn)
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def assign_patient():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a room")
            return
            
        room_id = tree.item(selected[0])['values'][0]
        patient_id = simpledialog.askstring("Assign Patient", "Enter Patient ID:")
        
        if not patient_id:
            return
            
        try:
            with conn.cursor() as cursor:
                # Check if patient exists
                cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id,))
                if not cursor.fetchone():
                    messagebox.showerror("Error", "Patient not found")
                    return
                
                # Assign patient to room
                cursor.execute("""
                    UPDATE Rooms 
                    SET Status = 'Occupied', 
                        CurrentPatientID = %s,
                        LastCleanedDate = CURDATE()
                    WHERE RoomID = %s
                """, (patient_id, room_id))
                
                conn.commit()
                messagebox.showinfo("Success", "Patient assigned to room successfully")
                refresh_rooms()
                
        except MySQLError as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to assign patient: {e}")
    
    assign_btn = tk.Button(
        action_frame,
        text="Assign Patient",
        command=assign_patient,
        width=15
    )
    apply_styles(assign_btn)
    assign_btn.pack(side=tk.LEFT, padx=5)
    
    def discharge_patient():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a room")
            return
            
        room_id = tree.item(selected[0])['values'][0]
        
        try:
            with conn.cursor() as cursor:
                # Check if room is occupied
                cursor.execute("SELECT Status FROM Rooms WHERE RoomID = %s", (room_id,))
                room = cursor.fetchone()
                
                if room['Status'] != 'Occupied':
                    messagebox.showerror("Error", "Room is not currently occupied")
                    return
                
                # Discharge patient
                cursor.execute("""
                    UPDATE Rooms 
                    SET Status = 'Available', 
                        CurrentPatientID = NULL
                    WHERE RoomID = %s
                """, (room_id,))
                
                conn.commit()
                messagebox.showinfo("Success", "Patient discharged from room")
                refresh_rooms()
                
        except MySQLError as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to discharge patient: {e}")
    
    discharge_btn = tk.Button(
        action_frame,
        text="Discharge Patient",
        command=discharge_patient,
        width=15
    )
    apply_styles(discharge_btn)
    discharge_btn.pack(side=tk.LEFT, padx=5)
    
    def set_maintenance():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a room")
            return
            
        room_id = tree.item(selected[0])['values'][0]
        
        try:
            with conn.cursor() as cursor:
                # Check if room is available
                cursor.execute("SELECT Status FROM Rooms WHERE RoomID = %s", (room_id,))
                room = cursor.fetchone()
                
                if room['Status'] == 'Occupied':
                    messagebox.showerror("Error", "Cannot set occupied room to maintenance")
                    return
                
                # Set to maintenance
                cursor.execute("""
                    UPDATE Rooms 
                    SET Status = 'Maintenance'
                    WHERE RoomID = %s
                """, (room_id,))
                
                conn.commit()
                messagebox.showinfo("Success", "Room set to maintenance")
                refresh_rooms()
                
        except MySQLError as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to update room status: {e}")
    
    maintenance_btn = tk.Button(
        action_frame,
        text="Set Maintenance",
        command=set_maintenance,
        width=15
    )
    apply_styles(maintenance_btn)
    maintenance_btn.pack(side=tk.LEFT, padx=5)
    
    def set_available():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a room")
            return
            
        room_id = tree.item(selected[0])['values'][0]
        
        try:
            with conn.cursor() as cursor:
                # Set to available
                cursor.execute("""
                    UPDATE Rooms 
                    SET Status = 'Available',
                        CurrentPatientID = NULL
                    WHERE RoomID = %s
                """, (room_id,))
                
                conn.commit()
                messagebox.showinfo("Success", "Room set to available")
                refresh_rooms()
                
        except MySQLError as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to update room status: {e}")
    
    available_btn = tk.Button(
        action_frame,
        text="Set Available",
        command=set_available,
        width=15
    )
    apply_styles(available_btn)
    available_btn.pack(side=tk.LEFT, padx=5)
    
    # Load initial data
    refresh_rooms()
    
    room_window.mainloop()

def generate_financial_report_gui(conn):
    """GUI for generating financial reports"""
    report_window = tk.Toplevel()
    report_window.title("Financial Report")
    report_window.geometry("600x500")
    report_window.config(bg=BG_COLOR)
    center_window(report_window)
    
    # Main frame
    main_frame = tk.Frame(report_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Report type selection
    type_frame = tk.Frame(main_frame, bg=BG_COLOR)
    type_frame.pack(fill=tk.X)
    
    tk.Label(type_frame, text="Report Type:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    report_type = tk.StringVar()
    report_type.set("month")
    tk.Radiobutton(type_frame, text="Monthly", variable=report_type, value="month", bg=BG_COLOR).grid(row=0, column=1, sticky="w")
    tk.Radiobutton(type_frame, text="Yearly", variable=report_type, value="year", bg=BG_COLOR).grid(row=0, column=2, sticky="w")
    
    # Year input (for monthly reports)
    year_frame = tk.Frame(main_frame, bg=BG_COLOR)
    year_frame.pack(fill=tk.X)
    
    tk.Label(year_frame, text="Year (for monthly report):", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_year = tk.Entry(year_frame)
    entry_year.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_year)
    
    # Results area
    text_area = create_scrollable_text(main_frame, height=20, width=70)
    
    def generate():
        report_type_val = report_type.get()
        year = entry_year.get() if report_type_val == "month" else None
        
        success, result = generate_financial_report(conn, report_type_val, year)
        
        text_area.delete(1.0, tk.END)
        
        if success:
            title, data = result
            text_area.insert(tk.END, f"{title}\n")
            text_area.insert(tk.END, "-"*40 + "\n")
            
            total = 0
            for row in data:
                if report_type_val == "month":
                    text_area.insert(tk.END, f"Month {row['Month']}: {row['Total']:,.2f} VND\n")
                else:
                    text_area.insert(tk.END, f"Year {row['Year']}: {row['Total']:,.2f} VND\n")
                total += row['Total']
            
            text_area.insert(tk.END, "-"*40 + "\n")
            text_area.insert(tk.END, f"GRAND TOTAL: {total:,.2f} VND\n")
        else:
            messagebox.showerror("Error", result)
            report_window.focus_force()

    # Generate button
    gen_btn = tk.Button(
        main_frame,
        text="Generate Report",
        command=generate
    )
    apply_styles(gen_btn)
    gen_btn.pack(pady=10)
    
    # Configure grid weights
    type_frame.grid_columnconfigure(1, weight=1)
    year_frame.grid_columnconfigure(1, weight=1)

def change_password_gui(conn, username):
    """GUI for changing password"""
    change_window = tk.Toplevel()
    change_window.title("Change Password")
    change_window.geometry("400x300")
    change_window.config(bg=BG_COLOR)
    center_window(change_window)
    
    # Main frame
    main_frame = tk.Frame(change_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Current password
    tk.Label(form_frame, text="Current Password:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_current = tk.Entry(form_frame, show="*")
    entry_current.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_current)
    
    # New password
    tk.Label(form_frame, text="New Password:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_new = tk.Entry(form_frame, show="*")
    entry_new.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_new)
    
    # Confirm new password
    tk.Label(form_frame, text="Confirm New Password:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_confirm = tk.Entry(form_frame, show="*")
    entry_confirm.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_confirm)
    
    def submit():
        current = entry_current.get()
        new = entry_new.get()
        confirm = entry_confirm.get()
        
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        success, message = change_password(conn, username, current, new)
        if success:
            messagebox.showinfo("Success", message)
            change_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Change Password",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def logout_action(current_window):
    """Handle logout action"""
    if messagebox.askokcancel("Logout", "Are you sure you want to logout?"):
        current_window.destroy()
        main()

def main():
    """Main application entry point"""
    root = tk.Tk()
    root.title("Hospital Management System")
    root.geometry("400x300")
    root.config(bg=BG_COLOR)
    center_window(root)
    
    # Main frame
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame,
        text="Hospital Management System",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 30))
    
    # Welcome message
    welcome_label = tk.Label(
        main_frame,
        text="Welcome to the Hospital Management System",
        font=LABEL_FONT,
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    welcome_label.pack(pady=(0, 20))
    
    # Login button
    login_btn = tk.Button(
        main_frame,
        text="Login",
        command=lambda: open_login_window(root),
        width=15
    )
    apply_styles(login_btn)
    login_btn.pack(pady=10)
    
    # Initialize admin account if not exists
    initialize_admin()
    
    root.mainloop()
 

if __name__ == "__main__":
    main()