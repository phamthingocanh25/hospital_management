# core_logic
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
            pdf.add_font('DejaVu', '', 'C:\\DMS\\prj_0205\\DejaVuSans.ttf', uni=True)
            pdf.add_font('DejaVu', 'B', 'C:\\DMS\\prj_0205\\DejaVuSans-Bold.ttf', uni=True)
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

#GUI
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
