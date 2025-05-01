-- Drop the database if it exists to ensure a clean start (Use with caution in production!)
DROP DATABASE IF EXISTS hospitalmanagementsystem;

-- Create the database
CREATE DATABASE hospitalmanagementsystem;

-- Select the database to use
USE hospitalmanagementsystem;

-- Table Creation Order: Start with tables that don't have foreign keys or whose FKs reference tables created earlier.

-- Bảng Khoa (Departments)
CREATE TABLE Departments (
    DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL UNIQUE COMMENT 'Tên khoa phòng (VD: Khoa Nội, Khoa Ngoại)'
) COMMENT = 'Lưu trữ danh sách các khoa trong bệnh viện';

-- Bảng Loại phòng (RoomTypes)
CREATE TABLE RoomTypes (
    RoomTypeID INT AUTO_INCREMENT PRIMARY KEY,
    TypeName VARCHAR(50) NOT NULL UNIQUE COMMENT 'Tên loại phòng (Standard, VIP, ICU)',
    BaseCost DECIMAL(12, 2) NOT NULL CHECK (BaseCost >= 0) COMMENT 'Chi phí cơ bản mỗi ngày cho loại phòng này',
    Description TEXT NULL COMMENT 'Mô tả thêm về loại phòng (tiện nghi, etc.)'
) COMMENT = 'Định nghĩa các loại phòng bệnh và chi phí cơ bản';

-- Bảng Bệnh nhân (Patients)
CREATE TABLE Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    PatientName VARCHAR(100) NOT NULL,
    DateOfBirth DATE NULL,
    Gender ENUM('M', 'F', 'O') NULL COMMENT 'M: Male, F: Female, O: Other',
    Address VARCHAR(255) NULL,
    PhoneNumber VARCHAR(20) NULL UNIQUE COMMENT 'Số điện thoại nên là duy nhất'
) COMMENT = 'Thông tin cơ bản của bệnh nhân';

-- Bảng Bác sĩ (Doctors)
CREATE TABLE Doctors (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    DoctorName VARCHAR(100) NOT NULL,
    Specialty VARCHAR(100) NULL COMMENT 'Chuyên khoa của bác sĩ',
    DepartmentID INT NULL COMMENT 'Khoa mà bác sĩ thuộc về',
    DoctorUser VARCHAR(50) UNIQUE COMMENT 'Tên đăng nhập liên kết với tài khoản user (nếu có)',
    PhoneNumber VARCHAR(20) NULL UNIQUE,
    Email VARCHAR(100) NULL UNIQUE,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
        ON DELETE SET NULL -- Nếu xóa khoa, bác sĩ không thuộc khoa nào nhưng vẫn tồn tại
        ON UPDATE CASCADE
) COMMENT = 'Thông tin chi tiết về các bác sĩ';

-- Bảng Thuốc (Medicine)
CREATE TABLE Medicine (
    MedicineID INT AUTO_INCREMENT PRIMARY KEY,
    MedicineName VARCHAR(150) NOT NULL UNIQUE COMMENT 'Tên thuốc',
    Unit VARCHAR(50) DEFAULT 'Viên' COMMENT 'Đơn vị tính (Viên, Lọ, Tuýp, Hộp)',
    Quantity INT NOT NULL DEFAULT 0 CHECK (Quantity >= 0) COMMENT 'Số lượng tồn kho',
    MedicineCost DECIMAL(10, 2) NOT NULL CHECK (MedicineCost >= 0) COMMENT 'Giá mỗi đơn vị thuốc'
) COMMENT = 'Quản lý kho thuốc';

-- Bảng Kho vật tư (Inventory)
CREATE TABLE Inventory (
    InventoryID INT AUTO_INCREMENT PRIMARY KEY,
    ItemName VARCHAR(150) NOT NULL UNIQUE COMMENT 'Tên vật tư/thiết bị',
    Quantity INT NOT NULL DEFAULT 0 CHECK (Quantity >= 0) COMMENT 'Số lượng tồn kho',
    Unit VARCHAR(50) DEFAULT 'Cái' COMMENT 'Đơn vị tính (Cái, Bộ, Hộp)',
    Status VARCHAR(50) DEFAULT 'Available' COMMENT 'Trạng thái vật tư (Available, Low Stock, Out of Stock)'
) COMMENT = 'Quản lý kho vật tư, thiết bị y tế';

