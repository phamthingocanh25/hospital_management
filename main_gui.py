from core_logic import *
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from tkinter.font import Font
from tkinter import simpledialog
from tkinter import scrolledtext
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import tkinter as tk 
from tkinter import ttk 
from tkinter import messagebox 
from PIL import Image, ImageDraw
from tkinter import font as tkFont
from tkcalendar import DateEntry
from datetime import datetime, time, timedelta
from tkinter import filedialog
import csv
import sys
from decimal import Decimal
sys.stdout.reconfigure(encoding='utf-8')


# Custom color scheme
BG_COLOR = "#f0f8ff"
BUTTON_COLOR = "#4682b4"
BUTTON_HOVER = "#5f9ea0"
TEXT_COLOR = "#2f4f4f"
ACCENT_COLOR = "#008080"
ENTRY_BG = "#ffffff"
TITLE_FONT = ("Helvetica", 12, "bold") 
LABEL_FONT = ("Helvetica", 10)
BUTTON_FONT = ("Helvetica", 10, "bold")
TREEVIEW_FONT = ("Helvetica", 9)

# Font settings
TITLE_FONT = ("Helvetica", 14, "bold")
LABEL_FONT = ("Helvetica", 10)
BUTTON_FONT = ("Helvetica", 10, "bold")

global_refresh_callbacks = {}

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

