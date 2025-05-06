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
DROP TABLE IF EXISTS Patients;
CREATE TABLE Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    PatientName VARCHAR(100) NOT NULL,
    DateOfBirth DATE NULL,
    Gender ENUM('M', 'F', 'O') NULL COMMENT 'M: Male, F: Female, O: Other',
    Address VARCHAR(255) NULL,
    PhoneNumber VARCHAR(20) NULL UNIQUE COMMENT 'Số điện thoại nên là duy nhất',
    Status VARCHAR(20) DEFAULT 'Active' COMMENT 'e.g., Active, Inpatient, Discharged, Disabled'
) COMMENT = 'Thông tin cơ bản của bệnh nhân';

-- Bảng Bác sĩ (Doctors)
DROP TABLE IF EXISTS Doctors;
CREATE TABLE Doctors (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    DoctorName VARCHAR(100) NOT NULL,
    Specialty VARCHAR(100) NULL COMMENT 'Chuyên khoa của bác sĩ',
    DepartmentID INT NULL COMMENT 'Khoa mà bác sĩ thuộc về',
    DoctorUser VARCHAR(50) UNIQUE COMMENT 'Tên đăng nhập liên kết với tài khoản user (nếu có)',
    PhoneNumber VARCHAR(20) NULL UNIQUE,
    Email VARCHAR(100) NULL UNIQUE,
    status ENUM('active', 'disabled') DEFAULT 'active',
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
        ON DELETE SET NULL -- Nếu xóa khoa, bác sĩ không thuộc khoa nào nhưng vẫn tồn tại
        ON UPDATE CASCADE
) COMMENT = 'Thông tin chi tiết về các bác sĩ';

-- Bảng Thuốc (Medicine)
CREATE TABLE Medicine (
    MedicineID INT AUTO_INCREMENT PRIMARY KEY,
    MedicineName VARCHAR(150) NOT NULL UNIQUE COMMENT 'Tên thuốc',
    Unit VARCHAR(50) DEFAULT 'Viên' COMMENT 'Đơn vị tính (Viên, Lọ, Tuýp, Hộp)',
    Quantity INT NOT NULL DEFAULT 0 CHECK (Quantity >= 0) COMMENT 'Số lượng tồn kho tổng cộng',
    MedicineCost DECIMAL(10, 2) NOT NULL CHECK (MedicineCost >= 0) COMMENT 'Giá mỗi đơn vị thuốc (tham khảo, giá thực tế có thể theo lô)'
) COMMENT = 'Quản lý thông tin thuốc và tổng tồn kho';

-- Bảng quản lý kho thuốc (MedicineBatch)
DROP TABLE IF EXISTS MedicineBatch;
CREATE TABLE MedicineBatch (
    BatchID INT AUTO_INCREMENT PRIMARY KEY,
    MedicineID INT NOT NULL,
    BatchNumber VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity >=0),
    ImportDate DATE NOT NULL,
    ExpiryDate DATE NOT NULL,
    SupplierName VARCHAR(100) NOT NULL,
    MedicineCost DECIMAL(10, 2) NOT NULL COMMENT 'Giá nhập của lô thuốc này',
    Status ENUM('Active', 'Discontinued', 'Expired', 'UsedUp') DEFAULT 'Active',
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID) ON DELETE RESTRICT ON UPDATE CASCADE
) COMMENT = 'Quản lý chi tiết các lô thuốc nhập kho';

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
    role  VARCHAR(30) NOT NULL,
    FullName VARCHAR(100) NULL,
    Email VARCHAR(100) NULL UNIQUE,
    IsActive BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT = 'Quản lý tài khoản đăng nhập hệ thống';

-- Bảng Hóa đơn (Invoices)
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