-- Bảng Tài khoản Người dùng (users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL COMMENT 'Store hashed passwords only!',
    role ENUM('admin', 'doctor', 'receptionist', 'accountant') NOT NULL,
    FullName VARCHAR(100) NULL,
    Email VARCHAR(100) NULL UNIQUE,
    IsActive BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT = 'Quản lý tài khoản đăng nhập hệ thống';

-- Bảng Hóa đơn (Invoices) - Added PaymentStatus
CREATE TABLE Invoices (
    InvoiceID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NULL COMMENT 'ID bệnh nhân liên kết (NULL nếu bệnh nhân bị xóa)',
    InvoiceDate DATE NOT NULL COMMENT 'Ngày xuất hóa đơn',
    RoomCost DECIMAL(12, 2) DEFAULT 0.00 COMMENT 'Chi phí phòng bệnh (nếu có)',
    MedicineCost DECIMAL(12, 2) DEFAULT 0.00 COMMENT 'Chi phí thuốc (nếu có)',
    ServiceCost DECIMAL(12, 2) DEFAULT 0.00 COMMENT 'Chi phí dịch vụ (xét nghiệm, khám,...)',
    TotalAmount DECIMAL(14, 2) NOT NULL COMMENT 'Tổng số tiền cần thanh toán (sau bảo hiểm, giảm giá)',
    AmountPaid DECIMAL(14, 2) DEFAULT 0.00 COMMENT 'Số tiền đã thanh toán',
    PaymentStatus VARCHAR(20) NOT NULL DEFAULT 'Unpaid' COMMENT 'Trạng thái thanh toán (Unpaid, Partially Paid, Paid, Cancelled)',
    IsBHYTApplied BOOLEAN DEFAULT FALSE COMMENT 'Đã áp dụng BHYT hay chưa?',
    Notes TEXT NULL COMMENT 'Ghi chú thêm về hóa đơn',

    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
        ON DELETE SET NULL -- Giữ lại hóa đơn nếu bệnh nhân bị xóa
        ON UPDATE CASCADE,

    CHECK (TotalAmount >= 0),
    CHECK (RoomCost >= 0),
    CHECK (MedicineCost >= 0),
    CHECK (ServiceCost >= 0),
    CHECK (AmountPaid >= 0)
) COMMENT = 'Lưu trữ thông tin hóa đơn chi tiết của bệnh nhân';

-- Bảng Dịch vụ (Services) - Modified to link optionally to Invoice
CREATE TABLE Services (
    ServiceID INT AUTO_INCREMENT PRIMARY KEY,
    ServiceName VARCHAR(150) NOT NULL COMMENT 'Tên dịch vụ (Xét nghiệm máu, Chụp X-quang, Khám chuyên khoa)',
    ServiceCode VARCHAR(50) UNIQUE COMMENT 'Mã dịch vụ (tùy chọn, để dễ tra cứu)',
    ServiceCost DECIMAL(10, 2) NOT NULL CHECK (ServiceCost >= 0) COMMENT 'Chi phí dịch vụ',
    Description TEXT NULL COMMENT 'Mô tả chi tiết dịch vụ'
) COMMENT = 'Danh mục các dịch vụ y tế bệnh viện cung cấp và chi phí';

-- Bảng Chi tiết Dịch vụ sử dụng (PatientServices) - Linking Patients, Services, and optionally Invoices
CREATE TABLE PatientServices (
    PatientServiceID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    ServiceID INT NOT NULL,
    DoctorID INT NULL COMMENT 'Bác sĩ chỉ định hoặc thực hiện dịch vụ (nếu có)',
    ServiceDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Ngày giờ thực hiện dịch vụ',
    Quantity INT DEFAULT 1 CHECK (Quantity > 0),
    CostAtTime DECIMAL(10, 2) NOT NULL COMMENT 'Chi phí dịch vụ tại thời điểm thực hiện',
    InvoiceID INT NULL COMMENT 'Liên kết với hóa đơn sau khi thanh toán',
    Notes TEXT NULL,

    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID) ON DELETE RESTRICT ON UPDATE CASCADE, -- Không xóa dịch vụ gốc nếu đã có người dùng
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID) ON DELETE SET NULL ON UPDATE CASCADE
) COMMENT = 'Ghi lại các dịch vụ cụ thể đã cung cấp cho bệnh nhân';


