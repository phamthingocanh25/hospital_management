from 7.core_logic import *
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

# Custom color scheme
BG_COLOR = "#f0f8ff"  # Alice Blue
BUTTON_COLOR = "#4682b4"  # Steel Blue
BUTTON_HOVER = "#5f9ea0"  # Cadet Blue
TEXT_COLOR = "#2f4f4f"  # Dark Slate Gray
ACCENT_COLOR = "#008080"  # Teal
ENTRY_BG = "#ffffff"  # White

# Font settings
TITLE_FONT = ("Helvetica", 14, "bold")
LABEL_FONT = ("Helvetica", 10)
BUTTON_FONT = ("Helvetica", 10, "bold")

def apply_styles(widget):
    """Apply consistent styling to widgets"""
    if isinstance(widget, tk.Button):
        widget.config(
            bg=BUTTON_COLOR,
            fg="white",
            font=BUTTON_FONT,
            relief=tk.RAISED,
            borderwidth=3,
            padx=10,
            pady=5
        )
        widget.bind("<Enter>", lambda e: widget.config(bg=BUTTON_HOVER))
        widget.bind("<Leave>", lambda e: widget.config(bg=BUTTON_COLOR))
    elif isinstance(widget, tk.Label):
        widget.config(
            fg=TEXT_COLOR,
            font=LABEL_FONT,
            padx=5,
            pady=5
        )
    elif isinstance(widget, tk.Entry):
        widget.config(
            bg=ENTRY_BG,
            relief=tk.SUNKEN,
            borderwidth=2,
            font=LABEL_FONT
        )

def create_scrollable_text(window, height=15, width=60):
    """Create a scrollable text widget with consistent styling"""
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
    admin_window.geometry("800x600")
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
    doctor_window.geometry("600x400")
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
    receptionist_window.geometry("700x500")
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

def view_appointments_gui(conn, role, username=None):
    """GUI for viewing appointments"""
    view_window = tk.Toplevel()
    view_window.title("View Appointments")
    view_window.geometry("700x600")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    
    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Filter frame
    filter_frame = tk.Frame(main_frame, bg=BG_COLOR)
    filter_frame.pack(fill=tk.X)
    
    # Year
    tk.Label(filter_frame, text="Year:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_year = tk.Entry(filter_frame)
    entry_year.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_year)
    
    # Month
    tk.Label(filter_frame, text="Month:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_month = tk.Entry(filter_frame)
    entry_month.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_month)
    
    # Day
    tk.Label(filter_frame, text="Day:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_day = tk.Entry(filter_frame)
    entry_day.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_day)
    
    # Results area
    text_area = create_scrollable_text(main_frame, height=20, width=80)
    
    def fetch():
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
                for appt in result:
                    text_area.insert(tk.END, f"Appointment ID: {appt['AppointmentID']}\n")
                    text_area.insert(tk.END, f"Doctor ID: {appt['DoctorID']}\n")
                    text_area.insert(tk.END, f"Patient ID: {appt['PatientID']}\n")
                    text_area.insert(tk.END, f"Date: {appt['AppointmentDate']}\n")
                    text_area.insert(tk.END, "-"*40 + "\n")
            else:
                text_area.insert(tk.END, "No appointments found\n")
        else:
            messagebox.showerror("Error", result)

    # Fetch button
    fetch_btn = tk.Button(
        main_frame,
        text="Fetch Appointments",
        command=fetch
    )
    apply_styles(fetch_btn)
    fetch_btn.pack(pady=10)
    
    # Configure grid weights
    filter_frame.grid_columnconfigure(1, weight=1)

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

def create_invoice_gui(conn):
    """GUI for creating invoices"""
    invoice_window = tk.Toplevel()
    invoice_window.title("Create Invoice")
    invoice_window.geometry("400x250")
    invoice_window.config(bg=BG_COLOR)
    center_window(invoice_window)
    
    # Main frame
    main_frame = tk.Frame(invoice_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient = tk.Entry(form_frame)
    entry_patient.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient)
    
    # Amount
    tk.Label(form_frame, text="Amount:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_amount = tk.Entry(form_frame)
    entry_amount.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_amount)
    
    def submit():
        patient_id = entry_patient.get()
        amount = entry_amount.get()
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number")
            return
        
        success, message = create_invoice(conn, patient_id, amount)
        if success:
            messagebox.showinfo("Success", message)
            invoice_window.destroy()
        else:
            messagebox.showerror("Error", message)

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Create Invoice",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

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