-- Bảng Dịch vụ (Services)
CREATE TABLE Services (
    ServiceID INT AUTO_INCREMENT PRIMARY KEY,
    ServiceName VARCHAR(150) NOT NULL COMMENT 'Tên dịch vụ (Xét nghiệm máu, Chụp X-quang, Khám chuyên khoa)',
    ServiceCode VARCHAR(50) UNIQUE COMMENT 'Mã dịch vụ (tùy chọn, để dễ tra cứu)',
    ServiceCost DECIMAL(10, 2) NOT NULL CHECK (ServiceCost >= 0) COMMENT 'Chi phí dịch vụ',
    Description TEXT NULL COMMENT 'Mô tả chi tiết dịch vụ'
) COMMENT = 'Danh mục các dịch vụ y tế bệnh viện cung cấp và chi phí';

-- Bảng Chi tiết Dịch vụ sử dụng (PatientServices)
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
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID) ON DELETE RESTRICT ON UPDATE CASCADE,
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

-- Bảng Bảo hiểm (Insurance)
CREATE TABLE Insurance (
    InsuranceRecordID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    InsuranceProvider VARCHAR(150) NOT NULL COMMENT 'Tên nhà cung cấp bảo hiểm (BHYT, PVI, Bảo Việt, Prudential...)',
    PolicyNumber VARCHAR(50) NOT NULL COMMENT 'Số hợp đồng/Số thẻ bảo hiểm',
    BHYTCardNumber VARCHAR(20) NULL UNIQUE COMMENT 'Mã số thẻ BHYT (nếu có, riêng cho VN)',
    EffectiveDate DATE NOT NULL COMMENT 'Ngày bắt đầu hiệu lực',
    EndDate DATE NOT NULL COMMENT 'Ngày hết hạn hiệu lực',
    CoverageDetails TEXT NULL COMMENT 'Mô tả phạm vi bảo hiểm chung',

    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
        ON DELETE CASCADE -- Nếu xóa bệnh nhân, xóa luôn thông tin bảo hiểm
        ON UPDATE CASCADE
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
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE CASCADE ON UPDATE CASCADE,

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
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT ON UPDATE CASCADE
) COMMENT = 'Thông tin chung về một đơn thuốc';

-- Bảng Chi tiết Đơn thuốc (PrescriptionDetails)
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
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID) ON DELETE RESTRICT ON UPDATE CASCADE
) COMMENT = 'Chi tiết các loại thuốc trong một đơn thuốc';

-- Bảng Phiếu nhập viện (AdmissionOrders)
CREATE TABLE AdmissionOrders (
    AdmissionOrderID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    DepartmentID INT NOT NULL,
    OrderDate DATE NOT NULL,
    Reason TEXT NOT NULL,
    Notes TEXT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Pending' COMMENT 'e.g., Pending, Processed, Cancelled',
    ProcessedByUserID INT NULL COMMENT 'FK to users table (ID of receptionist/admin who processed)',
    ProcessedDate DATETIME NULL,
    AssignedRoomID INT NULL COMMENT 'FK to Rooms table',
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID) ON DELETE RESTRICT,
    FOREIGN KEY (ProcessedByUserID) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (AssignedRoomID) REFERENCES Rooms(RoomID) ON DELETE SET NULL
) COMMENT = 'Quản lý phiếu yêu cầu nhập viện';

-- Bảng Điều chỉnh kho (Adjustments)
CREATE TABLE Adjustments (
    AdjustmentID INT AUTO_INCREMENT PRIMARY KEY,
    InventoryID INT NULL COMMENT 'Liên kết vật tư (nếu điều chỉnh vật tư)',
    BatchID INT NULL COMMENT 'Liên kết lô thuốc (nếu điều chỉnh thuốc)',
    AdjustmentType ENUM('IN', 'OUT', 'ADJUST') NOT NULL COMMENT 'Loại điều chỉnh: Nhập/Xuất/Điều chỉnh',
    QuantityChanged INT NOT NULL COMMENT 'Số lượng thay đổi (+/-)',
    AdjustmentDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ChangedBy VARCHAR(100) NOT NULL COMMENT 'Người thực hiện (username hoặc userID)',
    Reason TEXT NULL COMMENT 'Lý do điều chỉnh',

    FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
        ON DELETE SET NULL ON UPDATE CASCADE, -- Or RESTRICT if adjustment history relies on inventory item existence
    FOREIGN KEY (BatchID) REFERENCES MedicineBatch(BatchID)
        ON DELETE SET NULL ON UPDATE CASCADE -- Or RESTRICT if adjustment history relies on batch existence
) COMMENT = 'Lịch sử điều chỉnh tồn kho vật tư và thuốc';