-- Bảng Phòng bệnh (Rooms)
CREATE TABLE Rooms (
    RoomID INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID định danh duy nhất cho mỗi phòng',
    RoomNumber VARCHAR(20) NOT NULL UNIQUE COMMENT 'Số phòng hoặc mã định danh phòng (VD: A101, B205)',
    RoomTypeID INT NOT NULL COMMENT 'Khóa ngoại liên kết đến loại phòng',
    DepartmentID INT NOT NULL COMMENT 'Phòng thuộc khoa nào',
    Status VARCHAR(50) DEFAULT 'Available' NOT NULL COMMENT 'Trạng thái phòng (Available, Occupied, Maintenance, Cleaning)',
    CurrentPatientID INT NULL COMMENT 'ID bệnh nhân đang ở phòng (NULL nếu trống)',
    LastCleanedDate DATE NULL COMMENT 'Ngày dọn dẹp cuối cùng',

    FOREIGN KEY (RoomTypeID) REFERENCES RoomTypes(RoomTypeID)
        ON DELETE RESTRICT -- Không cho xóa loại phòng nếu còn phòng thuộc loại đó
        ON UPDATE CASCADE,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
        ON DELETE RESTRICT -- Không cho xóa khoa nếu còn phòng thuộc khoa đó
        ON UPDATE CASCADE,
    FOREIGN KEY (CurrentPatientID) REFERENCES Patients(PatientID)
        ON DELETE SET NULL -- Nếu bệnh nhân xuất viện/xóa, phòng trống ra
        ON UPDATE CASCADE
) COMMENT = 'Lưu thông tin chi tiết của từng phòng bệnh cụ thể';

-- Bảng Liên hệ Khẩn cấp (EmergencyContact)
CREATE TABLE EmergencyContact (
    ContactID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    ContactName VARCHAR(100) NOT NULL,
    Relationship VARCHAR(50) NULL COMMENT 'Mối quan hệ với bệnh nhân (Vợ, Chồng, Con, Bố, Mẹ...)',
    PhoneNumber VARCHAR(20) NOT NULL,
    Address VARCHAR(255) NULL,

    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE ON UPDATE CASCADE
) COMMENT = 'Thông tin liên hệ khẩn cấp của bệnh nhân';

-- Bảng Bảo hiểm (Insurance) - Using the detailed structure
CREATE TABLE Insurance (
    InsuranceRecordID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    InsuranceProvider VARCHAR(150) NOT NULL COMMENT 'Tên nhà cung cấp bảo hiểm (BHYT, PVI, Bảo Việt, Prudential...)',
    PolicyNumber VARCHAR(50) NOT NULL COMMENT 'Số hợp đồng/Số thẻ bảo hiểm',
    BHYTCardNumber VARCHAR(20) NULL UNIQUE COMMENT 'Mã số thẻ BHYT (nếu có, riêng cho VN)',
    EffectiveDate DATE NOT NULL COMMENT 'Ngày bắt đầu hiệu lực',
    EndDate DATE NOT NULL COMMENT 'Ngày hết hạn hiệu lực',
    CoverageDetails TEXT NULL COMMENT 'Mô tả phạm vi bảo hiểm chung',
    -- Removed CoveragePercent as it's too simplistic. Coverage varies by service type.
    -- Coverage should ideally be checked dynamically against Service Costs & Insurance rules.

    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
        ON DELETE CASCADE -- Nếu xóa bệnh nhân, xóa luôn thông tin bảo hiểm
        ON UPDATE CASCADE

    -- CHECK (CoveragePercent >= 0 AND CoveragePercent <= 100) -- Removed this check
) COMMENT = 'Lưu thông tin các gói bảo hiểm của bệnh nhân';