def main():
    login_window = tk.Tk()
    login_window.title("Hospital Management System - Login")
    login_window.geometry("900x700") # Match example size
    login_window.resizable(False, False) # Optional: prevent resizing

    # --- Background Image Handling (from AppWithBackground example) ---
    try:
        # IMPORTANT: Change this path to your actual background image file
        bg_image_path = "C:\\DMS\\prj_0205\\anh_bv.png"
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((900, 700), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = tk.Label(login_window, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo # Keep a reference!
        bg_label.lower() # Place background behind other widgets
    except FileNotFoundError:
        print(f"Warning: Background image '{bg_image_path}' not found. Using fallback color.")
        login_window.config(bg="#f0f0f0") # Fallback background color
    except Exception as e:
        print(f"Error loading background image: {e}")
        login_window.config(bg="#f0f0f0") # Fallback background color
    # --- End Background Image Handling ---

    # --- Centered Login Frame (from AppWithBackground example) ---
    # Use ttk.Frame for potentially better theme integration if desired
    main_frame = ttk.Frame(login_window, style='Login.TFrame', padding=(50, 30)) # Added padding
    # Define a style for the frame to set background
    style = ttk.Style()
    style.configure('Login.TFrame', background='white', borderwidth=2, relief=tk.RIDGE)
    main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=350)
    # --- End Centered Login Frame ---

    # --- Authentication Logic (Keep your original logic here) ---
    def authenticate_user_action():
        """Handles authentication for the login window"""
        username = username_entry.get()
        password = password_entry.get()

        # !!! IMPORTANT: Your existing call to authenticate_user remains the same !!!
        user, role, conn, role_id, error = authenticate_user(username, password)

        if error:
           messagebox.showerror("Login Failed", error, parent=login_window) # Add parent
           login_window.focus_force() # Keep focus
           return

        login_window.destroy() # Close login window on success

        # !!! IMPORTANT: Your existing role handling remains the same !!!
        welcome_messages = {
            "admin": "Welcome Admin!",
            "doctor": "Welcome Doctor!",
            "receptionist": "Welcome Receptionist!",
            "accountant": "Welcome Accountant!",
            "pharmacist":"Welcome Pharmacist!",
            "nurse": "Welcome Nurse!",
            "director": "Welcome Director!",
            "inventory_manager": "Welcome Inventory Manager!",

        }

        if role in welcome_messages:
            def open_role_menu():
                if role == "admin":
                    open_admin_menu(conn, username) # Pass conn and username
                elif role == "doctor":
                    open_doctor_menu(conn, role_id, username) # Pass conn, role_id (DoctorID), username
                elif role == "receptionist":
                    open_receptionist_menu(conn, username) # Pass conn and username
                elif role == "accountant":
                    open_accountant_menu(conn, username) # Pass conn and username
                elif role == "pharmacist":
                    open_pharmacist_menu(conn, username) # Pass conn and username
                elif role == "nurse":
                    open_nurse_menu(conn, username) # Pass conn and username
                elif role == "director":
                    open_director_menu(conn, username) # Pass conn and username
                elif role == "inventory_manager":
                     open_inventory_manager_menu(conn, username) # Pass conn and username 
                
                else:
                     messagebox.showerror("Login Error", f"No menu defined for role: {role}")
                     main() # Go back to initial screen or handle appropriately

            # Show welcome message first, then open the specific menu
            messagebox.showinfo("Login Successful", welcome_messages[role])
            open_role_menu()
        else:
            messagebox.showerror("Login Failed", f"Unknown or unsupported role: {role}")
            # Decide what to do for unknown roles, e.g., go back to main screen
            main() # Or just return, or try login again

    # --- Login Widgets (Styled like AppWithBackground example) ---
    # Title
    # Use ttk Label for consistency if using ttk Frame
    title_label = ttk.Label(main_frame, text="SYSTEM LOGIN",
                            font=("Arial", 16, "bold"), background="white")
    title_label.pack(pady=20)

    # Username
    # Use ttk Label for consistency
    ttk.Label(main_frame, text="Username:", background="white",
              font=("Arial", 10)).pack(padx=20, anchor="w")
    username_entry = ttk.Entry(main_frame, width=30, font=("Arial", 10))
    username_entry.pack(padx=20, pady=5, fill=tk.X) # Use fill=tk.X

    # Password
    # Use ttk Label for consistency
    ttk.Label(main_frame, text="Password:", background="white",
              font=("Arial", 10)).pack(padx=20, anchor="w")
    password_entry = ttk.Entry(main_frame, width=30, show="*", font=("Arial", 10))
    password_entry.pack(padx=20, pady=5, fill=tk.X) # Use fill=tk.X

    # Bind Enter key for convenience
    username_entry.bind("<Return>", lambda event: password_entry.focus())
    password_entry.bind("<Return>", lambda event: authenticate_user_action())

    # Login button
    # Use ttk Button for consistency
    login_btn = ttk.Button(main_frame, text="Login", width=15,
                           command=authenticate_user_action, style='Login.TButton') # Optional style
    # Define style for button if needed
    style.configure('Login.TButton', font=("Arial", 9, "bold"), padding=(10, 5))
    login_btn.pack(pady=20)
    # --- End Login Widgets ---

    # --- Copyright Label (from AppWithBackground example) ---
    # Placed directly on the window, not the centered frame
    copyright_label = tk.Label(login_window, text="© 2025 Hospital Management System",
                               font=("Arial", 8), bg="#333333", fg="white")
    copyright_label.pack(side="bottom", fill="x")
    # --- End Copyright Label ---

    # Center the window on the screen AFTER creating widgets
    center_window(login_window, 800, 600)
    login_window.mainloop()

def admin_menu_item_clicked(item_name, conn, username, admin_window, refresh_callback):
    """Calls the appropriate original GUI function based on the menu item clicked."""
    print(f"Admin action requested: {item_name}") # For debugging

    # Map button labels (use English) to the original functions
    action_map = {
        # Doctor Menu Items
        "Add Doctor": lambda: add_doctor_gui(conn),
        "Delete Doctor": lambda: delete_doctor_gui(conn),
        "Update Doctor Info": lambda: update_doctor_info_gui(conn),
        "Assign Doctor to User": lambda: assign_doctor_user_gui(conn),
        "View Doctors": lambda: view_doctor_gui(conn),
        "Disable Doctor": lambda: disable_doctor_gui(conn),

        # Patient Menu Items
        "Add Patient": lambda: add_patient_gui(conn),
        "Delete Patient": lambda: delete_patient_gui(conn),
        "View Patients": lambda: view_patient_gui(conn),
        "Update Patient Info": lambda: update_patient_info_gui(conn),
        "Disable Patient Account": lambda: disable_patient_account_gui(conn),
        "View Emergency Contacts": lambda: view_emergency_contacts_gui(conn),
        "Add Emergency Contact": lambda: add_emergency_contact_gui(conn),
        "Update Emergency Contact": lambda: update_emergency_contact_gui(conn),
        "Delete Emergency Contact": lambda: delete_emergency_contact_gui(conn),

        # Department Menu Items
        "View Departments": lambda: view_departments_gui(conn),
        "Add Department": lambda: add_department_gui(conn),
        "Update Department": lambda: update_department_gui(conn),

        # Appointment Menu Items
        "Schedule Appointment": lambda: schedule_appointment_gui(conn),
        "View Appointments": lambda: view_appointments_gui(conn, 'admin'), # Specify role
        "Update Appointment Status": lambda: update_appointment_status_gui(conn),

        # Room Menu Items
        "View Rooms": lambda: view_rooms_gui(conn),
        "Add Room": lambda: add_room_gui(conn),
        "Update Room": lambda: update_room_gui(conn),
        "Disable Room": lambda: disable_room_gui(conn),
        "View Room Types": lambda: view_room_types_gui(conn),
        "Add Room Type": lambda: add_room_type_gui(conn),
        "Update Room Type": lambda: update_room_type_gui(conn),
        "Assign Room": lambda: assign_room_gui(conn),

        # Service Menu Items
        "View Services": lambda: view_services_gui(conn),
        "Add Service": lambda: add_service_gui(conn),
        "Update Service": lambda: update_service_gui(conn),

        # Patient Service Menu Items
        "View Patient Services": lambda: view_patient_services_gui(conn),
        "Add Patient Service": lambda: create_patient_services_gui(conn),
        "Delete Patient Service": lambda: delete_patient_service_gui(conn),

        # Prescription Menu Items
        "View Prescriptions": lambda: view_prescriptions_gui(conn),
        "Delete Prescription": lambda: delete_prescription_gui(conn),
        "Delete Prescription Item": lambda: delete_prescription_details_gui(conn),

        # Medicine Menu Items
        "View Medicines": lambda: view_medicine_gui(conn),
        "Add Medicine": lambda: add_medicine_gui(conn),
        "Update Medicine": lambda: update_medicine_gui(conn),
        "Delete Medicine": lambda: delete_medicine_gui(conn),
        "View Medicine Batches": lambda: view_medicine_batches_gui(conn),
        "Add Medicine Batch": lambda: add_medicine_batch_gui(conn),
        "Update Medicine Batch": lambda: update_medicine_batch_gui(conn),
        "Delete Medicine Batch": lambda: delete_medicine_batch_gui(conn),
        "Adjust Medicine Stock": lambda: adjust_medicine_batch_gui(conn),

        # Inventory Menu Items
        "View Inventory": lambda: view_inventory_gui(conn),
        "Add Inventory Item": lambda: add_inventory_gui(conn),
        "Disable Inventory Item": lambda: disable_inventory_item_gui(conn), # Needs Inventory ID - how to get? Maybe disable button for now.
        "Adjust Inventory": lambda: adjust_inventory_gui(conn),

        # Insurance Menu Items
        "View Insurance": lambda: view_insurance_gui(conn),
        "Create Insurance": lambda: add_insurance_gui(conn),
        "Update Insurance": lambda: update_insurance_gui(conn),
        "Delete Insurance": lambda: delete_insurance_gui(conn),

        # Invoice Menu Items
        "View Invoices": lambda: view_invoices_gui(conn),
        "Create Invoice": lambda: create_invoice_gui(conn),

        # Reports Menu Items
        "Financial Report": lambda: generate_financial_report_gui(conn),
        # "Room Report": lambda: get_room_statistics_gui(conn),
        "Statistics Report": lambda: generate_statistics_gui(conn), # Added this based on your functions

        # System Menu Items
        "Register New User": lambda: register_user_gui(conn),
        "Delete User": lambda: delete_user_gui(conn),
        "View System Users": lambda: view_system_users_gui(conn), # Added this based on your functions
        "Change Password": lambda: change_password_gui(conn, username),
        "Logout": lambda: logout_action(admin_window),
    }

    action = action_map.get(item_name)
    refresh_needed_actions = [
        "Add Doctor", "Delete Doctor", "Disable Doctor",
        "Add Patient", "Delete Patient", "Disable Patient Account",
        "Schedule Appointment", "Update Appointment Status", # Có thể ảnh hưởng Appointments Today
        "Assign Room", "Disable Room", "Add Room" # Có thể ảnh hưởng Available Rooms
    ]
    if action:
        try:
            # Execute the original GUI function, which will likely open a Toplevel
            action()
            if item_name in refresh_needed_actions and callable(refresh_callback):
                 # Đợi một chút để cửa sổ Toplevel có thể đã đóng
                 # và DB có thời gian cập nhật (nếu cần)
                 print(f"Action '{item_name}' completed, scheduling stats refresh.")
                 admin_window.after(200, refresh_callback) # Gọi hàm refresh sau 200ms
        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform action '{item_name}':\n{str(e)}", parent=admin_window)
            if admin_window.winfo_exists(): admin_window.focus_force()
    else:
        # Xử lý các hành động chưa được map
        print(f"Action for '{item_name}' not yet implemented.")
        messagebox.showinfo("Info", f"Action for '{item_name}' is not yet implemented.", parent=admin_window)
        if admin_window.winfo_exists(): admin_window.focus_force()

def open_admin_menu(conn, username):
    """
    Opens the Admin Dashboard window with the new layout and fetches stats.

    Args:
        conn: The database connection object.
        username (str): The username of the logged-in admin.
    """
    admin_window = tk.Tk()
    admin_window.lift()
    admin_window.attributes('-topmost',True)
    admin_window.after(100, lambda: admin_window.attributes('-topmost', False))
    admin_window.title(f"Admin Dashboard - {username}")
    admin_window.geometry("1200x700")
    admin_window.resizable(False, False)

    # --- Left Menu Frame ---
    # ... (code tạo menu bên trái giữ nguyên như trước) ...
    menu_frame = tk.Frame(admin_window, bg="#2c3e50", width=250)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    title_label = tk.Label(menu_frame, text="ADMIN MENU", font=("Arial", 16, "bold"),
                           fg="white", bg="#2c3e50", pady=20)
    title_label.pack(fill="x")

    menu_canvas = tk.Canvas(menu_frame, bg="#2c3e50", highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg="#2c3e50")

    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

    menu_canvas.pack(side="left", fill="both", expand=True)
    menu_scrollbar.pack(side="right", fill="y")

    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
    menu_buttons_frame.bind("<Configure>", update_scroll_region)

    def _on_mousewheel_menu(event):
        if event.num == 4 or event.delta > 0:
            menu_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            menu_canvas.yview_scroll(1, "units")

    for widget in [menu_canvas, menu_buttons_frame]:
        widget.bind("<MouseWheel>", _on_mousewheel_menu)
        widget.bind("<Button-4>", _on_mousewheel_menu)
        widget.bind("<Button-5>", _on_mousewheel_menu)

    menu_items = [ # Giữ nguyên danh sách menu items của bạn
        ("Doctor", "--- DOCTOR ---"), "Add Doctor", "Delete Doctor", "Update Doctor Info", "Assign Doctor to User", "View Doctors", "Disable Doctor",
        ("Patient", "--- PATIENT ---"), "Add Patient", "Delete Patient", "View Patients", "Update Patient Info", "Disable Patient Account", "View Emergency Contacts", "Add Emergency Contact", "Update Emergency Contact", "Delete Emergency Contact",
        ("Department", "--- DEPARTMENT ---"), "View Departments", "Add Department", "Update Department",
        ("Appointment", "--- APPOINTMENT ---"), "Schedule Appointment", "View Appointments", "Update Appointment Status",
        ("Room", "--- ROOM ---"), "View Rooms", "Add Room", "Update Room", "Disable Room", "View Room Types", "Add Room Type", "Update Room Type", "Assign Room",
        ("Service", "--- SERVICE ---"), "View Services", "Add Service", "Update Service",
        ("Patient Service", "--- PATIENT SERVICE ---"), "View Patient Services", "Add Patient Service", "Delete Patient Service",
        ("Prescription", "--- PRESCRIPTION ---"), "View Prescriptions", "Delete Prescription", "Delete Prescription Item",
        ("Medicine", "--- MEDICINE ---"), "View Medicines", "Add Medicine", "Update Medicine", "Delete Medicine", "View Medicine Batches", "Add Medicine Batch", "Update Medicine Batch", "Delete Medicine Batch", "Adjust Medicine Stock",
        ("Inventory", "--- INVENTORY ---"), "View Inventory", "Add Inventory Item", "Adjust Inventory",
        ("Insurance", "--- INSURANCE ---"), "View Insurance", "Create Insurance", "Update Insurance", "Delete Insurance",
        ("Invoice", "--- INVOICE ---"), "View Invoices", "Create Invoice",
        ("Reports", "--- REPORTS ---"), "Financial Report", "Statistics Report",
        ("System", "--- SYSTEM ---"), "Register New User", "Delete User", "View System Users", "Change Password", "Logout"
    ]

    for item in menu_items:
        is_separator = isinstance(item, tuple)
        if is_separator:
            category_title = item[1]
            separator_label = tk.Label(menu_buttons_frame, text=category_title, font=("Arial", 10, "italic"), fg="#aed6f1", bg="#2c3e50", anchor="w")
            separator_label.pack(fill="x", padx=10, pady=(10, 2))
            separator_label.bind("<MouseWheel>", _on_mousewheel_menu); separator_label.bind("<Button-4>", _on_mousewheel_menu); separator_label.bind("<Button-5>", _on_mousewheel_menu)
        else:
            button_text = item
            btn = tk.Button(menu_buttons_frame, text=button_text, font=("Arial", 11), bg="#34495e", fg="white", bd=0, padx=20, pady=8, width=25, anchor="w",
                            # <<< TRUYỀN HÀM REFRESH VÀO DISPATCHER >>>
                            command=lambda name=button_text: admin_menu_item_clicked(name, conn, username, admin_window, refresh_dashboard_statistics)) # Thêm refresh_dashboard_statistics
            btn.pack(fill="x", padx=10, pady=1)
            default_bg = "#34495e"; hover_bg = "#3d566e"
            btn.bind("<Enter>", lambda e, b=btn, h_bg=hover_bg: b.config(bg=h_bg))
            btn.bind("<Leave>", lambda e, b=btn, d_bg=default_bg: b.config(bg=d_bg))
            btn.bind("<MouseWheel>", _on_mousewheel_menu); btn.bind("<Button-4>", _on_mousewheel_menu); btn.bind("<Button-5>", _on_mousewheel_menu)
    # --- End Left Menu Frame ---

    # --- Main Dashboard Area ---
    dash_frame = tk.Frame(admin_window, bg="#f0f2f5")
    dash_frame.pack(side="right", fill="both", expand=True)

    # Header
    header_frame = tk.Frame(dash_frame, bg="#3498db", height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    header_label = tk.Label(header_frame, text="Admin Dashboard", font=("Arial", 20, "bold"), fg="white", bg="#3498db")
    header_label.pack(side="left", padx=30, pady=20)
    user_frame = tk.Frame(header_frame, bg="#3498db")
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg="#3498db").pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Administrator", font=("Arial", 10), fg="#eaf2f8", bg="#3498db").pack(side="bottom", anchor="e")

    # Content Frame
    content_frame = tk.Frame(dash_frame, bg="#f0f2f5", padx=20, pady=20)
    content_frame.pack(fill="both", expand=True)

    # --- * MỚI: Lấy dữ liệu cho các ô thống kê * ---
    def get_dashboard_stats(db_conn):
        stats_data = {"total_doctors": "E", "active_patients": "E", "appointments_today": "E", "available_rooms": "E"}
        if not db_conn: return stats_data
        try:
            with db_conn.cursor() as cursor:
                # !! Nhớ điều chỉnh các câu lệnh SQL này cho phù hợp CSDL của bạn !!
                cursor.execute("SELECT COUNT(*) as count FROM Doctors WHERE Status = 'Active'")
                result = cursor.fetchone(); stats_data["total_doctors"] = str(result['count']) if result else "0"
                cursor.execute("SELECT COUNT(*) as count FROM Patients WHERE Status = 'Active'")
                result = cursor.fetchone(); stats_data["active_patients"] = str(result['count']) if result else "0"
                cursor.execute("SELECT COUNT(*) as count FROM Appointments WHERE DATE(AppointmentDate) = CURDATE() AND Status = 'Scheduled'")
                result = cursor.fetchone(); stats_data["appointments_today"] = str(result['count']) if result else "0"
                cursor.execute("SELECT COUNT(*) as count FROM Rooms WHERE Status = 'Available'")
                result = cursor.fetchone(); stats_data["available_rooms"] = str(result['count']) if result else "0"
        except Exception as e: print(f"Database error fetching dashboard stats: {e}")
        return stats_data

    # Gọi hàm để lấy dữ liệu, truyền kết nối 'conn' vào
    dashboard_stats = get_dashboard_stats(conn)
    # --- * KẾT THÚC LẤY DỮ LIỆU * ---

    # --- Tạo các ô thống kê với dữ liệu đã lấy ---
    stats_frame = tk.Frame(content_frame, bg="#f0f2f5")
    stats_frame.pack(fill=tk.X, pady=(10, 20)) # Thêm padding trên
    stat_value_labels = {} # Dictionary để lưu các label hiển thị số liệu
    stats_data_initial = get_dashboard_stats(conn)

    # Sử dụng dữ liệu từ dashboard_stats thay vì "?"
    stats_definitions = [
        {"title": "Total Doctors", "key": "total_doctors", "color": "#e74c3c"},
        {"title": "Active Patients", "key": "active_patients", "color": "#3498db"},
        {"title": "Appointments Today", "key": "appointments_today", "color": "#2ecc71"},
        {"title": "Available Rooms", "key": "available_rooms", "color": "#f39c12"}
    ]


    for stat_def in stats_definitions:
        card = tk.Frame(stats_frame, bg="white", bd=0, highlightthickness=1,
                       highlightbackground="#dddddd", padx=20, pady=15)
        card.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(card, text=stat_def["title"], font=("Arial", 12),
               fg="#7f8c8d", bg="white").pack(anchor="w")

        # Tạo label giá trị và lưu tham chiếu vào dictionary
        value_text = stats_data_initial.get(stat_def["key"], "E") # Lấy giá trị ban đầu
        value_label = tk.Label(card, text=value_text, font=("Arial", 24, "bold"),
                               fg=stat_def["color"], bg="white")
        value_label.pack(anchor="w", pady=5)
        stat_value_labels[stat_def["key"]] = value_label # Lưu label theo key dữ liệu

        card.bind("<Enter>", lambda e, c=card: c.config(highlightbackground="#bbbbbb"))
        card.bind("<Leave>", lambda e, c=card: c.config(highlightbackground="#dddddd"))
    # --- Kết thúc tạo ô thống kê ---
    def refresh_dashboard_statistics():
        print("Refreshing dashboard statistics...") # Debug message
        new_stats_data = get_dashboard_stats(conn)
        for key, label_widget in stat_value_labels.items():
            new_value = new_stats_data.get(key, "E") # Lấy giá trị mới theo key
            if label_widget.winfo_exists(): # Kiểm tra xem label còn tồn tại không
                 label_widget.config(text=str(new_value))
            else:
                 print(f"Warning: Label for '{key}' no longer exists.")
        print("Dashboard statistics updated.")

    refresh_btn = tk.Button(header_frame, text="Refresh Stats", command=refresh_dashboard_statistics,
                            font=("Arial", 9), bg="#2980b9", fg="white", relief=tk.RAISED, bd=1)
    # Căn chỉnh nút refresh ở góc trên bên phải header, trước user_frame
    refresh_btn.pack(side="right", padx=(0, 10), pady=5)
    # --- Placeholder cho biểu đồ ---
    chart_frame = tk.Frame(content_frame, bg="white", height=250, bd=0,
                           highlightthickness=1, highlightbackground="#dddddd")
    chart_frame.pack(fill="both", expand=True, pady=20)
    chart_frame.pack_propagate(False)
    tk.Label(chart_frame, text="Activity Overview (Placeholder)", font=("Arial", 14, "bold"),
           fg="#34495e", bg="white").pack(side="top", anchor="nw", padx=15, pady=10)
    tk.Label(chart_frame, text="Charts or detailed tables can be added here later.", font=("Arial", 11),
           fg="#7f8c8d", bg="white").pack(padx=15, pady=10)
    # --- End Placeholder ---

    # --- End Main Dashboard Area ---

    # Center window and run main loop
    center_window(admin_window, 1200, 700)
    admin_window.mainloop()

def open_doctor_menu(conn, doctor_id, username):
    """Mở cửa sổ Bảng điều khiển Bác sĩ với giao diện hiện đại, rõ ràng."""
    # Lưu ý: Sử dụng tk.Toplevel() thường tốt hơn cho cửa sổ phụ
    # nhưng giữ tk.Tk() để nhất quán với các hàm menu khác trong file của bạn.
    doctor_window = tk.Tk()
    doctor_window.title(f"Doctor Dashboard - {username} (ID: {doctor_id})")
    doctor_window.lift()
    doctor_window.attributes('-topmost',True)
    doctor_window.after(100, lambda: doctor_window.attributes('-topmost', False))

    # Kích thước cửa sổ linh hoạt hơn một chút
    doctor_window.geometry("1200x700")
    # Cho phép thay đổi kích thước tối thiểu
    doctor_window.minsize(1000, 600)
    doctor_window.configure(bg="#ffffff")  # Nền trắng
    
    # Bảng màu hiện đại (giữ nguyên từ code của bạn)
    primary_color = "#4a6fa5"
    secondary_color = "#6bbd99"
    accent_color = "#5d9cec"
    dark_color = "#333333"
    light_color = "#f5f7fa"
    menu_bg = "#2c3e50"
    menu_fg = "#ecf0f1"
    menu_hover_bg = "#34495e"
    menu_header_bg = "#1a252f"
    card_bg = "white"
    card_border = "#e0e0e0"

    # Cài đặt font (giữ nguyên từ code của bạn)
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
        # Đảm bảo font được tải
        tkFont.Font(family="Segoe UI", size=10)
    except tk.TclError:
        print("Cảnh báo: Không tìm thấy font 'Segoe UI', sử dụng font dự phòng.")
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Khung Menu Bên Trái ---
    buttons = [
        ("Dashboard", lambda: show_dashboard_content),
        ("Order Admission", lambda: order_admission_gui(conn, doctor_id)), # <<< ADDED THIS
        ("View Patients", lambda: view_patient_gui(conn)),
        ("View Appointments", lambda: view_appointments_gui(conn, 'doctor', doctor_id)), # Pass doctor_id
        ("Update Appointment Status", lambda: update_appointment_status_gui(conn)), # Abbreviated
        ("View Prescriptions", lambda: view_prescriptions_gui(conn)),
        ("Create Prescription", lambda: create_prescription_gui(conn, doctor_id)),
        ("Delete Prescription Item", lambda: delete_prescription_details_gui(conn)),
        ("View Emergency Contacts", lambda: view_emergency_contacts_gui(conn)),
        ("View Services", lambda: view_services_gui(conn)),
        ("Add Patient Service", lambda: create_patient_services_gui(conn, doctor_id)),
        ("View Medicines", lambda: view_medicine_gui(conn)),
        ("View Insurance", lambda: view_insurance_gui(conn)),
        ("View Rooms", lambda: view_rooms_gui(conn)),
        ("Change Password", lambda: change_password_gui(conn, username)),
        ("Logout", lambda: logout_action(doctor_window))
    ]

    menu_frame = tk.Frame(doctor_window, bg=menu_bg, width=230) # Tăng nhẹ chiều rộng
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Khung Header trong Menu (Thông tin bác sĩ)
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170) # Tăng chiều cao
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)

    # Avatar (hình tròn)
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10)) # Tăng khoảng đệm trên
    avatar_canvas.create_oval(5, 5, 65, 65, fill=primary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper() if username else 'D',
                            font=(title_font[0], 24, "bold"), fill="white") # Tăng kích thước chữ

    # Tên bác sĩ
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"), # Tăng kích thước
            fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))

    # Lấy tên khoa từ CSDL (logic giữ nguyên)
    department_name = "Unknown Department" # Giá trị mặc định tốt hơn
    try:
        if conn:
            # Sử dụng try-with-resources để đảm bảo cursor được đóng
            with conn.cursor() as cursor:
                query = """
                SELECT dep.DepartmentName
                FROM Doctors doc
                JOIN Departments dep ON doc.DepartmentID = dep.DepartmentID
                WHERE doc.DoctorID = %s
                """
                cursor.execute(query, (doctor_id,))
                result = cursor.fetchone()
                if result and result.get('DepartmentName'):
                    department_name = result['DepartmentName']
    except Exception as e:
        # Ghi log lỗi cụ thể hơn
        print(f"Lỗi khi lấy tên khoa cho DoctorID {doctor_id}: {e}")
        # Sử dụng parent=doctor_window để messagebox hiện trên cửa sổ doctor
        messagebox.showwarning("Database Warning", f"Could not fetch department name: {e}", parent=doctor_window)

    department_label = tk.Label(menu_header_frame, text=department_name,
                                fg="#bdc3c7", bg=menu_header_bg, font=small_font)
    department_label.pack(pady=(0, 15))

    # --- Các Mục Menu với thanh cuộn ---
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)

    # --- Khu Vực Nội Dung Chính ---
    content_frame = tk.Frame(doctor_window, bg=light_color)
    content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # --- Hàm Hiển Thị Nội Dung (logic gần như giữ nguyên) ---
    def clear_content():
        """Xóa tất cả widget khỏi khung nội dung chính."""
        # Sử dụng winfo_children() để lấy danh sách an toàn hơn
        for widget in list(content_frame.winfo_children()):
            widget.destroy()

    def create_card(parent, title, value, color, icon=None):
        """Tạo một thẻ (card) hiển thị thông tin."""
        card = tk.Frame(parent, bg=card_bg, bd=0, relief="flat",
                        highlightbackground=card_border, highlightthickness=1,
                        padx=15, pady=15)

        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))

        if icon:
            # Tăng kích thước icon
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                    bg=card_bg, fg=color).pack(side="left", padx=(0, 10))

        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"), # Tăng kích thước
                bg=card_bg, fg="#7f8c8d").pack(side="left")

        tk.Label(card, text=str(value), font=card_font,
                bg=card_bg, fg=dark_color).pack(anchor="w", pady=5) # Thêm padding

        return card

    def show_dashboard_content():
        """Hiển thị nội dung của bảng điều khiển chính."""
        clear_content()
        try:
            # Khung Header (Chào mừng, Ngày giờ)
            header_frame = tk.Frame(content_frame, bg=light_color)
            header_frame.pack(fill="x", pady=(0, 20))

            # Hiển thị tên ngắn gọn hơn nếu tên dài
            display_name = username.split()[0] if len(username.split()) > 1 else username
            tk.Label(header_frame, text=f"Welcome, Dr. {display_name}",
                    font=title_font, bg=light_color, fg=dark_color).pack(side="left")

            tk.Label(header_frame, text=datetime.now().strftime("%A, %B %d, %Y"),
                    font=small_font, bg=light_color, fg="#7f8c8d").pack(side="right", padx=10)

            # Khung chứa các thẻ thống kê
            stats_frame = tk.Frame(content_frame, bg=light_color)
            stats_frame.pack(fill="x", pady=(0, 25))

            # Lấy dữ liệu thống kê (Cần hàm thực tế từ core_logic.py)
            stats_data = {"appointments": "N/A", "patients": "N/A", "prescriptions": "N/A"}
            try:
                # Giả sử bạn có một hàm get_doctor_dashboard_stats trong core_logic.py
                # Nó trả về (True, {"appointments": count1, "patients": count2, "prescriptions": count3})
                # hoặc (False, error_message)
                success_stats, stats_result = get_doctor_dashboard_stats(conn, doctor_id)
                if success_stats:
                    stats_data = stats_result # Mong đợi dict như {"appointments": 5, ...}
                else:
                    print(f"Warning: Could not fetch dashboard stats: {stats_result}")
                    # Hiển thị lỗi trên UI nếu cần
                    # tk.Label(stats_frame, text=f"Error loading stats: {stats_result}", fg="red", bg=light_color).pack()
            except NameError:
                # Nếu hàm get_doctor_dashboard_stats chưa được định nghĩa trong core_logic
                print("Warning: Hàm 'get_doctor_dashboard_stats' không tồn tại (sử dụng dữ liệu N/A).")
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu thống kê dashboard: {e}")
                # Hiển thị lỗi trên UI nếu cần
                # tk.Label(stats_frame, text=f"Error loading stats: {e}", fg="red", bg=light_color).pack()


            # Định nghĩa và tạo các thẻ thống kê
            cards_info = [
                ("Today's Appointments", stats_data.get("appointments", "N/A"), primary_color, "📅"),
                ("Recent Patients", stats_data.get("patients", "N/A"), secondary_color, "👥"),
                ("Recent Prescriptions", stats_data.get("prescriptions", "N/A"), accent_color, "💊")
            ]

            for i, (title, value, color, icon) in enumerate(cards_info):
                card = create_card(stats_frame, title, value, color, icon)
                card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
                stats_frame.grid_columnconfigure(i, weight=1) # Cho phép thẻ co giãn

            # --- Khung Lịch hẹn sắp tới ---
            appointments_container = tk.Frame(content_frame, bg=light_color)
            appointments_container.pack(fill="both", expand=True)

            # Hàm làm mới Treeview lịch hẹn
            def refresh_appointments_view(tree_widget):
                # Kiểm tra xem widget còn tồn tại không trước khi thao tác
                if not tree_widget or not tree_widget.winfo_exists():
                    print("Debug: Appointments tree widget no longer exists. Skipping refresh.")
                    return
                try:
                    # Xóa các item cũ một cách an toàn
                    for item in tree_widget.get_children():
                        tree_widget.delete(item)
                except tk.TclError as e:
                    # Bắt lỗi nếu widget đã bị hủy trong quá trình xóa
                    print(f"Debug: Error clearing appointments tree (widget might be destroyed): {e}")
                    return # Không thể tiếp tục nếu widget không hợp lệ

                try:
                    success, appts_data = search_appointments(
                        conn,
                        role='doctor',        # Vai trò hiện tại
                        username=username,    # <<< THAY ĐỔI TẠI ĐÂY: Truyền username của bác sĩ
                        year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day,
                        status="Scheduled"    # Chỉ lấy các cuộc hẹn đã lên lịch cho hôm nay
                    )

                    if success:
                        if appts_data: # Nếu có dữ liệu trả về
                            for appt in appts_data:
                                # (Giữ nguyên phần xử lý và hiển thị dữ liệu)
                                appt_time_obj = appt.get("AppointmentTime")
                                time_str = "N/A"
                                if appt_time_obj is not None: # Quan trọng: Kiểm tra None trước
                                    if isinstance(appt_time_obj, time):
                                        time_str = appt_time_obj.strftime('%H:%M')
                                    elif isinstance(appt_time_obj, datetime): # Nếu cột là DATETIME/TIMESTAMP
                                        time_str = appt_time_obj.strftime('%H:%M')
                                # *** THÊM KIỂM TRA VÀ XỬ LÝ TIMEDELTA ***
                                    elif isinstance(appt_time_obj, timedelta):
                                    # Chuyển timedelta (số giây từ nửa đêm) thành chuỗi HH:MM
                                        total_seconds = int(appt_time_obj.total_seconds())
                                        hours = total_seconds // 3600
                                        minutes = (total_seconds % 3600) // 60
                                        time_str = f"{hours:02}:{minutes:02}"
                                # **************************************
                                    elif isinstance(appt_time_obj, str): # Xử lý nếu CSDL trả về chuỗi
                                        try:
                                            parsed_time = datetime.strptime(appt_time_obj, '%H:%M:%S').time()
                                            time_str = parsed_time.strftime('%H:%M')
                                        except ValueError:
                                            try: # Thử định dạng khác nếu cần
                                                parsed_time = datetime.strptime(appt_time_obj, '%H:%M').time()
                                                time_str = parsed_time.strftime('%H:%M')
                                            except ValueError:
                                                print(f"Warning: Could not parse time string '{appt_time_obj}'")
                                                time_str = "Invalid Str" # Hoặc giữ N/A
                                    else:
                                    # Ghi log nếu gặp kiểu dữ liệu không mong muốn khác
                                        print(f"Warning: Unexpected type for AppointmentTime: {type(appt_time_obj)}")
                                        time_str = "Unknown Type"

                                patient_name = appt.get("PatientName", "N/A")
                                status = appt.get("Status", "N/A")

                                tree_widget.insert("", "end", values=(time_str, patient_name, status))
                        else:
                            tree_widget.insert("", "end", values=("", "No scheduled appointments today", ""))
                    else:
                        print(f"Lỗi khi tải lịch hẹn: {appts_data}")
                        tree_widget.insert("", "end", values=("Error", "Could not load appointments", str(appts_data)))

                except NameError:
                    print("Warning: Hàm 'search_appointments' không tồn tại trong core_logic (hiển thị thông báo).")
                    tree_widget.insert("", "end", values=("N/A", "Function missing", "Error"))
                except Exception as e:
                    print(f"Lỗi không mong đợi khi làm mới lịch hẹn: {e}")
                    import traceback
                    traceback.print_exc()
                    tree_widget.insert("", "end", values=("Error", "Unexpected error", str(e)))


            # Header của mục lịch hẹn
            appointments_header = tk.Frame(appointments_container, bg=light_color)
            appointments_header.pack(fill="x", pady=(10, 5))

            tk.Label(appointments_header, text="UPCOMING APPOINTMENTS",
                    font=(small_font[0], 10, "bold"), bg=light_color, fg="#7f8c8d").pack(side="left")

            # Nút làm mới bên cạnh header
            # Đảm bảo command gọi đúng hàm refresh với widget tree làm đối số
            refresh_btn = tk.Button(appointments_header, text="🔄 Refresh",
                                    # command=lambda: refresh_appointments_view(appointments_tree), # Gán command sau khi appointments_tree được tạo
                                    font=(small_font[0], 9), fg=accent_color, bg=light_color, relief="flat", bd=0, activebackground=light_color, activeforeground=primary_color)
            refresh_btn.pack(side="right", padx=5)


            # Tạo Treeview cho lịch hẹn
            appt_columns = ["Time", "Patient", "Status"]
            appt_style = ttk.Style()
            # Cấu hình style cho heading và rows
            appt_style.configure("Appointments.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
            appt_style.configure("Appointments.Treeview", font=small_font, rowheight=28) # Tăng chiều cao dòng
            # Tạo widget Treeview sau khi style được cấu hình
            appointments_tree = ttk.Treeview(appointments_container, columns=appt_columns, show="headings", height=8, style="Appointments.Treeview") 

            # Cấu hình cột sau khi tạo Treeview
            for col in appt_columns:
                anchor = tk.W if col != "Time" else tk.CENTER
                width = 120 if col == "Time" else (280 if col == "Patient" else 100) # Điều chỉnh chiều rộng cột
                appointments_tree.heading(col, text=col, anchor=anchor)
                appointments_tree.column(col, width=width, anchor=anchor, stretch=True)

            # Gán lệnh cho nút Refresh SAU KHI appointments_tree được tạo
            refresh_btn.config(command=lambda: refresh_appointments_view(appointments_tree))

            # Thanh cuộn cho Treeview lịch hẹn
            appt_scrollbar = ttk.Scrollbar(appointments_container, orient="vertical", command=appointments_tree.yview)
            appointments_tree.configure(yscrollcommand=appt_scrollbar.set)

            # Đặt Treeview và Scrollbar vào grid hoặc pack để dễ quản lý hơn
            # Sử dụng pack cho đơn giản trong trường hợp này
            appointments_tree_frame = tk.Frame(appointments_container) # Frame chứa tree và scrollbar
            appointments_tree_frame.pack(fill="both", expand=True)
            appt_scrollbar.pack(side="right", fill="y") # Đặt scrollbar trước
            appointments_tree.pack(side="left", fill="both", expand=True) # Treeview lấp đầy phần còn lại


            # Tải dữ liệu lịch hẹn ban đầu
            refresh_appointments_view(appointments_tree)

        except Exception as e:
            clear_content() # Xóa nếu có lỗi nghiêm trọng khi vẽ dashboard
            messagebox.showerror("Dashboard Error", f"Failed to display dashboard: {e}", parent=doctor_window)
            print(f"Lỗi nghiêm trọng khi hiển thị dashboard bác sĩ: {e}")
            import traceback
            traceback.print_exc() # In traceback để debug

    # --- Định Nghĩa Các Mục Menu và Lệnh ---
    # Sử dụng lambda để đảm bảo các đối số được truyền đúng cách tại thời điểm gọi
    def on_enter(e, btn):
        btn['bg'] = menu_hover_bg
    def on_leave(e, btn):
        btn['bg'] = menu_bg

    for text, command in buttons:
        btn = tk.Button(menu_buttons_frame, text=text, font=normal_font, fg=menu_fg, bg=menu_bg,
                        activebackground=menu_hover_bg, activeforeground=menu_fg, bd=0, padx=10, pady=10,
                        anchor="w", command=command)
        btn.pack(fill="x", padx=10, pady=2)
        btn.bind("<Enter>", lambda e, b=btn: on_enter(e, b))
        btn.bind("<Leave>", lambda e, b=btn: on_leave(e, b))

    # --- Footer trong Menu ---
    tk.Label(menu_frame, text="Hospital Management System © 2025", # Thêm năm
            fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    # Hiển thị dashboard mặc định sau khi cửa sổ đã sẵn sàng
    doctor_window.after(100, show_dashboard_content)

    # Đảm bảo cửa sổ được căn giữa sau khi các widget được tạo
    # Gọi center_window() ở đây nếu hàm đó tồn tại
    try:
        center_window(doctor_window) # Giả sử hàm center_window tồn tại
    except NameError:
        print("Warning: center_window function not found.")
        # Fallback: Tự căn giữa cơ bản
        doctor_window.update_idletasks()
        width = doctor_window.winfo_width()
        height = doctor_window.winfo_height()
        x = (doctor_window.winfo_screenwidth() // 2) - (width // 2)
        y = (doctor_window.winfo_screenheight() // 2) - (height // 2)
        doctor_window.geometry(f'{width}x{height}+{x}+{y}')


    doctor_window.mainloop()

def open_receptionist_menu(conn, username):
    """Mở cửa sổ Bảng điều khiển Receptionist với giao diện hiện đại và đầy đủ chức năng."""
    receptionist_window = tk.Tk()
    receptionist_window.lift()
    receptionist_window.attributes('-topmost',True)
    receptionist_window.after(100, lambda: receptionist_window.attributes('-topmost', False))
    
    receptionist_window.title(f"Receptionist Dashboard - {username}")
    receptionist_window.geometry("1200x700")
    receptionist_window.minsize(1000, 600)
    receptionist_window.configure(bg="#ffffff")

    # Bảng màu hiện đại (Keep your color definitions)
    primary_color = "#4a6fa5"
    secondary_color = "#6bbd99"
    accent_color = "#5d9cec"
    dark_color = "#333333"
    light_color = "#f5f7fa"
    menu_bg = "#2c3e50"
    menu_fg = "#ecf0f1"
    menu_hover_bg = "#34495e"
    menu_header_bg = "#1a252f"
    card_bg = "white"
    card_border = "#e0e0e0"

    # Font settings (Keep your font definitions)
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
    except tk.TclError:
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Khung Menu Bên Trái ---
    # (Keep menu_frame, menu_header_frame, avatar_canvas, labels)
    menu_frame = tk.Frame(receptionist_window, bg=menu_bg, width=280)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170)
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10))
    avatar_canvas.create_oval(5, 5, 65, 65, fill=primary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper() if username else 'R',
                             font=(title_font[0], 24, "bold"), fill="white")
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"),
             fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))
    tk.Label(menu_header_frame, text="Receptionist", font=small_font,
             fg="#bdc3c7", bg=menu_header_bg).pack(pady=(0, 15))


    # --- Các Mục Menu với thanh cuộn ---
    # (Keep menu_canvas, scrollbar, menu_buttons_frame, and scrolling logic)
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)


    # --- Khu Vực Nội Dung Chính ---
    # (Keep content_frame, header_frame, user_frame, stats_frame, create_stat_card)
    content_frame = tk.Frame(receptionist_window, bg=light_color)
    content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
    header_frame = tk.Frame(content_frame, bg=primary_color, height=80)
    header_frame.pack(fill="x"); header_frame.pack_propagate(False)
    tk.Label(header_frame, text="Receptionist Dashboard", font=title_font, fg="white", bg=primary_color).pack(side="left", padx=30, pady=20)
    user_frame = tk.Frame(header_frame, bg=primary_color)
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg=primary_color).pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Receptionist", font=("Arial", 10), fg="#eaf2f8", bg=primary_color).pack(side="bottom", anchor="e")
    stats_frame = tk.Frame(content_frame, bg=light_color); stats_frame.pack(fill=tk.X, pady=(10, 20))

    def get_receptionist_stats(db_conn):
        stats_data = {"today_appointments": "N/A", "pending_admissions": "N/A", "available_rooms": "N/A"}
        
        if not db_conn:
            return stats_data
        
        try:
            with db_conn.cursor() as cursor:
                # Ensure today is in the correct format: YYYY-MM-DD
                today = datetime.now().date()  # Get today's date
                today_str = today.strftime('%Y-%m-%d')  # Format it as a string
                
                # Print for debugging
                print(f"Executing query with date: {today_str}")
                
                # Today's appointments count
                query = f"SELECT COUNT(*) as count FROM Appointments WHERE DATE(AppointmentDate) = '{today_str}'"
                cursor.execute(query)
                result = cursor.fetchone()
                stats_data["today_appointments"] = str(result['count']) if result and result['count'] is not None else "0"
                
                # Pending admissions count
                cursor.execute("SELECT COUNT(*) as count FROM AdmissionOrders WHERE Status = 'Pending'")
                result = cursor.fetchone()
                stats_data["pending_admissions"] = str(result['count']) if result and result['count'] is not None else "0"
                
                # Available rooms count
                cursor.execute("SELECT COUNT(*) as count FROM Rooms WHERE Status = 'Available'")
                result = cursor.fetchone()
                stats_data["available_rooms"] = str(result['count']) if result and result['count'] is not None else "0"
        
        except Exception as e:
            print(f"Database error fetching receptionist stats: {e}")
        
        return stats_data

    def create_stat_card(parent, title, value, color, icon=None):
        card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=1,
                    highlightbackground=card_border, padx=15, pady=15)
        
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))
        
        if icon:
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                    bg=card_bg, fg=color).pack(side="left", padx=(0, 10))
        
        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"),
                bg=card_bg, fg="#7f8c8d").pack(side="left")
        
        tk.Label(card, text=str(value), font=card_font,
                bg=card_bg, fg=dark_color).pack(anchor="w", pady=5)
        
        return card

    # Get stats data from the database
    stats_data = get_receptionist_stats(conn)

    # Info for each stat card
    stat_cards_info = [
        ("Today's Appointments", stats_data.get("today_appointments", "N/A"), accent_color, "📅"),
        ("Pending Admissions", stats_data.get("pending_admissions", "N/A"), secondary_color, "📋"),
        ("Available Rooms", stats_data.get("available_rooms", "N/A"), primary_color, "🏥")
    ]

    # Create and place the stat cards
    for i, (title, value, color, icon) in enumerate(stat_cards_info):
        card = create_stat_card(stats_frame, title, value, color, icon)
        card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)


    # --- Danh sách hẹn hôm nay (Sử dụng dữ liệu thật) ---
    # (Keep the today_frame, treeview, scrollbar, and refresh function setup)
    today_frame = tk.Frame(content_frame, bg=card_bg, bd=0, relief="flat", highlightbackground=card_border, highlightthickness=1)
    today_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    list_header = tk.Frame(today_frame, bg=card_bg); list_header.pack(fill=tk.X, pady=(10, 5), padx=15)
    tk.Label(list_header, text="TODAY'S APPOINTMENTS", font=(small_font[0], 10, "bold"), bg=card_bg, fg="#7f8c8d").pack(side="left")
    tree_container = tk.Frame(today_frame, bg=card_bg); tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    columns = ("Time", "Patient", "Doctor", "Status"); tree_style = ttk.Style()
    tree_style.configure("Receptionist.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
    tree_style.configure("Receptionist.Treeview", font=small_font, rowheight=28)
    tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=10, style="Receptionist.Treeview")
    for col in columns: # Keep column setup
        anchor = tk.CENTER if col == "Time" else tk.W; width = 100 if col == "Time" else (150 if col == "Status" else 200)
        tree.heading(col, text=col, anchor=anchor); tree.column(col, width=width, anchor=anchor, stretch=(col != "Time"))
    scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y"); tree.pack(side="left", fill=tk.BOTH, expand=True)
    tree.tag_configure('Confirmed', background='#e8f5e9'); tree.tag_configure('Pending', background='#fff9c4')
    tree.tag_configure('Cancelled', background='#ffebee'); tree.tag_configure('Scheduled', background='#e3f2fd')

    def refresh_today_appointments():
        if not tree.winfo_exists():
            return
        try:
            for item in tree.get_children():
                tree.delete(item)
        except tk.TclError:
            return

        try:
            today = datetime.now().date()
            success, appointments = search_appointments(conn, role='receptionist', username=username, status=None)

            if success:
                count_today_appointments = 0  # ✅ Biến đếm số lịch hôm nay

                for appt in appointments:
                    appt_date = appt.get("AppointmentDate")
                    if not appt_date:
                        continue

                    # Chuyển đổi sang kiểu date nếu cần
                    if isinstance(appt_date, str):
                        try:
                            appt_date = datetime.strptime(appt_date, "%Y-%m-%d").date()
                        except ValueError:
                            continue
                    elif isinstance(appt_date, datetime):
                        appt_date = appt_date.date()

                    if appt_date != today:
                        continue

                    # ✅ Nếu đúng là hôm nay thì xử lý tiếp
                    count_today_appointments += 1

                    # Xử lý giờ hẹn
                    time_str = "N/A"
                    appt_time = appt.get("AppointmentTime")
                    if appt_time:
                        if isinstance(appt_time, time):
                            time_str = appt_time.strftime('%H:%M')
                        elif isinstance(appt_time, datetime):
                            time_str = appt_time.strftime('%H:%M')
                        elif isinstance(appt_time, str):
                            for fmt in ("%H:%M:%S", "%H:%M"):
                                try:
                                    time_str = datetime.strptime(appt_time, fmt).strftime('%H:%M')
                                    break
                                except ValueError:
                                    continue
                            else:
                                time_str = appt_time

                    patient_name = appt.get("PatientName", "N/A")
                    doctor_name = appt.get("DoctorName", "N/A")
                    status = appt.get("Status", "N/A")

                    tree.insert("", tk.END, values=(time_str, patient_name, doctor_name, status), tags=(status,))

                if count_today_appointments == 0:
                    # ✅ Không có lịch hôm nay → thông báo rõ
                    tree.insert("", tk.END, values=("", "No appointments scheduled for today", "", ""))

            else:
                messagebox.showerror("Load Error", f"Could not load appointments: {appointments}", parent=receptionist_window)

        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Error: {str(e)}", parent=receptionist_window)
            import traceback
            traceback.print_exc()

    refresh_btn = tk.Button(list_header, text="🔄 Refresh", font=(small_font[0], 9), fg=accent_color, bg=card_bg, relief="flat", bd=0, activebackground=light_color, activeforeground=primary_color, command=refresh_today_appointments)
    refresh_btn.pack(side="right", padx=5)
    receptionist_window.after(100, refresh_today_appointments)


    # --- Các nút chức năng chính (Updated with user's list + Create Invoice) ---
    menu_actions = {
        # Patient Management
        "Add Patient": ("➕🧑", lambda: add_patient_gui(conn)),
        "View Patient": ("🔍🧑", lambda: view_patient_gui(conn)),
        "Update Patient Info": ("✏️🧑", lambda: update_patient_info_gui(conn)),
        "Delete Patient": ("❌🧑", lambda: delete_patient_gui(conn)),

        # Emergency Contacts
        "Add Emergency Contact": ("➕🆘", lambda: add_emergency_contact_gui(conn)),
        "Update Emergency Contact": ("✏️🆘", lambda: update_emergency_contact_gui(conn)),
        "Delete Emergency Contact": ("❌🆘", lambda: delete_emergency_contact_gui(conn)),

        # Appointments
        "Schedule Appointment": ("➕📅", lambda: schedule_appointment_gui(conn)),
        "View Appointments": ("🔍📅", lambda: view_appointments_gui(conn, 'receptionist')),

        # Admissions & Rooms
        "Process Admission": ("➡️🏥", lambda: process_admission_gui(conn, username)),
        "View Rooms": ("🔍🚪", lambda: view_rooms_gui(conn)),
        "Assign Room": ("➡️🚪", lambda: assign_room_gui(conn)),

        # Billing & Insurance
        "Create Invoice": ("➕💰", lambda: create_invoice_gui(conn)), # <<< ADDED
        "View Invoices": ("🔍💰", lambda: view_and_print_invoices_by_patient(conn)),
        "View Insurance": ("🛡️", lambda: view_insurance_gui(conn)),
        "Create Insurance": ("➕🛡️", lambda: add_insurance_gui(conn)),

        # Other Lookups
        "View Departments": ("🏢", lambda: view_departments_gui(conn)),
        "View Services": ("⚕️", lambda: view_services_gui(conn)),
        "View Doctors": ("🧑‍⚕️", lambda: view_doctor_gui(conn)),

        # System
        "Change Password": ("🔒", lambda: change_password_gui(conn, username)),
        "Logout": ("🚪", lambda: logout_action(receptionist_window))
    }

    # --- Generate Menu Buttons from the Dictionary ---
    categories = {
        "Patient": ["Add Patient", "View Patient", "Update Patient Info", "Delete Patient"],
        "Emergency": ["Add Emergency Contact", "Update Emergency Contact", "Delete Emergency Contact"],
        "Scheduling": ["Schedule Appointment", "View Appointments"],
        "Admissions & Rooms": ["Process Admission", "Assign Room", "View Rooms"],
        "Billing & Insurance": ["Create Invoice", "View Invoices", "Create Insurance", "View Insurance"], # <<< Added Create Invoice here
        "Information": ["View Departments", "View Services", "View Doctors"],
        "System": ["Change Password", "Logout"]
    }

    # (Keep the loop that creates buttons based on categories and menu_actions)
    for widget in menu_buttons_frame.winfo_children(): widget.destroy() # Clear existing
    for category, items in categories.items():
        sep_label = tk.Label(menu_buttons_frame, text=f"--- {category.upper()} ---", font=(small_font[0], 9, "italic"), fg="#aed6f1", bg=menu_bg, anchor="w")
        sep_label.pack(fill="x", padx=10, pady=(8, 2))
        for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: sep_label.bind(event_type, _on_mousewheel_menu)
        for text in items:
            if text in menu_actions:
                icon, command = menu_actions[text]
                btn = tk.Button(menu_buttons_frame, text=f" {icon}  {text}", anchor="w", font=normal_font, fg=menu_fg, bg=menu_bg, bd=0, padx=15, pady=10, relief="flat", activebackground=menu_hover_bg, activeforeground=menu_fg, command=command)
                btn.pack(fill="x", pady=1, padx=5)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=menu_hover_bg)); btn.bind("<Leave>", lambda e, b=btn: b.config(bg=menu_bg))
                for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: btn.bind(event_type, _on_mousewheel_menu)


    # Footer menu
    tk.Label(menu_frame, text="Hospital System © 2025", fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    # Center and run
    try: center_window(receptionist_window)
    except NameError: print("Warning: center_window function not defined.")
    receptionist_window.mainloop()

def open_accountant_menu(conn, username):
    """Opens the Accountant Dashboard with modern UI similar to doctor/receptionist menus"""
    accountant_window = tk.Tk()
    accountant_window.lift()
    accountant_window.attributes('-topmost',True)
    accountant_window.after(100, lambda: accountant_window.attributes('-topmost', False))
    accountant_window.title(f"Accountant Dashboard - {username}")
    accountant_window.geometry("1200x700")
    accountant_window.minsize(1000, 600)
    accountant_window.configure(bg="#ffffff")  # White background

    # Modern color scheme
    primary_color = "#4a6fa5"  # Blue
    secondary_color = "#6bbd99"  # Green
    accent_color = "#5d9cec"  # Light blue
    dark_color = "#333333"  # Dark text
    light_color = "#f5f7fa"  # Light background
    menu_bg = "#2c3e50"  # Dark menu background
    menu_fg = "#ecf0f1"  # Light menu text
    menu_hover_bg = "#34495e"  # Menu hover
    menu_header_bg = "#1a252f"  # Darker menu header
    card_bg = "white"  # Card background
    card_border = "#e0e0e0"  # Card border

    # Font settings
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
        tkFont.Font(family="Segoe UI", size=10)
    except tk.TclError:
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Left Menu Frame ---
    menu_frame = tk.Frame(accountant_window, bg=menu_bg, width=280)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Menu header with user info
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170)
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)

    # Avatar (circular)
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10))
    avatar_canvas.create_oval(5, 5, 65, 65, fill=primary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper() if username else 'A',
                             font=(title_font[0], 24, "bold"), fill="white")

    # User info
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"),
             fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))
    tk.Label(menu_header_frame, text="Accountant", font=small_font,
             fg="#bdc3c7", bg=menu_header_bg).pack(pady=(0, 15))

    # --- Scrollable Menu Items ---
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)

    # --- Main Dashboard Area ---
    dash_frame = tk.Frame(accountant_window, bg=light_color)
    dash_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Header
    header_frame = tk.Frame(dash_frame, bg=primary_color, height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="Accountant Dashboard", font=title_font, fg="white", bg=primary_color).pack(side="left", padx=30, pady=20)
    
    user_frame = tk.Frame(header_frame, bg=primary_color)
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg=primary_color).pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Accountant", font=("Arial", 10), fg="#eaf2f8", bg=primary_color).pack(side="bottom", anchor="e")

    # --- Stats Cards ---
    stats_frame = tk.Frame(dash_frame, bg=light_color)
    stats_frame.pack(fill=tk.X, pady=(10, 20))

    def get_accountant_stats(db_conn):
        stats_data = {"partial_invoices": "N/A", "total_revenue": "N/A", "unpaid_invoices": "N/A"}
        if not db_conn: return stats_data
        try:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM Invoices WHERE PaymentStatus = 'Partial'")
                result = cursor.fetchone()
                stats_data["partial_invoices"] = str(result['count']) if result else "0"
                
                cursor.execute("SELECT SUM(TotalAmount) as total FROM Invoices WHERE PaymentStatus = 'Paid' AND MONTH(InvoiceDate) = MONTH(CURRENT_DATE())")
                result = cursor.fetchone()
                stats_data["total_revenue"] = f"{result['total']:,.0f} VND" if result and result['total'] else "0 VND"
                
                cursor.execute("SELECT COUNT(*) as count FROM Invoices WHERE PaymentStatus = 'Unpaid'")
                result = cursor.fetchone()
                stats_data["unpaid_invoices"] = str(result['count']) if result else "0"
        except Exception as e: 
            print(f"Database error fetching accountant stats: {e}")
        return stats_data

    def create_stat_card(parent, title, value, color, icon=None):
        card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=1,
                       highlightbackground=card_border, padx=15, pady=15)
        
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))
        
        if icon:
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                     bg=card_bg, fg=color).pack(side="left", padx=(0, 10))
        
        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"),
                 bg=card_bg, fg="#7f8c8d").pack(side="left")
        
        tk.Label(card, text=str(value), font=card_font,
                 bg=card_bg, fg=dark_color).pack(anchor="w", pady=5)
        
        return card

    stats_data = get_accountant_stats(conn)
    
    stat_cards_info = [
        ("Partial Invoices", stats_data.get("partial_invoices", "N/A"), accent_color, "📋"),
        ("Monthly Revenue", stats_data.get("total_revenue", "N/A"), secondary_color, "💰"),
        ("Unpaid Invoices", stats_data.get("unpaid_invoices", "N/A"), primary_color, "⚠️")
    ]

    for i, (title, value, color, icon) in enumerate(stat_cards_info):
        card = create_stat_card(stats_frame, title, value, color, icon)
        card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

    # --- Recent Invoices Table ---
    invoices_frame = tk.Frame(dash_frame, bg=card_bg, bd=0, relief="flat",
                            highlightbackground=card_border, highlightthickness=1)
    invoices_frame.pack(fill="both", expand=True, pady=(0, 10))

    # Header
    invoices_header = tk.Frame(invoices_frame, bg=card_bg)
    invoices_header.pack(fill="x", pady=(10, 5), padx=15)
    
    tk.Label(invoices_header, text="RECENT INVOICES", font=(small_font[0], 10, "bold"),
             bg=card_bg, fg="#7f8c8d").pack(side="left")

    # Treeview for invoices
    columns = ("InvoiceID", "Patient", "InvoiceDate", "TotalAmount", "Status")
    tree_style = ttk.Style()
    tree_style.configure("Accountant.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
    tree_style.configure("Accountant.Treeview", font=small_font, rowheight=28)
    
    tree = ttk.Treeview(invoices_frame, columns=columns, show="headings", height=8, style="Accountant.Treeview")
    
    # Configure columns
    col_widths = [80, 200, 100, 100, 100]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.CENTER if col in ["InvoiceID", "TotalAmount"] else tk.W)

    # Scrollbar
    scrollbar = ttk.Scrollbar(invoices_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Pack tree and scrollbar
    tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
    scrollbar.pack(side="right", fill="y")

    # Tag configurations for status
    tree.tag_configure('Paid', background='#e8f5e9')
    tree.tag_configure('Partial', background='#fff3e0')
    tree.tag_configure('Unpaid', background='#ffebee')

    def load_recent_invoices():
        tree.delete(*tree.get_children())
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT i.InvoiceID, p.PatientName, i.InvoiceDate, 
                           i.TotalAmount, i.PaymentStatus
                    FROM Invoices i
                    JOIN Patients p ON i.PatientID = p.PatientID
                    ORDER BY i.InvoiceDate DESC
                    LIMIT 15
                """)
                invoices = cursor.fetchall()
                
                if invoices:
                    for inv in invoices:
                        tree.insert("", tk.END, values=(
                            inv['InvoiceID'],
                            inv['PatientName'],
                            inv['InvoiceDate'].strftime('%Y-%m-%d') if inv['InvoiceDate'] else "",
                            f"{inv['TotalAmount']:,.0f} VND",
                            inv['PaymentStatus']
                        ), tags=(inv['PaymentStatus'],))
                else:
                    tree.insert("", tk.END, values=("", "No invoices found", "", "", ""))
        except Exception as e:
            print(f"Error loading invoices: {e}")
            tree.insert("", tk.END, values=("Error", "Could not load data", "", "", ""))

    # Load initial data
    load_recent_invoices()

    # --- Menu Items ---
    menu_actions = {
        "Dashboard": ("📊", lambda: load_recent_invoices()),
        "View Invoices": ("📋", lambda: view_invoices_gui(conn)),
        "Create Invoice": ("➕", lambda: create_invoice_gui(conn)),
        "View Services": ("⚕️", lambda: view_services_gui(conn)),
        "View Insurance": ("🛡️", lambda: view_insurance_gui(conn)),
        "Financial Report": ("📈", lambda: generate_financial_report_gui(conn)),
        "Statistics Report": ("📊", lambda: generate_statistics_gui(conn)),
        "Change Password": ("🔒", lambda: change_password_gui(conn, username)),
        "Logout": ("🚪", lambda: logout_action(accountant_window))
    }

    # Organize menu items into categories
    categories = {
        "Billing": ["View Invoices", "Create Invoice"],
        "Reports": ["Financial Report", "Statistics Report"],
        "Information": ["View Services", "View Insurance"],
        "System": ["Change Password", "Logout"]
    }

    # Create menu buttons
    for widget in menu_buttons_frame.winfo_children(): widget.destroy()  # Clear existing
    
    for category, items in categories.items():
        # Category separator
        sep_label = tk.Label(menu_buttons_frame, text=f"--- {category.upper()} ---", 
                            font=(small_font[0], 9, "italic"), fg="#aed6f1", bg=menu_bg, anchor="w")
        sep_label.pack(fill="x", padx=10, pady=(8, 2))
        
        # Bind scroll events to separator
        for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
            sep_label.bind(event_type, _on_mousewheel_menu)
        
        # Menu items
        for text in items:
            if text in menu_actions:
                icon, command = menu_actions[text]
                btn = tk.Button(menu_buttons_frame, text=f" {icon}  {text}", anchor="w",
                                font=normal_font, fg=menu_fg, bg=menu_bg,
                                bd=0, padx=15, pady=10, relief="flat",
                                activebackground=menu_hover_bg, activeforeground=menu_fg,
                                command=command)
                btn.pack(fill="x", pady=1, padx=5)
                
                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=menu_hover_bg))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=menu_bg))
                
                # Bind scroll events
                for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
                    btn.bind(event_type, _on_mousewheel_menu)

    # Footer
    tk.Label(menu_frame, text="Hospital System © 2025", 
             fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    # Center window
    try:
        center_window(accountant_window)
    except NameError:
        accountant_window.update_idletasks()
        width = accountant_window.winfo_width()
        height = accountant_window.winfo_height()
        x = (accountant_window.winfo_screenwidth() // 2) - (width // 2)
        y = (accountant_window.winfo_screenheight() // 2) - (height // 2)
        accountant_window.geometry(f'{width}x{height}+{x}+{y}')

    accountant_window.mainloop()

def open_nurse_menu(conn, username):
    """Opens the Nurse Dashboard with modern UI"""
    nurse_window = tk.Tk()
    nurse_window.lift()
    nurse_window.attributes('-topmost',True)
    nurse_window.after(100, lambda: nurse_window.attributes('-topmost', False))
    nurse_window.title(f"Nurse Dashboard - {username}")
    nurse_window.geometry("1200x700")
    nurse_window.minsize(1000, 600)
    nurse_window.configure(bg="#ffffff")

    # Modern color scheme
    primary_color = "#3498db"  # Blue
    secondary_color = "#e74c3c"  # Red
    accent_color = "#f39c12"  # Orange
    dark_color = "#333333"
    light_color = "#f5f7fa"
    menu_bg = "#2c3e50"
    menu_fg = "#ecf0f1"
    menu_hover_bg = "#34495e"
    menu_header_bg = "#1a252f"
    card_bg = "white"
    card_border = "#e0e0e0"

    # Font settings
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
        tkFont.Font(family="Segoe UI", size=10)
    except tk.TclError:
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Left Menu Frame ---
    menu_frame = tk.Frame(nurse_window, bg=menu_bg, width=280)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Menu header with user info
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170)
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)

    # Avatar
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10))
    avatar_canvas.create_oval(5, 5, 65, 65, fill=primary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper() if username else 'N',
                             font=(title_font[0], 24, "bold"), fill="white")

    # User info
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"),
             fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))
    tk.Label(menu_header_frame, text="Nurse", font=small_font,
             fg="#bdc3c7", bg=menu_header_bg).pack(pady=(0, 15))

    # --- Scrollable Menu Items ---
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)

    # --- Main Dashboard Area ---
    dash_frame = tk.Frame(nurse_window, bg=light_color)
    dash_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Header
    header_frame = tk.Frame(dash_frame, bg=primary_color, height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="Nurse Dashboard", font=title_font, fg="white", bg=primary_color).pack(side="left", padx=30, pady=20)
    
    user_frame = tk.Frame(header_frame, bg=primary_color)
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg=primary_color).pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Nurse", font=("Arial", 10), fg="#eaf2f8", bg=primary_color).pack(side="bottom", anchor="e")

    # --- Stats Cards ---
    stats_frame = tk.Frame(dash_frame, bg=light_color)
    stats_frame.pack(fill=tk.X, pady=(10, 20))

    def get_nurse_stats(db_conn):
        stats_data = {"active_patients": "N/A", "pending_tasks": "N/A", "available_rooms": "N/A"}
        if not db_conn: return stats_data
        try:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM Patients WHERE Status = 'Active'")
                result = cursor.fetchone()
                stats_data["active_patients"] = str(result['count']) if result else "0"
                
                cursor.execute("SELECT COUNT(*) as count FROM Appointments WHERE Status = 'Scheduled'")
                result = cursor.fetchone()
                stats_data["scheduled_tasks"] = str(result['count']) if result else "0"
                
                cursor.execute("SELECT COUNT(*) as count FROM Rooms WHERE Status = 'Available'")
                result = cursor.fetchone()
                stats_data["available_rooms"] = str(result['count']) if result else "0"
        except Exception as e: 
            print(f"Database error fetching nurse stats: {e}")
        return stats_data

    def create_stat_card(parent, title, value, color, icon=None):
        card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=1,
                       highlightbackground=card_border, padx=15, pady=15)
        
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))
        
        if icon:
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                     bg=card_bg, fg=color).pack(side="left", padx=(0, 10))
        
        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"),
                 bg=card_bg, fg="#7f8c8d").pack(side="left")
        
        tk.Label(card, text=str(value), font=card_font,
                 bg=card_bg, fg=dark_color).pack(anchor="w", pady=5)
        
        return card

    stats_data = get_nurse_stats(conn)
    
    stat_cards_info = [
        ("Active Patients", stats_data.get("active_patients", "N/A"), primary_color, "👩‍⚕️"),
        ("Scheduled Tasks", stats_data.get("scheduled_tasks", "N/A"), accent_color, "📝"),
        ("Available Rooms", stats_data.get("available_rooms", "N/A"), secondary_color, "🏥")
    ]

    for i, (title, value, color, icon) in enumerate(stat_cards_info):
        card = create_stat_card(stats_frame, title, value, color, icon)
        card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

    # --- Recent Patients Table ---
    patients_frame = tk.Frame(dash_frame, bg=card_bg, bd=0, relief="flat",
                            highlightbackground=card_border, highlightthickness=1)
    patients_frame.pack(fill="both", expand=True, pady=(0, 10))

    # Header
    patients_header = tk.Frame(patients_frame, bg=card_bg)
    patients_header.pack(fill="x", pady=(10, 5), padx=15)
    
    tk.Label(patients_header, text="RECENT PATIENTS", font=(small_font[0], 10, "bold"),
             bg=card_bg, fg="#7f8c8d").pack(side="left")

    # Treeview for patients
    columns = ("PatientID", "Name", "Gender", "Status")
    tree_style = ttk.Style()
    tree_style.configure("Nurse.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
    tree_style.configure("Nurse.Treeview", font=small_font, rowheight=28)
    
    tree = ttk.Treeview(patients_frame, columns=columns, show="headings", height=8, style="Nurse.Treeview")
    
    # Configure columns
    col_widths = [80, 200, 100, 100]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.CENTER if col in ["PatientID", "Gender"] else tk.W)

    # Scrollbar
    scrollbar = ttk.Scrollbar(patients_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Pack tree and scrollbar
    tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
    scrollbar.pack(side="right", fill="y")

    def load_recent_patients():
        tree.delete(*tree.get_children())
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT PatientID, PatientName, Gender, 
       CASE 
           WHEN Status = 'Active' THEN 'Active' 
           ELSE '⚪ Inactive' 
       END AS StatusLabel
FROM Patients
                """)
                patients = cursor.fetchall()
                
                if patients:
                    for p in patients:
                        tree.insert("", tk.END, values=(
                            p['PatientID'],
                            p['PatientName'],
                            p['Gender'],
                            p['StatusLabel']
                        ))
                else:
                    tree.insert("", tk.END, values=("", "No patients found", "", ""))
        except Exception as e:
            print(f"Error loading patients: {e}")
            tree.insert("", tk.END, values=("Error", "Could not load data", "", ""))

    # Load initial data
    load_recent_patients()

    # --- Menu Items ---
    menu_actions = {
        "Dashboard": ("📊", lambda: load_recent_patients()),
        "View Patient": ("👨‍⚕️", lambda: view_patient_gui(conn)),
        "View Emergency Contacts": ("🆘", lambda: view_emergency_contacts_gui(conn)),
        "View Prescriptions": ("💊", lambda: view_prescriptions_gui(conn)),
        "View Medicines": ("🧪", lambda: view_medicine_gui(conn)),
        "View Rooms": ("🏨", lambda: view_rooms_gui(conn)),
        "View Appointments": ("📅", lambda: view_appointments_gui(conn, 'nurse')),
        "View Insurance": ("🛡️", lambda: view_insurance_gui(conn)),
        "View Services": ("⚕️", lambda: view_services_gui(conn)),
        "View Departments": ("🏛️", lambda: view_departments_gui(conn)),
        "Change Password": ("🔒", lambda: change_password_gui(conn, username)),
        "Logout": ("🚪", lambda: nurse_window.destroy())
    }

    # Organize menu items into categories
    categories = {
        "Patient Care": ["View Patient", "View Emergency Contacts", "View Prescriptions"],
        "Facility": ["View Rooms", "View Departments"],
        "Information": ["View Medicines", "View Appointments", "View Insurance", "View Services"],
        "System": ["Change Password", "Logout"]
    }

    # Create menu buttons
    for widget in menu_buttons_frame.winfo_children(): widget.destroy()  # Clear existing
    
    for category, items in categories.items():
        # Category separator
        sep_label = tk.Label(menu_buttons_frame, text=f"--- {category.upper()} ---", 
                            font=(small_font[0], 9, "italic"), fg="#aed6f1", bg=menu_bg, anchor="w")
        sep_label.pack(fill="x", padx=10, pady=(8, 2))
        
        # Bind scroll events to separator
        for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
            sep_label.bind(event_type, _on_mousewheel_menu)
        
        # Menu items
        for text in items:
            if text in menu_actions:
                icon, command = menu_actions[text]
                btn = tk.Button(menu_buttons_frame, text=f" {icon}  {text}", anchor="w",
                                font=normal_font, fg=menu_fg, bg=menu_bg,
                                bd=0, padx=15, pady=10, relief="flat",
                                activebackground=menu_hover_bg, activeforeground=menu_fg,
                                command=command)
                btn.pack(fill="x", pady=1, padx=5)
                
                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=menu_hover_bg))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=menu_bg))
                
                # Bind scroll events
                for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
                    btn.bind(event_type, _on_mousewheel_menu)

    # Footer
    tk.Label(menu_frame, text="Hospital System © 2025", 
             fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    # Center window
    center_window(nurse_window)

    nurse_window.mainloop()

def open_pharmacist_menu(conn, username):
    """Opens the Pharmacist Dashboard with modern UI"""
    pharmacist_window = tk.Tk()
    pharmacist_window.lift()
    pharmacist_window.attributes('-topmost',True)
    pharmacist_window.after(100, lambda: pharmacist_window.attributes('-topmost', False))
    pharmacist_window.title(f"Pharmacist Dashboard - {username}")
    pharmacist_window.geometry("1200x700")
    pharmacist_window.minsize(1000, 600)
    pharmacist_window.configure(bg="#ffffff")

    # Modern color scheme
    primary_color = "#8e44ad"  # Purple
    secondary_color = "#16a085"  # Teal
    accent_color = "#d35400"  # Pumpkin
    dark_color = "#333333"
    light_color = "#f5f7fa"
    menu_bg = "#2c3e50"
    menu_fg = "#ecf0f1"
    menu_hover_bg = "#34495e"
    menu_header_bg = "#1a252f"
    card_bg = "white"
    card_border = "#e0e0e0"

    # Font settings
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
        tkFont.Font(family="Segoe UI", size=10)
    except tk.TclError:
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Left Menu Frame ---
    menu_frame = tk.Frame(pharmacist_window, bg=menu_bg, width=280)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Menu header with user info
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170)
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)

    # Avatar
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10))
    avatar_canvas.create_oval(5, 5, 65, 65, fill=primary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper() if username else 'P',
                             font=(title_font[0], 24, "bold"), fill="white")

    # User info
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"),
             fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))
    tk.Label(menu_header_frame, text="Pharmacist", font=small_font,
             fg="#bdc3c7", bg=menu_header_bg).pack(pady=(0, 15))

    # --- Scrollable Menu Items ---
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)

    # --- Main Dashboard Area ---
    dash_frame = tk.Frame(pharmacist_window, bg=light_color)
    dash_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Header
    header_frame = tk.Frame(dash_frame, bg=primary_color, height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="Pharmacist Dashboard", font=title_font, fg="white", bg=primary_color).pack(side="left", padx=30, pady=20)
    
    user_frame = tk.Frame(header_frame, bg=primary_color)
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg=primary_color).pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Pharmacist", font=("Arial", 10), fg="#eaf2f8", bg=primary_color).pack(side="bottom", anchor="e")

    # --- Stats Cards ---
    stats_frame = tk.Frame(dash_frame, bg=light_color)
    stats_frame.pack(fill=tk.X, pady=(10, 20))

    def get_pharmacist_stats(db_conn):
        stats_data = { "low_stock": "N/A", "total_medicines": "N/A"}
        if not db_conn: return stats_data
        try:
            with db_conn.cursor() as cursor:
                
                cursor.execute("SELECT COUNT(*) as count FROM MedicineBatch WHERE Quantity < 10")
                result = cursor.fetchone()
                stats_data["low_stock"] = str(result['count']) if result else "0"
                
                cursor.execute("SELECT COUNT(DISTINCT MedicineID) as count FROM Medicine")
                result = cursor.fetchone()
                stats_data["total_medicines"] = str(result['count']) if result else "0"
        except Exception as e: 
            print(f"Database error fetching pharmacist stats: {e}")
        return stats_data

    def create_stat_card(parent, title, value, color, icon=None):
        card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=1,
                       highlightbackground=card_border, padx=15, pady=15)
        
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))
        
        if icon:
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                     bg=card_bg, fg=color).pack(side="left", padx=(0, 10))
        
        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"),
                 bg=card_bg, fg="#7f8c8d").pack(side="left")
        
        tk.Label(card, text=str(value), font=card_font,
                 bg=card_bg, fg=dark_color).pack(anchor="w", pady=5)
        
        return card

    stats_data = get_pharmacist_stats(conn)
    
    stat_cards_info = [
        ("Low Stock Medicines", stats_data.get("low_stock", "N/A"), accent_color, "⚠️"),
        ("Total Medicines", stats_data.get("total_medicines", "N/A"), secondary_color, "🧪")
    ]

    for i, (title, value, color, icon) in enumerate(stat_cards_info):
        card = create_stat_card(stats_frame, title, value, color, icon)
        card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

    # --- Recent Prescriptions Table ---
    prescriptions_frame = tk.Frame(dash_frame, bg=card_bg, bd=0, relief="flat",
                            highlightbackground=card_border, highlightthickness=1)
    prescriptions_frame.pack(fill="both", expand=True, pady=(0, 10))

    # Header
    prescriptions_header = tk.Frame(prescriptions_frame, bg=card_bg)
    prescriptions_header.pack(fill="x", pady=(10, 5), padx=15)
    
    tk.Label(prescriptions_header, text="RECENT PRESCRIPTIONS", font=(small_font[0], 10, "bold"),
             bg=card_bg, fg="#7f8c8d").pack(side="left")

    # Treeview for prescriptions
    columns = ("PrescriptionID", "Patient", "Doctor", "Date")
    tree_style = ttk.Style()
    tree_style.configure("Pharmacist.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
    tree_style.configure("Pharmacist.Treeview", font=small_font, rowheight=28)
    
    tree = ttk.Treeview(prescriptions_frame, columns=columns, show="headings", height=8, style="Pharmacist.Treeview")
    
    # Configure columns
    col_widths = [100, 180, 150, 100]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.CENTER if col in ["PrescriptionID"] else tk.W)

    # Scrollbar
    scrollbar = ttk.Scrollbar(prescriptions_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Pack tree and scrollbar
    tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
    scrollbar.pack(side="right", fill="y")

    def load_recent_prescriptions():
        tree.delete(*tree.get_children())
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.PrescriptionID, pt.PatientName, d.DoctorName, 
                           p.PrescriptionDate
                    FROM Prescription p
                    JOIN Patients pt ON p.PatientID = pt.PatientID
                    JOIN Doctors d ON p.DoctorID = d.DoctorID
                    ORDER BY p.PrescriptionDate DESC
                    LIMIT 15
                """)
                prescriptions = cursor.fetchall()
                
                if prescriptions:
                    for rx in prescriptions:
                        tree.insert("", tk.END, values=(
                            rx['PrescriptionID'],
                            rx['PatientName'],
                            rx['DoctorName'],
                            rx['PrescriptionDate'].strftime('%Y-%m-%d') if rx['PrescriptionDate'] else ""
                        ))
                else:
                    tree.insert("", tk.END, values=("", "No prescriptions found", "", "", ""))
        except Exception as e:
            print(f"Error loading prescriptions: {e}")
            tree.insert("", tk.END, values=("Error", "Could not load data", "", "", ""))

    # Load initial data
    load_recent_prescriptions()

    # --- Menu Items ---
    menu_actions = {
        "Dashboard": ("📊", lambda: load_recent_prescriptions()),
        "View Prescriptions": ("💊", lambda: view_prescriptions_gui(conn)),
        "View Prescriptions Details": ("💊", lambda: view_prescription_gui(conn)),
        "View Medicines": ("🧪", lambda: view_medicine_gui(conn)),
        "View Medicine Batch": ("📦", lambda: view_medicine_batches_gui(conn)),
        "Adjust Medicine Stock": ("🔄", lambda: adjust_medicine_batch_gui(conn)),
        "View Inventory": ("📋", lambda: view_inventory_gui(conn)),
        "Adjust Inventory": ("✏️", lambda: adjust_inventory_gui(conn)),
        "View Patient Services": ("⚕️", lambda: view_patient_services_gui(conn)),
        "View Insurance": ("🛡️", lambda: view_insurance_gui(conn)),
        "Change Password": ("🔒", lambda: change_password_gui(conn, username)),
        "Logout": ("🚪", lambda: pharmacist_window.destroy())
    }

    # Organize menu items into categories
    categories = {
        "Prescriptions": ["View Prescriptions", "View Prescriptions Details"],
        "Medicines": ["View Medicines", "View Medicine Batch", "Adjust Medicine Stock"],
        "Inventory": ["View Inventory", "Adjust Inventory"],
        "Information": ["View Patient Services", "View Insurance"],
        "System": ["Change Password", "Logout"]
    }

    # Create menu buttons
    for widget in menu_buttons_frame.winfo_children(): widget.destroy()  # Clear existing
    
    for category, items in categories.items():
        # Category separator
        sep_label = tk.Label(menu_buttons_frame, text=f"--- {category.upper()} ---", 
                            font=(small_font[0], 9, "italic"), fg="#aed6f1", bg=menu_bg, anchor="w")
        sep_label.pack(fill="x", padx=10, pady=(8, 2))
        
        # Bind scroll events to separator
        for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
            sep_label.bind(event_type, _on_mousewheel_menu)
        
        # Menu items
        for text in items:
            if text in menu_actions:
                icon, command = menu_actions[text]
                btn = tk.Button(menu_buttons_frame, text=f" {icon}  {text}", anchor="w",
                                font=normal_font, fg=menu_fg, bg=menu_bg,
                                bd=0, padx=15, pady=10, relief="flat",
                                activebackground=menu_hover_bg, activeforeground=menu_fg,
                                command=command)
                btn.pack(fill="x", pady=1, padx=5)
                
                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=menu_hover_bg))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=menu_bg))
                
                # Bind scroll events
                for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
                    btn.bind(event_type, _on_mousewheel_menu)

    # Footer
    tk.Label(menu_frame, text="Hospital System © 2025", 
             fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    # Center window
    center_window(pharmacist_window)

    pharmacist_window.mainloop()

def open_director_menu(conn, username):
    """Opens the Director Dashboard with modern UI"""
    director_window = tk.Tk()
    director_window.lift()
    director_window.attributes('-topmost',True)
    director_window.after(100, lambda: director_window.attributes('-topmost', False))
    director_window.title(f"Director Dashboard - {username}")
    director_window.geometry("1200x700")
    director_window.minsize(1000, 600)
    director_window.configure(bg="#ffffff")

    # Modern color scheme for director
    primary_color = "#2c3e50"   # Dark Blue
    secondary_color = "#2980b9" # Blue
    accent_color = "#27ae60"    # Green
    dark_color = "#333333"
    light_color = "#f5f7fa"
    menu_bg = "#34495e"
    menu_fg = "#ecf0f1"
    menu_hover_bg = "#2c3e50"
    menu_header_bg = "#1a252f"
    card_bg = "white"
    card_border = "#e0e0e0"

    # Font settings
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
        tkFont.Font(family="Segoe UI", size=10)
    except tk.TclError:
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Left Menu Frame ---
    menu_frame = tk.Frame(director_window, bg=menu_bg, width=280)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Menu header with user info
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170)
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)

    # Avatar
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10))
    avatar_canvas.create_oval(5, 5, 65, 65, fill=secondary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper() if username else 'D',
                             font=(title_font[0], 24, "bold"), fill="white")

    # User info
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"),
             fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))
    tk.Label(menu_header_frame, text="Hospital Director", font=small_font,
             fg="#bdc3c7", bg=menu_header_bg).pack(pady=(0, 15))

    # --- Scrollable Menu Items ---
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)

    # --- Main Dashboard Area ---
    dash_frame = tk.Frame(director_window, bg=light_color)
    dash_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Header
    header_frame = tk.Frame(dash_frame, bg=primary_color, height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="Director Dashboard", font=title_font, fg="white", bg=primary_color).pack(side="left", padx=30, pady=20)
    
    user_frame = tk.Frame(header_frame, bg=primary_color)
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg=primary_color).pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Director", font=("Arial", 10), fg="#eaf2f8", bg=primary_color).pack(side="bottom", anchor="e")

    # --- Stats Cards ---
    stats_frame = tk.Frame(dash_frame, bg=light_color)
    stats_frame.pack(fill=tk.X, pady=(10, 20))

    def create_stat_card(parent, title, value, color, icon=None):
        card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=1,
                      highlightbackground=card_border, padx=15, pady=15)
        
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))
        
        if icon:
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                     bg=card_bg, fg=color).pack(side="left", padx=(0, 10))
        
        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"),
                 bg=card_bg, fg="#7f8c8d").pack(side="left")
        
        tk.Label(card, text=str(value), font=card_font,
                 bg=card_bg, fg=dark_color).pack(anchor="w", pady=5)
        
        return card

    def get_director_stats(db_conn):
        stats_data = {
            "total_doctors": "N/A",
            "total_patients": "N/A",
            "total_departments": "N/A",
            "total_revenue": "N/A"
        }
        try:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM Doctors")
                stats_data["total_doctors"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) AS count FROM Patients")
                stats_data["total_patients"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) AS count FROM Departments")
                stats_data["total_departments"] = cursor.fetchone()['count']
                
                cursor.execute("SELECT SUM(TotalAmount) AS total FROM Invoices WHERE PaymentStatus = 'Paid'")
                total = cursor.fetchone()['total'] or 0
                stats_data["total_revenue"] = f"${total:,.2f}"
                
        except Exception as e:
            print(f"Database error: {e}")
        return stats_data

    stats_data = get_director_stats(conn)
    
    stat_cards_info = [
        ("Total Doctors", stats_data["total_doctors"], secondary_color, "👨⚕️"),
        ("Total Patients", stats_data["total_patients"], accent_color, "👩⚕️"),
        ("Departments", stats_data["total_departments"], primary_color, "🏥"),
        ("Total Revenue", stats_data["total_revenue"], "#27ae60", "💰")
    ]

    for i, (title, value, color, icon) in enumerate(stat_cards_info):
        card = create_stat_card(stats_frame, title, value, color, icon)
        card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

    # --- Recent Financial Transactions Table ---
    transactions_frame = tk.Frame(dash_frame, bg=card_bg, highlightthickness=1,
                                highlightbackground=card_border)
    transactions_frame.pack(fill="both", expand=True, pady=(0, 10))

    # Header
    tk.Label(transactions_frame, text="RECENT FINANCIAL TRANSACTIONS", 
            font=(small_font[0], 10, "bold"), bg=card_bg, fg="#7f8c8d").pack(pady=(10,5), padx=15, anchor="w")

    # Treeview
    columns = ("InvoiceID", "Patient", "Amount", "Date", "Status")
    tree_style = ttk.Style()
    tree_style.configure("Director.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
    tree_style.configure("Director.Treeview", font=small_font, rowheight=28)
    
    tree = ttk.Treeview(transactions_frame, columns=columns, show="headings", height=8, style="Director.Treeview")
    
    # Configure columns
    col_widths = [80, 150, 100, 100, 80]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.CENTER if col in ["Amount", "Status"] else tk.W)

    # Scrollbar
    scrollbar = ttk.Scrollbar(transactions_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
    scrollbar.pack(side="right", fill="y")

    def load_recent_transactions():
        tree.delete(*tree.get_children())
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT i.InvoiceID, p.PatientName, i.TotalAmount, 
                           i.InvoiceDate, i.PaymentStatus 
                    FROM Invoices i
                    JOIN Patients p ON i.PatientID = p.PatientID
                    ORDER BY i.InvoiceDate DESC 
                    LIMIT 15
                """)
                for invoice in cursor.fetchall():
                    tree.insert("", tk.END, values=(
                        invoice['InvoiceID'],
                        invoice['PatientName'],
                        f"${invoice['TotalAmount']:,.2f}",
                        invoice['InvoiceDate'].strftime('%Y-%m-%d'),
                        invoice['PaymentStatus']
                    ))
        except Exception as e:
            print(f"Error loading transactions: {e}")

    load_recent_transactions()

    # --- Menu Items ---
    menu_actions = {
        "View Doctors": ("👨⚕️", lambda: view_doctor_gui(conn)),
        "View Patients": ("👩⚕️", lambda: view_patient_gui(conn)),
        "View Departments": ("🏥", lambda: view_departments_gui(conn)),
        "Financial Report": ("📊", lambda: generate_financial_report_gui(conn)),
        "Room Report": ("🏨", lambda: get_room_statistics_gui(conn)),
        "Statistics Report": ("📈", lambda: generate_statistics_gui(conn)),
        "View Insurance": ("🛡️", lambda: view_insurance_gui(conn)),
        "View Invoices": ("🧾", lambda: view_invoices_gui(conn)),
        "View Appointments": ("📅", lambda: view_appointments_gui(conn, 'director')),
        "View Services": ("⚕️", lambda: view_services_gui(conn)),
        "View Inventory": ("📦", lambda: view_inventory_gui(conn)),
        "System Users": ("👥", lambda: view_system_users_gui(conn)),
        "Change Password": ("🔒", lambda: change_password_gui(conn, username)),
        "Logout": ("🚪", lambda: director_window.destroy())
    }

    categories = {
        "Management": ["View Doctors", "View Patients", "View Departments"],
        "Reports": ["Financial Report", "Room Report", "Statistics Report"],
        "Financial": ["View Invoices", "View Insurance"],
        "Operations": ["View Appointments", "View Services", "View Inventory"],
        "System": ["System Users", "Change Password", "Logout"]
    }

    # Create menu buttons
    for widget in menu_buttons_frame.winfo_children(): widget.destroy()
    
    for category, items in categories.items():
        # Category separator
        sep_label = tk.Label(menu_buttons_frame, text=f"--- {category.upper()} ---", 
                            font=(small_font[0], 9, "italic"), fg="#aed6f1", bg=menu_bg, anchor="w")
        sep_label.pack(fill="x", padx=10, pady=(8, 2))
        
        for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
            sep_label.bind(event_type, _on_mousewheel_menu)
        
        for text in items:
            if text in menu_actions:
                icon, command = menu_actions[text]
                btn = tk.Button(menu_buttons_frame, text=f" {icon}  {text}", anchor="w",
                                font=normal_font, fg=menu_fg, bg=menu_bg,
                                bd=0, padx=15, pady=10, relief="flat",
                                activebackground=menu_hover_bg, activeforeground=menu_fg,
                                command=command)
                btn.pack(fill="x", pady=1, padx=5)
                
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=menu_hover_bg))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=menu_bg))
                
                for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
                    btn.bind(event_type, _on_mousewheel_menu)

    # Footer
    tk.Label(menu_frame, text="Hospital System © 2025", 
             fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    center_window(director_window)
    director_window.mainloop()

def open_inventory_manager_menu(conn, username):
    """Opens the Inventory Management Dashboard with modern UI"""
    inv_window = tk.Tk()
    inv_window.lift()
    inv_window.attributes('-topmost',True)
    inv_window.after(100, lambda: inv_window.attributes('-topmost', False))
    inv_window.title(f"Inventory Manager - {username}")
    inv_window.geometry("1200x700")
    inv_window.minsize(1000, 600)
    inv_window.configure(bg="#ffffff")

    # Modern color scheme
    primary_color = "#16a085"  # Teal
    secondary_color = "#2980b9"  # Blue
    accent_color = "#f39c12"  # Orange
    dark_color = "#333333"
    light_color = "#f5f7fa"
    menu_bg = "#2c3e50"
    menu_fg = "#ecf0f1"
    menu_hover_bg = "#34495e"
    menu_header_bg = "#1a252f"
    card_bg = "white"
    card_border = "#e0e0e0"

    # Font settings
    try:
        title_font = ("Segoe UI", 18, "bold")
        header_font = ("Segoe UI", 14, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
        card_font = ("Segoe UI", 14, "bold")
        tkFont.Font(family="Segoe UI", size=10)
    except tk.TclError:
        title_font = ("Arial", 18, "bold")
        header_font = ("Arial", 14, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)
        card_font = ("Arial", 14, "bold")

    # --- Left Menu Frame ---
    menu_frame = tk.Frame(inv_window, bg=menu_bg, width=280)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    # Menu header with user info
    menu_header_frame = tk.Frame(menu_frame, bg=menu_header_bg, height=170)
    menu_header_frame.pack(fill="x")
    menu_header_frame.pack_propagate(False)

    # Avatar
    avatar_canvas = tk.Canvas(menu_header_frame, width=70, height=70, bg=menu_header_bg, highlightthickness=0)
    avatar_canvas.pack(pady=(25, 10))
    avatar_canvas.create_oval(5, 5, 65, 65, fill=primary_color, outline="")
    avatar_canvas.create_text(35, 35, text=username[0].upper(), 
                            font=(title_font[0], 24, "bold"), fill="white")

    # User info
    tk.Label(menu_header_frame, text=username, font=(normal_font[0], 12, "bold"),
            fg=menu_fg, bg=menu_header_bg).pack(pady=(0, 5))
    tk.Label(menu_header_frame, text="Inventory Manager", font=small_font,
            fg="#bdc3c7", bg=menu_header_bg).pack(pady=(0, 15))

    # --- Scrollable Menu Items ---
    menu_canvas = tk.Canvas(menu_frame, bg=menu_bg, highlightthickness=0)
    menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
    menu_buttons_frame = tk.Frame(menu_canvas, bg=menu_bg)
    
    menu_canvas.create_window((0, 0), window=menu_buttons_frame, anchor="nw", tags="menu_buttons_frame")
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
    
    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)
    
    def update_scroll_region(event):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfig("menu_buttons_frame", width=event.width)
    menu_buttons_frame.bind("<Configure>", update_scroll_region)
    
    def _on_mousewheel_menu(event):
        delta = 0
        if hasattr(event, 'delta') and event.delta != 0: delta = -1 * (event.delta // 120)
        elif hasattr(event, 'num') and event.num in (4, 5): delta = -1 if event.num == 4 else 1
        if delta: menu_canvas.yview_scroll(delta, "units")
    
    menu_frame.bind_all("<MouseWheel>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-4>", _on_mousewheel_menu)
    menu_frame.bind_all("<Button-5>", _on_mousewheel_menu)

    # --- Main Dashboard Area ---
    dash_frame = tk.Frame(inv_window, bg=light_color)
    dash_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Header
    header_frame = tk.Frame(dash_frame, bg=primary_color, height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="Inventory Dashboard", font=title_font, fg="white", bg=primary_color).pack(side="left", padx=30, pady=20)
    
    user_frame = tk.Frame(header_frame, bg=primary_color)
    user_frame.pack(side="right", padx=20, pady=15)
    tk.Label(user_frame, text=f"Welcome, {username}", font=("Arial", 12), fg="white", bg=primary_color).pack(side="top", anchor="e")
    tk.Label(user_frame, text="Role: Inventory Manager", font=("Arial", 10), fg="#eaf2f8", bg=primary_color).pack(side="bottom", anchor="e")

    # --- Stats Cards ---
    stats_frame = tk.Frame(dash_frame, bg=light_color)
    stats_frame.pack(fill=tk.X, pady=(10, 20))

    def get_inventory_stats(db_conn):
        stats = {
            "total_items": "N/A",
            "low_stock": "N/A", 
            "total_medicines": "N/A",
            "expiring_soon": "N/A"
        }
        try:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(distinct InventoryID) as count FROM Inventory")
                result = cursor.fetchone()
                stats["total_items"] = str(result['count']) if result and result['count'] is not None else "0"
                
                cursor.execute("SELECT COUNT(*) as count FROM Inventory WHERE Quantity < 5")
                result = cursor.fetchone()
                stats["low_stock"] = str(result['count']) if result and result['count'] is not None else "0"
                
                cursor.execute("SELECT COUNT(DISTINCT MedicineID) as count FROM Medicine")
                result = cursor.fetchone()
                stats["total_medicines"] = str(result['count']) if result and result['count'] is not None else "0"
                
                cursor.execute("""SELECT COUNT(*) as count FROM MedicineBatch 
                               WHERE ExpiryDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)""")
                result = cursor.fetchone()
                stats["expiring_soon"] = str(result['count']) if result and result['count'] is not None else "0"
                
        except Exception as e:
            print(f"Database error: {e}")
        return stats

    def create_stat_card(parent, title, value, color, icon=None):
        card = tk.Frame(parent, bg=card_bg, bd=0, highlightthickness=1,
                      highlightbackground=card_border, padx=15, pady=15)
        
        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", pady=(0, 10))
        
        if icon:
            tk.Label(header, text=icon, font=(normal_font[0], 16),
                     bg=card_bg, fg=color).pack(side="left", padx=(0, 10))
        
        tk.Label(header, text=title.upper(), font=(small_font[0], 10, "bold"),
                 bg=card_bg, fg="#7f8c8d").pack(side="left")
        
        tk.Label(card, text=str(value), font=card_font,
                 bg=card_bg, fg=dark_color).pack(anchor="w", pady=5)
        
        return card

    stats_data = get_inventory_stats(conn)
    
    stat_cards_info = [
        ("Total Items", stats_data.get("total_items","N/A"), primary_color, "📦"),
        ("Low Stock", stats_data.get("low_stock","N/A"), accent_color, "⚠️"),
        ("Total Medicines", stats_data.get("total_medicines","N/A"), secondary_color, "💊"),
        ("Expiring Soon", stats_data.get("expiring_soon","N/A"), "#e74c3c", "⏳")
    ]

    for i, (title, value, color, icon) in enumerate(stat_cards_info):
        card = create_stat_card(stats_frame, title, value, color, icon)
        card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

    # --- Recent Adjustments Table ---
    adjustments_frame = tk.Frame(dash_frame, bg=card_bg, highlightthickness=1,
                               highlightbackground=card_border)
    adjustments_frame.pack(fill="both", expand=True, pady=(0, 10))

    # Header
    tk.Label(adjustments_frame, text="RECENT STOCK ADJUSTMENTS", 
            font=(small_font[0], 10, "bold"), bg=card_bg, fg="#7f8c8d").pack(pady=(10,5), padx=15, anchor="w")

    # Treeview
    columns = ("Date", "Type", "Item", "Quantity", "User")
    tree_style = ttk.Style()
    tree_style.configure("Inventory.Treeview.Heading", font=(small_font[0], small_font[1], 'bold'))
    tree_style.configure("Inventory.Treeview", font=small_font, rowheight=28)
    
    tree = ttk.Treeview(adjustments_frame, columns=columns, show="headings", height=8, style="Inventory.Treeview")
    
    # Configure columns
    col_widths = [120, 100, 200, 80, 150]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.CENTER if col in ["Quantity"] else tk.W)

    # Scrollbar
    scrollbar = ttk.Scrollbar(adjustments_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
    scrollbar.pack(side="right", fill="y")

    def load_recent_adjustments():
        tree.delete(*tree.get_children())
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT a.AdjustmentDate, a.AdjustmentType, 
                           COALESCE(i.ItemName, m.MedicineName), 
                           a.QuantityChanged, a.ChangedBy 
                    FROM Adjustments a
                    LEFT JOIN Inventory i ON a.InventoryID = i.InventoryID
                    LEFT JOIN MedicineBatch mb ON a.BatchID = mb.BatchID
                    LEFT JOIN Medicine m ON mb.MedicineID = m.MedicineID
                    ORDER BY a.AdjustmentDate DESC 
                    LIMIT 15
                """)
                for row in cursor.fetchall():
                    tree.insert("", tk.END, values=(
                        row[0].strftime('%Y-%m-%d'),
                        row[1],
                        row[2],
                        row[3],
                        row[4]
                    ))
        except Exception as e:
            print(f"Error loading adjustments: {e}")

    load_recent_adjustments()

    # --- Menu Items ---
    menu_actions = {
        "Dashboard": ("📊", lambda: load_recent_adjustments()),
        "View Inventory": ("📋", lambda: view_inventory_gui(conn)),
        "Add Inventory Item": ("➕", lambda: add_inventory_gui(conn)),
        "Update Inventory Item": ("✏️", lambda: update_inventory_gui(conn)),
        "Disable Inventory Item": ("❌", lambda: disable_inventory_item_gui(conn)),
        "Adjust Inventory": ("🔄", lambda: adjust_inventory_gui(conn)),
        "View Medicines": ("💊", lambda: view_medicine_gui(conn)),
        "Add Medicine": ("➕", lambda: add_medicine_gui(conn)),
        "Update Medicine": ("✏️", lambda: update_medicine_gui(conn)),
        "Delete Medicine": ("❌", lambda: delete_medicine_gui(conn)),
        "View Medicine Batch": ("📦", lambda: view_medicine_batches_gui(conn)),
        "Add Medicine Batch": ("➕", lambda: add_medicine_batch_gui(conn)),
        "Update Medicine Batch": ("✏️", lambda: update_medicine_batch_gui(conn)),
        "Delete Medicine Batch": ("❌", lambda: delete_medicine_batch_gui(conn)),
        "Adjust Medicine Stock": ("🔄", lambda: adjust_medicine_batch_gui(conn)),
        "Change Password": ("🔒", lambda: change_password_gui(conn, username)),
        "Logout": ("🚪", lambda: inv_window.destroy())
    }

    categories = {
        "Inventory Management": ["View Inventory", "Add Inventory Item", "Update Inventory Item",
                               "Disable Inventory Item", "Adjust Inventory"],
        "Medicine Management": ["View Medicines", "Add Medicine", "Update Medicine",
                              "Delete Medicine", "View Medicine Batch", "Add Medicine Batch",
                              "Update Medicine Batch", "Delete Medicine Batch", "Adjust Medicine Stock"],
        "System": ["Change Password", "Logout"]
    }

    # Create menu buttons
    for widget in menu_buttons_frame.winfo_children(): widget.destroy()
    
    for category, items in categories.items():
        # Category separator
        sep_label = tk.Label(menu_buttons_frame, text=f"--- {category.upper()} ---", 
                            font=(small_font[0], 9, "italic"), fg="#aed6f1", bg=menu_bg, anchor="w")
        sep_label.pack(fill="x", padx=10, pady=(8, 2))
        
        for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
            sep_label.bind(event_type, _on_mousewheel_menu)
        
        for text in items:
            if text in menu_actions:
                icon, command = menu_actions[text]
                btn = tk.Button(menu_buttons_frame, text=f" {icon}  {text}", anchor="w",
                                font=normal_font, fg=menu_fg, bg=menu_bg,
                                bd=0, padx=15, pady=10, relief="flat",
                                activebackground=menu_hover_bg, activeforeground=menu_fg,
                                command=command)
                btn.pack(fill="x", pady=1, padx=5)
                
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=menu_hover_bg))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=menu_bg))
                
                for event_type in ["<MouseWheel>", "<Button-4>", "<Button-5>"]: 
                    btn.bind(event_type, _on_mousewheel_menu)

    # Footer
    tk.Label(menu_frame, text="Hospital System © 2025", 
             fg="#7f8c8d", bg=menu_bg, font=(small_font[0], 8)).pack(side="bottom", pady=15)

    center_window(inv_window)
    inv_window.mainloop()

def view_system_users_gui(conn):

    view_window = tk.Toplevel()
    view_window.title("View System Users")
    view_window.geometry("800x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="System Users", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Username:", bg=BG_COLOR).grid(row=0, column=0, padx=5, sticky='w')
    username_entry = tk.Entry(search_frame)
    username_entry.grid(row=0, column=1, padx=5)
    apply_styles(username_entry)

    tk.Label(search_frame, text="Role:", bg=BG_COLOR).grid(row=0, column=2, padx=5, sticky='w')
    role_var = tk.StringVar()
    role_menu = ttk.OptionMenu(search_frame, role_var, "All", "All", "admin", "doctor", "receptionist", "accountant", "nurse", "pharmacist", "director", "inventory_manager")
    role_menu.grid(row=0, column=3, padx=5)

    # Treeview
    columns = ("UserID", "Username", "Role", "Status")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def search():
        username = username_entry.get().strip() or None
        role = role_var.get() if role_var.get() != "All" else None
        success, result = search_system_users(conn, username, role)
        if success:
            tree.delete(*tree.get_children())
            for row in result:
                tree.insert("", tk.END, values=(row["UserID"], row["Username"], row["Role"], row["Status"]))
        else:
            messagebox.showerror("Error", f"Failed to search users: {result}")
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(search_frame, text="Search", command=search)
    apply_styles(search_btn)
    search_btn.grid(row=0, column=4, padx=10)

    view_window.after(100, search)

# GUI Wrapper Functions for Core Logic
def register_user_gui(conn):
    """GUI for registering a new user"""
    reg_window = tk.Toplevel()
    reg_window.title("Register New User")
    reg_window.geometry("400x320")
    reg_window.config(bg=BG_COLOR)
    center_window(reg_window)
    reg_window.lift()
    reg_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    reg_window.after(100, lambda: reg_window.attributes('-topmost', False))
    
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
    role_var.set("admin")
    role_menu = ttk.OptionMenu(form_frame, role_var, role_var.get(), "admin", "accountant", "receptionist", "nurse", "pharmacist", "director", "inventory_manager")
    role_menu.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    
    def submit():
        username = entry_username.get().strip()
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
    delete_window.lift()
    delete_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    delete_window.after(100, lambda: delete_window.attributes('-topmost', False))
    
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
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Delete User",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

# Doctor GUI Functions
def add_doctor_gui(conn):
    """GUI for adding a doctor"""
    add_window = tk.Toplevel()
    add_window.title("Add Doctor")
    add_window.geometry("400x350")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    add_window.lift()
    add_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    add_window.after(100, lambda: add_window.attributes('-topmost', False))
    
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
            add_window.lift()
            add_window.focus_force()

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
    delete_window.lift()
    delete_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng

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
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Delete Doctor",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def update_doctor_info_gui(conn):
    """GUI to update doctor info"""
    update_window = tk.Toplevel()
    update_window.title("Update Doctor Information")
    update_window.geometry("400x350")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Title
    title_label = tk.Label(main_frame, text="Update Doctor Information", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR)
    title_label.pack(pady=(0, 20))

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Doctor ID
    tk.Label(form_frame, text="Doctor ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_doctor_id = tk.Entry(form_frame)
    entry_doctor_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_doctor_id)

    # Doctor Name
    tk.Label(form_frame, text="Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    # Speciality
    tk.Label(form_frame, text="Speciality:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_speciality = tk.Entry(form_frame)
    entry_speciality.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_speciality)

    # Department ID
    tk.Label(form_frame, text="Department ID:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_dept_id = tk.Entry(form_frame)
    entry_dept_id.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_dept_id)

    # Phone Number
    tk.Label(form_frame, text="Phone:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    entry_phone = tk.Entry(form_frame)
    entry_phone.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_phone)

    # Email
    tk.Label(form_frame, text="Email:", bg=BG_COLOR).grid(row=5, column=0, sticky="e", pady=5)
    entry_email = tk.Entry(form_frame)
    entry_email.grid(row=5, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_email)

    def submit():
        doctor_id = entry_doctor_id.get()
        name = entry_name.get()
        speciality = entry_speciality.get()
        dept_id = entry_dept_id.get()
        phone = entry_phone.get()
        email = entry_email.get()

        success, message = update_doctor_info(conn, doctor_id, name, speciality, dept_id, phone, email)
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Update Doctor", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def assign_doctor_user_gui(conn):
    """GUI để gán username mới cho bác sĩ"""
    window = tk.Toplevel()
    window.title("Assign Doctor User")
    window.geometry("400x350")
    window.config(bg=BG_COLOR)
    center_window(window)
    window.lift()
    window.attributes('-topmost', True)
    window.after(100, lambda: window.attributes('-topmost', False))

    # Frame chính
    frame = tk.Frame(window, bg=BG_COLOR)
    frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Doctor ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_doctor_id = tk.Entry(frame)
    entry_doctor_id.grid(row=0, column=1, pady=5)
    apply_styles(entry_doctor_id)

    tk.Label(frame, text="New Username:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_username = tk.Entry(frame)
    entry_username.grid(row=1, column=1, pady=5)
    apply_styles(entry_username)

    tk.Label(frame, text="Password (optional):", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_password = tk.Entry(frame, show="*")
    entry_password.grid(row=2, column=1, pady=5)
    apply_styles(entry_password)

    def submit():
        doctor_id = entry_doctor_id.get().strip()
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if not doctor_id or not username:
            messagebox.showerror("Error", "⚠️ Doctor ID and Username are required.")
            window.lift()
            window.focus_force()
            return

        success, message = assign_doctor_user(conn, doctor_id, username, password)
        if success:
            messagebox.showinfo("Success", message)
            window.destroy()
        else:
            messagebox.showerror("Error", message)
            window.lift()
            window.focus_force()

    # Nút Submit
    submit_btn = tk.Button(frame, text="Assign User", command=submit)
    apply_styles(submit_btn)
    submit_btn.grid(row=3, columnspan=2, pady=20)

    # Giãn cột
    frame.grid_columnconfigure(1, weight=1)

def view_doctor_gui(conn):
    """GUI để xem và tìm kiếm thông tin bác sĩ"""
    view_window = tk.Toplevel()
    view_window.title("Doctor Directory")
    view_window.geometry("800x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="Doctor Information", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(pady=5)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()


    tk.Label(search_frame, text="Doctor ID:", bg=BG_COLOR).grid(row=0, column=0, padx=5)
    doctor_id_entry = tk.Entry(search_frame)
    doctor_id_entry.grid(row=0, column=1, padx=5)
    apply_styles(doctor_id_entry)

    tk.Label(search_frame, text="Doctor Name:", bg=BG_COLOR).grid(row=0, column=2, padx=5)
    doctor_name_entry = tk.Entry(search_frame)
    doctor_name_entry.grid(row=0, column=3, padx=5)
    apply_styles(doctor_name_entry)

    # Treeview
    columns = ("DoctorID", "DoctorName", "Specialty", "DepartmentID", "PhoneNumber", "Email")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    # Set column headings and widths
    col_widths = [80, 150, 130, 100, 110, 200]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def load_data():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        doctor_id = doctor_id_entry.get().strip() or None
        doctor_name = doctor_name_entry.get().strip() or None
        success, result = search_doctors(conn, doctor_id, doctor_name)
        if success and result:
            for row in result:
                if len(row) >= 6:  # Đảm bảo đủ cột
                    tree.insert("", tk.END, values=(
                        row['DoctorID'], row['DoctorName'], row['Specialty'], row['DepartmentID'], row['PhoneNumber'], row['Email']
                    ))
                else:
                    error_label.config(text="No data found")
                    view_window.lift()
                    view_window.focus_force()
                    return
        else:
            error_label.config(text="No data found")
            view_window.lift()

    # Search button
    search_btn = tk.Button(search_frame, text="Search", command=load_data)
    apply_styles(search_btn)
    search_btn.grid(row=0, column=4, padx=10)

    # ✅ Load all data immediately when GUI opens
    view_window.after(100, load_data)

def disable_doctor_gui(conn):
    """GUI for disabling a doctor's account"""
    disable_window = tk.Toplevel()
    disable_window.title("Disable Doctor Account")
    disable_window.geometry("300x150")
    disable_window.config(bg=BG_COLOR)
    center_window(disable_window)
    disable_window.lift()
    disable_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    disable_window.after(100, lambda: disable_window.attributes('-topmost', False))
    
    # Main frame
    main_frame = tk.Frame(disable_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Doctor ID
    tk.Label(main_frame, text="Doctor ID:", bg=BG_COLOR).pack()
    entry_doctorID = tk.Entry(main_frame)
    entry_doctorID.pack(pady=5)
    apply_styles(entry_doctorID)
    
    def submit():
        doctorID = entry_doctorID.get()
        success, message = disable_doctor(conn, doctorID)
        if success:
            messagebox.showinfo("Success", message)
            disable_window.destroy()
        else:
            messagebox.showerror("Error", message)
            disable_window.lift()
            disable_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Disable Doctor",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

#Patient GUI Functions
def add_patient_gui(conn):
    """GUI to add a new patient"""
    window = tk.Toplevel()
    window.title("Add New Patient")
    window.geometry("400x450")
    window.config(bg=BG_COLOR)
    center_window(window)
    window.lift()
    window.attributes('-topmost', True)
    window.after(100, lambda: window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Title
    title_label = tk.Label(main_frame, text="Add New Patient", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR)
    title_label.pack(pady=(0, 20))

    # Form fields
    fields = {
        "Name": tk.StringVar(),
        "Date of Birth (YYYY-MM-DD)": tk.StringVar(),
        "Gender": tk.StringVar(),
        "Address": tk.StringVar(),
        "Phone Number": tk.StringVar()
    }

    entries = {}
    for i, (label, var) in enumerate(fields.items()):
        tk.Label(main_frame, text=label + ":", bg=BG_COLOR).pack(anchor="w", pady=(5, 0))
        entry = tk.Entry(main_frame, textvariable=var)
        apply_styles(entry)
        entry.pack(fill=tk.X, pady=5)
        entries[label] = entry

    def submit():
        name = fields["Name"].get().strip()
        dob = fields["Date of Birth (YYYY-MM-DD)"].get().strip()
        gender = fields["Gender"].get().strip()
        address = fields["Address"].get().strip()
        phone = fields["Phone Number"].get().strip()

        if not all([name, dob, gender, phone]):
            messagebox.showerror("Error", "❌ Name, Date of Birth, Gender, and Phone Number are required.")
            window.lift()
            window.focus_force()
            return
        
        if gender not in ("M","F","O"):
            messagebox.showerror("Error", "Gender must be 'M', 'F', or 'O'.")
            window.lift()
            window.focus_force()
            return
        
        if len(phone) < 10:
            messagebox.showerror("Error", "❌ Phone Number must be at least 10 digits.")
            window.lift()
            window.focus_force()
            return

        success, message = add_patient(conn, name, dob, gender, address, phone)
        if success:
            messagebox.showinfo("Success", message)
            window.destroy()
        else:
            messagebox.showerror("Error", message)
            window.lift()
            window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Add Patient", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=20)

def delete_patient_gui(conn):
    """GUI for deleting a patient"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Patient")
    delete_window.geometry("300x150")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    delete_window.lift()
    delete_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    delete_window.after(100, lambda: delete_window.attributes('-topmost', False))
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
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Delete Patient",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
def view_patient_gui(conn):
    """GUI to view and search patient information"""
    view_window = tk.Toplevel()
    view_window.title("Patient Directory")
    view_window.geometry("800x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="Patient Information", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(pady=5)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    tk.Label(search_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, padx=5)
    patient_id_entry = tk.Entry(search_frame)
    patient_id_entry.grid(row=0, column=1, padx=5)
    apply_styles(patient_id_entry)

    tk.Label(search_frame, text="Patient Name:", bg=BG_COLOR).grid(row=0, column=2, padx=5)
    patient_name_entry = tk.Entry(search_frame)
    patient_name_entry.grid(row=0, column=3, padx=5)
    apply_styles(patient_name_entry)

    # Treeview
    columns = ("PatientID", "PatientName", "DateOfBirth", "Gender", "Address", "PhoneNumber")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')
    # Set column headings and widths
    col_widths = [80, 150, 130, 100, 200, 110]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def load_data():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        patient_id = patient_id_entry.get().strip() or None
        patient_name = patient_name_entry.get().strip() or None
        success, result = search_patients(conn, patient_id, patient_name)
        if success and result:
            for row in result:
                if len(row) >= 6:
                    tree.insert("", tk.END, values=(
                        row['PatientID'], row['PatientName'], row['DateOfBirth'], row['Gender'], row['Address'], row['PhoneNumber']
                    ))
                else:
                    error_label.config(text="No data found")
                    view_window.lift()
                    view_window.focus_force()
                    return
        else:
            error_label.config(text="No data found")
            view_window.lift()

    # Search button
    search_btn = tk.Button(search_frame, text="Search", command=load_data)
    apply_styles(search_btn)
    search_btn.grid(row=0, column=4, padx=10)

    ## Load all data immediately when GUI opens
    view_window.after(100, load_data)

def update_patient_info_gui(conn):
    """GUI for updating patient information"""
    update_window = tk.Toplevel()
    update_window.title("Update Patient Information")
    update_window.geometry("400x350")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    update_window.after(100, lambda: update_window.attributes('-topmost', False))
    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Title
    title_label = tk.Label(main_frame, text="Update Patient Information", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR)
    title_label.pack(pady=(0, 20))

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(form_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    # Patient Name
    tk.Label(form_frame, text="Patient Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    # Date of Birth
    tk.Label(form_frame, text="Date of Birth (YYYY-MM-DD):", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_dob = tk.Entry(form_frame)
    entry_dob.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_dob)

    # Gender
    tk.Label(form_frame, text="Gender (M/F/O):", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_gender = tk.Entry(form_frame)
    entry_gender.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_gender)

    # Address
    tk.Label(form_frame, text="Address:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    entry_address = tk.Entry(form_frame)
    entry_address.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_address)

    # Phone Number
    tk.Label(form_frame, text="Phone Number:", bg=BG_COLOR).grid(row=5, column=0, sticky="e", pady=5) 
    entry_phone = tk.Entry(form_frame)
    entry_phone.grid(row=5, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_phone)

    def submit():
        patient_id = entry_patient_id.get()
        name = entry_name.get()
        dob = entry_dob.get()
        gender = entry_gender.get()
        address = entry_address.get()
        phone_number = entry_phone.get()   
        success, message = update_patient_info(conn, patient_id, name, dob, gender, address, phone_number)
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Update", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def disable_patient_account_gui(conn):
    """GUI for disabling patient account"""
    disable_window = tk.Toplevel()
    disable_window.title("Disable Patient Account")
    disable_window.geometry("300x150")
    disable_window.config(bg=BG_COLOR)
    center_window(disable_window)
    disable_window.lift()
    disable_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    disable_window.after(100, lambda: disable_window.attributes('-topmost', False))
    # Main frame
    main_frame = tk.Frame(disable_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).pack()
    entry_patient_id = tk.Entry(main_frame)
    entry_patient_id.pack(pady=5)
    apply_styles(entry_patient_id)

    def submit():
        patient_id = entry_patient_id.get()
        success, message = disable_patient_account(conn, patient_id)
        if success:
            messagebox.showinfo("Success", message)
            disable_window.destroy()
        else:
            messagebox.showerror("Error", message)
            disable_window.lift()
            disable_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Disable Account", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

#Department GUI Functions
def add_department_gui(conn):
    """GUI for adding a department"""
    add_window = tk.Toplevel()
    add_window.title("Add Department")
    add_window.geometry("400x200")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    add_window.lift()
    add_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    add_window.after(100, lambda: add_window.attributes('-topmost', False))
    # Main frame
    main_frame = tk.Frame(add_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Department Name
    tk.Label(form_frame, text="Department Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    def submit():
        name = entry_name.get()
        success, message = add_department(conn, name)
        if success:
            messagebox.showinfo("Success", message)
            add_window.destroy()
        else:
            messagebox.showerror("Error", message)
            add_window.lift()
            add_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Add Department",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def update_department_gui(conn):
    """GUI for updating a department"""
    update_window = tk.Toplevel()
    update_window.title("Update Department")
    update_window.geometry("400x200")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)

    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Department ID
    tk.Label(form_frame, text="Department ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(form_frame)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)

    # Department Name
    tk.Label(form_frame, text="New Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    def submit():
        dept_id = entry_id.get()
        name = entry_name.get()
        success, message = update_department(conn, dept_id, name)
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Update Department",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

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

# Appointment GUI Functions
def schedule_appointment_gui(conn):
    """GUI for scheduling appointments with improved validation and auto-refresh"""
    appt_window = tk.Toplevel()
    appt_window.title("Schedule Appointment")
    appt_window.geometry("500x400")  # Increased size for better layout
    appt_window.config(bg=BG_COLOR)
    center_window(appt_window)
    
    # Main frame
    main_frame = tk.Frame(appt_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(
        main_frame, 
        text="Schedule New Appointment",
        font=TITLE_FONT,
        bg=BG_COLOR,
        fg=ACCENT_COLOR
    )
    title_label.pack(pady=(0, 20))
    
    # Form frame with better organization
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)
    
    # Current date and time for reference
    now = datetime.now()
    tk.Label(form_frame, 
             text=f"Current Date/Time: {now.strftime('%Y-%m-%d %H:%M')}",
             bg=BG_COLOR).grid(row=0, columnspan=2, pady=5)
    
    # Patient ID with validation
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_patient = tk.Entry(form_frame)
    entry_patient.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient)
    
    # Button to search for patient
    def search_patient():
        patient_id = entry_patient.get()
        if patient_id:
            success, patient = search_patients(conn, patient_id=patient_id)
            if success and patient:
                messagebox.showinfo("Patient Found", 
                                  f"Patient: {patient[0]['PatientName']}", 
                                  parent=appt_window)
            else:
                messagebox.showerror("Error", "Patient not found", parent=appt_window)
    
    search_patient_btn = tk.Button(form_frame, text="Verify Patient", command=search_patient)
    apply_styles(search_patient_btn)
    search_patient_btn.grid(row=1, column=2, padx=5)
    
    # Doctor ID with validation
    tk.Label(form_frame, text="Doctor ID:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_doctor = tk.Entry(form_frame)
    entry_doctor.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_doctor)
    
    # Button to search for doctor
    def search_doctor():
        doctor_id = entry_doctor.get()
        if doctor_id:
            success, doctor = search_doctors(conn, doctor_id=doctor_id)
            if success and doctor:
                messagebox.showinfo("Doctor Found", 
                                  f"Doctor: {doctor[0]['DoctorName']}", 
                                  parent=appt_window)
            else:
                messagebox.showerror("Error", "Doctor not found", parent=appt_window)
    
    search_doctor_btn = tk.Button(form_frame, text="Verify Doctor", command=search_doctor)
    apply_styles(search_doctor_btn)
    search_doctor_btn.grid(row=2, column=2, padx=5)
    
    # Date picker (better than text entry)
    tk.Label(form_frame, text="Appointment Date:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    cal = DateEntry(form_frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    cal.grid(row=3, column=1, pady=5, padx=5, sticky="w")
    
    # Time picker
    tk.Label(form_frame, text="Appointment Time:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    time_var = tk.StringVar(value="09:00")
    time_options = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in [0, 30]]
    time_menu = ttk.Combobox(form_frame, textvariable=time_var, values=time_options)
    time_menu.grid(row=4, column=1, pady=5, padx=5, sticky="w")
    
    # Reason/Notes
    tk.Label(form_frame, text="Reason/Notes:", bg=BG_COLOR).grid(row=5, column=0, sticky="ne", pady=5)
    notes_entry = tk.Text(form_frame, height=4, width=30)
    notes_entry.grid(row=5, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(notes_entry)
    
    def submit():
        # Get all values with validation
        patient_id = entry_patient.get().strip()
        doctor_id = entry_doctor.get().strip()
        date = cal.get_date().strftime('%Y-%m-%d')
        time = time_var.get().strip()
        notes = notes_entry.get("1.0", tk.END).strip()
        
        # Validate inputs
        if not all([patient_id, doctor_id, date, time]):
            messagebox.showerror("Error", "All fields are required except notes", parent=appt_window)
            return
            
        try:
            # Validate time format
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format (use HH:MM)", parent=appt_window)
            return
            
        # Call core function
        success, message = schedule_appointment(conn, patient_id, doctor_id, date, time, notes)
        
        if success:
            messagebox.showinfo("Success", message, parent=appt_window)
            appt_window.destroy()
            
            # Refresh appointments in doctor menu if it exists
            for window in appt_window.winfo_children():
                if isinstance(window, tk.Toplevel) and "Doctor Dashboard" in window.title():
                    # Find and refresh the appointments view
                    for widget in window.winfo_children():
                        if hasattr(widget, '_name') and widget._name == "appointments_frame":
                            refresh_appointments(widget)
        else:
            messagebox.showerror("Error", message, parent=appt_window)
    
    # Submit button
    submit_btn = tk.Button(
        main_frame,
        text="Schedule Appointment",
        command=submit
    )
    apply_styles(submit_btn)
    submit_btn.pack(pady=15)
    
    # Configure grid weights
    form_frame.grid_columnconfigure(1, weight=1)

def refresh_appointments(conn, doctor_id, tree_widget):
    """
    Truy vấn cơ sở dữ liệu và cập nhật Treeview cuộc hẹn sắp tới.

    Args:
        conn: Đối tượng kết nối cơ sở dữ liệu.
        doctor_id (int): ID của bác sĩ hiện tại.
        tree_widget (ttk.Treeview): Widget Treeview để cập nhật.
    """
    if not tree_widget or not tree_widget.winfo_exists():
        print("Debug: Appointment tree widget no longer exists. Skipping refresh.")
        return

    try:
        for item in tree_widget.get_children():
            tree_widget.delete(item)
    except tk.TclError as e:
         print(f"Debug: Error clearing tree (widget might be destroyed): {e}")
         return

    try:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DATE_FORMAT(AppointmentTime, '%H:%i') as ApptTime, p.PatientName, a.Status
                    FROM Appointments a
                    JOIN Patients p ON a.PatientID = p.PatientID
                    WHERE a.DoctorID = %s AND a.AppointmentDate >= CURDATE() AND a.Status = 'Scheduled'
                    ORDER BY a.AppointmentDate, a.AppointmentTime
                    LIMIT 15
                """, (doctor_id,))
                upcoming_appts = cursor.fetchall()

                if upcoming_appts:
                     for appt in upcoming_appts:
                         time_val = appt.get('ApptTime', 'N/A')
                         patient_val = appt.get('PatientName', 'N/A')
                         status_val = appt.get('Status', 'N/A')
                         tree_widget.insert("", tk.END, values=(time_val, patient_val, status_val))
                else:
                     tree_widget.insert("", tk.END, values=("", "No upcoming appointments", ""))
        else:
            tree_widget.insert("", tk.END, values=("Error", "Database connection lost", ""))
            print("Debug: Database connection lost during refresh.")

    except MySQLError as db_error:
        print(f"Database Error during appointment refresh: {db_error}")
        try:
            for item in tree_widget.get_children(): tree_widget.delete(item)
            tree_widget.insert("", tk.END, values=("DB Error", "Check logs", "Error"))
        except tk.TclError: pass
    except Exception as e:
        print(f"Unexpected Error during appointment refresh: {e}")
        try:
            for item in tree_widget.get_children(): tree_widget.delete(item)
            tree_widget.insert("", tk.END, values=("Error", "Check logs", "Error"))
        except tk.TclError: pass

def view_appointments_gui(conn, role, user_id=None):
    """GUI for viewing appointments with consistent styling to doctor dashboard"""
    view_window = tk.Toplevel()
    view_window.title("Appointment Management")
    view_window.geometry("1100x700")
    view_window.config(bg="#f5f7fa")  # Matching light background
    center_window(view_window)
    
    # Modern color scheme matching doctor dashboard
    primary_color = "#4a6fa5"
    accent_color = "#5d9cec"
    dark_color = "#333333"
    light_color = "#f5f7fa"
    card_bg = "white"
    card_border = "#e0e0e0"
    
    # Font settings matching doctor dashboard
    try:
        title_font = ("Segoe UI", 16, "bold")
        header_font = ("Segoe UI", 12, "bold")
        normal_font = ("Segoe UI", 11)
        small_font = ("Segoe UI", 10)
    except tk.TclError:
        title_font = ("Arial", 16, "bold")
        header_font = ("Arial", 12, "bold")
        normal_font = ("Arial", 11)
        small_font = ("Arial", 10)

    # Main container frame
    main_frame = tk.Frame(view_window, bg=light_color, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # Header
    header_frame = tk.Frame(main_frame, bg=light_color)
    header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(header_frame, text="Appointment Management", 
            font=title_font, bg=light_color, fg=dark_color).pack(side="left")
    
    # Filter controls in a card
    filter_card = tk.Frame(main_frame, bg=card_bg, bd=0, relief="flat",
                         highlightbackground=card_border, highlightthickness=1,
                         padx=15, pady=15)
    filter_card.pack(fill="x", pady=(0, 15))

    # Date filters
    tk.Label(filter_card, text="Filter by Date:", font=small_font, 
            bg=card_bg, fg="#7f8c8d").grid(row=0, column=0, padx=5, sticky="w")
    
    tk.Label(filter_card, text="Year:", bg=card_bg).grid(row=1, column=0, padx=5)
    entry_year = tk.Entry(filter_card, width=8, font=normal_font, bd=1, relief="solid")
    entry_year.grid(row=1, column=1, padx=5)
    
    tk.Label(filter_card, text="Month:", bg=card_bg).grid(row=1, column=2, padx=5)
    entry_month = tk.Entry(filter_card, width=8, font=normal_font, bd=1, relief="solid")
    entry_month.grid(row=1, column=3, padx=5)
    
    tk.Label(filter_card, text="Day:", bg=card_bg).grid(row=1, column=4, padx=5)
    entry_day = tk.Entry(filter_card, width=8, font=normal_font, bd=1, relief="solid")
    entry_day.grid(row=1, column=5, padx=5)
    
    tk.Label(filter_card, text="Status:", bg=card_bg).grid(row=1, column=6, padx=5)
    status_var = tk.StringVar(value="All")
    status_options = ["All", "Scheduled", "Completed", "Cancelled"]
    status_menu = tk.OptionMenu(filter_card, status_var, *status_options)
    status_menu.config(font=small_font, width=12, bd=1, relief="solid")
    status_menu.grid(row=1, column=7, padx=5)
    
    # Search button with matching style
    search_btn = tk.Button(filter_card, text="Search", 
                         bg=accent_color, fg="white", font=small_font,
                         bd=0, relief="flat", padx=15, pady=5)
    search_btn.grid(row=1, column=8, padx=10)
    
    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    # Treeview in a card
    tree_card = tk.Frame(main_frame, bg=card_bg, bd=0, relief="flat",
                        highlightbackground=card_border, highlightthickness=1,
                        padx=15, pady=15)
    tree_card.pack(fill="both", expand=True)
    
    # Configure treeview style to match the theme
    style = ttk.Style()
    style.configure("Treeview.Heading", font=small_font, background=light_color, 
                   foreground=dark_color, relief="flat")
    style.configure("Treeview", font=small_font, rowheight=28, 
                   fieldbackground=card_bg, background=card_bg)
    style.map("Treeview", background=[('selected', primary_color)], 
             foreground=[('selected', 'white')])
    
    # Treeview columns
    columns = ("ID", "Date", "Time", "Status", "Doctor", "Patient")
    tree = ttk.Treeview(tree_card, columns=columns, show='headings', height=15)
    
    # Column configurations
    tree.column("ID", width=80, anchor=tk.W)
    tree.column("Date", width=100, anchor=tk.W)
    tree.column("Time", width=80, anchor=tk.W)
    tree.column("Status", width=100, anchor=tk.W)
    tree.column("Doctor", width=200, anchor=tk.W)
    tree.column("Patient", width=200, anchor=tk.W)
    
    # Headings
    for col in columns:
        tree.heading(col, text=col)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_card, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Grid layout
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree_card.grid_rowconfigure(0, weight=1)
    tree_card.grid_columnconfigure(0, weight=1)
    
    # Tag configurations for different statuses
    tree.tag_configure('Scheduled', background='#e3f2fd')
    tree.tag_configure('Completed', background='#e8f5e9')
    tree.tag_configure('Cancelled', background='#ffebee')

    def fetch_appointments():
        try:
            year = entry_year.get().strip()
            month = entry_month.get().strip()
            day = entry_day.get().strip()
            status = status_var.get() if status_var.get() != "All" else None

            year = int(year) if year else None
            month = int(month) if month else None
            day = int(day) if day else None

            success, result = search_appointments(conn, role, user_id, year, month, day, status)

            tree.delete(*tree.get_children())

            if not success:
                error_label.config ("Error", result)
                return
            if not result:
                error_label.config(text="No appointments found matching the criteria.")
                return

            for appt in result:
                tree.insert("", tk.END, values=(
                    appt["AppointmentID"],
                    appt["AppointmentDate"].strftime('%Y-%m-%d') if appt["AppointmentDate"] else "",
                    f"{int(appt['AppointmentTime'].seconds // 3600):02d}:{int((appt['AppointmentTime'].seconds % 3600) // 60):02d}"
                    if appt["AppointmentTime"] else "",
                    appt["Status"],
                    appt["DoctorName"],
                    appt["PatientName"]
                ), tags=(appt["Status"],))


        except ValueError:
            error_label.config(text="Please enter valid numbers for year/month/day")
            view_window.lift()
            view_window.focus_force()
            return
        except Exception as e:
            error_label.config(text=f"An unexpected error occurred: {str(e)}")
            view_window.lift()

    search_btn.config(command=fetch_appointments)
    
    # Add some padding at the bottom
    tk.Frame(main_frame, bg=light_color, height=20).pack()
    
    # Initial data load
    view_window.after(100, fetch_appointments)

def update_appointment_status_gui(conn):
    """GUI for updating appointment status"""
    update_window = tk.Toplevel()
    update_window.title("Update Appointment Status")
    update_window.geometry("400x250")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)
    update_window.after(100, lambda: update_window.attributes('-topmost', False))
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
            update_window.lift()
            update_window.focus_force()

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

# Room GUI Functions
def add_room_gui(conn):
    """GUI for adding a room"""
    add_window = tk.Toplevel()
    add_window.title("Add Room")
    add_window.geometry("400x300")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    add_window.lift()
    add_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    add_window.after(100, lambda: add_window.attributes('-topmost', False))
    # Main frame
    main_frame = tk.Frame(add_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Room Number
    tk.Label(form_frame, text="Room Number:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_number = tk.Entry(form_frame)
    entry_number.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_number)

    # Room Type
    tk.Label(form_frame, text="Room Type:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_type = tk.Entry(form_frame)
    entry_type.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_type)

    # Department ID
    tk.Label(form_frame, text="Department ID:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_dept_id = tk.Entry(form_frame)
    entry_dept_id.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_dept_id)

    # Cost per day
    tk.Label(form_frame, text="Cost/Day (VND):", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_cost = tk.Entry(form_frame)
    entry_cost.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_cost)

    def submit():
        room_number = entry_number.get()
        room_type = entry_type.get()
        dept_id = entry_dept_id.get()
        cost_per_day = entry_cost.get()

        success, message = add_room(conn, room_number, room_type, dept_id, cost_per_day)
        if success:
            messagebox.showinfo("Success", message)
            add_window.destroy()
        else:
            messagebox.showerror("Error", message)
            add_window.lift()
            add_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Add Room", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def update_room_gui(conn):
    """GUI for updating a room"""
    update_window = tk.Toplevel()
    update_window.title("Update Room")
    update_window.geometry("400x300")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Room ID
    tk.Label(form_frame, text="Room ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(form_frame)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)

    # Room Number
    tk.Label(form_frame, text="Room Number:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_number = tk.Entry(form_frame)
    entry_number.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_number)

    # Room Type ID
    tk.Label(form_frame, text="Room Type ID:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_type_id = tk.Entry(form_frame)
    entry_type_id.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_type_id)

    # Department ID
    tk.Label(form_frame, text="Department ID:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_dept_id = tk.Entry(form_frame)
    entry_dept_id.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_dept_id)

    # Status
    tk.Label(form_frame, text="Status:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    entry_status = tk.Entry(form_frame)
    entry_status.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_status)

    def submit():
        room_id = entry_id.get()
        room_number = entry_number.get()
        room_type_id = entry_type_id.get()
        department_id = entry_dept_id.get()
        status = entry_status.get()

        # Call the core logic function
        success, message = update_room(conn, room_id, room_number, room_type_id, department_id, status)
        
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Update Room", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def disable_room_gui(conn):
    """GUI for disabling a room"""
    disable_window = tk.Toplevel()
    disable_window.title("Disable Room")
    disable_window.geometry("300x150")
    disable_window.config(bg=BG_COLOR)
    center_window(disable_window)
    disable_window.lift()
    disable_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    disable_window.after(100, lambda: disable_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(disable_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Room Number
    tk.Label(main_frame, text="Room Number:", bg=BG_COLOR).pack()
    entry_number = tk.Entry(main_frame)
    entry_number.pack(pady=5)
    apply_styles(entry_number)

    def submit():
        room_number = entry_number.get()
        success, message = disable_room(conn, room_number)
        if success:
            messagebox.showinfo("Success", message)
            disable_window.destroy()
        else:
            messagebox.showerror("Error", message)
            disable_window.lift()
            disable_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Disable Room", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def view_rooms_gui(conn):
    """GUI for searching rooms and displaying them in Treeview"""
    view_window = tk.Toplevel()
    view_window.title("Room Directory")
    view_window.geometry("700x400")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="View Room", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(pady=5)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    # Room ID Label and Entry
    tk.Label(search_frame, text="Room ID:", bg=BG_COLOR).grid(row=0, column=0, padx=5, sticky='w')
    room_id_entry = tk.Entry(search_frame)
    room_id_entry.grid(row=0, column=1, padx=5)
    apply_styles(room_id_entry)

    # Room Number Label and Entry
    tk.Label(search_frame, text="Room Number:", bg=BG_COLOR).grid(row=1, column=0, padx=5, sticky='w')
    room_number_entry = tk.Entry(search_frame)
    room_number_entry.grid(row=1, column=1, padx=5)
    apply_styles(room_number_entry)

    # Status Label and Entry (Added)
    tk.Label(search_frame, text="Status:", bg=BG_COLOR).grid(row=2, column=0, padx=5, sticky='w')
    status_entry = tk.Entry(search_frame)
    status_entry.grid(row=2, column=1, padx=5)
    apply_styles(status_entry)

    # Treeview
    columns = ("RoomID", "RoomNumber", "RoomTypeID", "DepartmentID", "Status", "CurrentPatientID", "LastCleanedDate")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')
    col_widths = [120, 200, 120, 100]

    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def search():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        room_id = room_id_entry.get().strip() or None
        room_number = room_number_entry.get().strip() or None
        status = status_entry.get().strip() or None  # Get status filter input

        success, result = search_rooms(conn, room_id, room_number, status)  # Pass status to search function
        if success and result:
            for room in result:
                if len(room) > 4:
                    tree.insert("", tk.END, values=(
                        room["RoomID"],
                        room["RoomNumber"],
                        room["RoomTypeID"],
                        room["DepartmentID"],
                        room["Status"],
                        room["CurrentPatientID"],
                        room["LastCleanedDate"],
                    ))
                else:
                    error_label.config(text="Invalid room data format")
                    view_window.lift()
                    view_window.focus_force()
                    return
        else:
            error_label.config(text="No rooms found matching the criteria.")
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(search_frame, text="Search", command=search)
    apply_styles(search_btn)
    search_btn.grid(row=3, column=0, columnspan=2, pady=10)  # Adjusted row for new field

    view_window.after(100, search)

def view_room_types_gui(conn):
    """GUI for viewing room types using Treeview"""
    view_window = tk.Toplevel()
    view_window.title("Room Types")
    view_window.geometry("900x600")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="Room Types", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame for RoomTypeID and TypeName
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=10)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    # RoomTypeID filter
    tk.Label(search_frame, text="Room Type ID:", bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
    room_type_id_entry = tk.Entry(search_frame)
    room_type_id_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(room_type_id_entry)

    # TypeName filter
    tk.Label(search_frame, text="Type Name:", bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
    type_name_entry = tk.Entry(search_frame)
    type_name_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(type_name_entry)

    # Search button
    search_btn = tk.Button(search_frame, text="Search", command=lambda: search())
    apply_styles(search_btn)
    search_btn.pack(side=tk.LEFT, padx=10)

    def search():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        room_type_id = room_type_id_entry.get().strip() or None
        type_name = type_name_entry.get().strip() or None

        success, result = search_room_types(conn, room_type_id, type_name)
        if success:
            tree.delete(*tree.get_children())
            for room_type in result:
                tree.insert("", tk.END, values=(
                    room_type.get("RoomTypeID", ""),
                    room_type.get("TypeName", ""),
                    room_type.get("BaseCost", ""),
                    room_type.get("Description", "")
                ))
        else:
            error_label.config(text="Failed to fetch room types.")
            view_window.lift()
            view_window.focus_force()
    # Treeview
    columns = ("Room Type ID", "Type Name", "Base Cost", "Description")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')
    col_widths = [80, 100, 100, 250]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    view_window.after(100, search)

def add_room_type_gui(conn):
    """GUI for adding a room type"""
    add_window = tk.Toplevel()
    add_window.title("Add Room Type")
    add_window.geometry("400x200")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    add_window.lift()
    add_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    add_window.after(100, lambda: add_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(add_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Room Type Name
    tk.Label(form_frame, text="Room Type Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    # Base Cost
    tk.Label(form_frame, text="Base Cost (VND):", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_base_cost = tk.Entry(form_frame)
    entry_base_cost.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_base_cost)

    # Description
    tk.Label(form_frame, text="Description:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_description = tk.Entry(form_frame)
    entry_description.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_description)

    def submit():
        name = entry_name.get()
        cost = entry_base_cost.get()
        des = entry_description.get()
        success, message = add_room_type(conn, name, cost, des)
        if success:
            messagebox.showinfo("Success", message)
            add_window.destroy()
        else:
            messagebox.showerror("Error", message)
            add_window.lift()
            add_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Add Room Type", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def update_room_type_gui(conn):
    """GUI for updating a room type"""
    update_window = tk.Toplevel()
    update_window.title("Update Room Type")
    update_window.geometry("400x250")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Room Type ID
    tk.Label(form_frame, text="Room Type ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(form_frame)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)

    # Room Type Name
    tk.Label(form_frame, text="New Room Type Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    # Base Cost
    tk.Label(form_frame, text="Base Cost (VND):", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_base_cost = tk.Entry(form_frame)
    entry_base_cost.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_base_cost)

    def submit():
        room_type_id = entry_id.get()
        type_name = entry_name.get()
        base_cost = entry_base_cost.get()

        # Call the core logic function
        success, message = update_room_type(conn, room_type_id, type_name, base_cost)
        
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Update Room Type", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

# def get_room_statistics_gui(conn):
#     """GUI for getting room statistics"""
#     stats_window = tk.Toplevel()
#     stats_window.title("Room Statistics")
#     stats_window.geometry("400x300")
#     stats_window.config(bg=BG_COLOR)
#     center_window(stats_window)
#     stats_window.lift()
#     stats_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
#     stats_window.after(100, lambda: stats_window.attributes('-topmost', False))
#     # Main frame
#     main_frame = tk.Frame(stats_window, bg=BG_COLOR)
#     main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

#     # Title
#     title_label = tk.Label(main_frame, text="Room Statistics", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR)
#     title_label.pack(pady=(0, 20))

#     # Get all room statistics
#     success, room_stats = get_room_statistics(conn)
#     if not success:
#         messagebox.showerror("Error", room_stats)
#         return

#     # Display room statistics
#     listbox = tk.Listbox(main_frame, width=50, height=15)
#     listbox.pack(padx=10, pady=10)

#     for stat in room_stats:
#         listbox.insert(tk.END, f"Room Number: {stat['RoomNumber']}, Status: {stat['Status']}")

# report
def assign_room_gui(conn):
    """GUI for assigning a room to a patient"""
    assign_window = tk.Toplevel()
    assign_window.title("Assign Room")
    assign_window.geometry("400x200")
    assign_window.config(bg=BG_COLOR)
    center_window(assign_window)
    assign_window.lift()
    assign_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    assign_window.after(100, lambda: assign_window.attributes('-topmost', False))
    # Main frame
    main_frame = tk.Frame(assign_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(form_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    # Room Number
    tk.Label(form_frame, text="Room Type ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_room_number = tk.Entry(form_frame)
    entry_room_number.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_room_number)

    def submit():
        patient_id = entry_patient_id.get()
        room_number = entry_room_number.get()
        success, message = assign_patient_to_room(conn, patient_id, room_number)
        if success:
            messagebox.showinfo("Success", message)
            assign_window.destroy()
        else:
            messagebox.showerror("Error", message)
            assign_window.lift()
            assign_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Assign Room", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

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

### Admission_order
def order_admission_gui(conn, doctor_id):
    """GUI for Doctor to order patient admission."""
    order_window = tk.Toplevel()
    order_window.title("Order Patient Admission")
    order_window.geometry("450x350") # Increased height slightly
    order_window.config(bg=BG_COLOR)
    center_window(order_window)
    order_window.lift()
    order_window.attributes('-topmost', True)
    order_window.after(100, lambda: order_window.attributes('-topmost', False))

    main_frame = tk.Frame(order_window, bg=BG_COLOR, padx=15, pady=15)
    main_frame.pack(fill=tk.BOTH, expand=True)
    main_frame.columnconfigure(1, weight=1) # Make entry column expand

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR, font=LABEL_FONT).grid(row=0, column=0, sticky="e", pady=5)
    patient_id_entry = tk.Entry(main_frame, font=LABEL_FONT)
    patient_id_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
    apply_styles(patient_id_entry)

    # Department Selection
    tk.Label(main_frame, text="Department:", bg=BG_COLOR, font=LABEL_FONT).grid(row=1, column=0, sticky="e", pady=5)
    dept_var = tk.StringVar()
    dept_combobox = ttk.Combobox(main_frame, textvariable=dept_var, state="readonly", font=LABEL_FONT)
    dept_combobox.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

    # Load departments into combobox
    success_dept, departments = get_departments_list(conn)
    if success_dept:
        dept_dict = {f"{d['DepartmentID']} - {d['DepartmentName']}": d['DepartmentID'] for d in departments}
        dept_combobox['values'] = list(dept_dict.keys())
    else:
        messagebox.showerror("Error", f"Could not load departments: {departments}", parent=order_window)
        dept_combobox['values'] = ["Error loading"]

    # Reason for Admission
    tk.Label(main_frame, text="Reason:", bg=BG_COLOR, font=LABEL_FONT).grid(row=2, column=0, sticky="ne", pady=5)
    reason_text = scrolledtext.ScrolledText(main_frame, height=4, width=30, wrap=tk.WORD, font=LABEL_FONT)
    reason_text.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
    apply_styles(reason_text) # Basic styling

    # Optional Notes
    tk.Label(main_frame, text="Notes (Optional):", bg=BG_COLOR, font=LABEL_FONT).grid(row=3, column=0, sticky="ne", pady=5)
    notes_text = scrolledtext.ScrolledText(main_frame, height=3, width=30, wrap=tk.WORD, font=LABEL_FONT)
    notes_text.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
    apply_styles(notes_text)

    def submit_order():
        patient_id = patient_id_entry.get().strip()
        dept_selection = dept_var.get()
        reason = reason_text.get("1.0", tk.END).strip()
        notes = notes_text.get("1.0", tk.END).strip() or None

        if not patient_id or not dept_selection or not reason:
            messagebox.showerror("Input Error", "Patient ID, Department, and Reason are required.", parent=order_window)
            order_window.lift(); order_window.focus_force(); return

        # Get DepartmentID from selection
        dept_id = dept_dict.get(dept_selection)
        if not dept_id:
            messagebox.showerror("Input Error", "Invalid department selected.", parent=order_window)
            order_window.lift(); order_window.focus_force(); return

        success, message = create_admission_order(conn, patient_id, doctor_id, dept_id, reason, notes)

        if success:
            messagebox.showinfo("Success", message, parent=order_window)
            order_window.destroy()
        else:
            messagebox.showerror("Error", message, parent=order_window)
            order_window.lift(); order_window.focus_force();

    submit_btn = tk.Button(main_frame, text="Submit Admission Order", command=submit_order)
    apply_styles(submit_btn)
    submit_btn.grid(row=4, column=0, columnspan=2, pady=15)

# <<< REPLACE the placeholder select_room_gui with this >>>
def select_room_gui(parent_window, conn):
    """Modal dialog for selecting an available room from all departments."""
    dialog = tk.Toplevel(parent_window)
    dialog.title("Select Available Room")
    dialog.geometry("650x450")  # Tăng kích thước để hiển thị thêm cột
    dialog.config(bg=BG_COLOR)
    center_window(dialog)
    dialog.transient(parent_window)
    dialog.grab_set()

    selected_room = {'id': None, 'number': None, 'status': None}

    tk.Label(dialog, text="Available Rooms in Hospital",
             font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Thêm nút refresh
    refresh_btn = tk.Button(dialog, text="🔄 Refresh", command=lambda: load_rooms())
    apply_styles(refresh_btn)
    refresh_btn.pack(anchor='ne', padx=10)

    tree_frame = tk.Frame(dialog, bg=BG_COLOR)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Thêm cột Status
    cols = ("RoomID", "RoomNumber", "TypeName", "Department", "Status", "Cost")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
    
    # Định dạng cột
    col_widths = [60, 100, 120, 120, 100, 100]
    for col, width in zip(cols, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.CENTER if col in ["RoomID", "Status"] else tk.W)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Tag màu cho các trạng thái
    tree.tag_configure('Available', background='#e8f5e9')  # Xanh nhạt
    tree.tag_configure('Occupied', background='#ffebee')   # Đỏ nhạt
    tree.tag_configure('Maintenance', background='#fff3e0') # Cam nhạt
    tree.tag_configure('Cleaning', background='#e3f2fd')   # Xanh da trời nhạt

    def load_rooms():
        tree.delete(*tree.get_children())
        try:
            success, rooms_data = get_all_rooms_with_status(conn)
            if success:
                if rooms_data:
                    for room in rooms_data:
                        status = room.get('Status', 'Unknown')
                        tags = (status,)
                        
                        tree.insert("", tk.END, 
                                  values=(
                                      room.get('RoomID', 'N/A'),
                                      room.get('RoomNumber', 'N/A'),
                                      room.get('TypeName', 'N/A'),
                                      room.get('DepartmentName', 'N/A'),
                                      status,
                                      f"{room.get('BaseCost', 0):,.0f} VND"
                                  ),
                                  tags=tags)
                else:
                    tree.insert("", tk.END, values=("", "No rooms found", "", "", "", ""))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rooms: {str(e)}", parent=dialog)

    def confirm_selection():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select a room first", parent=dialog)
            return

        item = tree.item(selected_items[0])
        if item['values'][4] != 'Available':  # Check Status column
            messagebox.showwarning("Invalid Selection", 
                                 "Please select an AVAILABLE room only", 
                                 parent=dialog)
            return

        selected_room.update({
            'id': item['values'][0],
            'number': item['values'][1],
            'status': item['values'][4]
        })
        dialog.destroy()

    # Button frame
    btn_frame = tk.Frame(dialog, bg=BG_COLOR)
    btn_frame.pack(pady=10)

    select_btn = tk.Button(btn_frame, text="Select Room", command=confirm_selection)
    apply_styles(select_btn)
    select_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy)
    apply_styles(cancel_btn)
    cancel_btn.pack(side=tk.LEFT, padx=10)

    load_rooms()  # Load data immediately
    dialog.wait_window()
    return selected_room

def process_admission_gui(conn, receptionist_username):
    """GUI for Receptionist to process pending admission orders (Improved Version)."""
    proc_window = tk.Toplevel()
    proc_window.title("Process Patient Admission")
    proc_window.geometry("1100x750")
    proc_window.config(bg=BG_COLOR)
    center_window(proc_window)
    proc_window.lift()
    proc_window.attributes('-topmost', True)
    proc_window.after(100, lambda: proc_window.attributes('-topmost', False))

    main_frame = tk.Frame(proc_window, bg=BG_COLOR, padx=15, pady=15)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # --- Pending Orders Section (Treeview) ---
    pending_frame = tk.LabelFrame(main_frame,
                                text="Pending Admission Orders",
                                bg=BG_COLOR,
                                fg=TEXT_COLOR,
                                padx=10,
                                pady=10,
                                font=LABEL_FONT)
    pending_frame.pack(fill=tk.X, pady=(0, 10))

    pending_cols = ("OrderID", "PatientName", "DoctorName", "Department", "OrderDate", "Reason")
    pending_tree = ttk.Treeview(pending_frame, columns=pending_cols, show="headings", height=8)
    pending_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    pending_scroll = ttk.Scrollbar(pending_frame, orient="vertical", command=pending_tree.yview)
    pending_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    pending_tree.configure(yscrollcommand=pending_scroll.set)

    # Configure columns
    col_widths = [80, 150, 150, 120, 100, 200]
    for col, width in zip(pending_cols, col_widths):
        pending_tree.heading(col, text=col)
        pending_tree.column(col, width=width, anchor=tk.W)

    # --- Details Frame (Patient Info + Room Assignment) ---
    details_frame = tk.LabelFrame(main_frame,
                                text="Admission Details",
                                bg=BG_COLOR,
                                fg=TEXT_COLOR,
                                padx=15,
                                pady=10,
                                font=LABEL_FONT)
    details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

    # Divide details frame into left (patient info) and right (room assignment)
    left_frame = tk.Frame(details_frame, bg=BG_COLOR)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    right_frame = tk.Frame(details_frame, bg=BG_COLOR)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))

    # --- Patient Details Display ---
    tk.Label(left_frame, text="Patient Information:",
            font=(LABEL_FONT[0], LABEL_FONT[1], 'bold'),
            bg=BG_COLOR).pack(anchor='w', pady=(0, 10))

    # Create a dictionary to hold all the StringVars for patient details
    details_vars = {
        "order_id": tk.StringVar(value="Not selected"),
        "patient_id": tk.StringVar(value="Not selected"),
        "patient_name": tk.StringVar(value="Not selected"),
        "dob": tk.StringVar(value="Not selected"),
        "gender": tk.StringVar(value="Not selected"),
        "address": tk.StringVar(value="Not selected"),
        "phone": tk.StringVar(value="Not selected"),
        "doctor": tk.StringVar(value="Not selected"),
        "department": tk.StringVar(value="Not selected"),
        "reason": tk.StringVar(value="Not selected"),
        "insurance": tk.StringVar(value="Not selected")
    }

    # Helper function to create labeled fields
    def create_labeled_field(parent, label_text, var):
        frame = tk.Frame(parent, bg=BG_COLOR)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label_text, width=15, anchor='e',
                bg=BG_COLOR, font=LABEL_FONT).pack(side=tk.LEFT)
        tk.Label(frame, textvariable=var, relief=tk.SUNKEN,
                bg=ENTRY_BG, font=LABEL_FONT, anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Create all patient info fields
    create_labeled_field(left_frame, "Order ID:", details_vars["order_id"])
    create_labeled_field(left_frame, "Patient ID:", details_vars["patient_id"])
    create_labeled_field(left_frame, "Patient Name:", details_vars["patient_name"])
    create_labeled_field(left_frame, "Date of Birth:", details_vars["dob"])
    create_labeled_field(left_frame, "Gender:", details_vars["gender"])
    create_labeled_field(left_frame, "Address:", details_vars["address"])
    create_labeled_field(left_frame, "Phone:", details_vars["phone"])
    create_labeled_field(left_frame, "Doctor:", details_vars["doctor"])
    create_labeled_field(left_frame, "Department:", details_vars["department"])
    create_labeled_field(left_frame, "Reason:", details_vars["reason"])
    create_labeled_field(left_frame, "Insurance:", details_vars["insurance"])

    # --- Room Selection and Display ---
    room_info_frame = tk.Frame(right_frame, bg=BG_COLOR)
    room_info_frame.pack(fill=tk.X, pady=5)

    tk.Label(room_info_frame, text="Selected Room:", bg=BG_COLOR).pack(anchor='w')
    selected_room_var = tk.StringVar(value="No room selected")
    tk.Label(room_info_frame, textvariable=selected_room_var,
        font=('Helvetica', 10, 'bold'), bg=BG_COLOR).pack(anchor='w')

    # This dictionary will store the details of the chosen room
    # It needs to be accessible by both select_room and process_admission
    # Making it an instance variable or passing it around might be cleaner,
    # but using a dictionary accessible within the scope works here.
    _selected_room_data = {'id': None, 'number': None, 'status': None}

    # Select room button
    def select_room():
        # Call the GUI function to select a room. It returns a dictionary.
        room_info = select_room_gui(proc_window, conn) # Assuming select_room_gui is defined elsewhere

        # Check if a valid room ID was returned
        if room_info and room_info.get('id'):
             _selected_room_data['id'] = room_info.get('id')
             _selected_room_data['number'] = room_info.get('number')
             _selected_room_data['status'] = room_info.get('status')

             # Update the display label
             selected_room_var.set(f"Room {_selected_room_data['number']} (ID: {_selected_room_data['id']}, Status: {_selected_room_data['status']})")
        else:
             # Reset if no room was selected or selection was cancelled
             _selected_room_data.update({'id': None, 'number': None, 'status': None})
             selected_room_var.set("No room selected")


    select_room_btn = tk.Button(right_frame, text="Select Room",
                               command=select_room)
    apply_styles(select_room_btn)
    select_room_btn.pack(pady=5)

    # --- Process Admission Button ---
    def process_admission():
        order_id_str = details_vars["order_id"].get()
        patient_id_str = details_vars["patient_id"].get()

        # Check if an order is selected
        if order_id_str == "Not selected" or not order_id_str:
            messagebox.showwarning("No Order Selected",
                                "Please select an admission order first",
                                parent=proc_window)
            proc_window.lift(); proc_window.focus_force(); return

        # **** CRITICAL CHANGE: Check the _selected_room_data dictionary ****
        if not _selected_room_data.get('id'):
            messagebox.showwarning("No Room Selected",
                                "Please select a room for the patient",
                                parent=proc_window)
            proc_window.lift(); proc_window.focus_force(); return

        # Ensure the selected room is 'Available' (or handle other statuses if needed)
        if _selected_room_data.get('status') != 'Available':
             messagebox.showwarning("Room Not Available",
                                  f"Selected room ({_selected_room_data.get('number')}) is not Available.",
                                  parent=proc_window)
             proc_window.lift(); proc_window.focus_force(); return

        # Get all needed information
        order_id = int(order_id_str)
        patient_id = int(patient_id_str)
        room_id = _selected_room_data['id'] # Get ID from the dictionary
        room_number = _selected_room_data['number'] # Get number for confirmation message

        # Confirm with the receptionist
        confirm_msg = f"Confirm admission for patient {details_vars['patient_name'].get()}?\n"
        confirm_msg += f"Room: {room_number} (ID: {room_id})\n" # Show number and ID
        confirm_msg += f"Order ID: {order_id}"

        if not messagebox.askyesno("Confirm Admission", confirm_msg, parent=proc_window):
            return

        # Call the core logic function to process admission
        # Assuming process_admission_order exists in core_logic
        success, message = process_admission_order(conn, order_id, patient_id, room_id, receptionist_username)

        if success:
            messagebox.showinfo("Success", message, parent=proc_window)
            # Refresh the pending orders list
            load_pending_orders()
            # Clear the details and selected room info
            for var in details_vars.values():
                var.set("Not selected")
            _selected_room_data.update({'id': None, 'number': None, 'status': None})
            selected_room_var.set("No room selected")
        else:
            messagebox.showerror("Error", message, parent=proc_window)
            proc_window.lift(); proc_window.focus_force()


    process_btn = tk.Button(main_frame, text="Process Admission",
                          command=process_admission)
    apply_styles(process_btn)
    process_btn.pack(pady=10)

    # --- Function to Load Pending Orders ---
    def load_pending_orders():
        pending_tree.delete(*pending_tree.get_children())
        # Assuming get_pending_admission_orders exists in core_logic
        success, orders = get_pending_admission_orders(conn)

        if success:
            if orders:
                for order in orders:
                    pending_tree.insert("", tk.END, values=(
                        order["OrderID"],
                        order["PatientName"],
                        order["DoctorName"],
                        order["DepartmentName"],
                        order["OrderDate"].strftime('%Y-%m-%d') if order["OrderDate"] else "N/A",
                        order["Reason"]
                    ))
            else:
                pending_tree.insert("", tk.END, values=("", "No pending admission orders found", "", "", "", ""))
        else:
            messagebox.showerror("Error", f"Failed to load orders: {orders}", parent=proc_window)

    # --- Function to Handle Order Selection ---
    def on_order_select(event):
        selected_item = pending_tree.focus()
        if not selected_item:
            return

        item_data = pending_tree.item(selected_item)
        values = item_data['values']

        if not values or len(values) < 6:
            return

        order_id = values[0]

        # Get full order details from database
        # Assuming get_admission_order_details exists in core_logic
        success, order_details = get_admission_order_details(conn, order_id)

        if success:
            # Update the patient details display
            details_vars["order_id"].set(order_details["OrderID"])
            details_vars["patient_id"].set(order_details["PatientID"])
            details_vars["patient_name"].set(order_details["PatientName"])
            details_vars["dob"].set(str(order_details["DateOfBirth"]))
            details_vars["gender"].set(order_details["Gender"])
            details_vars["address"].set(order_details["Address"])
            details_vars["phone"].set(order_details["PhoneNumber"])
            details_vars["doctor"].set(order_details["DoctorName"])
            details_vars["department"].set(order_details["DepartmentName"])
            details_vars["reason"].set(order_details["Reason"])
            details_vars["insurance"].set(order_details.get("InsuranceProvider", "None"))

            # **** Clear previously selected room when a new order is selected ****
            _selected_room_data.update({'id': None, 'number': None, 'status': None})
            selected_room_var.set("No room selected")
        else:
            messagebox.showerror("Error", f"Failed to load order details: {order_details}", parent=proc_window)
            # Clear details if loading fails
            for var in details_vars.values(): var.set("Not selected")
            _selected_room_data.update({'id': None, 'number': None, 'status': None})
            selected_room_var.set("No room selected")


    # Bind selection event
    pending_tree.bind('<<TreeviewSelect>>', on_order_select)

    # Initial load of pending orders
    load_pending_orders()

    proc_window.mainloop()

def room_management_gui(conn):
    """GUI quản lý phòng (cho receptionist)"""
    room_window = tk.Toplevel()
    room_window.title("Room Management")
    room_window.geometry("1000x700")
    room_window.config(bg=BG_COLOR)
    center_window(room_window)
    room_window.lift()
    room_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    room_window.after(100, lambda: room_window.attributes('-topmost', False))
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
    type_dropdown = ttk.Combobox(filter_frame, textvariable=type_var)
    
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

# Service GUI Functions
def add_service_gui(conn):
    """GUI for adding a service"""
    add_window = tk.Toplevel()
    add_window.title("Add Service")
    add_window.geometry("400x300")
    add_window.config(bg=BG_COLOR)
    center_window(add_window)
    add_window.lift()
    add_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    add_window.after(100, lambda: add_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(add_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Service Name
    tk.Label(form_frame, text="Service Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    # Service Code
    tk.Label(form_frame, text="Service Code:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_code = tk.Entry(form_frame)
    entry_code.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_code)

    # Cost
    tk.Label(form_frame, text="Cost (VND):", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_cost = tk.Entry(form_frame)
    entry_cost.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_cost)

    # Description
    tk.Label(form_frame, text="Description:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_description = tk.Entry(form_frame)
    entry_description.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_description)

    def submit():
        name = entry_name.get()
        code = entry_code.get()
        cost = entry_cost.get()
        des = entry_description.get()

        success, message = add_service(conn, name, code, cost, des)
        if success:
            messagebox.showinfo("Success", message)
            add_window.destroy()
        else:
            messagebox.showerror("Error", message)
            add_window.lift()
            add_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Add Service", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def update_service_gui(conn):
    """GUI for updating a service"""
    update_window = tk.Toplevel()
    update_window.title("Update Service")
    update_window.geometry("400x250")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Service ID
    tk.Label(form_frame, text="Service ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(form_frame)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)

    # Service Name
    tk.Label(form_frame, text="New Service Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(form_frame)
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    # Service Cost
    tk.Label(form_frame, text="New Service Cost (VND):", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_cost = tk.Entry(form_frame)
    entry_cost.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_cost)

    def submit():
        service_id = entry_id.get()
        service_name = entry_name.get()
        service_cost = entry_cost.get()

        # Call core logic update function
        success, message = update_service(conn, service_id, service_name, service_cost)
        
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Update Service", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def view_services_gui(conn):
    """GUI for searching a service by Service ID or Service Name"""
    view_window = tk.Toplevel()
    view_window.title("Search Service")
    view_window.geometry("800x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="View Service", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    search_window = tk.Frame(view_window, bg=BG_COLOR)
    search_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    # Service ID Label and Entry
    tk.Label(search_window, text="Service ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_id = tk.Entry(search_window)
    entry_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_id)

    # Service Name Label and Entry
    tk.Label(search_window, text="Service Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(search_window)  
    entry_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    columns = ("ServiceID", "ServiceName", "ServiceCode", "ServiceCost", "Description")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')
    col_widths = [50, 200, 150, 100, 200]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def load_data():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        service_id = entry_id.get().strip()
        service_name = entry_name.get().strip()

        success, result = search_services(conn, service_id, service_name)
        if success and result:
            for service in result:
                tree.insert("", tk.END, values=(
                    service["ServiceID"],
                    service["ServiceName"],
                    service["ServiceCode"],
                    service["ServiceCost"],
                    service["Description"]
                ))
        else:
            error_label.config(text="No services found matching the criteria.")
            view_window.lift()
            view_window.focus_force()
            return

    # Search button
    search_btn = tk.Button(search_window, text="Search", command=load_data)
    apply_styles(search_btn)
    search_btn.grid(row=2, column=0, columnspan=2, pady=10)

    view_window.after(100, load_data)  # Automatically trigger search on window open

# PatientService GUI Functions
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

def create_patient_services_gui(conn, doctor_id=None):
    """GUI thêm dịch vụ cho bệnh nhân"""
    svc_window = tk.Toplevel()
    svc_window.title("Add Patient Services")
    svc_window.state('zoomed')
    svc_window.config(bg=BG_COLOR)
    center_window(svc_window)
    svc_window.lift()
    svc_window.attributes('-topmost', True)
    svc_window.after(100, lambda: svc_window.attributes('-topmost', False))

    # Main Frame
    main_frame = tk.Frame(svc_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Title
    tk.Label(
        main_frame, text="Add Services for Patient",
        font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR
    ).pack(pady=(0, 20))

    # Form Frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X, pady=(0, 15))
    form_frame.columnconfigure(1, weight=1)

    # Patient ID
    tk.Label(form_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5, padx=(0, 5))
    patient_id_entry = tk.Entry(form_frame)
    patient_id_entry.grid(row=0, column=1, pady=5, sticky="ew")
    apply_styles(patient_id_entry)

    # Appointment ID (optional)
    tk.Label(form_frame, text="Appointment ID (optional):", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5, padx=(0, 5))
    appointment_id_entry = tk.Entry(form_frame)
    appointment_id_entry.grid(row=1, column=1, pady=5, sticky="ew")
    apply_styles(appointment_id_entry)

    # Notes
    tk.Label(form_frame, text="Notes:", bg=BG_COLOR).grid(row=2, column=0, sticky="ne", pady=5, padx=(0, 5))
    notes_entry = tk.Text(form_frame, height=4, width=40)
    notes_entry.grid(row=2, column=1, pady=5, sticky="ew")
    apply_styles(notes_entry)
    # Scrollbar for Text widget (correct usage)
    scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=notes_entry.yview)
    scrollbar.grid(row=2, column=2, sticky="ns")
    notes_entry.config(yscrollcommand=scrollbar.set)


    # Service Frame
    svc_frame = tk.LabelFrame(main_frame, text="Services Used", bg=BG_COLOR, fg=TEXT_COLOR, padx=10, pady=10)
    svc_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    columns = ("Service", "Quantity", "Price", "Notes")

    # Scrollbar for Treeview (correct usage)
    svc_scrollbar = ttk.Scrollbar(svc_frame, orient="vertical")
    svc_scrollbar.pack(side="right", fill="y")

    svc_tree = ttk.Treeview(svc_frame, columns=columns, show="headings", yscrollcommand=svc_scrollbar.set)
    for col in columns:
        svc_tree.heading(col, text=col)
        svc_tree.column(col, width=150 if col != "Notes" else 200, anchor="w")
    svc_tree.pack(side="left", fill="both", expand=True)

    svc_scrollbar.config(command=svc_tree.yview)

    # Controls
    svc_controls = tk.Frame(main_frame, bg=BG_COLOR)
    svc_controls.pack(fill=tk.X, pady=5)

    tk.Label(svc_controls, text="Service:", bg=BG_COLOR).grid(row=0, column=0, padx=5, sticky='e')
    service_var = tk.StringVar()
    service_dropdown = ttk.Combobox(svc_controls, textvariable=service_var, width=30, state='readonly')
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ServiceID, ServiceName FROM Services ORDER BY ServiceID")
            services = cursor.fetchall()
            service_dropdown['values'] = [f"{s['ServiceID']} - {s['ServiceName']}" for s in services]
    except Exception as e:
        messagebox.showerror("Error", f"Could not load services: {e}", parent=svc_window)
    service_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

    tk.Label(svc_controls, text="Quantity:", bg=BG_COLOR).grid(row=1, column=0, padx=5, sticky='e')
    quantity_entry = tk.Entry(svc_controls, width=10)
    quantity_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
    apply_styles(quantity_entry)

    tk.Label(svc_controls, text="Notes:", bg=BG_COLOR).grid(row=2, column=0, padx=5, sticky='e')
    svc_note_entry = tk.Entry(svc_controls)
    svc_note_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
    apply_styles(svc_note_entry)

    def add_service():
        svc = service_var.get()
        qty = quantity_entry.get().strip()
        note = svc_note_entry.get().strip()

        if not svc or not qty:
            messagebox.showwarning("Warning", "Please select a service and quantity.", parent=svc_window)
            return

        try:
            with conn.cursor() as cursor:
                service_id = svc.split(" - ")[0]
                cursor.execute("SELECT ServiceCost FROM Services WHERE ServiceID = %s", (service_id,))
                result = cursor.fetchone()

            if not result:
                raise ValueError("Service not found")
            
            service_cost = result["ServiceCost"]

            qty_int = int(qty)
            if qty_int <= 0:
                raise ValueError()

            svc_tree.insert("", "end", values=(svc, qty_int, float(service_cost*qty_int), note or ""))
            clear_service_fields()

        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a positive integer and service must exist.", parent=svc_window)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add service: {e}", parent=svc_window)

    def clear_service_fields():
        service_var.set("")
        quantity_entry.delete(0, tk.END)
        svc_note_entry.delete(0, tk.END)

    def remove_service():
        selected = svc_tree.selection()
        if selected:
            for item in selected:
                svc_tree.delete(item)
        else:
            messagebox.showinfo("Info", "Please select a service to remove.", parent=svc_window)

    btn_frame = tk.Frame(svc_controls, bg=BG_COLOR)
    btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
    tk.Button(btn_frame, text="Add Service", command=add_service).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Remove Selected", command=remove_service).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Clear Fields", command=clear_service_fields).pack(side=tk.LEFT, padx=5)

    def submit_services():
        patient_id = patient_id_entry.get().strip()
        appointment_id = appointment_id_entry.get().strip() or None
        notes = notes_entry.get("1.0", tk.END).strip() or None
        if not patient_id:
            messagebox.showerror("Error", "Patient ID is required", parent=svc_window)
            return
        try:
            patient_id_int = int(patient_id)
        except:
            messagebox.showerror("Error", "Invalid Patient ID", parent=svc_window)
            return

        if appointment_id:
            try:
                appointment_id = int(appointment_id)
            except:
                messagebox.showerror("Error", "Invalid Appointment ID", parent=svc_window)
                return

        service_items = svc_tree.get_children()
        if not service_items:
            messagebox.showwarning("Warning", "Please add at least one service.", parent=svc_window)
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id_int,))
                if not cursor.fetchone():
                    messagebox.showerror("Error", f"Patient ID {patient_id_int} not found.", parent=svc_window)
                    return

                # Insert logic here
                # Example: Insert into PatientService (you must adapt with your schema)
                for item in service_items:
                    values = svc_tree.item(item)["values"]
                    service_id = int(values[0].split(" - ")[0])
                    service_cost = float(values[2])
                    service_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')                   
                    quantity = int(values[1])
                    service_note = values[3]
                    cursor.execute("""
                        INSERT INTO PatientServices (PatientID, ServiceID, DoctorID, ServiceDate, Quantity, CostAtTime, Notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (patient_id_int, service_id, doctor_id, service_date, quantity, service_cost, service_note)
                    )
                    
                conn.commit()
                messagebox.showinfo("Success", "Services added successfully!", parent=svc_window)
                svc_window.destroy()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to add services: {e}", parent=svc_window)

    submit_btn = tk.Button(main_frame, text="Submit Services", command=submit_services)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def delete_patient_service_gui(conn):
    """GUI for deleting a service from a patient"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Service from Patient")
    delete_window.geometry("400x200")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    delete_window.lift()
    delete_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng

    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Patient Serivce ID
    tk.Label(form_frame, text="Patient Service ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(form_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    def submit():
        patient_id = entry_patient_id.get()

        success, message = delete_patient_service (conn, patient_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Delete Service from Patient", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def view_patient_services_gui(conn):
    """GUI to view all services used by a patient"""
    view_window = tk.Toplevel()
    view_window.title("Patient Service History")
    view_window.geometry("900x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="Patient Service History", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(pady=5)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    tk.Label(search_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, padx=5)
    patient_id_entry = tk.Entry(search_frame)
    patient_id_entry.grid(row=0, column=1, padx=5)
    apply_styles(patient_id_entry)

    tk.Label(search_frame, text="Patient Name:", bg=BG_COLOR).grid(row=0, column=2, padx=5)
    patient_name_entry = tk.Entry(search_frame)
    patient_name_entry.grid(row=0, column=3, padx=5)
    apply_styles(patient_name_entry)

    # Treeview
    columns = ("Patient Service ID", "Patient Name", "Service Name", "Service Date", "Quantity", "Service Cost")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    col_widths = [100, 100, 250, 100, 50, 100]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def load_data():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        patient_id = patient_id_entry.get().strip()
        patient_name = patient_name_entry.get().strip()

        success, result = search_patient_services(conn, patient_id, patient_name)
        if success and result:
            for row in result:
                tree.insert("", tk.END, values=(
                    row["PatientServiceID"], row["PatientName"], row["ServiceName"], row["ServiceDate"], row["Quantity"], f"${row['ServiceCost']:.2f}"
                ))
        elif success:
            error_label.config(text="No services found for this patient.")
        else:
            error_label.config(text=result)

    # Search button
    search_btn = tk.Button(search_frame, text="Search", command=load_data)
    apply_styles(search_btn)
    search_btn.grid(row=0, column=4, padx=10)

    view_window.after(100, load_data)

# Prescription GUI Functions
def create_prescription_gui(conn, doctor_id=None):
    """GUI tạo đơn thuốc mới (cho bác sĩ)"""
    pres_window = tk.Toplevel()
    pres_window.title("Create New Prescription")
    pres_window.state('zoomed')
    pres_window.config(bg=BG_COLOR)
    center_window(pres_window)
    pres_window.lift()
    pres_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    pres_window.after(100, lambda: pres_window.attributes('-topmost', False))  # Reset after 100ms

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
    med_tree.heading("Medicine", text="Medicine"); med_tree.column("Medicine", width=200)
    med_tree.heading("Dosage", text="Dosage"); med_tree.column("Dosage", width=100)
    med_tree.heading("Frequency", text="Frequency"); med_tree.column("Frequency", width=120)
    med_tree.heading("Duration", text="Duration"); med_tree.column("Duration", width=100)
    med_tree.heading("Instruction", text="Instruction"); med_tree.column("Instruction", width=200)
    med_tree.heading("Quantity", text="Quantity"); med_tree.column("Quantity", width=80, anchor="center")

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
    med_dropdown = ttk.Combobox(med_controls_frame, textvariable=med_var, width=25, state='readonly') # Start readonly
    # Load medicines
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MedicineID, MedicineName FROM Medicine ORDER BY MedicineID")
            medicines = cursor.fetchall()
            med_dropdown['values'] = [f"{m['MedicineID']} - {m['MedicineName']}" for m in medicines]
    except MySQLError as e:
        messagebox.showerror("Error", f"Failed to load medicines: {e}", parent=pres_window)
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error loading medicines: {e}", parent=pres_window)

    med_dropdown.grid(row=0, column=1, columnspan=3, padx=5, sticky='ew')

    # Other input fields
    tk.Label(med_controls_frame, text="Dosage:", bg=BG_COLOR).grid(row=1, column=0, padx=5, pady=2, sticky='e')
    dosage_entry = tk.Entry(med_controls_frame, width=15); dosage_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew'); apply_styles(dosage_entry)
    tk.Label(med_controls_frame, text="Frequency:", bg=BG_COLOR).grid(row=1, column=2, padx=5, pady=2, sticky='e')
    freq_entry = tk.Entry(med_controls_frame, width=15); freq_entry.grid(row=1, column=3, padx=5, pady=2, sticky='ew'); apply_styles(freq_entry)

    tk.Label(med_controls_frame, text="Duration:", bg=BG_COLOR).grid(row=2, column=0, padx=5, pady=2, sticky='e')
    duration_entry = tk.Entry(med_controls_frame, width=15); duration_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew'); apply_styles(duration_entry)
    tk.Label(med_controls_frame, text="Quantity:", bg=BG_COLOR).grid(row=2, column=2, padx=5, pady=2, sticky='e')
    quantity_entry = tk.Entry(med_controls_frame, width=10); quantity_entry.grid(row=2, column=3, padx=5, pady=2, sticky='ew'); apply_styles(quantity_entry)

    tk.Label(med_controls_frame, text="Instruction:", bg=BG_COLOR).grid(row=3, column=0, padx=5, pady=2, sticky='e')
    instruction_entry = tk.Entry(med_controls_frame); instruction_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=2, sticky='ew'); apply_styles(instruction_entry)

    # --- Nested Functions for Medicine Actions ---
    def add_medicine():
        med = med_var.get()
        dosage = dosage_entry.get().strip()
        freq = freq_entry.get().strip()
        duration = duration_entry.get().strip()
        instruction = instruction_entry.get().strip()
        quantity_str = quantity_entry.get().strip()

        if not med:
            messagebox.showerror("Error", "Please select a medicine", parent=pres_window)
            pres_window.lift(); pres_window.focus_force(); return
        if not all([dosage, freq, quantity_str]):
            messagebox.showerror("Error", "Dosage, Frequency, and Quantity are required", parent=pres_window)
            pres_window.lift(); pres_window.focus_force(); return

        try:
            quantity_int = int(quantity_str)
            if quantity_int <= 0: raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive number", parent=pres_window)
            pres_window.lift(); pres_window.focus_force(); return

        med_tree.insert("", "end", values=(med, dosage, freq, duration or "", instruction or "", quantity_int))
        clear_medicine_fields()

    def remove_medicine():
        selected_items = med_tree.selection()
        if selected_items:
            if messagebox.askyesno("Confirm", "Remove selected medicine(s)?", parent=pres_window):
                 for item in selected_items: med_tree.delete(item)
        else:
             messagebox.showwarning("Selection Required", "Please select medicine(s) to remove", parent=pres_window)
             pres_window.lift(); pres_window.focus_force()

    def clear_medicine_fields():
        med_var.set("")
        dosage_entry.delete(0, tk.END)
        freq_entry.delete(0, tk.END)
        duration_entry.delete(0, tk.END)
        instruction_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)

    def move_medicine_up():
        selected = med_tree.selection()
        if not selected: return
        selected_item = selected[0]
        prev_item = med_tree.prev(selected_item)
        if prev_item: med_tree.move(selected_item, med_tree.parent(selected_item), med_tree.index(prev_item))

    # --- Button Frame for Medicine Actions ---
    btn_frame = tk.Frame(med_controls_frame, bg=BG_COLOR)
    btn_frame.grid(row=4, column=0, columnspan=4, pady=8, sticky='ew') # Use grid
    # Place buttons
    add_btn = tk.Button(btn_frame, text="Add Medicine", command=add_medicine, width=15); apply_styles(add_btn); add_btn.pack(side=tk.LEFT, padx=5)
    remove_btn = tk.Button(btn_frame, text="Remove Selected", command=remove_medicine, width=15); apply_styles(remove_btn); remove_btn.pack(side=tk.LEFT, padx=5)
    clear_btn = tk.Button(btn_frame, text="Clear Fields", command=clear_medicine_fields, width=15); apply_styles(clear_btn); clear_btn.pack(side=tk.LEFT, padx=5)
    up_btn = tk.Button(btn_frame, text="↑ Move Up", command=move_medicine_up, width=10); apply_styles(up_btn); up_btn.pack(side=tk.LEFT, padx=5)


    # --- Nested Function to Submit the Entire Prescription ---
    def submit_prescription():
        patient_id_str = patient_id_entry.get().strip()
        appointment_id_str = appointment_id_entry.get().strip() or None
        diagnosis = diagnosis_entry.get().strip() or None
        notes = notes_entry.get("1.0", tk.END).strip() or None

        # Validation
        if not patient_id_str:
            messagebox.showerror("Error", "Patient ID is required", parent=pres_window)
            pres_window.lift(); pres_window.focus_force(); return
        try: patient_id_int = int(patient_id_str)
        except ValueError:
            messagebox.showerror("Error", "Patient ID must be a number", parent=pres_window)
            pres_window.lift(); pres_window.focus_force(); return

        appointment_id_int = None
        if appointment_id_str:
            try: appointment_id_int = int(appointment_id_str)
            except ValueError:
                 messagebox.showerror("Error", "Appointment ID must be a number if provided", parent=pres_window)
                 pres_window.lift(); pres_window.focus_force(); return

        medicine_items = med_tree.get_children()
        if not medicine_items:
            messagebox.showerror("Error", "Please add at least one medicine", parent=pres_window)
            pres_window.lift(); pres_window.focus_force(); return

        # Database Interaction
        try:
            with conn.cursor() as cursor:
                # Validate Patient ID
                cursor.execute("SELECT PatientID FROM Patients WHERE PatientID = %s", (patient_id_int,))
                if not cursor.fetchone():
                    messagebox.showerror("Error", f"Patient ID '{patient_id_int}' not found.", parent=pres_window)
                    pres_window.lift(); pres_window.focus_force(); return

                # Validate Appointment ID if provided
                if appointment_id_int:
                    cursor.execute("""SELECT AppointmentID FROM Appointments WHERE AppointmentID = %s AND DoctorID = %s AND PatientID = %s""",
                                   (appointment_id_int, doctor_id, patient_id_int)) # Use doctor_id parameter
                    if not cursor.fetchone():
                        messagebox.showerror("Error", "Appointment ID not found or doesn't match patient/doctor.", parent=pres_window)
                        pres_window.lift(); pres_window.focus_force(); return

                # *** Insert Prescription using the doctor_id PARAMETER ***
                cursor.execute("""INSERT INTO Prescription (AppointmentID, PatientID, DoctorID, PrescriptionDate, Diagnosis, Notes)
                                  VALUES (%s, %s, %s, CURDATE(), %s, %s)""",
                               (appointment_id_int, patient_id_int, doctor_id, diagnosis, notes)) # doctor_id is now defined
                pres_id = cursor.lastrowid

                # Insert Details
                for item_id in medicine_items:
                    med_display_text, dosage, freq, duration, instruction, quantity_str = med_tree.item(item_id)['values']
                    try:
                        med_id_str = med_display_text.split(" - ")[0]
                        med_id_int = int(med_id_str)
                        quantity_int = int(quantity_str)
                    except (ValueError, IndexError, TypeError):
                        conn.rollback()
                        messagebox.showerror("Data Error", f"Invalid medicine ID or quantity format: {med_display_text}", parent=pres_window)
                        pres_window.lift(); pres_window.focus_force(); return

                    cursor.execute("""INSERT INTO PrescriptionDetails (PrescriptionID, MedicineID, Dosage, Frequency, Duration, Instruction, QuantityPrescribed)
                                      VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                   (pres_id, med_id_int, dosage, freq, duration or None, instruction or None, quantity_int))

                conn.commit()
                messagebox.showinfo("Success", f"Prescription #{pres_id} created successfully", parent=pres_window)

                if messagebox.askyesno("Print Prescription", "Would you like to print this prescription?", parent=pres_window):
                    if 'export_prescription_pdf' in globals(): export_prescription_pdf(conn, pres_id)
                    else: print("Warning: export_prescription_pdf function not found.")

                pres_window.destroy()

        except MySQLError as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to create prescription: {e}", parent=pres_window)
            pres_window.lift(); pres_window.focus_force();
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Unexpected Error", f"An error occurred: {e}", parent=pres_window)
            pres_window.lift(); pres_window.focus_force();
    # --- End of submit_prescription ---


    # --- Final Submit Button ---
    submit_frame = tk.Frame(main_frame, bg=BG_COLOR)
    submit_frame.pack(fill=tk.X, pady=10)

    submit_btn = tk.Button(submit_frame, text="Submit Prescription", command=submit_prescription, width=20)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

import tkinter.simpledialog as simpledialog

def view_prescription_gui(conn):
    prescription_id = simpledialog.askinteger("Input", "Enter Prescription ID:")
    if not prescription_id:
        return
    """GUI xem và xuất đơn thuốc"""
    view_window = tk.Toplevel()
    view_window.title(f"Prescription #{prescription_id}")
    view_window.geometry("800x600")
    view_window.config(bg=BG_COLOR)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Content frame with scrollbar
    content_frame = tk.Frame(main_frame, bg=BG_COLOR)
    content_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(content_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
            # Get prescription details
            cursor.execute("""
                SELECT p.*, d.DoctorName, pt.PatientName, pt.DateOfBirth, pt.Gender, pt.PatientID
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

            # Get medicine details
            cursor.execute("""
                SELECT pd.*, m.MedicineName, m.Unit
                FROM PrescriptionDetails pd
                JOIN Medicine m ON pd.MedicineID = m.MedicineID
                WHERE pd.PrescriptionID = %s
            """, (prescription_id,))
            details = cursor.fetchall()

            # Header
            text_area.insert(tk.END, "=== PRESCRIPTION DETAILS ===\n\n", "title")
            text_area.insert(tk.END, f"Prescription ID: {prescription_id}\n")
            text_area.insert(tk.END, f"Date: {prescription['PrescriptionDate']}\n\n")

            # Patient Info
            text_area.insert(tk.END, "=== PATIENT INFORMATION ===\n", "subtitle")
            text_area.insert(tk.END, f"Name: {prescription['PatientName']}\n")
            text_area.insert(tk.END, f"DOB: {prescription['DateOfBirth']}\n")
            text_area.insert(tk.END, f"Gender: {prescription['Gender']}\n\n")

            # Doctor Info
            text_area.insert(tk.END, "=== DOCTOR INFORMATION ===\n", "subtitle")
            text_area.insert(tk.END, f"Doctor: {prescription['DoctorName']}\n\n")

            # Diagnosis
            text_area.insert(tk.END, "=== DIAGNOSIS ===\n", "subtitle")
            text_area.insert(tk.END, f"{prescription['Diagnosis'] or 'Not specified'}\n\n")

            # Medicine list
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

            # Insurance Info
            cursor.execute("""
                SELECT *
                FROM Insurance
                WHERE PatientID = %s AND EffectiveDate <= %s AND EndDate >= %s
                ORDER BY EndDate DESC
                LIMIT 1
            """, (prescription['PatientID'], prescription['PrescriptionDate'], prescription['PrescriptionDate']))
            insurance = cursor.fetchone()

            text_area.insert(tk.END, "\n=== INSURANCE INFORMATION ===\n", "subtitle")
            if insurance:
                text_area.insert(tk.END, f"Provider: {insurance['InsuranceProvider']}\n")
                text_area.insert(tk.END, f"Policy Number: {insurance['PolicyNumber']}\n")
                text_area.insert(tk.END, f"BHYT Card: {insurance['BHYTCardNumber'] or 'N/A'}\n")
                text_area.insert(tk.END, f"Coverage: {insurance['CoverageDetails']}\n")
                text_area.insert(tk.END, f"Valid: {insurance['EffectiveDate']} to {insurance['EndDate']}\n")
                text_area.insert(tk.END, "Note: Cost will be calculated when an invoice is created.\n")
            else:
                text_area.insert(tk.END, "No valid insurance found at the time of prescription.\n")

    except Exception as e:
        messagebox.showerror("Error", f"Error fetching prescription details: {e}")

    # Export button
    def on_export_pdf():
        export_prescription_pdf(conn, prescription_id)
        messagebox.showinfo("Success", "Prescription exported to PDF")

    export_button = tk.Button(view_window, text="Export to PDF", font=("Arial", 12), command=on_export_pdf)
    export_button.pack(pady=10)

def view_prescriptions_gui(conn):
    """GUI xem danh sách đơn thuốc (chỉ xem)"""
    prescriptions_window = tk.Toplevel()
    prescriptions_window.title("Prescriptions")
    prescriptions_window.geometry("1000x750")
    prescriptions_window.config(bg=BG_COLOR)
    center_window(prescriptions_window)
    prescriptions_window.lift()
    prescriptions_window.attributes('-topmost', True)
    prescriptions_window.after(100, lambda: prescriptions_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(prescriptions_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Results area
    text_area = create_scrollable_text(main_frame, height=25, width=100)

    # Initial view
    search_prescriptions(conn, None, text_area)

    prescriptions_window.mainloop()

def search_prescriptions(conn, patient_id, text_area):
    """Tìm kiếm và hiển thị danh sách đơn thuốc (theo PatientID hoặc tất cả)"""
    text_area.config(state=tk.NORMAL)
    text_area.delete("1.0", tk.END)

    try:
        with conn.cursor() as cursor:
            if patient_id:
                cursor.execute("""
                    SELECT p.PrescriptionID, p.PrescriptionDate, pt.PatientName, d.DoctorName
                    FROM Prescription p
                    JOIN Patients pt ON p.PatientID = pt.PatientID
                    JOIN Doctors d ON p.DoctorID = d.DoctorID
                    WHERE p.PatientID = %s
                    ORDER BY p.PrescriptionDate DESC
                """, (patient_id,))
            else:
                cursor.execute("""
                    SELECT p.PrescriptionID, p.PrescriptionDate, pt.PatientName, d.DoctorName
                    FROM Prescription p
                    JOIN Patients pt ON p.PatientID = pt.PatientID
                    JOIN Doctors d ON p.DoctorID = d.DoctorID
                    ORDER BY p.PrescriptionDate DESC
                """)

            prescriptions = cursor.fetchall()

            if not prescriptions:
                text_area.insert(tk.END, "No prescriptions found.\n")
            else:
                for pres in prescriptions:
                    text_area.insert(tk.END, f"Prescription ID: {pres['PrescriptionID']}\n")
                    text_area.insert(tk.END, f"Date: {pres['PrescriptionDate']}\n")
                    text_area.insert(tk.END, f"Patient: {pres['PatientName']}\n")
                    text_area.insert(tk.END, f"Doctor: {pres['DoctorName']}\n")
                    text_area.insert(tk.END, "-"*60 + "\n")

    except MySQLError as e:
        messagebox.showerror("Database Error", f"Failed to fetch prescriptions: {e}")

    text_area.config(state=tk.DISABLED)

def view_patient_prescriptions_gui(conn):
    """GUI xem đơn thuốc của bệnh nhân (cho bác sĩ)"""
    patient_id = simpledialog.askstring("Patient ID", "Enter Patient ID:")
    if not patient_id:
        return
    
    view_prescriptions_gui(conn, patient_id)

def delete_prescription_gui(conn):
    """GUI for deleting a prescription"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Prescription")
    delete_window.geometry("400x200")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    delete_window.lift()
    delete_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    delete_window.after(100, lambda: delete_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Prescription ID
    tk.Label(form_frame, text="Prescription ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_pres_id = tk.Entry(form_frame)
    entry_pres_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_pres_id)

    def submit():
        pres_id = entry_pres_id.get()

        success, message = delete_prescription(conn, pres_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Delete Prescription", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def delete_prescription_details_gui(conn):
    """GUI for deleting a prescription detail"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Prescription Detail")
    delete_window.geometry("400x200")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    delete_window.lift()
    delete_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    delete_window.after(100, lambda: delete_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Form frame
    form_frame = tk.Frame(main_frame, bg=BG_COLOR)
    form_frame.pack(fill=tk.X)

    # Prescription ID
    tk.Label(form_frame, text="Prescription ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_pres_id = tk.Entry(form_frame)
    entry_pres_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_pres_id)

    # Medicine ID
    tk.Label(form_frame, text="Medicine ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_med_id = tk.Entry(form_frame)
    entry_med_id.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_med_id)

    def submit():
        pres_id = entry_pres_id.get()
        med_id = entry_med_id.get()

        success, message = delete_prescription_detail(conn, pres_id, med_id)
        if success:
            messagebox.showinfo("Success", message)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_btn = tk.Button(main_frame, text="Delete Prescription Detail", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

def create_invoice_gui(conn):
    """GUI Tạo Hóa Đơn Chi Tiết có Scrollbar và nhập % BH thủ công"""
    invoice_window = tk.Toplevel()
    invoice_window.title("Create Detailed Invoice - Manual Discount")
    invoice_window.geometry("980x800")
    invoice_window.config(bg=BG_COLOR)
    center_window(invoice_window)
    invoice_window.lift()
    invoice_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    invoice_window.after(100, lambda: invoice_window.attributes('-topmost', False))

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
    discounted_cost = {'prescription': 0.0, 'room': 0.0, 'service': 0.0}
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
        search_term = patient_search_entry.get().strip()
        if not search_term: 
            return messagebox.showwarning("Input Required", "Enter Patient Name/ID.")
        clear_all_details()
        try:
            p_id = int(search_term) if search_term.isdigit() else None
            success, result = search_patients(conn, patient_id=p_id, name=None if p_id else search_term)
            if not success or not result: return messagebox.showinfo("Not Found", f"Patient not found: '{search_term}'.")
            patient_data = result[0]
            if len(result) > 1: messagebox.showinfo("Multiple Found", "Using first result.")
            p_id = patient_data['PatientID']; p_name = patient_data['PatientName']; p_dob = patient_data['DateOfBirth']; p_phone = patient_data.get('PhoneNumber', 'N/A')
            current_patient_id.set(str(p_id)); patient_info_var.set(f"ID: {p_id} | Name: {p_name} | DoB: {p_dob} | Phone: {p_phone}")
            load_prescription_details(p_id); display_insurance_info(p_id); load_services_list(p_id)
            calculate_subtotals_action() # Calculate initial subtotals and update summary
            main_frame.update_idletasks(); canvas.config(scrollregion=canvas.bbox("all"))
        except Exception as e: messagebox.showerror("Search Error", f"Error: {str(e)}"); clear_all_details()
    search_btn.config(command=search_patient_action)

    def load_prescription_details(p_id):
        for item in pres_tree.get_children(): 
            pres_tree.delete(item)
        try:
            # This now calls the CORRECTED function in core_logic.py
            success, prescriptions_details = get_patient_prescriptions(conn, p_id) # Use the corrected function name

            if success: # Check if the DB query succeeded
                 if prescriptions_details: # Check if any details were returned
                     for pres_detail in prescriptions_details: # Iterate through the list of details
                         price = float(pres_detail.get('MedicineCost', 0.0)) # Ensure float
                         qty = int(pres_detail.get('QuantityPrescribed', 0)) # Ensure int
                         raw_total = qty * price
                         # Store raw total in the hidden column 'raw_total'
                         pres_tree.insert("", tk.END, values=(
                             pres_detail.get('MedicineName', 'N/A'),
                             pres_detail.get('Dosage', ''),
                             qty,
                             format_currency(price),
                             format_currency(raw_total), # Display formatted total
                             raw_total                     # Store raw total
                         ))
                 else:
                     # Optional: Insert a row indicating no prescriptions found, or just leave it empty
                     # pres_tree.insert("", tk.END, values=("No prescription items found", "", "", "", "", 0.0))
                     pass # Treeview will just be empty
            else:
                 # Show the error message returned by get_patient_prescriptions
                 messagebox.showerror("Prescription Load Error", f"Could not load prescriptions: {prescriptions_details}", parent=invoice_window)


            # After loading/potentially failing, recalculate subtotals
            # It's important this runs even if loading fails to reset the cost to 0
            calculate_subtotals_action()

        except Exception as e:
            # General catch-all for unexpected errors during loading/processing
            print(f"Error in load_prescription_details GUI function: {e}")
            messagebox.showerror("Prescription Load Error", f"GUI Error loading prescriptions: {e}", parent=invoice_window)
            # Still recalculate subtotals to ensure UI consistency
            calculate_subtotals_action()

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

    def load_services_list(p_id):
        try:
            if not p_id:
                service_combo['values'] = []
                return
            
            patient_id_int = int(p_id)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ps.PatientServiceID, s.ServiceName, ps.Quantity, s.ServiceCost, ps.CostAtTime
                FROM PatientServices ps
                JOIN Services s ON ps.ServiceID = s.ServiceID
                WHERE ps.PatientID = %s AND ps.InvoiceID IS NULL
            """, (patient_id_int,))
            services = cursor.fetchall()
            
            if services:
                all_services_list.clear()
                service_display_list = []
                for row in services:
                    psid = row['PatientServiceID']
                    sname = row['ServiceName']
                    qty = int(row['Quantity'])
                    cost = float(row['ServiceCost'])
                    total_cost = cost * qty
                    all_services_list.append({
                        'PatientServiceID': psid,
                        'ServiceName': sname,
                        'Quantity': qty,
                        'ServiceCost': cost,
                        'Total': row['CostAtTime']
                    })
                    display_text = f"{sname} ×{qty} ({format_currency(total_cost)})"
                    service_display_list.append(display_text)


                service_combo['values'] = service_display_list
                if service_display_list:
                    service_combo.current(0)
            else:
                service_combo['values'] = []
        except Exception as e:
            print(f"Error loading services: {e}")
            messagebox.showerror("Service Load Error", f"Error loading services: {e}")

    def add_selected_service():
        selected_index = service_combo.current()
        if selected_index == -1 or selected_index >= len(all_services_list):
            messagebox.showwarning("No selection", "Please select a service to add.")
            return

        service = all_services_list[selected_index]
        name = service['ServiceName']
        price = service['ServiceCost']
        qty = service['Quantity']
        total = float(price) * int(qty)

        svc_tree.insert("", "end", values=(
            name,
            format_currency(price),
            qty,
            format_currency(total),
            total,  # raw_total (hidden)
            price   # raw_price (hidden)
        ))
    add_svc_btn.config(command=add_selected_service)

    def update_patientservices_invoice(patient_id_int, new_invoice_id):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE PatientServices
            SET InvoiceID = %s
            WHERE PatientID = %s AND InvoiceID IS NULL
        """, (new_invoice_id, patient_id_int))
        conn.commit()
    
    def add_service_action():
        selected_index = service_combo.current()
        if selected_index == -1:
            return messagebox.showwarning("Input Required", "Please select a service.")
        if not current_patient_id.get():
            return messagebox.showwarning("Patient Required", "Search patient first.")

        try:
            # Get service info directly from the indexed list
            s_info = all_services_list[selected_index]
            raw_price = float(s_info.get('ServiceCost', 0.0))
            qty = int(s_info.get('Quantity', 1))
            assert qty > 0
            raw_total = raw_price * qty

            # Insert to the tree
            svc_tree.insert("", tk.END, values=(
                s_info['ServiceName'],
                format_currency(raw_price),
                qty,
                format_currency(raw_total),
                raw_total,   # hidden
                raw_price    # hidden
            ))

            # Reset UI
            service_var.set("")
            service_combo.set("")
            calculate_subtotals_action()
        except Exception as e:
            messagebox.showerror("Error Adding Service", f"Error: {str(e)}")
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
            
            discounted_cost = {'prescription': med_after, 'room': room_after, 'service': svc_after}

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

        
        med_cost_f = float(discounted_cost.get('prescription', 0.0))
        room_cost_f = float(discounted_cost.get('room', 0.0))
        svc_cost_f = float(discounted_cost.get('service', 0.0))

        # Tạo notes chi tiết (bao gồm cả % đã áp dụng)
        notes = f"--- INVOICE DETAILS (Patient ID: {p_id}) ---\n"
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

        if discount>0:
            bhyt=1
        else:
            bhyt=0

        # Gọi hàm lưu từ core_logic (Pass original costs and final calculated amounts)
        success, message, new_invoice_id = save_calculated_invoice(
            conn, p_id,
            room_cost_f, med_cost_f, svc_cost_f,# Pass original costs
            final_amount, # Pass calculated discount and final amount
            notes, bhyt
        )
        if success: messagebox.showinfo("Success", f"Invoice #{new_invoice_id} created!"); invoice_window.destroy()
        else: messagebox.showerror("Save Error", f"Failed to save invoice: {message}")
        update_patientservices_invoice(p_id, new_invoice_id)


    create_invoice_btn.config(command=save_invoice_action)

    # --- Final Setup ---
    center_window(invoice_window, 980, 800)
    main_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0) # Đảm bảo scroll lên đầu khi mở

    # Initial calculation after window setup
    calculate_subtotals_action()

    invoice_window.mainloop()

#report
# Emergency GUI function
def add_emergency_contact_gui(conn):
    """GUI for adding emergency contact"""
    emergency_window = tk.Toplevel()
    emergency_window.title("Add Emergency Contact")
    emergency_window.geometry("400x300")
    emergency_window.config(bg=BG_COLOR)
    center_window(emergency_window)
    emergency_window.lift()
    emergency_window.attributes('-topmost', True) # Keep on top of other windows
    emergency_window.after(100, lambda: emergency_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(emergency_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(main_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    # Emergency contact name
    tk.Label(main_frame, text="Contact Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_contact_name = tk.Entry(main_frame)
    entry_contact_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_contact_name)

    # Relationship
    tk.Label(main_frame, text="Relationship:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_relationship = tk.Entry(main_frame)
    entry_relationship.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_relationship)

    # Phone number
    tk.Label(main_frame, text="Phone Number:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_phone_number = tk.Entry(main_frame)
    entry_phone_number.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_phone_number)

    def submit_contact():
        """Submit the emergency contact details to the database."""
        patient_id = entry_patient_id.get().strip()
        contact_name = entry_contact_name.get().strip()
        relationship = entry_relationship.get().strip()
        phone_number = entry_phone_number.get().strip()

        if not patient_id or not contact_name or not relationship or not phone_number:
            messagebox.showerror("Error", "All fields are required.")
            return

        # Call the function to add emergency contact
        success, message = add_emergency_contact(conn, patient_id, contact_name, relationship, phone_number)
        if success:
            messagebox.showinfo("Success", "Emergency contact added successfully.")
            emergency_window.destroy()
        else:
            messagebox.showerror("Error", message)
            emergency_window.lift()
        emergency_window.attributes('-topmost', True) # Keep on top of other windows
        emergency_window.after(100, lambda: emergency_window.attributes('-topmost', False))
            
    # Submit button
    submit_button = tk.Button(main_frame, text="Add Emergency Contact", command=submit_contact)
    submit_button.grid(row=4, columnspan=2, pady=(10, 0))
    apply_styles(submit_button)

    main_frame.grid_columnconfigure(1, weight=1) # Make the second column expand
    main_frame.update_idletasks() # Update the layout to ensure proper spacing

def update_emergency_contact_gui(conn):
    """GUI for updating emergency contact"""
    update_window = tk.Toplevel()
    update_window.title("Update Emergency Contact")
    update_window.geometry("400x300")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True) # Keep on top of other windows
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Fetch existing emergency contact details
    # Contact ID
    tk.Label(main_frame, text="Contact ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_contact_id = tk.Entry(main_frame)
    entry_contact_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_contact_id)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(main_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)
      
    # Emergency contact name
    tk.Label(main_frame, text="Contact Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_contact_name = tk.Entry(main_frame)
    entry_contact_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_contact_name)

    # Relationship
    tk.Label(main_frame, text="Relationship:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_relationship = tk.Entry(main_frame)
    entry_relationship.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_relationship)

    # Phone number
    tk.Label(main_frame, text="Phone Number:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_phone_number = tk.Entry(main_frame)
    entry_phone_number.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_phone_number)

    # Address
    tk.Label(main_frame, text="Address:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    entry_address = tk.Entry(main_frame)
    entry_address.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_address)

    def submit_update():
        """Submit the updated emergency contact details to the database."""
        contact_id = entry_contact_id.get().strip()
        patient_id = entry_patient_id.get().strip()
        contact_name = entry_contact_name.get().strip()
        relationship = entry_relationship.get().strip()
        phone_number = entry_phone_number.get().strip()
        address = entry_address.get().strip()

        if not contact_id:
            messagebox.showerror("Error", "Contact ID is required.")
            update_window.lift()
            update_window.focus_force()
            return
        
        if not patient_id or contact_name or relationship or phone_number or address:
            messagebox.showerror("Error", "At least one field must be updated.")
            update_window.lift()
            update_window.focus_force()
            return

        # Call the function to update emergency contact
        success, message = update_emergency_contact(conn, contact_id, patient_id, contact_name, relationship, phone_number, address)
        if success:
            messagebox.showinfo("Success", "Emergency contact updated successfully.")
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Submit button
    submit_button = tk.Button(main_frame, text="Update Emergency Contact", command=submit_update)
    submit_button.grid(row=5, columnspan=2, pady=(10, 0))
    apply_styles(submit_button)

def delete_emergency_contact_gui(conn):
    """GUI for deleting emergency contact"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Emergency Contact")
    delete_window.geometry("400x200")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    delete_window.lift()
    delete_window.attributes('-topmost', True) # Keep on top of other windows
    delete_window.after(100, lambda: delete_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(main_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    def submit_delete():
        """Submit the delete request for the emergency contact."""
        patient_id = entry_patient_id.get().strip()

        if not patient_id:
            messagebox.showerror("Error", "Patient ID is required.")
            delete_window.lift() # Bring the window to the front
            delete_window.focus_force()
            return

        # Call the function to delete emergency contact
        success, message = delete_emergency_contact(conn, patient_id)
        if success:
            messagebox.showinfo("Success", "Emergency contact deleted successfully.")
            delete_window.destroy()
        else:
            messagebox.showerror("Error", message)
            delete_window.lift()
            delete_window.focus_force()

    # Submit button
    submit_button = tk.Button(main_frame, text="Delete Emergency Contact", command=submit_delete)
    submit_button.grid(row=1, columnspan=2, pady=(10, 0))
    apply_styles(submit_button)

def view_emergency_contacts_gui(conn):
    """GUI for viewing emergency contacts for a patient"""
    view_window = tk.Toplevel()
    view_window.title("View Emergency Contacts")
    view_window.geometry("600x400")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Input section
    input_frame = tk.Frame(main_frame, bg=BG_COLOR)
    input_frame.pack(fill=tk.X, pady=10)

    tk.Label(input_frame, text="Enter Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", padx=5)
    entry_patient_id = tk.Entry(input_frame)
    entry_patient_id.grid(row=0, column=1, sticky="w")
    apply_styles(entry_patient_id)

    # Treeview
    columns = ("ContactName", "Relationship", "PhoneNumber")
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180)
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    # Search handler
    def load_contacts():
        patient_id = entry_patient_id.get().strip()
        tree.delete(*tree.get_children())

        if not patient_id:
            messagebox.showwarning("Input Error", "Please enter a valid Patient ID.")
            view_window.lift() # Bring the window to the front
            view_window.focus_force() # Bring the window to the front
            return

        success, contacts = get_emergency_contacts(conn, patient_id)
        if success:
            if contacts:
                for contact in contacts:
                    tree.insert("", tk.END, values=(contact['ContactName'], contact['Relationship'], contact['PhoneNumber']))
                tree.pack(fill=tk.BOTH, expand=True, pady=10)
            else:
                messagebox.showinfo("No Data", "No emergency contacts found for this patient.")
                view_window.lift()
                view_window.focus_force()
        else:
            messagebox.showerror("Error", contacts)
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(main_frame, text="Search", command=load_contacts)
    apply_styles(search_btn)
    search_btn.pack()

# Medicine GUI function
def view_medicine_gui(conn):
    """GUI để tìm kiếm và xem danh sách thuốc"""
    view_window = tk.Toplevel()
    view_window.title("Medicine Directory")
    view_window.geometry("800x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    tk.Label(view_window, text="View Medicines", font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    # Search frame
    search_frame = tk.Frame(view_window, bg=BG_COLOR)
    search_frame.pack(pady=5)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    tk.Label(search_frame, text="Medicine ID:", bg=BG_COLOR).grid(row=0, column=0, padx=5, sticky='w')
    id_entry = tk.Entry(search_frame)
    id_entry.grid(row=0, column=1, padx=5)
    apply_styles(id_entry)

    tk.Label(search_frame, text="Medicine Name:", bg=BG_COLOR).grid(row=1, column=0, padx=5, sticky='w')
    name_entry = tk.Entry(search_frame)
    name_entry.grid(row=1, column=1, padx=5)
    apply_styles(name_entry)

    # Treeview
    columns = ("MedicineID", "MedicineName", "Unit", "Quantity", "MedicineCost")
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def search():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        medicine_id = id_entry.get().strip() or None
        medicine_name = name_entry.get().strip() or None
        success, result = search_medicine(conn, medicine_id, medicine_name)
        if success:
            for row in result:
                tree.insert("", tk.END, values=(
                    row["MedicineID"],
                    row["MedicineName"],
                    row["Unit"],
                    row["Quantity"],
                    row["MedicineCost"]
                ))
        else:
            error_label.config(text=f"Failed to search medicines: {result}")
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(search_frame, text="Search", command=search)
    apply_styles(search_btn)
    search_btn.grid(row=2, column=0, columnspan=2, pady=10)

    view_window.after(100, search)

def add_medicine_gui(conn):
    """GUI for adding medicine"""
    medicine_window = tk.Toplevel()
    medicine_window.title("Add Medicine")
    medicine_window.geometry("400x300")
    medicine_window.config(bg=BG_COLOR)
    center_window(medicine_window)
    medicine_window.lift()
    medicine_window.attributes('-topmost', True)
    medicine_window.after(100, lambda: medicine_window.attributes('-topmost', False))

    main_frame = tk.Frame(medicine_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Labels & entries
    tk.Label(main_frame, text="Medicine Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_name = tk.Entry(main_frame)
    entry_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_name)

    tk.Label(main_frame, text="Unit:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_unit = tk.Entry(main_frame)
    entry_unit.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_unit)

    tk.Label(main_frame, text="Quantity:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_quantity = tk.Entry(main_frame)
    entry_quantity.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_quantity)

    tk.Label(main_frame, text="Cost (VND):", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_cost = tk.Entry(main_frame)
    entry_cost.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_cost)

    def save():
        name = entry_name.get().strip()
        unit = entry_unit.get().strip()
        quantity_str = entry_quantity.get().strip()
        cost_str = entry_cost.get().strip()

        if not all([name, unit, quantity_str, cost_str]):
            messagebox.showerror("Error", "❌ All fields are required.")
            medicine_window.lift()
            medicine_window.focus_force()
            return

        try:
            quantity = int(quantity_str)
            cost = float(cost_str.replace(",", ""))
        except ValueError:
            messagebox.showerror("Error", "❌ Quantity must be integer, cost must be a number.")
            medicine_window.lift()
            medicine_window.focus_force()
            return

        result = add_medicine(conn, name, unit, quantity, cost)
        if result is None:
            messagebox.showerror("Error", "❌ Failed to add medicine.")
        else:
            success, msg = result
            if success:
                messagebox.showinfo("Success", msg)
                medicine_window.destroy()
            else:
                messagebox.showerror("Error", msg)
                medicine_window.lift()
                medicine_window.focus_force()

    save_button = tk.Button(main_frame, text="Save", command=save)
    save_button.grid(row=4, columnspan=2, pady=10)
    apply_styles(save_button)

def update_medicine_gui(conn):
    """GUI for updating medicine"""
    update_window = tk.Toplevel()
    update_window.title("Update Medicine")
    update_window.geometry("400x450")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Medicine ID
    tk.Label(main_frame, text="Medicine ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_medicine_id = tk.Entry(main_frame)
    entry_medicine_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_medicine_id)

    # Medicine Name
    tk.Label(main_frame, text="Medicine Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_medicine_name = tk.Entry(main_frame)
    entry_medicine_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_medicine_name)

    # Unit
    tk.Label(main_frame, text="Unit:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_unit = tk.Entry(main_frame)
    entry_unit.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_unit)

    # Quantity
    tk.Label(main_frame, text="Quantity:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_quantity = tk.Entry(main_frame)
    entry_quantity.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_quantity)

    # Medicine Cost
    tk.Label(main_frame, text="Medicine Cost (VND):", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
    entry_medicine_cost = tk.Entry(main_frame)
    entry_medicine_cost.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_medicine_cost)

    def submit():
        medicine_id = entry_medicine_id.get().strip()
        medicine_name = entry_medicine_name.get().strip()
        unit = entry_unit.get().strip()
        quantity = entry_quantity.get().strip()
        medicine_cost = entry_medicine_cost.get().strip()

        if not medicine_id:
            messagebox.showerror("Error", "Medicine ID is required.")
            update_window.lift()
            update_window.focus_force()
            return

        success, message = update_medicine(conn, medicine_id, medicine_name, unit, quantity, medicine_cost)
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    submit_button = tk.Button(main_frame, text="Update Medicine", command=submit)
    submit_button.grid(row=5, columnspan=2, pady=10)
    apply_styles(submit_button)

def delete_medicine_gui(conn):
    """GUI for deleting medicine"""
    delete_window = tk.Toplevel()
    delete_window.title("Delete Medicine")
    delete_window.geometry("400x200")
    delete_window.config(bg=BG_COLOR)
    center_window(delete_window)
    delete_window.lift()
    delete_window.attributes('-topmost', True)
    delete_window.after(100, lambda: delete_window.attributes('-topmost', False))

    main_frame = tk.Frame(delete_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Medicine ID input
    tk.Label(main_frame, text="Enter Medicine ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_medicine_id = tk.Entry(main_frame)
    entry_medicine_id.grid(row=0, column=1, padx=5, pady=5)
    apply_styles(entry_medicine_id)

    def confirm_delete():
        medicine_id = entry_medicine_id.get()
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this medicine?")
        if not confirm:
            return

        success, msg = delete_medicine(conn, medicine_id)
        if success:
            messagebox.showinfo("Success", msg)
            delete_window.destroy()
        else:
            messagebox.showerror("Error", msg)

    delete_button = tk.Button(main_frame, text="Delete", command=confirm_delete)
    apply_styles(delete_button)
    delete_button.grid(row=1, columnspan=2, pady=15)

#MedicineBatch GUI function
def add_medicine_batch_gui(conn):
    """GUI for adding medicine batch"""
    batch_window = tk.Toplevel()
    batch_window.title("Add Medicine Batch")
    batch_window.geometry("400x350")
    batch_window.config(bg=BG_COLOR)
    center_window(batch_window)
    batch_window.lift()
    batch_window.attributes('-topmost', True)
    batch_window.after(100, lambda: batch_window.attributes('-topmost', False))

    main_frame = tk.Frame(batch_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    labels = [
        "Medicine ID:", "Batch Number:", "Expiry Date (YYYY-MM-DD):",
        "Quantity:", "Cost (VND):"
    ]
    entries = []

    for idx, text in enumerate(labels):
        tk.Label(main_frame, text=text, bg=BG_COLOR).grid(row=idx, column=0, sticky="e", pady=5)
        entry = tk.Entry(main_frame)
        entry.grid(row=idx, column=1, pady=5, padx=5, sticky="ew")
        apply_styles(entry)
        entries.append(entry)

    def submit():
        try:
            medicine_id = entries[0].get().strip()
            batch_number = entries[1].get().strip()
            expiry_date = entries[2].get().strip()
            quantity = entries[3].get().strip()
            cost = entries[4].get().strip()

            if not all([medicine_id, batch_number, expiry_date]):
                raise ValueError("❌ All fields except cost/quantity must be filled.")
            
            if quantity < 0 or cost < 0:
                raise ValueError("❌ Quantity and cost must be non-negative.")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            batch_window.lift()
            batch_window.focus_force()
            return

        result = add_medicine_batch(conn, medicine_id, batch_number, expiry_date, quantity, cost)
        if result is None:
            messagebox.showerror("Error", "❌ Failed to add batch (internal error).")
        else:
            success, message = result
            if success:
                messagebox.showinfo("Success", message)
                batch_window.destroy()
            else:
                messagebox.showerror("Error", message)
                batch_window.lift()
                batch_window.focus_force()

    save_button = tk.Button(main_frame, text="Save", command=submit)
    apply_styles(save_button)
    save_button.grid(row=len(labels), columnspan=2, pady=(10, 0))

def update_medicine_batch_gui(conn):
    """GUI for updating medicine batch"""
    prompt_window = tk.Toplevel()
    prompt_window.title("Update Medicine Batch")
    prompt_window.geometry("350x320")
    prompt_window.config(bg=BG_COLOR)
    center_window(prompt_window)
    prompt_window.lift()
    prompt_window.attributes('-topmost', True)
    prompt_window.focus_force()
    prompt_window.after(100, lambda: prompt_window.attributes('-topmost', False))

    main_frame = tk.Frame(prompt_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Entry fields
    fields = {
        "Batch ID": tk.Entry(main_frame),
        "Medicine ID": tk.Entry(main_frame),
        "Batch Number": tk.Entry(main_frame),
        "Expiry Date (YYYY-MM-DD)": tk.Entry(main_frame),
        "Quantity": tk.Entry(main_frame),
        "Medicine Cost (VND)": tk.Entry(main_frame),
    }

    for i, (label, entry) in enumerate(fields.items()):
        tk.Label(main_frame, text=label + ":", bg=BG_COLOR).grid(row=i, column=0, sticky="e", pady=5)
        entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
        apply_styles(entry)

    # Button
    def submit():
        values = {label: entry.get().strip() for label, entry in fields.items()}
        batch_id = values["Batch ID"]
        if not batch_id:
            messagebox.showerror("Error", "Batch ID is required.")
            prompt_window.lift()
            prompt_window.focus_force()
            return

        success, message = update_medicine_batch(
            conn,
            batch_id,
            values["Medicine ID"],
            values["Batch Number"],
            values["Expiry Date (YYYY-MM-DD)"],
            values["Quantity"],
            values["Medicine Cost (VND)"]
        )

        if success:
            messagebox.showinfo("Success", message)
            prompt_window.destroy()
        else:
            messagebox.showerror("Error", message)
            prompt_window.lift()
            prompt_window.focus_force()

    submit_button = tk.Button(main_frame, text="Update Batch", command=submit)
    submit_button.grid(row=len(fields), columnspan=2, pady=(10, 0))
    apply_styles(submit_button)

def delete_medicine_batch_gui(conn):
    """GUI for deleting medicine batch"""
    prompt_window = tk.Toplevel()
    prompt_window.title("Enter Batch ID")
    prompt_window.geometry("300x150")
    prompt_window.config(bg=BG_COLOR)
    center_window(prompt_window)
    prompt_window.lift()
    prompt_window.attributes('-topmost', True)
    prompt_window.focus_force()
    prompt_window.after(100, lambda: prompt_window.attributes('-topmost', False))

    tk.Label(prompt_window, text="Enter Batch ID to delete:", bg=BG_COLOR).pack(pady=10)
    batch_id_entry = tk.Entry(prompt_window)
    batch_id_entry.pack(pady=5)
    apply_styles(batch_id_entry)

    def proceed():
        batch_id = batch_id_entry.get().strip()
        prompt_window.destroy()
        show_delete_window(batch_id)

    tk.Button(prompt_window, text="Submit", command=proceed).pack(pady=10)

    def show_delete_window(batch_id):
        delete_window = tk.Toplevel()
        delete_window.title("Delete Medicine Batch")
        delete_window.geometry("400x200")
        delete_window.config(bg=BG_COLOR)
        center_window(delete_window)
        delete_window.lift()
        delete_window.attributes('-topmost', True)
        delete_window.focus_force()
        delete_window.after(100, lambda: delete_window.attributes('-topmost', False))

        main_frame = tk.Frame(delete_window, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="Batch ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
        tk.Label(main_frame, text=batch_id, bg=BG_COLOR).grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        tk.Label(main_frame, text="Are you sure you want to delete this batch?", bg=BG_COLOR).grid(row=1, columnspan=2, pady=(10, 0))

        delete_button = tk.Button(main_frame, text="Delete", command=lambda: delete_medicine_batch(conn, batch_id))
        delete_button.grid(row=2, columnspan=2, pady=(10, 0))
        apply_styles(delete_button)

def view_medicine_batches_gui(conn):
    """GUI để xem thông tin các lô thuốc và lọc theo batchID, expiryDate, và medicineCost"""
    view_window = tk.Toplevel()
    view_window.title("View Medicine Batches")
    view_window.geometry("900x600")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)  # Đưa cửa sổ lên trên cùng
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Search frame
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=10)

    error_label = tk.Label(view_window, text="", fg="red", bg=BG_COLOR, font=("Arial", 10))
    error_label.pack()

    # Lọc theo BatchID, ExpiryDate, và Status
    tk.Label(search_frame, text="Batch ID:", bg=BG_COLOR).pack(side=tk.LEFT)
    batch_id_entry = tk.Entry(search_frame)
    batch_id_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(batch_id_entry)

    tk.Label(search_frame, text="Expiry Date:", bg=BG_COLOR).pack(side=tk.LEFT, padx=(10, 5))
    expiry_date_entry = tk.Entry(search_frame)
    expiry_date_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(expiry_date_entry)

    tk.Label(search_frame, text="Status:", bg=BG_COLOR).pack(side=tk.LEFT, padx=(10, 5))
    status_entry = tk.Entry(search_frame)
    status_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(status_entry)

    columns = ("BatchID", "MedicineID", "BatchNumber","Quantity","ImportDate","ExpiryDate","SupplierName","MedicineCost",'Status')
    tree = ttk.Treeview(view_window, columns=columns, show='headings')

    col_widths = [50, 100, 100, 80, 100,100,100,100]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def search():
        error_label.config(text="")
        tree.delete(*tree.get_children())
        batch_id = batch_id_entry.get().strip() or None
        expiry_date = expiry_date_entry.get().strip() or None
        status = status_entry.get().strip() or None

        success, result = search_medicine_batches(conn, batch_id, expiry_date, status)
        if success and result:
            for batch in result:
                tree.insert("", tk.END, values=(
                    batch["BatchID"],
                    batch["MedicineID"],
                    batch["BatchNumber"],
                    batch["Quantity"],
                    batch["ImportDate"],
                    batch["ExpiryDate"],
                    batch["SupplierName"],
                    batch["MedicineCost"],
                    batch["Status"]
                ))
        else:
            error_label.config(text="No batches found matching the criteria.")
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(search_frame, text="Search", command=search)
    apply_styles(search_btn)
    search_btn.pack(side=tk.LEFT, padx=10)

    view_window.after(100, search)

def adjust_medicine_batch_gui(conn):
    """GUI for adjusting medicine batch"""
    adjust_window = tk.Toplevel()
    adjust_window.title("Adjust Medicine Batch")
    adjust_window.geometry("400x250")
    adjust_window.config(bg=BG_COLOR)
    center_window(adjust_window)
    adjust_window.lift()
    adjust_window.attributes('-topmost', True)
    adjust_window.focus_force()
    adjust_window.after(100, lambda: adjust_window.attributes('-topmost', False))

    main_frame = tk.Frame(adjust_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Batch ID
    tk.Label(main_frame, text="Batch ID:", bg=BG_COLOR).pack(anchor="w", pady=5)
    batch_id_entry = tk.Entry(main_frame)
    batch_id_entry.pack(fill=tk.X, pady=5)
    apply_styles(batch_id_entry)

    # Adjust Quantity
    tk.Label(main_frame, text="Adjust Quantity:", bg=BG_COLOR).pack(anchor="w", pady=5)
    entry_adjust_quantity = tk.Entry(main_frame)
    entry_adjust_quantity.pack(fill=tk.X, pady=5)
    apply_styles(entry_adjust_quantity)

    # Result message
    result_label = tk.Label(main_frame, text="", bg=BG_COLOR, fg="red")
    result_label.pack(pady=10)

    def submit():
        batch_id = batch_id_entry.get().strip()
        try:
            quantity = int(entry_adjust_quantity.get().strip())
        except ValueError:
            result_label.config(text="❌ Please enter valid numeric values.")
            return

        success, message = adjust_medicine_quantity(conn, batch_id, quantity)
        if success:
            messagebox.showinfo("Success", message)
            adjust_window.destroy()
        else:
            result_label.config(text=message)
            adjust_window.lift()

    # Adjust button
    submit_btn = tk.Button(main_frame, text="Adjust", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

# Inventory GUI function
def add_inventory_gui(conn):
    """GUI for adding inventory"""
    inventory_window = tk.Toplevel()
    inventory_window.title("Add Inventory")
    inventory_window.geometry("400x300")
    inventory_window.config(bg=BG_COLOR)
    center_window(inventory_window)
    inventory_window.lift()
    inventory_window.attributes('-topmost', True)
    inventory_window.after(100, lambda: inventory_window.attributes('-topmost', False))

    main_frame = tk.Frame(inventory_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Labels and Entries
    tk.Label(main_frame, text="Item Name:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_item_name = tk.Entry(main_frame)
    entry_item_name.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_item_name)

    tk.Label(main_frame, text="Quantity:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_quantity = tk.Entry(main_frame)
    entry_quantity.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_quantity)

    tk.Label(main_frame, text="Unit:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
    entry_unit = tk.Entry(main_frame)
    entry_unit.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_unit)

    tk.Label(main_frame, text="Status:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
    entry_status = tk.Entry(main_frame)
    entry_status.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_unit)

    def submit():
        try:
            item_name = entry_item_name.get().strip()
            quantity = entry_quantity.get().strip()
            unit = entry_unit.get().strip()
            status = entry_status.get().strip()

            if not item_name or not unit or not quantity:
                raise ValueError("Item name, unit and quantity are required.")
            if int(quantity) < 0:
                raise ValueError("Quantity must be non-negative.")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            inventory_window.lift()
            return

        result = add_inventory_item(conn, item_name, quantity, unit, status)
        if result is None:
            messagebox.showerror("Error", "❌ Failed to add inventory item.")
        else:
            success, message = result
            if success:
                messagebox.showinfo("Success", message)
                inventory_window.destroy()
            else:
                messagebox.showerror("Error", message)
                inventory_window.lift()

    save_button = tk.Button(main_frame, text="Save", command=submit)
    apply_styles(save_button)
    save_button.grid(row=4, columnspan=2, pady=(10, 0))

# def update_inventory_gui(conn, inventory_id=None):
#     """GUI for updating inventory"""
#     update_window = tk.Toplevel()
#     update_window.title("Update Inventory")
#     update_window.geometry("400x350")
#     update_window.config(bg=BG_COLOR)
#     center_window(update_window)
#     update_window.lift()
#     update_window.attributes('-topmost', True)
#     update_window.after(100, lambda: update_window.attributes('-topmost', False))

#     # Main frame
#     main_frame = tk.Frame(update_window, bg=BG_COLOR)
#     main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

#     # Inventory ID
#     tk.Label(main_frame, text="Inventory ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
#     entry_inventory_id = tk.Entry(main_frame)
#     entry_inventory_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
#     apply_styles(entry_inventory_id)
#     if inventory_id:
#         entry_inventory_id.insert(0, str(inventory_id))

#     # Item Name (editable)
#     tk.Label(main_frame, text="Item Name:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
#     entry_item_name = tk.Entry(main_frame)
#     entry_item_name.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
#     apply_styles(entry_item_name)

#     # Quantity
#     tk.Label(main_frame, text="Quantity:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=5)
#     entry_quantity = tk.Entry(main_frame)
#     entry_quantity.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
#     apply_styles(entry_quantity)

#     # Unit
#     tk.Label(main_frame, text="Unit:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=5)
#     entry_unit = tk.Entry(main_frame)
#     entry_unit.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
#     apply_styles(entry_unit)

#     # Status
#     tk.Label(main_frame, text="Status:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=5)
#     entry_status = tk.Entry(main_frame)
#     entry_status.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
#     apply_styles(entry_unit)

    # # Load button
    # def load_inventory():
    #     inv_id = entry_inventory_id.get()
    #     if not inv_id:
    #         messagebox.showerror("Error", "Please enter an inventory ID.")
    #         return
        
    #     success, inventory_info = update_inventory_item(conn, inv_id, )
    #     if not success or not inventory_info:
    #         messagebox.showerror("Error", "No inventory item found with this ID.")
    #         return

    #     entry_item_name.delete(0, tk.END)
    #     entry_item_name.insert(0, inventory_info['ItemName'])
    #     entry_quantity.delete(0, tk.END)
    #     entry_quantity.insert(0, inventory_info['Quantity'])
    #     entry_unit.delete(0, tk.END)
    #     entry_unit.insert(0, inventory_info['Unit'])
    #     entry_status.delete(0, tk.END)
    #     entry_status.insert(0, inventory_info['Status'])

    # load_button = tk.Button(main_frame, text="Load Info", command=load_inventory)
    # apply_styles(load_button)
    # load_button.grid(row=4, columnspan=2, pady=(10, 0))

    # Save button
    # def save_inventory():
    #     item_name = entry_item_name.get().strip()
    #     quantity = entry_quantity.get().strip()
    #     unit = entry_unit.get().strip()

    #     # Gọi hàm cập nhật
    #     success, message = add_inventory_item(conn, item_name, quantity, unit, status)
        
    #     # Hiển thị kết quả
    #     if success:
    #         messagebox.showinfo("Success", message)
    #         update_window.lift()
    #         update_window.focus_force()
    #     else:
    #         messagebox.showerror("Error", message)
    #         update_window.lift()
    #         update_window.focus_force()


    # # Nút Save
    # save_button = tk.Button(main_frame, text="Save", command=save_inventory)
    # apply_styles(save_button)
    # save_button.grid(row=6, columnspan=2, pady=(10, 0))

    # main_frame.grid_columnconfigure(1, weight=1)


def disable_inventory_item_gui(conn, inventory_id):
    """GUI for disabling inventory item"""
    disable_window = tk.Toplevel()
    disable_window.title("Disable Inventory Item")
    disable_window.geometry("400x200")
    disable_window.config(bg=BG_COLOR)
    center_window(disable_window)
    disable_window.lift()
    disable_window.attributes('-topmost', True) # Keep on top of other windows
    disable_window.after(100, lambda: disable_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(disable_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Inventory ID (read-only)
    tk.Label(main_frame, text="Inventory ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    label_inventory_id = tk.Label(main_frame, text=inventory_id, bg=BG_COLOR)
    label_inventory_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

    # Confirmation message
    tk.Label(main_frame, text="Are you sure you want to disable this item?", bg=BG_COLOR).grid(row=1, columnspan=2, pady=(10, 0))

    # Disable button
    disable_button = tk.Button(main_frame, text="Disable", command=lambda: disable_inventory_item(conn, inventory_id))
    disable_button.grid(row=2, columnspan=2, pady=(10, 0))
    
    apply_styles(disable_button)

def view_inventory_gui(conn):
    """GUI for viewing inventory items"""
    view_window = tk.Toplevel()
    view_window.title("View Inventory")
    view_window.geometry("800x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Search frame
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=10)

    # Search by Item ID
    tk.Label(search_frame, text="Inventory ID:", bg=BG_COLOR).pack(side=tk.LEFT, padx=(10, 5))
    item_id_entry = tk.Entry(search_frame)
    item_id_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(item_id_entry)

    # Search by Item Name
    tk.Label(search_frame, text="Item Name:", bg=BG_COLOR).pack(side=tk.LEFT)
    item_name_entry = tk.Entry(search_frame)
    item_name_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(item_name_entry)

    # Search by Status
    tk.Label(search_frame, text="Status:", bg=BG_COLOR).pack(side=tk.LEFT, padx=(10, 5))
    status_entry = tk.Entry(search_frame)
    status_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(status_entry)

    # Treeview for displaying inventory
    columns = ("InventoryID", "ItemName", "Quantity", "Unit", "Status")
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')

    col_widths = [80,200, 80,80,100]
    for col, width in zip(columns,col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def search():
        item_name = item_name_entry.get().strip() or None
        item_id = item_id_entry.get().strip() or None

        success, result = search_inventory_item(conn, item_id, item_name)
        if success:
            tree.delete(*tree.get_children())
            for item in result:
                tree.insert("", tk.END, values=(
                    item["InventoryID"],
                    item["ItemName"],
                    item["Quantity"],
                    item["Unit"],
                    item["Status"]
                ))
        else:
            messagebox.showerror("Error", f"Failed to search inventory: {result}")
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(search_frame, text="Search", command=search)
    apply_styles(search_btn)
    search_btn.pack(side=tk.LEFT, padx=10)

    view_window.after(100, search)

def adjust_inventory_gui(conn):
    """GUI to adjust the quantity of an inventory item"""
    window = tk.Toplevel()
    window.title("Adjust Inventory Quantity")
    window.geometry("400x250")
    window.config(bg=BG_COLOR)
    center_window(window)
    window.lift()
    window.attributes('-topmost', True) # Keep on top of other windows
    window.after(100, lambda: window.attributes('-topmost', False))

    frame = tk.Frame(window, bg=BG_COLOR)
    frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Inventory ID
    tk.Label(frame, text="Inventory ID:", bg=BG_COLOR).pack(anchor="w")
    entry_id = tk.Entry(frame)
    entry_id.pack(fill=tk.X, pady=5)
    apply_styles(entry_id)

    # Quantity to adjust
    tk.Label(frame, text="Quantity to Adjust (+/-):", bg=BG_COLOR).pack(anchor="w")
    entry_qty = tk.Entry(frame)
    entry_qty.pack(fill=tk.X, pady=5)
    apply_styles(entry_qty)

    # Result message
    result_label = tk.Label(frame, text="", bg=BG_COLOR, fg="red")
    result_label.pack(pady=10)

    def submit():
        try:
            inventory_id = int(entry_id.get().strip())
            quantity = int(entry_qty.get().strip())
        except ValueError:
            result_label.config(text="❌ Please enter valid numeric values.")
            return

        success, message = adjust_inventory(conn, inventory_id, quantity)
        if success:
            messagebox.showinfo("Success", message)
            window.destroy()
        else:
            result_label.config(text=message)
            window.lift()

    # Submit Button
    submit_btn = tk.Button(frame, text="Adjust Quantity", command=submit)
    apply_styles(submit_btn)
    submit_btn.pack(pady=10)

# Insurance GUI function
def add_insurance_gui(conn):
    """GUI for adding insurance"""
    insurance_window = tk.Toplevel()
    insurance_window.title("Add Insurance")
    insurance_window.geometry("400x400")
    insurance_window.config(bg=BG_COLOR)
    center_window(insurance_window)
    insurance_window.lift()
    insurance_window.attributes('-topmost', True)
    insurance_window.after(100, lambda: insurance_window.attributes('-topmost', False))

    main_frame = tk.Frame(insurance_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Labels & Entry widgets
    labels = [
        "Patient ID:", "Insurance Provider:", "Policy Number:", "BHYT Card Number:",
        "Effective Date (YYYY-MM-DD):", "End Date (YYYY-MM-DD):", "Coverage Details:"
    ]
    entries = []
    for i, label in enumerate(labels):
        tk.Label(main_frame, text=label, bg=BG_COLOR).grid(row=i, column=0, sticky="e", pady=5)
        entry = tk.Entry(main_frame)
        entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
        apply_styles(entry)
        entries.append(entry)

    def validate_date(date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def submit():
        try:
            patient_id = entries[0].get().strip()
            insurance_provider = entries[1].get().strip()
            policy_number = entries[2].get().strip()
            bhyt_card_number = entries[3].get().strip()
            effective_date = entries[4].get().strip()
            end_date = entries[5].get().strip()
            coverage_details = entries[6].get().strip()

            if not insurance_provider or not policy_number or not effective_date or not end_date:
                raise ValueError("Required fields must not be empty.")
            if not validate_date(effective_date) or not validate_date(end_date):
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            insurance_window.lift()
            return

        result = add_insurance_record(conn, patient_id, insurance_provider, policy_number,
                                      bhyt_card_number, effective_date, end_date, coverage_details)
        if result is None:
            messagebox.showerror("Error", "❌ Failed to add insurance record.")
        else:
            success, msg = result
            if success:
                messagebox.showinfo("Success", msg)
                insurance_window.destroy()
            else:
                messagebox.showerror("Error", msg)
                insurance_window.lift()

    # Save button
    save_button = tk.Button(main_frame, text="Save", command=submit)
    save_button.grid(row=7, columnspan=2, pady=(10, 0))
    apply_styles(save_button)

def update_insurance_gui(conn):
    """GUI for updating insurance"""
    update_window = tk.Toplevel()
    update_window.title("Update Insurance")
    update_window.geometry("900x600")
    update_window.config(bg=BG_COLOR)
    center_window(update_window)
    update_window.lift()
    update_window.attributes('-topmost', True)
    update_window.focus_force()
    update_window.after(100, lambda: update_window.attributes('-topmost', False))

    main_frame = tk.Frame(update_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Insurance ID
    tk.Label(main_frame, text="Insurance ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=10)
    insurance_id_entry = tk.Entry(main_frame)
    insurance_id_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(insurance_id_entry)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=10)
    patient_id_entry = tk.Entry(main_frame)
    patient_id_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(patient_id_entry)

    # Provider
    tk.Label(main_frame, text="Provider:", bg=BG_COLOR).grid(row=2, column=0, sticky="e", pady=10)
    provider_entry = tk.Entry(main_frame)
    provider_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(provider_entry)

    # Policy Number
    tk.Label(main_frame, text="Policy Number:", bg=BG_COLOR).grid(row=3, column=0, sticky="e", pady=10)
    policy_no_entry = tk.Entry(main_frame)
    policy_no_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(policy_no_entry)

    # BHYT Card Number
    tk.Label(main_frame, text="BHYT Card Number:", bg=BG_COLOR).grid(row=4, column=0, sticky="e", pady=10)
    bhyt_no_entry = tk.Entry(main_frame)
    bhyt_no_entry.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(bhyt_no_entry)

    # Effective Date
    tk.Label(main_frame, text="Effective Date (YYYY-MM-DD):", bg=BG_COLOR).grid(row=5, column=0, sticky="e", pady=10)
    eff_date_entry = tk.Entry(main_frame)
    eff_date_entry.grid(row=5, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(eff_date_entry)

    # End Date
    tk.Label(main_frame, text="End Date (YYYY-MM-DD):", bg=BG_COLOR).grid(row=6, column=0, sticky="e", pady=10)
    end_date_entry = tk.Entry(main_frame)
    end_date_entry.grid(row=6, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(end_date_entry)

    # Coverage Details
    tk.Label(main_frame, text="Coverage Details:", bg=BG_COLOR).grid(row=7, column=0, sticky="e", pady=10)
    coverage_details_entry = tk.Entry(main_frame)
    coverage_details_entry.grid(row=7, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(coverage_details_entry)

    # Result message
    result_label = tk.Label(main_frame, text="", bg=BG_COLOR, fg="red")
    result_label.grid(row=3, columnspan=2, pady=10)

    def submit():
        insurance_id = insurance_id_entry.get().strip()
        patient_id = patient_id_entry.get().strip()
        provider = provider_entry.get().strip()
        policy_no = policy_no_entry.get().strip()
        bhyt_no = bhyt_no_entry.get().strip()
        eff_date = eff_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        coverage_details = coverage_details_entry.get().strip()

        # Attempt to update the insurance information
        success, message = update_insurance_record(conn, insurance_id, patient_id, provider, policy_no, bhyt_no, eff_date, end_date, coverage_details)
        if success:
            messagebox.showinfo("Success", message)
            update_window.destroy()
        else:
            messagebox.showerror("Error", message)
            update_window.lift()
            update_window.focus_force()

    # Save button
    save_button = tk.Button(main_frame, text="Save", command=submit)
    apply_styles(save_button)
    save_button.grid(row=8, columnspan=2, pady=10)

def delete_insurance_gui(conn):
    """GUI for deleting insurance"""
    prompt_window = tk.Toplevel()
    prompt_window.title("Enter Insurance ID")
    prompt_window.geometry("300x150")
    prompt_window.config(bg=BG_COLOR)
    center_window(prompt_window)
    prompt_window.lift()
    prompt_window.attributes('-topmost', True)
    prompt_window.focus_force()
    prompt_window.after(100, lambda: prompt_window.attributes('-topmost', False))

    tk.Label(prompt_window, text="Enter Insurance ID to delete:", bg=BG_COLOR).pack(pady=10)
    insurance_id_entry = tk.Entry(prompt_window)
    insurance_id_entry.pack(pady=5)
    apply_styles(insurance_id_entry)

    def proceed():
        insurance_id = insurance_id_entry.get().strip()
        success, message = delete_insurance_record(conn, insurance_id)
        if not success:
            messagebox.showerror("Error", message)
            prompt_window.lift()
            prompt_window.focus_force()
            return
        else:
            messagebox.showinfo("Success", message)
            prompt_window.destroy()
            show_delete_window(insurance_id)

    tk.Button(prompt_window, text="Submit", command=proceed).pack(pady=10)

    def show_delete_window(insurance_id):
        delete_window = tk.Toplevel()
        delete_window.title("Delete Insurance")
        delete_window.geometry("400x200")
        delete_window.config(bg=BG_COLOR)
        center_window(delete_window)
        delete_window.lift()
        delete_window.attributes('-topmost', True)
        delete_window.focus_force()
        delete_window.after(100, lambda: delete_window.attributes('-topmost', False))

        main_frame = tk.Frame(delete_window, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="Insurance ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
        tk.Label(main_frame, text=insurance_id, bg=BG_COLOR).grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        tk.Label(main_frame, text="Are you sure you want to delete this insurance?", bg=BG_COLOR).grid(
            row=1, columnspan=2, pady=(10, 0))

        delete_button = tk.Button(main_frame, text="Delete", command=lambda: delete_insurance_record(conn, insurance_id))
        delete_button.grid(row=2, columnspan=2, pady=(10, 0))
        apply_styles(delete_button)

def view_insurance_gui(conn):  
    """GUI to view and search insurance records"""
    view_window = tk.Toplevel()
    view_window.title("View Insurance Records")
    view_window.geometry("900x600")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True)
    view_window.after(100, lambda: view_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(view_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Search frame
    search_frame = tk.Frame(main_frame, bg=BG_COLOR)
    search_frame.pack(fill=tk.X, pady=10)

    # Patient ID entry
    tk.Label(search_frame, text="Patient ID:", bg=BG_COLOR).pack(side=tk.LEFT)
    patient_id_entry = tk.Entry(search_frame)
    patient_id_entry.pack(side=tk.LEFT, padx=5)
    apply_styles(patient_id_entry)

    # Treeview for displaying results
    columns = ("InsuranceRecordID", "PatientID", "InsuranceProvider", "PolicyNumber", "BHYTCardNumber", "EffectiveDate", "EndDate", "CoverageDetails")
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')

    col_widths = [100, 100, 150, 150, 100, 120, 120, 200]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def search():
        patient_id = patient_id_entry.get().strip() or None

        success, result = search_insurance(conn, patient_id)
        if success:
            tree.delete(*tree.get_children())
            for ins in result:
                tree.insert("", tk.END, values=(
                    ins["InsuranceRecordID"],
                    ins["PatientID"],
                    ins["InsuranceProvider"],
                    ins["PolicyNumber"],
                    ins["BHYTCardNumber"] or 'N/A',
                    ins["EffectiveDate"],
                    ins["EndDate"],
                    ins["CoverageDetails"]
                ))
        else:
            messagebox.showerror("Error", f"Failed to search insurance: {result}")
            view_window.lift()
            view_window.focus_force()

    search_btn = tk.Button(search_frame, text="Search", command=search)
    apply_styles(search_btn)
    search_btn.pack(side=tk.LEFT, padx=10)

    view_window.after(100, search)

def calculate_insurance_coverage_gui(conn):
    """GUI for calculating insurance coverage"""
    coverage_window = tk.Toplevel()
    coverage_window.title("Calculate Insurance Coverage")
    coverage_window.geometry("400x300")
    coverage_window.config(bg=BG_COLOR)
    center_window(coverage_window)

    # Main frame
    main_frame = tk.Frame(coverage_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(main_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    # Insurance ID
    tk.Label(main_frame, text="Insurance ID:", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_insurance_id = tk.Entry(main_frame)
    entry_insurance_id.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_insurance_id)

    # Calculate button
    calculate_button = tk.Button(main_frame, text="Calculate", command=lambda: calculate_insurance_coverage_gui(conn,
        entry_patient_id.get(), entry_insurance_id.get()))
    calculate_button.grid(row=2, columnspan=2, pady=(10, 0))

# Invoice GUI function
def add_invoice_gui(conn):
    """GUI for adding invoice"""
    invoice_window = tk.Toplevel()
    invoice_window.title("Add Invoice")
    invoice_window.geometry("400x300")
    invoice_window.config(bg=BG_COLOR)
    center_window(invoice_window)
    invoice_window.lift()
    invoice_window.attributes('-topmost', True) # Keep on top of other windows
    invoice_window.after(100, lambda: invoice_window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(invoice_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Patient ID
    tk.Label(main_frame, text="Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
    entry_patient_id = tk.Entry(main_frame)
    entry_patient_id.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_patient_id)

    # Total Amount
    tk.Label(main_frame, text="Total Amount (VND):", bg=BG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
    entry_total_amount = tk.Entry(main_frame)
    entry_total_amount.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
    apply_styles(entry_total_amount)

    # Save button
    save_button = tk.Button(main_frame, text="Save", command=lambda: add_invoice_gui(conn,
        entry_patient_id.get(), entry_total_amount.get()))
    save_button.grid(row=2, columnspan=2, pady=(10, 0))

def view_invoices_gui(conn):
    """GUI for viewing invoices"""
    view_window = tk.Toplevel()
    view_window.title("View Invoices")
    view_window.geometry("700x500")
    view_window.config(bg=BG_COLOR)
    center_window(view_window)
    view_window.lift()
    view_window.attributes('-topmost', True) # Keep on top of other windows
    view_window.after(100, lambda: view_window.attributes('-topmost', False))
    
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
                    text_area.insert(tk.END, f"Status: {invoice['PaymentStatus']}\n\n")
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

def view_and_print_invoices_by_patient(conn):
    """GUI to view and print invoices by Patient ID"""
    window = tk.Toplevel()
    window.title("View & Print Invoices by Patient")
    window.geometry("700x550")
    window.config(bg=BG_COLOR)
    center_window(window)
    window.lift()
    window.attributes('-topmost', True)
    window.after(100, lambda: window.attributes('-topmost', False))

    # Main frame
    main_frame = tk.Frame(window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Patient ID input
    input_frame = tk.Frame(main_frame, bg=BG_COLOR)
    input_frame.pack(fill=tk.X, pady=5)
    tk.Label(input_frame, text="Enter Patient ID:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", padx=5)
    entry_patient = tk.Entry(input_frame)
    entry_patient.grid(row=0, column=1, sticky="ew", padx=5)
    apply_styles(entry_patient)
    input_frame.grid_columnconfigure(1, weight=1)

    # Text area for results
    text_area = create_scrollable_text(main_frame, height=20, width=80)

    # Function to fetch invoices
    def fetch_invoices():
        patient_id = entry_patient.get().strip()
        if not patient_id.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid Patient ID.")
            return

        success, result = view_invoices(conn, patient_id)
        text_area.delete(1.0, tk.END)

        if success:
            if result:
                for invoice in result:
                    text_area.insert(tk.END, f"Invoice ID: {invoice['InvoiceID']}\n")
                    text_area.insert(tk.END, f"Patient ID: {invoice['PatientID']}\n")
                    text_area.insert(tk.END, f"Date: {invoice['InvoiceDate']}\n")
                    text_area.insert(tk.END, f"Amount: {invoice['TotalAmount']:.2f} VND\n")
                    text_area.insert(tk.END, f"Status: {invoice['PaymentStatus']}\n")
                    text_area.insert(tk.END, "-" * 40 + "\n")
            else:
                text_area.insert(tk.END, "No invoices found for this patient.\n")
        else:
            messagebox.showerror("Error", result)

    # Fetch button
    fetch_btn = tk.Button(main_frame, text="Fetch Invoices", command=fetch_invoices)
    apply_styles(fetch_btn)
    fetch_btn.pack(pady=10)

    # Print section
    print_frame = tk.Frame(main_frame, bg=BG_COLOR)
    print_frame.pack(pady=10, fill=tk.X)

    tk.Label(print_frame, text="Enter Invoice ID to Print:", bg=BG_COLOR).grid(row=0, column=0, sticky="e", padx=5)
    entry_invoice_id = tk.Entry(print_frame)
    entry_invoice_id.grid(row=0, column=1, sticky="ew", padx=5)
    apply_styles(entry_invoice_id)

    def print_invoice():
        invoice_id = entry_invoice_id.get().strip()
        if not invoice_id.isdigit():
            messagebox.showwarning("Invalid Input", "Please enter a valid Invoice ID.")
            return

        file_path = f"Invoice_{invoice_id}.pdf"
        success, msg = generate_invoice_pdf(conn, int(invoice_id), file_path)
        if success:
            messagebox.showinfo("Success", msg)
            try:
                os.startfile(file_path)  # Open PDF (on Windows)
            except:
                pass
        else:
            messagebox.showerror("Error", msg)

    print_btn = tk.Button(print_frame, text="Print Invoice", command=print_invoice)
    apply_styles(print_btn)
    print_btn.grid(row=0, column=2, padx=10)
    print_frame.grid_columnconfigure(1, weight=1)

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

def export_report_txt(report_title, report_period, content_widget):
    """Exports the content of a ScrolledText or Treeview widget to a TXT file."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title=f"Save {report_title}",
        initialfile=f"{report_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
    )
    if not file_path:
        return # User cancelled

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"--- {report_title} ---\n")
            f.write(f"Period: {report_period}\n")
            f.write("=" * (len(report_title) + 6) + "\n\n")

            if isinstance(content_widget, scrolledtext.ScrolledText):
                # For ScrolledText, get all content
                content = content_widget.get("1.0", tk.END)
                f.write(content)
            elif isinstance(content_widget, ttk.Treeview):
                # For Treeview, write headers and rows
                columns = content_widget['columns']
                # Write header, joining with a clear separator like Tab or multiple spaces
                f.write("\t".join(str(content_widget.heading(col)['text']) for col in columns) + "\n")
                f.write("-" * 80 + "\n") # Separator line
                # Write data rows
                for item_id in content_widget.get_children():
                    values = content_widget.item(item_id, 'values')
                    f.write("\t".join(str(v) for v in values) + "\n")
            else:
                 f.write("Error: Unsupported widget type for export.")

        messagebox.showinfo("Export Successful", f"Report exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export report: {e}")

def generate_financial_report_gui(conn):
    """GUI for generating and displaying financial reports"""
    report_window = tk.Toplevel()
    report_window.title("Financial Report")
    report_window.geometry("1000x700")
    report_window.config(bg=BG_COLOR)
    center_window(report_window)
    
    # Main container
    main_frame = tk.Frame(report_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title and date controls
    header_frame = tk.Frame(main_frame, bg=BG_COLOR)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    tk.Label(header_frame, text="Financial Report", font=TITLE_FONT, 
            bg=BG_COLOR, fg=ACCENT_COLOR).pack(side=tk.LEFT)
    
    # Date range selection
    date_frame = tk.Frame(header_frame, bg=BG_COLOR)
    date_frame.pack(side=tk.RIGHT)
    
    tk.Label(date_frame, text="From:", bg=BG_COLOR).grid(row=0, column=0)
    start_date_entry = DateEntry(date_frame, width=12, date_pattern='yyyy-mm-dd')
    start_date_entry.grid(row=0, column=1, padx=5)
    
    tk.Label(date_frame, text="To:", bg=BG_COLOR).grid(row=0, column=2)
    end_date_entry = DateEntry(date_frame, width=12, date_pattern='yyyy-mm-dd')
    end_date_entry.grid(row=0, column=3, padx=5)
    
    def generate_report():
        start_date = start_date_entry.get_date().strftime('%Y-%m-%d') if start_date_entry.get() else None
        end_date = end_date_entry.get_date().strftime('%Y-%m-%d') if end_date_entry.get() else None
        
        success, report_data = get_financial_report_data(conn, start_date, end_date)
        
        if not success:
            messagebox.showerror("Error", report_data)
            return
            
        # Clear previous content
        for widget in report_frame.winfo_children():
            widget.destroy()
            
        # Display report data
        notebook = ttk.Notebook(report_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 1. Summary tab
        summary_frame = tk.Frame(notebook, bg=BG_COLOR)
        notebook.add(summary_frame, text="Summary")
        
        # Summary data
        tk.Label(summary_frame, 
                text=f"Financial Summary ({report_data['date_range']['start']} to {report_data['date_range']['end']})",
                font=("Helvetica", 12, "bold"), bg=BG_COLOR).pack(pady=10)
        
        summary_data = [
            ("Total Revenue", f"${report_data['summary']['total_revenue']:,.2f}"),
            ("Paid Amount", f"${report_data['summary']['paid_amount']:,.2f}"),
            ("Pending Amount", f"${report_data['summary']['pending_amount']:,.2f}"),
            ("Invoice Count", report_data['summary']['invoice_count']),
            ("Average Invoice", f"${report_data['summary']['avg_invoice']:,.2f}")
        ]
        
        for label, value in summary_data:
            row = tk.Frame(summary_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(row, text=label, width=20, anchor=tk.W, bg=BG_COLOR).pack(side=tk.LEFT)
            tk.Label(row, text=value, bg=BG_COLOR).pack(side=tk.LEFT)
        
        # 2. Service Revenue tab
        service_frame = tk.Frame(notebook, bg=BG_COLOR)
        notebook.add(service_frame, text="Service Revenue")
        
        columns = ("Service", "Count", "Revenue")
        tree = ttk.Treeview(service_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER if col != "Service" else tk.W)
        
        for service in report_data['service_revenue']:
            tree.insert("", tk.END, values=(
                service['ServiceName'],
                service['service_count'],
                f"${service['total_revenue']:,.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 3. Insurance tab
        insurance_frame = tk.Frame(notebook, bg=BG_COLOR)
        notebook.add(insurance_frame, text="Insurance")
        
        insurance_data = [
            ("Insurance Claims", report_data['insurance_data']['insurance_count']),
            ("Total Covered", f"${report_data['insurance_data']['total_covered']:,.2f}"),
            ("Patient Responsibility", f"${report_data['insurance_data']['total_patient_responsibility']:,.2f}")
        ]
        
        for label, value in insurance_data:
            row = tk.Frame(insurance_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(row, text=label, width=20, anchor=tk.W, bg=BG_COLOR).pack(side=tk.LEFT)
            tk.Label(row, text=value, bg=BG_COLOR).pack(side=tk.LEFT)
        
        # 4. Trends tab (simple line chart)
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            trends_frame = tk.Frame(notebook, bg=BG_COLOR)
            notebook.add(trends_frame, text="Trends")
            
            dates = [row['day'].strftime('%m-%d') for row in report_data['daily_trend']]
            amounts = [float(row['daily_revenue']) for row in report_data['daily_trend']]
            
            fig = plt.Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(dates, amounts, marker='o')
            ax.set_title("Daily Revenue Trend")
            ax.set_ylabel("Revenue ($)")
            ax.grid(True)
            
            # Rotate date labels if many dates
            if len(dates) > 7:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            canvas = FigureCanvasTkAgg(fig, master=trends_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except ImportError:
            tk.Label(trends_frame, text="Matplotlib required for charts", bg=BG_COLOR).pack()
    
    # Report frame
    report_frame = tk.Frame(main_frame, bg=BG_COLOR)
    report_frame.pack(fill=tk.BOTH, expand=True)
    
    # Generate button
    generate_btn = tk.Button(header_frame, text="Generate Report", command=generate_report)
    apply_styles(generate_btn)
    generate_btn.pack(side=tk.RIGHT, padx=10)
    
    # Generate initial report
    report_window.after(100, generate_report)

def get_room_statistics_gui(conn):
    """GUI for displaying room utilization statistics"""
    stats_window = tk.Toplevel()
    stats_window.title("Room Utilization Report")
    stats_window.geometry("900x600")
    stats_window.config(bg=BG_COLOR)
    center_window(stats_window)
    
    # Main container
    main_frame = tk.Frame(stats_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    tk.Label(main_frame, text="Room Utilization Statistics", 
            font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0, 20))
    
    # Get data
    success, stats_data = get_room_utilization_stats(conn)
    if not success:
        messagebox.showerror("Error", stats_data)
        stats_window.destroy()
        return
    
    # Notebook for multiple tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # 1. Overall Stats tab
    overall_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(overall_frame, text="Overview")
    
    overall_stats = [
        ("Total Rooms", stats_data['overall']['total_rooms']),
        ("Occupied Rooms", f"{stats_data['overall']['occupied_rooms']} ({stats_data['overall']['occupied_rooms']/stats_data['overall']['total_rooms']*100:.1f}%)"),
        ("Available Rooms", stats_data['overall']['available_rooms']),
        ("Maintenance Rooms", stats_data['overall']['maintenance_rooms']),
        ("Average Stay Duration", f"{stats_data['stay_stats']['avg_stay_days']:.1f} days")
    ]
    
    for label, value in overall_stats:
        row = tk.Frame(overall_frame, bg=BG_COLOR)
        row.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(row, text=label, width=25, anchor=tk.W, bg=BG_COLOR).pack(side=tk.LEFT)
        tk.Label(row, text=value, bg=BG_COLOR).pack(side=tk.LEFT)
    
    # 2. Department Stats tab
    dept_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(dept_frame, text="By Department")
    
    columns = ("Department", "Total Rooms", "Occupied", "Occupancy Rate")
    tree = ttk.Treeview(dept_frame, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor=tk.CENTER if col != "Department" else tk.W)
    
    for dept in stats_data['by_department']:
        tree.insert("", tk.END, values=(
            dept['DepartmentName'],
            dept['total_rooms'],
            dept['occupied'],
            f"{dept['occupancy_rate']}%"
        ))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 3. Revenue by Type tab
    revenue_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(revenue_frame, text="Revenue by Type")
    
    columns = ("Room Type", "Room Count", "Total Revenue")
    tree = ttk.Treeview(revenue_frame, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor=tk.CENTER if col != "Room Type" else tk.W)
    
    for room_type in stats_data['revenue_by_type']:
        tree.insert("", tk.END, values=(
            room_type['TypeName'],
            room_type['room_count'],
            f"${room_type['total_revenue']:,.2f}" if room_type['total_revenue'] else "$0.00"
        ))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add export button
    def export_to_csv():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save report as CSV"
        )
        if file_path:
            try:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write overall stats
                    writer.writerow(["Room Utilization Report - Overall Statistics"])
                    for label, value in overall_stats:
                        writer.writerow([label, value])
                    
                    writer.writerow([])
                    writer.writerow(["By Department"])
                    writer.writerow(columns[:4])  # Department columns
                    for dept in stats_data['by_department']:
                        writer.writerow([
                            dept['DepartmentName'],
                            dept['total_rooms'],
                            dept['occupied'],
                            f"{dept['occupancy_rate']}%"
                        ])
                    
                    writer.writerow([])
                    writer.writerow(["Revenue by Room Type"])
                    writer.writerow(columns)  # Revenue columns
                    for room_type in stats_data['revenue_by_type']:
                        writer.writerow([
                            room_type['TypeName'],
                            room_type['room_count'],
                            f"${room_type['total_revenue']:,.2f}" if room_type['total_revenue'] else "$0.00"
                        ])
                
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    export_btn = tk.Button(main_frame, text="Export to CSV", command=export_to_csv)
    apply_styles(export_btn)
    export_btn.pack(pady=10)

def generate_statistics_gui(conn):
    """GUI for generating hospital statistics report"""
    stats_window = tk.Toplevel()
    stats_window.title("Hospital Statistics Report")
    stats_window.geometry("1000x700")
    stats_window.config(bg=BG_COLOR)
    center_window(stats_window)
    
    # Main container
    main_frame = tk.Frame(stats_window, bg=BG_COLOR)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    tk.Label(main_frame, text="Hospital Statistics Report", 
            font=TITLE_FONT, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0, 20))
    
    # Get data
    success, stats_data = get_hospital_statistics(conn)
    if not success:
        messagebox.showerror("Error", stats_data)
        stats_window.destroy()
        return
    
    # Notebook for multiple tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # 1. Patient Demographics tab
    patient_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(patient_frame, text="Patient Demographics")
    
    patient_stats = [
        ("Total Patients", stats_data['patient_demographics']['total_patients']),
        ("Male Patients", f"{stats_data['patient_demographics']['male_patients']} ({stats_data['patient_demographics']['male_patients']/stats_data['patient_demographics']['total_patients']*100:.1f}%)"),
        ("Female Patients", f"{stats_data['patient_demographics']['female_patients']} ({stats_data['patient_demographics']['female_patients']/stats_data['patient_demographics']['total_patients']*100:.1f}%)"),
        ("Other Gender", f"{stats_data['patient_demographics']['other_patients']} ({stats_data['patient_demographics']['other_patients']/stats_data['patient_demographics']['total_patients']*100:.1f}%)"),
        ("Average Age", f"{stats_data['patient_demographics']['avg_age']:.1f} years")
    ]
    
    for label, value in patient_stats:
        row = tk.Frame(patient_frame, bg=BG_COLOR)
        row.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(row, text=label, width=25, anchor=tk.W, bg=BG_COLOR).pack(side=tk.LEFT)
        tk.Label(row, text=value, bg=BG_COLOR).pack(side=tk.LEFT)
    
    # 2. Doctor Productivity tab
    doctor_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(doctor_frame, text="Doctor Productivity")
    
    columns = ("Doctor", "Appointments", "Prescriptions", "Admissions")
    tree = ttk.Treeview(doctor_frame, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor=tk.CENTER if col != "Doctor" else tk.W)
    
    for doctor in stats_data['doctor_productivity']:
        tree.insert("", tk.END, values=(
            doctor['DoctorName'],
            doctor['appointment_count'],
            doctor['prescription_count'],
            doctor['admission_count']
        ))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 3. Service Utilization tab
    service_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(service_frame, text="Service Utilization")
    
    columns = ("Service", "Count", "Revenue")
    tree = ttk.Treeview(service_frame, columns=columns, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor=tk.CENTER if col != "Service" else tk.W)
    
    for service in stats_data['service_utilization']:
        tree.insert("", tk.END, values=(
            service['ServiceName'],
            service['service_count'],
            f"${service['total_revenue']:,.2f}"
        ))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 4. Appointment Metrics tab
    appt_frame = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(appt_frame, text="Appointment Metrics")
    
    appt_stats = [
        ("Total Appointments", stats_data['appointment_metrics']['total_appointments']),
        ("Completed", f"{stats_data['appointment_metrics']['completed']} ({stats_data['appointment_metrics']['completed']/stats_data['appointment_metrics']['total_appointments']*100:.1f}%)"),
        ("Cancelled", f"{stats_data['appointment_metrics']['cancelled']} ({stats_data['appointment_metrics']['cancelled']/stats_data['appointment_metrics']['total_appointments']*100:.1f}%)"),
        ("Scheduled", f"{stats_data['appointment_metrics']['scheduled']} ({stats_data['appointment_metrics']['scheduled']/stats_data['appointment_metrics']['total_appointments']*100:.1f}%)"),
        ("Average Duration", f"{stats_data['appointment_metrics']['avg_duration_minutes']:.1f} minutes")
    ]
    
    for label, value in appt_stats:
        row = tk.Frame(appt_frame, bg=BG_COLOR)
        row.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(row, text=label, width=25, anchor=tk.W, bg=BG_COLOR).pack(side=tk.LEFT)
        tk.Label(row, text=value, bg=BG_COLOR).pack(side=tk.LEFT)
    
    # Refresh button
    def refresh_data():
        success, new_stats_data = get_hospital_statistics(conn)
        if success:
            # Update all views with new data
            update_statistics_views(new_stats_data)
        else:
            messagebox.showerror("Error", new_stats_data)
    
    refresh_btn = tk.Button(main_frame, text="Refresh Data", command=refresh_data)
    apply_styles(refresh_btn)
    refresh_btn.pack(pady=10)
    
    def update_statistics_views(new_data):
        """Helper function to update all views with fresh data"""
        # Update patient demographics
        for i, (label, _) in enumerate(patient_stats):
            new_value = ""
            if label == "Total Patients":
                new_value = new_data['patient_demographics']['total_patients']
            elif label == "Male Patients":
                total = new_data['patient_demographics']['total_patients']
                male = new_data['patient_demographics']['male_patients']
                new_value = f"{male} ({male/total*100:.1f}%)"
            elif label == "Female Patients":
                total = new_data['patient_demographics']['total_patients']
                female = new_data['patient_demographics']['female_patients']
                new_value = f"{female} ({female/total*100:.1f}%)"
            elif label == "Other Gender":
                total = new_data['patient_demographics']['total_patients']
                other = new_data['patient_demographics']['other_patients']
                new_value = f"{other} ({other/total*100:.1f}%)"
            elif label == "Average Age":
                new_value = f"{new_data['patient_demographics']['avg_age']:.1f} years"
            
            # Update the label in the frame
            patient_frame.winfo_children()[i].winfo_children()[1].config(text=new_value)
        
        # Update doctor productivity
        tree = doctor_frame.winfo_children()[0]
        tree.delete(*tree.get_children())
        for doctor in new_data['doctor_productivity']:
            tree.insert("", tk.END, values=(
                doctor['DoctorName'],
                doctor['appointment_count'],
                doctor['prescription_count'],
                doctor['admission_count']
            ))
        
        # Update service utilization
        tree = service_frame.winfo_children()[0]
        tree.delete(*tree.get_children())
        for service in new_data['service_utilization']:
            tree.insert("", tk.END, values=(
                service['ServiceName'],
                service['service_count'],
                f"${service['total_revenue']:,.2f}"
            ))
        
        # Update appointment metrics
        for i, (label, _) in enumerate(appt_stats):
            new_value = ""
            if label == "Total Appointments":
                new_value = new_data['appointment_metrics']['total_appointments']
            elif label == "Completed":
                total = new_data['appointment_metrics']['total_appointments']
                completed = new_data['appointment_metrics']['completed']
                new_value = f"{completed} ({completed/total*100:.1f}%)"
            elif label == "Cancelled":
                total = new_data['appointment_metrics']['total_appointments']
                cancelled = new_data['appointment_metrics']['cancelled']
                new_value = f"{cancelled} ({cancelled/total*100:.1f}%)"
            elif label == "Scheduled":
                total = new_data['appointment_metrics']['total_appointments']
                scheduled = new_data['appointment_metrics']['scheduled']
                new_value = f"{scheduled} ({scheduled/total*100:.1f}%)"
            elif label == "Average Duration":
                new_value = f"{new_data['appointment_metrics']['avg_duration_minutes']:.1f} minutes"
            
            # Update the label in the frame
            appt_frame.winfo_children()[i].winfo_children()[1].config(text=new_value)

def change_password_gui(conn, username):
    """GUI for changing password"""
    change_window = tk.Toplevel()
    change_window.title("Change Password")
    change_window.geometry("400x300")
    change_window.config(bg=BG_COLOR)
    center_window(change_window)
    change_window.lift()
    change_window.attributes('-topmost', True) # Keep on top of other windows
    
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
            change_window.lift()
            change_window.focus_force()

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

if __name__ == "__main__":
    main()