-- Index Creation
-- Patients
CREATE INDEX idx_patient_name ON Patients(PatientName);
CREATE INDEX idx_patient_phone ON Patients(PhoneNumber);
CREATE INDEX idx_patient_status ON Patients(Status);

-- Doctors
CREATE INDEX idx_doctor_name ON Doctors(DoctorName);
CREATE INDEX idx_doctor_dept ON Doctors(DepartmentID);
CREATE INDEX idx_doctor_user ON Doctors(DoctorUser);
CREATE INDEX idx_doctor_status ON Doctors(status);

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
CREATE INDEX idx_inventory_status ON Inventory(Status);

-- Rooms
CREATE INDEX idx_rooms_status ON Rooms(Status);
CREATE INDEX idx_rooms_department ON Rooms(DepartmentID);
CREATE INDEX idx_rooms_type ON Rooms(RoomTypeID);
CREATE INDEX idx_rooms_patient ON Rooms(CurrentPatientID);

-- Medicine
CREATE INDEX idx_medicine_name ON Medicine(MedicineName);

-- MedicineBatch
CREATE INDEX idx_medicinebatch_medicineid ON MedicineBatch(MedicineID);
CREATE INDEX idx_medicinebatch_batchnumber ON MedicineBatch(BatchNumber);
CREATE INDEX idx_medicinebatch_expirydate ON MedicineBatch(ExpiryDate);
CREATE INDEX idx_medicinebatch_status ON MedicineBatch(Status);


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
CREATE INDEX idx_user_isactive ON users(IsActive);

-- AdmissionOrders
CREATE INDEX idx_admission_status ON AdmissionOrders(Status);
CREATE INDEX idx_admission_patient ON AdmissionOrders(PatientID);
CREATE INDEX idx_admission_doctor ON AdmissionOrders(DoctorID);
CREATE INDEX idx_admission_department ON AdmissionOrders(DepartmentID);
CREATE INDEX idx_admission_orderdate ON AdmissionOrders(OrderDate);


-- Adjustments
CREATE INDEX idx_adjustment_date ON Adjustments(AdjustmentDate);
CREATE INDEX idx_adjustment_type ON Adjustments(AdjustmentType);
CREATE INDEX idx_adjustment_batch ON Adjustments(BatchID);
CREATE INDEX idx_adjustment_inventory ON Adjustments(InventoryID);

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
    a.Reason,
    dept.DepartmentName
FROM Appointments a
JOIN Doctors d ON a.DoctorID = d.DoctorID
JOIN Patients p ON a.PatientID = p.PatientID
LEFT JOIN Departments dept ON d.DepartmentID = dept.DepartmentID
WHERE a.AppointmentDate = CURDATE()
ORDER BY a.AppointmentTime;

DROP VIEW IF EXISTS vw_AvailableRooms;
CREATE VIEW vw_AvailableRooms AS
SELECT
    r.RoomID,
    r.RoomNumber,
    rt.TypeName AS RoomType,
    d.DepartmentName,
    rt.BaseCost,
    r.Status
FROM Rooms r
JOIN RoomTypes rt ON r.RoomTypeID = rt.RoomTypeID
JOIN Departments d ON r.DepartmentID = d.DepartmentID
WHERE r.Status = 'Available';