-- Bảng Lịch hẹn (Appointments)
CREATE TABLE Appointments (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    AppointmentDate DATE NOT NULL,
    AppointmentTime TIME NOT NULL,
    Reason TEXT NULL COMMENT 'Lý do khám/Tình trạng sơ bộ',
    Status VARCHAR(20) DEFAULT 'Scheduled' NOT NULL COMMENT 'Trạng thái (Scheduled, Completed, Cancelled, No Show)',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE CASCADE ON UPDATE CASCADE, -- Or RESTRICT depending on policy

    UNIQUE KEY uk_appointment_slot (DoctorID, AppointmentDate, AppointmentTime) COMMENT 'Đảm bảo bác sĩ không bị trùng lịch tại cùng thời điểm'
) COMMENT = 'Quản lý lịch hẹn khám của bệnh nhân với bác sĩ';


-- Bảng Đơn thuốc (Prescription)
CREATE TABLE Prescription (
    PrescriptionID INT AUTO_INCREMENT PRIMARY KEY,
    AppointmentID INT NULL COMMENT 'Liên kết với cuộc hẹn (nếu có)',
    PatientID INT NOT NULL COMMENT 'Bệnh nhân nhận đơn',
    DoctorID INT NOT NULL COMMENT 'Bác sĩ kê đơn',
    PrescriptionDate DATE NOT NULL COMMENT 'Ngày kê đơn thuốc',
    Diagnosis TEXT NULL COMMENT 'Chẩn đoán liên quan đến đơn thuốc',
    Notes TEXT NULL COMMENT 'Ghi chú của bác sĩ cho đơn thuốc',

    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT ON UPDATE CASCADE -- Không xóa bác sĩ nếu đã kê đơn

) COMMENT = 'Thông tin chung về một đơn thuốc';

-- Bảng Chi tiết Đơn thuốc (PrescriptionDetails) - Links Prescription with Medicine
CREATE TABLE PrescriptionDetails (
    PrescriptionDetailID INT AUTO_INCREMENT PRIMARY KEY,
    PrescriptionID INT NOT NULL,
    MedicineID INT NOT NULL,
    Dosage VARCHAR(255) NOT NULL COMMENT 'Liều lượng (VD: 500mg)',
    Frequency VARCHAR(100) NOT NULL COMMENT 'Tần suất (VD: 2 lần/ngày, sáng 1 viên, tối 1 viên)',
    Duration VARCHAR(100) NULL COMMENT 'Thời gian sử dụng (VD: 7 ngày, 1 tháng)',
    Instruction TEXT NULL COMMENT 'Hướng dẫn sử dụng thêm (VD: Uống sau ăn)',
    QuantityPrescribed INT NOT NULL CHECK (QuantityPrescribed > 0) COMMENT 'Số lượng thuốc được kê',

    FOREIGN KEY (PrescriptionID) REFERENCES Prescription(PrescriptionID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID) ON DELETE RESTRICT ON UPDATE CASCADE -- Không xóa thuốc nếu đã được kê
) COMMENT = 'Chi tiết các loại thuốc trong một đơn thuốc';


-- Create Indexes for Performance Optimization

-- Patients
CREATE INDEX idx_patient_name ON Patients(PatientName);
CREATE INDEX idx_patient_phone ON Patients(PhoneNumber);

-- Doctors
CREATE INDEX idx_doctor_name ON Doctors(DoctorName);
CREATE INDEX idx_doctor_dept ON Doctors(DepartmentID);
CREATE INDEX idx_doctor_user ON Doctors(DoctorUser);

-- Appointments
CREATE INDEX idx_appointment_patient ON Appointments(PatientID);
CREATE INDEX idx_appointment_doctor ON Appointments(DoctorID);
CREATE INDEX idx_appointment_date ON Appointments(AppointmentDate);
CREATE INDEX idx_appointment_status ON Appointments(Status);

-- Invoices
CREATE INDEX idx_invoice_patient ON Invoices(PatientID);
CREATE INDEX idx_invoice_date ON Invoices(InvoiceDate);
CREATE INDEX idx_invoice_payment_status ON Invoices(PaymentStatus);

-- Insurance
CREATE INDEX idx_insurance_patient ON Insurance(PatientID);
CREATE INDEX idx_insurance_policy ON Insurance(PolicyNumber);
CREATE INDEX idx_insurance_end_date ON Insurance(EndDate);

-- EmergencyContact
CREATE INDEX idx_emergencycontact_patient ON EmergencyContact(PatientID);

-- Inventory
CREATE INDEX idx_inventory_itemname ON Inventory(ItemName);

-- Rooms
CREATE INDEX idx_rooms_status ON Rooms(Status);
CREATE INDEX idx_rooms_department ON Rooms(DepartmentID);
CREATE INDEX idx_rooms_type ON Rooms(RoomTypeID);
CREATE INDEX idx_rooms_patient ON Rooms(CurrentPatientID);

-- Medicine
CREATE INDEX idx_medicine_name ON Medicine(MedicineName);

-- Services
CREATE INDEX idx_services_name ON Services(ServiceName);
CREATE INDEX idx_services_code ON Services(ServiceCode);

-- PatientServices
CREATE INDEX idx_patientservice_patient ON PatientServices(PatientID);
CREATE INDEX idx_patientservice_service ON PatientServices(ServiceID);
CREATE INDEX idx_patientservice_invoice ON PatientServices(InvoiceID);
CREATE INDEX idx_patientservice_date ON PatientServices(ServiceDate);

-- Prescription
CREATE INDEX idx_prescription_patient ON Prescription(PatientID);
CREATE INDEX idx_prescription_doctor ON Prescription(DoctorID);
CREATE INDEX idx_prescription_date ON Prescription(PrescriptionDate);
CREATE INDEX idx_prescription_appointment ON Prescription(AppointmentID);

-- PrescriptionDetails
CREATE INDEX idx_prescriptiondetail_prescription ON PrescriptionDetails(PrescriptionID);
CREATE INDEX idx_prescriptiondetail_medicine ON PrescriptionDetails(MedicineID);

-- Users
CREATE INDEX idx_user_role ON users(role);
CREATE INDEX idx_user_email ON users(Email);


-- Advanced Database Objects (Views, Stored Procedures, Functions, Triggers)

-- 1. Views
DROP VIEW IF EXISTS vw_TodaysAppointments;
CREATE VIEW vw_TodaysAppointments AS
SELECT
    a.AppointmentID,
    d.DoctorName,
    p.PatientName,
    p.PhoneNumber AS PatientPhone,
    a.AppointmentDate,
    a.AppointmentTime,
    a.Status AS AppointmentStatus,
    a.Reason
FROM Appointments a
JOIN Doctors d ON a.DoctorID = d.DoctorID
JOIN Patients p ON a.PatientID = p.PatientID
WHERE a.AppointmentDate = CURDATE()
ORDER BY a.AppointmentTime;

DROP VIEW IF EXISTS vw_AvailableRooms;
CREATE VIEW vw_AvailableRooms AS
SELECT
    r.RoomID,
    r.RoomNumber,
    rt.TypeName AS RoomType,
    d.DepartmentName,
    rt.BaseCost
FROM Rooms r
JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
JOIN Departments d ON r.DepartmentID = d.DepartmentID
WHERE r.Status = 'Available';


-- 2. Stored Procedures

-- SP to get appointments for a specific doctor
DROP PROCEDURE IF EXISTS sp_GetDoctorAppointments;
DELIMITER //
CREATE PROCEDURE sp_GetDoctorAppointments(IN p_doctor_id INT, IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    SELECT
        a.AppointmentID,
        p.PatientName,
        a.AppointmentDate,
        a.AppointmentTime,
        a.Status,
        a.Reason
    FROM Appointments a
    JOIN Patients p ON a.PatientID = p.PatientID
    WHERE a.DoctorID = p_doctor_id
      AND a.AppointmentDate BETWEEN p_start_date AND p_end_date
    ORDER BY a.AppointmentDate, a.AppointmentTime;
END //
DELIMITER ;

-- SP to create an initial invoice shell (details added separately)
-- This is simplified. Real-world invoice creation often involves complex logic
-- summing up various costs (rooms, services, medicine) potentially via triggers or application logic.
DROP PROCEDURE IF EXISTS sp_CreateInvoiceForPatient;
DELIMITER //
CREATE PROCEDURE sp_CreateInvoiceForPatient(
    IN p_patient_id INT,
    OUT p_new_invoice_id INT
)
BEGIN
    -- Check if PatientID is valid
    IF EXISTS (SELECT 1 FROM Patients WHERE PatientID = p_patient_id) THEN
        INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, PaymentStatus)
        VALUES (p_patient_id, CURDATE(), 0.00, 'Unpaid'); -- Start with 0 total, Unpaid status

        SET p_new_invoice_id = LAST_INSERT_ID();
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid PatientID provided.';
        SET p_new_invoice_id = NULL;
    END IF;