DROP VIEW IF EXISTS vw_MedicineBatchDetails;
CREATE VIEW vw_MedicineBatchDetails AS
SELECT
    mb.BatchID,
    m.MedicineName,
    mb.BatchNumber,
    mb.Quantity AS BatchQuantity,
    mb.ImportDate,
    mb.ExpiryDate,
    mb.SupplierName,
    mb.MedicineCost AS BatchCost,
    mb.Status AS BatchStatus,
    m.Unit AS MedicineUnit,
    m.Quantity AS TotalMedicineStock -- From Medicine table
FROM
    MedicineBatch mb
JOIN Medicine m ON mb.MedicineID = m.MedicineID;


-- 2. Functions

DROP FUNCTION IF EXISTS fn_CalculateTotalRevenuePaid;
DELIMITER //
CREATE FUNCTION fn_CalculateTotalRevenuePaid(p_start_date DATE, p_end_date DATE)
RETURNS DECIMAL(16,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_revenue DECIMAL(16,2);

    SELECT SUM(AmountPaid) INTO total_revenue
    FROM Invoices
    WHERE InvoiceDate BETWEEN p_start_date AND p_end_date
      AND PaymentStatus = 'Paid';

    RETURN IFNULL(total_revenue, 0.00);
END //
DELIMITER ;

DROP FUNCTION IF EXISTS fn_GetTotalStockByMedicine;
DELIMITER //
CREATE FUNCTION fn_GetTotalStockByMedicine(p_medicine_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_quantity INT;
    SELECT SUM(Quantity) INTO total_quantity
    FROM MedicineBatch
    WHERE MedicineID = p_medicine_id AND Status = 'Active' AND ExpiryDate >= CURDATE(); -- Only active, non-expired batches
    RETURN IFNULL(total_quantity, 0);
END //
DELIMITER ;


-- 3. Stored Procedures

DROP PROCEDURE IF EXISTS sp_GetDoctorAppointments;
DELIMITER //
CREATE PROCEDURE sp_GetDoctorAppointments(IN p_doctor_id INT, IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    SELECT
        a.AppointmentID,
        p.PatientName,
        a.AppointmentDate,
        a.AppointmentTime,
        a.Status AS AppointmentStatus,
        a.Reason
    FROM Appointments a
    JOIN Patients p ON a.PatientID = p.PatientID
    WHERE a.DoctorID = p_doctor_id
      AND a.AppointmentDate BETWEEN p_start_date AND p_end_date
    ORDER BY a.AppointmentDate, a.AppointmentTime;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_CreateInvoiceForPatient;
DELIMITER //
CREATE PROCEDURE sp_CreateInvoiceForPatient(
    IN p_patient_id INT,
    OUT p_new_invoice_id INT
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Patients WHERE PatientID = p_patient_id AND Status != 'Disabled') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid or Inactive PatientID provided.';
        SET p_new_invoice_id = NULL;
    ELSE
        INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, RoomCost, MedicineCost, ServiceCost, PaymentStatus)
        VALUES (p_patient_id, CURDATE(), 0.00, 0.00, 0.00, 0.00, 'Unpaid');
        SET p_new_invoice_id = LAST_INSERT_ID();
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_AddPatientService;
DELIMITER //
CREATE PROCEDURE sp_AddPatientService(
    IN p_patient_id INT,
    IN p_service_id INT,
    IN p_doctor_id INT, -- Can be NULL
    IN p_quantity INT,
    IN p_invoice_id INT -- Can be NULL
)
BEGIN
    DECLARE v_service_cost DECIMAL(10,2);
    DECLARE v_cost_at_time DECIMAL(10,2);
    DECLARE v_patient_exists BOOLEAN;
    DECLARE v_service_exists BOOLEAN;
    DECLARE v_doctor_exists_or_null BOOLEAN;

    SELECT EXISTS(SELECT 1 FROM Patients WHERE PatientID = p_patient_id) INTO v_patient_exists;
    SELECT EXISTS(SELECT 1 FROM Services WHERE ServiceID = p_service_id) INTO v_service_exists;
    SET v_doctor_exists_or_null = (p_doctor_id IS NULL OR EXISTS(SELECT 1 FROM Doctors WHERE DoctorID = p_doctor_id));

    IF NOT v_patient_exists THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid PatientID provided.';
    ELSEIF NOT v_service_exists THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid ServiceID provided.';
    ELSEIF NOT v_doctor_exists_or_null THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid DoctorID provided.';
    ELSE
        SELECT ServiceCost INTO v_service_cost FROM Services WHERE ServiceID = p_service_id;
        SET v_cost_at_time = v_service_cost * p_quantity;

        INSERT INTO PatientServices (PatientID, ServiceID, DoctorID, ServiceDate, Quantity, CostAtTime, InvoiceID)
        VALUES (p_patient_id, p_service_id, p_doctor_id, NOW(), p_quantity, v_cost_at_time, p_invoice_id);

        IF p_invoice_id IS NOT NULL THEN
            IF EXISTS (SELECT 1 FROM Invoices WHERE InvoiceID = p_invoice_id) THEN
                UPDATE Invoices
                SET ServiceCost = ServiceCost + v_cost_at_time,
                    TotalAmount = RoomCost + MedicineCost + (ServiceCost + v_cost_at_time) -- Recalculate total
                WHERE InvoiceID = p_invoice_id;
            ELSE
                 -- Optionally handle if invoice ID is provided but doesn't exist, though FK constraint should catch this if PatientServices.InvoiceID is not NULL
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Provided InvoiceID does not exist for updating costs.';
            END IF;
        END IF;
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_AddMedicineBatch;
DELIMITER //
CREATE PROCEDURE sp_AddMedicineBatch(
    IN p_medicine_id INT,
    IN p_batch_number VARCHAR(100),
    IN p_quantity INT,
    IN p_import_date DATE,
    IN p_expiry_date DATE,
    IN p_supplier_name VARCHAR(155),
    IN p_medicine_cost DECIMAL(10, 2)
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Medicine WHERE MedicineID = p_medicine_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid MedicineID provided.';
    ELSEIF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be positive.';
    ELSEIF p_expiry_date < p_import_date THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Expiry date cannot be before import date.';
    ELSE
        INSERT INTO MedicineBatch (MedicineID, BatchNumber, Quantity, ImportDate, ExpiryDate, SupplierName, MedicineCost, Status)
        VALUES (p_medicine_id, p_batch_number, p_quantity, p_import_date, p_expiry_date, p_supplier_name, p_medicine_cost, 'Active');
        -- The trg_UpdateStockAfterInsert trigger will update Medicine.Quantity and log to Adjustments
    END IF;
END //
DELIMITER ;


-- 4. Triggers

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
          AND Status != 'Cancelled' AND Status != 'No Show' -- Consider existing active appointments
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bác sĩ đã có lịch hẹn khác (không phải trạng thái Cancelled/No Show) vào thời điểm này.';
    END IF;
END //
DELIMITER ;


DROP TRIGGER IF EXISTS trg_UpdateStockAfterInsertBatch; -- Renamed for clarity from generic "trg_UpdateStockAfterInsert"
DELIMITER //
CREATE TRIGGER trg_UpdateStockAfterInsertBatch
AFTER INSERT ON MedicineBatch
FOR EACH ROW
BEGIN
    -- Update total quantity in Medicine table
    UPDATE Medicine
    SET Quantity = Quantity + NEW.Quantity
    WHERE MedicineID = NEW.MedicineID;

    -- Log the adjustment for the new batch
    INSERT INTO Adjustments (BatchID, AdjustmentType, QuantityChanged, ChangedBy, Reason)
    VALUES (NEW.BatchID, 'IN', NEW.Quantity, USER(), CONCAT('Nhập lô thuốc mới: ', NEW.BatchNumber));
END //
DELIMITER ;


DROP TRIGGER IF EXISTS trg_UpdateMedicineStockOnPrescribe;
DELIMITER //
CREATE TRIGGER trg_UpdateMedicineStockOnPrescribe
AFTER INSERT ON PrescriptionDetails
FOR EACH ROW
BEGIN
    DECLARE v_selected_batch_id INT DEFAULT NULL;
    DECLARE v_quantity_to_prescribe INT;
    SET v_quantity_to_prescribe = NEW.QuantityPrescribed;

    -- Update total quantity in Medicine table first
    -- This assumes the prescription will succeed.
    -- A check for overall stock in Medicine table could be done BEFORE this trigger, in application logic or another BEFORE trigger.
    UPDATE Medicine
    SET Quantity = Quantity - v_quantity_to_prescribe
    WHERE MedicineID = NEW.MedicineID;

    -- Check if Medicine quantity would go negative (basic check, more robust needed)
    IF (SELECT Quantity FROM Medicine WHERE MedicineID = NEW.MedicineID) < 0 THEN
         -- Rollback the master quantity update if it went negative (though this indicates a prior issue)
         UPDATE Medicine SET Quantity = Quantity + v_quantity_to_prescribe WHERE MedicineID = NEW.MedicineID;
         SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Không đủ tổng số lượng thuốc trong kho (Medicine table).';
    END IF;

    -- Attempt to find a suitable active, non-expired batch with enough quantity
    SELECT BatchID INTO v_selected_batch_id
    FROM MedicineBatch
    WHERE MedicineID = NEW.MedicineID
      AND Status = 'Active'
      AND ExpiryDate >= CURDATE()
      AND Quantity >= v_quantity_to_prescribe
    ORDER BY ExpiryDate ASC -- FIFO based on expiry, could also be ImportDate for true FIFO
    LIMIT 1;

    IF v_selected_batch_id IS NOT NULL THEN
        -- Decrement the quantity in the chosen MedicineBatch
        UPDATE MedicineBatch
        SET Quantity = Quantity - v_quantity_to_prescribe
        WHERE BatchID = v_selected_batch_id;

        -- Log the adjustment referencing the specific batch
        INSERT INTO Adjustments (BatchID, AdjustmentType, QuantityChanged, ChangedBy, Reason)
        VALUES (v_selected_batch_id, 'OUT', -v_quantity_to_prescribe, USER(),
                CONCAT('Xuất theo đơn thuốc ID: ', NEW.PrescriptionID, ', Chi tiết ID: ', NEW.PrescriptionDetailID));
        
        -- If batch quantity becomes zero, update its status
        IF (SELECT Quantity FROM MedicineBatch WHERE BatchID = v_selected_batch_id) = 0 THEN
            UPDATE MedicineBatch SET Status = 'UsedUp' WHERE BatchID = v_selected_batch_id;
        END IF;
    ELSE
        -- No single suitable batch found.
        -- This is a critical issue: total stock was decremented, but no batch could fulfill it.
        -- This indicates a mismatch or need for more complex logic (e.g., splitting prescription over batches or erroring out earlier).
        -- For now, log an adjustment without a specific BatchID or with a note.
        -- Ideally, the transaction should fail here if medicine cannot be sourced from a specific batch.
        -- Reverting the initial Medicine.Quantity update:
         UPDATE Medicine SET Quantity = Quantity + v_quantity_to_prescribe WHERE MedicineID = NEW.MedicineID;
         SIGNAL SQLSTATE '45000'
         SET MESSAGE_TEXT = 'Không tìm thấy lô thuốc phù hợp (đủ số lượng, còn hạn, active) để xuất kho. Kê đơn thất bại.';

        -- Fallback logging if strict failure is not desired (NOT RECOMMENDED without further logic):
        /*
        INSERT INTO Adjustments (InventoryID, BatchID, AdjustmentType, QuantityChanged, ChangedBy, Reason)
        VALUES (NULL, NULL, 'OUT', -v_quantity_to_prescribe, USER(),
                CONCAT('Xuất theo đơn thuốc ID: ', NEW.PrescriptionID, ', Chi tiết ID: ', NEW.PrescriptionDetailID, ' - LƯU Ý: Không xác định được lô cụ thể hoặc lô không đủ.'));
        */
    END IF;
END //
DELIMITER ;


-- 5. Database Security and Administration

-- Drop existing users if they exist
DROP USER IF EXISTS 'admin_hms'@'localhost';
DROP USER IF EXISTS 'doctor_hms'@'localhost';
DROP USER IF EXISTS 'receptionist_hms'@'localhost';
DROP USER IF EXISTS 'accountant_hms'@'localhost';
DROP USER IF EXISTS 'pharmacist_hms'@'localhost';
DROP USER IF EXISTS 'nurse_hms'@'localhost';
DROP USER IF EXISTS 'warehouse_manager_hms'@'localhost';
DROP USER IF EXISTS 'director_hms'@'localhost';

-- Create users with strong passwords (replace 'strong_password_X' with actual strong passwords)
CREATE USER 'admin_hms'@'localhost' IDENTIFIED BY 'AdminHMS!2025Pass';
CREATE USER 'doctor_hms'@'localhost' IDENTIFIED BY 'DoctorHMS!2025Pass';
CREATE USER 'receptionist_hms'@'localhost' IDENTIFIED BY 'ReceptHMS!2025Pass';
CREATE USER 'accountant_hms'@'localhost' IDENTIFIED BY 'AccountHMS!2025Pass';
CREATE USER 'pharmacist_hms'@'localhost' IDENTIFIED BY 'PharmHMS!2025Pass';
CREATE USER 'warehouse_manager_hms'@'localhost' IDENTIFIED BY 'WarehouseHMS!2025Pass';
CREATE USER 'nurse_hms'@'localhost' IDENTIFIED BY 'NurseHMS!2025Pass';
CREATE USER 'director_hms'@'localhost' IDENTIFIED BY 'DirectorHMS!2025Pass';

-- Grant Privileges
-- Admin: Full control
GRANT ALL PRIVILEGES ON hospitalmanagementsystem.* TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_CreateInvoiceForPatient TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddPatientService TO 'admin_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddMedicineBatch TO 'admin_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_CalculateTotalRevenuePaid TO 'admin_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_GetTotalStockByMedicine TO 'admin_hms'@'localhost';

-- Director: Full overview, similar to admin but might have some restrictions in a real scenario. For now, same as admin for simplicity.
GRANT ALL PRIVILEGES ON hospitalmanagementsystem.* TO 'director_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'director_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_CreateInvoiceForPatient TO 'director_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddPatientService TO 'director_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddMedicineBatch TO 'director_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_CalculateTotalRevenuePaid TO 'director_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_GetTotalStockByMedicine TO 'director_hms'@'localhost';

-- Doctor:
GRANT SELECT ON hospitalmanagementsystem.Patients TO 'doctor_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE (Status, Reason) ON hospitalmanagementsystem.Appointments TO 'doctor_hms'@'localhost'; -- App logic should filter to own appointments for UPDATE
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Prescription TO 'doctor_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.PrescriptionDetails TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Medicine TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.MedicineBatch TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Services TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Insurance TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.EmergencyContact TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Rooms TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.RoomTypes TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Departments TO 'doctor_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.PatientServices TO 'doctor_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.AdmissionOrders TO 'doctor_hms'@'localhost'; -- Doctors can create/update admission orders
GRANT SELECT (username, FullName, role, id) ON hospitalmanagementsystem.users TO 'doctor_hms'@'localhost'; -- To see user details if needed (e.g. who processed order)

GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'doctor_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_GetTotalStockByMedicine TO 'doctor_hms'@'localhost';

-- Receptionist:
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Patients TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Appointments TO 'receptionist_hms'@'localhost';
GRANT SELECT, UPDATE (Status, CurrentPatientID, LastCleanedDate) ON hospitalmanagementsystem.Rooms TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON hospitalmanagementsystem.EmergencyContact TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON hospitalmanagementsystem.Insurance TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Doctors TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Departments TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.RoomTypes TO 'receptionist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Services TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.PatientServices TO 'receptionist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE (Status, ProcessedByUserID, ProcessedDate, AssignedRoomID, Notes) ON hospitalmanagementsystem.AdmissionOrders TO 'receptionist_hms'@'localhost';
GRANT SELECT (username, FullName, role, id) ON hospitalmanagementsystem.users TO 'receptionist_hms'@'localhost'; -- To set ProcessedByUserID

GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'receptionist_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_CreateInvoiceForPatient TO 'receptionist_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddPatientService TO 'receptionist_hms'@'localhost';

-- Accountant:
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Invoices TO 'accountant_hms'@'localhost';
GRANT SELECT (PatientID, PatientName, Address, PhoneNumber, Status) ON hospitalmanagementsystem.Patients TO 'accountant_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Services TO 'accountant_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Medicine TO 'accountant_hms'@'localhost'; -- For costs
GRANT SELECT ON hospitalmanagementsystem.MedicineBatch TO 'accountant_hms'@'localhost'; -- For batch specific costs if needed
GRANT SELECT ON hospitalmanagementsystem.Rooms TO 'accountant_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.RoomTypes TO 'accountant_hms'@'localhost'; -- For room costs
GRANT SELECT ON hospitalmanagementsystem.Insurance TO 'accountant_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.PatientServices TO 'accountant_hms'@'localhost';
GRANT SELECT (username, FullName, role, id) ON hospitalmanagementsystem.users TO 'accountant_hms'@'localhost';

GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_CreateInvoiceForPatient TO 'accountant_hms'@'localhost';
GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddPatientService TO 'accountant_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_CalculateTotalRevenuePaid TO 'accountant_hms'@'localhost';

-- Pharmacist:
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Medicine TO 'pharmacist_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.MedicineBatch TO 'pharmacist_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Prescription TO 'pharmacist_hms'@'localhost'; -- View prescriptions
GRANT SELECT ON hospitalmanagementsystem.PrescriptionDetails TO 'pharmacist_hms'@'localhost'; -- View prescription details
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Adjustments TO 'pharmacist_hms'@'localhost'; -- Pharmacists will also adjust stock
GRANT SELECT (username, FullName, role, id) ON hospitalmanagementsystem.users TO 'pharmacist_hms'@'localhost';

GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_AddMedicineBatch TO 'pharmacist_hms'@'localhost';
GRANT EXECUTE ON FUNCTION hospitalmanagementsystem.fn_GetTotalStockByMedicine TO 'pharmacist_hms'@'localhost';


-- Warehouse Manager (for non-medicine inventory):
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Inventory TO 'warehouse_manager_hms'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospitalmanagementsystem.Adjustments TO 'warehouse_manager_hms'@'localhost'; -- For inventory items
GRANT SELECT (username, FullName, role, id) ON hospitalmanagementsystem.users TO 'warehouse_manager_hms'@'localhost';

-- Nurse:
GRANT SELECT ON hospitalmanagementsystem.Patients TO 'nurse_hms'@'localhost';
GRANT SELECT, UPDATE (Status, Reason) ON hospitalmanagementsystem.Appointments TO 'nurse_hms'@'localhost'; -- Update status (e.g., completed)
GRANT SELECT ON hospitalmanagementsystem.Prescription TO 'nurse_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.PrescriptionDetails TO 'nurse_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Doctors TO 'nurse_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.Rooms TO 'nurse_hms'@'localhost';
GRANT SELECT ON hospitalmanagementsystem.PatientServices TO 'nurse_hms'@'localhost'; -- View services done
GRANT SELECT ON hospitalmanagementsystem.AdmissionOrders TO 'nurse_hms'@'localhost'; -- View admission orders
GRANT SELECT (username, FullName, role, id) ON hospitalmanagementsystem.users TO 'nurse_hms'@'localhost';

GRANT EXECUTE ON PROCEDURE hospitalmanagementsystem.sp_GetDoctorAppointments TO 'nurse_hms'@'localhost';

-- Apply the permission changes
FLUSH PRIVILEGES;