END //
DELIMITER ;

-- SP to add a service to a patient and potentially link to an invoice
DROP PROCEDURE IF EXISTS sp_AddPatientService;
DELIMITER //
CREATE PROCEDURE sp_AddPatientService(
    IN p_patient_id INT,
    IN p_service_id INT,
    IN p_doctor_id INT, -- Can be NULL if not applicable
    IN p_quantity INT,
    IN p_invoice_id INT -- Can be NULL if not invoicing immediately
)
BEGIN
    DECLARE v_service_cost DECIMAL(10,2);
    DECLARE v_cost_at_time DECIMAL(10,2);

    -- Get the current cost of the service
    SELECT ServiceCost INTO v_service_cost FROM Services WHERE ServiceID = p_service_id;

    IF v_service_cost IS NOT NULL THEN
        SET v_cost_at_time = v_service_cost * p_quantity;

        -- Insert the service usage record
        INSERT INTO PatientServices (PatientID, ServiceID, DoctorID, ServiceDate, Quantity, CostAtTime, InvoiceID)
        VALUES (p_patient_id, p_service_id, p_doctor_id, NOW(), p_quantity, v_cost_at_time, p_invoice_id);

        -- If an invoice ID is provided, update the invoice's service cost and total amount
        IF p_invoice_id IS NOT NULL THEN
            UPDATE Invoices
            SET ServiceCost = ServiceCost + v_cost_at_time,
                TotalAmount = TotalAmount + v_cost_at_time -- Assuming TotalAmount reflects sum before payment
            WHERE InvoiceID = p_invoice_id;
        END IF;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid ServiceID provided.';
    END IF;
END //
DELIMITER ;


-- 3. Functions

-- Function to calculate total revenue within a date range for PAID invoices
DROP FUNCTION IF EXISTS fn_CalculateTotalRevenuePaid;
DELIMITER //
CREATE FUNCTION fn_CalculateTotalRevenuePaid(start_date DATE, end_date DATE)
RETURNS DECIMAL(16,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total DECIMAL(16,2);

    SELECT SUM(AmountPaid) INTO total -- Sum what was actually paid
    FROM Invoices
    WHERE InvoiceDate BETWEEN start_date AND end_date
      AND PaymentStatus = 'Paid'; -- Consider only fully paid invoices

    RETURN IFNULL(total, 0.00);
END //
DELIMITER ;


-- 4. Triggers

-- Trigger to prevent double booking (using the unique key is often preferred, but trigger provides custom message)
DROP TRIGGER IF EXISTS trg_PreventDoubleBooking;
DELIMITER //
CREATE TRIGGER trg_PreventDoubleBooking
BEFORE INSERT ON Appointments
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM Appointments
        WHERE DoctorID = NEW.DoctorID
          AND AppointmentDate = NEW.AppointmentDate
          AND AppointmentTime = NEW.AppointmentTime
          AND Status != 'Cancelled' -- Don't count cancelled slots
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor already has a non-cancelled appointment scheduled at this specific date and time.';
    END IF;
END //
DELIMITER ;

-- Trigger to update medicine stock when prescribed (VERY SIMPLISTIC - assumes stock is available)
-- A more robust system would check stock BEFORE allowing prescription detail insertion or have a separate dispensing step.
DROP TRIGGER IF EXISTS trg_UpdateMedicineStockOnPrescribe;
DELIMITER //
CREATE TRIGGER trg_UpdateMedicineStockOnPrescribe
AFTER INSERT ON PrescriptionDetails
FOR EACH ROW
BEGIN
    UPDATE Medicine
    SET Quantity = Quantity - NEW.QuantityPrescribed
    WHERE MedicineID = NEW.MedicineID;
    -- WARNING: This doesn't check if Quantity goes below 0! Add checks or handle dispensing separately.
END //
DELIMITER ;


-- 5. Database Security and Administration

-- Drop existing users if they exist (for script re-runnability during development)
DROP USER IF EXISTS 'admin_hms'@'localhost';
DROP USER IF EXISTS 'doctor_hms'@'localhost';
DROP USER IF EXISTS 'receptionist_hms'@'localhost';
DROP USER IF EXISTS 'accountant_hms'@'localhost';

-- Create users with strong passwords (replace 'strong_password_X'!)
CREATE USER 'admin_hms'@'localhost' IDENTIFIED BY 'strong_password_admin';
CREATE USER 'doctor_hms'@'localhost' IDENTIFIED BY 'strong_password_doctor';
CREATE USER 'receptionist_hms'@'localhost' IDENTIFIED BY 'strong_password_recept';
CREATE USER 'accountant_hms'@'localhost' IDENTIFIED BY 'strong_password_account';

-- Grant Privileges
-- Admin: Full control
GRANT ALL PRIVILEGES ON hospitalmanagementsystem.* TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_CreateInvoiceForPatient TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddPatientService TO 'admin_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_CalculateTotalRevenuePaid TO 'admin_hms'@'localhost';


-- Doctor: Read patient, their appointments, manage prescriptions, read medicine/services/insurance/rooms
GRANT SELECT ON hospitalmanagementsystem.Patients TO 'doctor_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Appointments -- Needs application logic to filter by own DoctorID for SELECT/UPDATE
    TO 'doctor_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Prescription TO 'doctor_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.PrescriptionDetails TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Medicine TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Services TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Insurance TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.EmergencyContact TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Rooms TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Departments TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.PatientServices TO 'doctor_hms'@'localhost'; -- View services provided
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'doctor_hms'@'localhost';


-- Receptionist: Manage patients, appointments, rooms, contacts, insurance. Read doctors/departments.
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Patients TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Appointments TO 'receptionist_hms'@'localhost';
GRANT SELECT, UPDATE ON hospitalmanagementsystem.Rooms TO 'receptionist_hms'@'localhost'; -- Update status, assign patient
GRANT SELECT, INSERT, UPDATE, DELETE ON hospitalmanagementsystem.EmergencyContact TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON hospitalmanagementsystem.Insurance TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Doctors TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Departments TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.RoomTypes TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Services TO 'receptionist_hms'@'localhost'; -- To know available services
GRANT SELECT, INSERT ON hospitalmanagementsystem.PatientServices TO 'receptionist_hms'@'localhost'; -- Record basic service usage maybe? Or just view? Adjust as needed.
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'receptionist_hms'@'localhost'; -- To check doctor schedules


-- Accountant: Manage invoices. Read patients(limited), services, medicine, rooms, insurance for billing.
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Invoices TO 'accountant_hms'@'localhost';
GRANT SELECT (PatientID, PatientName, Address, PhoneNumber) ON hospitalmanagementsystem.Patients TO 'accountant_hms'@'localhost'; -- Limited patient view
GRANT SELECT ON hospitalmanagementsystem.Services TO 'accountant_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Medicine TO 'accountant_hms'@'localhost'; -- Read costs
GRANT SELECT ON hospitalmanagementsystem.Rooms TO 'accountant_hms'@'localhost'; -- Read room costs via RoomTypes join
GRANT SELECT ON hospitalmanagementsystem.RoomTypes TO 'accountant_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Insurance TO 'accountant_hms'@'localhost'; -- For coverage calculation logic (in app)
GRANT SELECT ON hospitalmanagementsystem.PatientServices TO 'accountant_hms'@'localhost'; -- To verify services billed
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_CreateInvoiceForPatient TO 'accountant_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddPatientService TO 'accountant_hms'@'localhost'; -- Can add services to invoice
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_CalculateTotalRevenuePaid TO 'accountant_hms'@'localhost';


-- Apply the permission changes
FLUSH PRIVILEGES;

