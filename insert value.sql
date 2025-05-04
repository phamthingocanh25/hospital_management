-- File: insert_all_sample_data.sql
-- Chèn dữ liệu mẫu vào tất cả các bảng của HospitalManagementSystem
-- Đã cập nhật bảng Invoices để thêm cột IsBHYTApplied

USE hospitalmanagementsystem;

-- !!! CHẠY LỆNH NÀY TRƯỚC NẾU CHƯA CÓ CỘT IsBHYTApplied TRONG BẢNG Invoices !!!
-- ALTER TABLE Invoices ADD COLUMN IsBHYTApplied BOOLEAN DEFAULT FALSE COMMENT 'Đánh dấu nếu BHYT đã được xem xét/áp dụng cho hóa đơn này';
-- !!! --------------------------------------------------------------------- !!!

-- 1. Bảng Departments
INSERT INTO Departments (DepartmentName) VALUES
('Cardiology'),        -- ID: 1
('Neurology'),         -- ID: 2
('Orthopedics'),       -- ID: 3
('Pediatrics'),        -- ID: 4
('General Surgery');   -- ID: 5

-- 2. Bảng users (Mật khẩu nên được hash trong ứng dụng thực tế)
-- Mật khẩu mẫu: Admin@123, DoctorP@ss1, RecepP@ss1, AccP@ss1
-- Lưu ý: Việc hash mật khẩu thường được thực hiện trong code Python (ví dụ: dùng bcrypt)
-- Ở đây chỉ minh họa tên đăng nhập và vai trò. Mật khẩu trong DB phải là dạng đã hash.

-- 3. Bảng Doctors (Liên kết với users qua DoctorUser)
INSERT INTO Doctors (DoctorName, DepartmentID, Specialty, DoctorUser) VALUES
('Dr. Smith', 1, 'Cardiac Surgery', 'drsmith'),       -- ID: 1
('Dr. Johnson', 2, 'Neurological Disorders', 'drjohnson'), -- ID: 2
('Dr. Williams', 3, 'Joint Replacement', NULL),        -- ID: 3 (Chưa có tài khoản user)
('Dr. Brown', 4, 'Child Healthcare', NULL),         -- ID: 4 (Chưa có tài khoản user)
('Dr. Davis', 5, 'General Surgery', NULL);          -- ID: 5 (Chưa có tài khoản user)

-- 4. Bảng Patients
INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber) VALUES
('John Doe', '1980-05-15', 'M', '123 Main St, Anytown', '555-0101'),       -- ID: 1
('Jane Smith', '1975-08-22', 'F', '456 Oak Ave, Somewhere', '555-0102'),  -- ID: 2
('Robert Johnson', '1990-03-10', 'M', '789 Pine Rd, Nowhere', '555-0103'), -- ID: 3
('Emily Davis', '1988-11-30', 'F', '321 Elm Blvd, Anycity', '555-0104'),   -- ID: 4
('Michael Wilson', '1972-07-18', 'M', '654 Maple Ln, Yourtown', '555-0105');-- ID: 5

-- 5. Bảng Appointments (Sử dụng Status mặc định 'Scheduled')
INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime, Status) VALUES
(1, 1, '2025-05-02', '09:00:00', 'Scheduled'), -- Dr. Smith, John Doe
(2, 2, '2025-05-02', '10:30:00', 'Scheduled'), -- Dr. Johnson, Jane Smith
(3, 3, '2025-05-03', '14:00:00', 'Scheduled'), -- Dr. Williams, Robert Johnson
(4, 4, '2025-05-04', '11:15:00', 'Completed'), -- Dr. Brown, Emily Davis (Giả sử đã hoàn thành)
(1, 5, '2025-05-05', '15:45:00', 'Scheduled'); -- Dr. Smith, Michael Wilson

-- 6. Bảng EmergencyContact
INSERT INTO EmergencyContact (PatientID, ContactName, PhoneNumber, Relationship) VALUES
(1, 'Mary Doe', '555-0201', 'Wife'),
(1, 'Peter Doe', '555-0202', 'Brother'),
(3, 'Anna Johnson', '555-0203', 'Mother'),
(5, 'David Wilson', '555-0205', 'Son');

-- 7. Bảng Inventory
INSERT INTO Inventory (ItemName, Quantity, Status) VALUES
('Bông gòn y tế (Gói)', 200, 'Available'),
('Gạc vô trùng 10x10cm (Hộp)', 150, 'Available'),
('Kim tiêm 23G (Hộp 100)', 80, 'Low Stock'),
('Máy đo huyết áp Omron', 10, 'Available'),
('Xe lăn tiêu chuẩn', 5, 'Available');

-- 8. Bảng Rooms
INSERT INTO RoomTypes (TypeName, BaseCost, Description) VALUES
('Standard', 500000.00, 'Phòng tiêu chuẩn, 2 giường, tiện nghi cơ bản.'),
('VIP', 1500000.00, 'Phòng VIP đơn, tiện nghi cao cấp, TV, tủ lạnh, sofa.'),
('ICU', 2500000.00, 'Phòng chăm sóc đặc biệt, trang thiết bị y tế hiện đại.');
-- Giả sử các RoomTypeID được tạo tự động là 1 (Standard), 2 (VIP), 3 (ICU)

-- Thêm các phòng cụ thể
INSERT INTO Rooms (RoomNumber, RoomTypeID, DepartmentID, Status, CurrentPatientID, LastCleanedDate) VALUES
('A101', 1, 1, 'Available', NULL, NULL),          -- Phòng Standard, Khoa Nội, Trống
('A102', 1, 1, 'Occupied', 1, '2025-04-30'),     -- Phòng Standard, Khoa Nội, Có bệnh nhân 1, giả sử dọn ngày hôm qua
('A201', 2, 1, 'Available', NULL, '2025-05-01'),     -- Phòng VIP, Khoa Nội, Trống, giả sử dọn hôm nay
('B101', 1, 2, 'Cleaning', NULL, '2025-04-29'),     -- Phòng Standard, Khoa Ngoại, Đang dọn dẹp, dọn lần cuối 2 ngày trước
('B102', 1, 2, 'Maintenance', NULL, NULL),         -- Phòng Standard, Khoa Ngoại, Bảo trì
('B201', 2, 2, 'Occupied', 2, '2025-04-30'),     -- Phòng VIP, Khoa Ngoại, Có bệnh nhân 2
('C301', 3, 3, 'Occupied', 3, '2025-05-01'),     -- Phòng ICU, Khoa Hồi sức, Có bệnh nhân 3
('C302', 3, 3, 'Available', NULL, NULL);         -- Phòng ICU, Khoa Hồi sức, Trống

-- 9. Bảng Medicine
INSERT INTO Medicine (MedicineName, Quantity, MedicineCost) VALUES
('Paracetamol 500mg', 1000, 500.00),      -- ID: 1
('Amoxicillin 250mg', 500, 1500.00),      -- ID: 2
('Omeprazole 20mg', 300, 2500.00),       -- ID: 3
('Salbutamol Inhaler', 100, 55000.00),     -- ID: 4
('Loratadine 10mg', 400, 1200.00);         -- ID: 5

-- Bảng MedicineBatch
INSERT INTO MedicineBatch (MedicineID, BatchNumber, Quantity, ImportDate, ExpiryDate, SupplierName, MedicineCost, Status) VALUES
(1, 'PARAC-001', 500, '2025-01-01', '2027-01-01', 'PharmaX', 500.00, 'Active'),
(2, 'AMOX-001', 200, '2025-03-01', '2027-03-01', 'MedSupply', 1500.00, 'Active'),
(3, 'OMEP-001', 100, '2025-02-01', '2027-02-01', 'HealthCo', 2500.00, 'Active'),
(4, 'SALB-001', 50, '2025-04-01', '2027-04-01', 'PharmaX', 55000.00, 'Active'),
(5, 'LORA-001', 400, '2025-05-01', '2027-05-01', 'MedSupply', 1200.00, 'Active');

-- 10. Bảng Invoices (Đã thêm cột IsBHYTApplied kiểu BOOLEAN/TINYINT(1))
INSERT INTO Invoices (PatientID, InvoiceDate, RoomCost, MedicineCost, ServiceCost, PaymentStatus, TotalAmount, IsBHYTApplied) VALUES
(1, '2025-04-15', 500000.00, 15000.00, 250000.00, 'Paid', 765000.00, TRUE),       -- BN 1, Có BHYT, Đã thanh toán
(2, '2025-04-16', 0.00, 10500.00, 180000.00, 'Unpaid', 190500.00, FALSE),      -- BN 2, Không có BHYT (hoặc có nhưng không áp dụng HĐ này), Chưa thanh toán
(3, '2025-04-17', 450000.00, 0.00, 320000.00, 'Paid', 770000.00, FALSE),      -- BN 3, Không có BHYT, Đã thanh toán
(4, '2025-04-18', 0.00, 16800.00, 150000.00, 'Partial', 166800.00, TRUE),      -- BN 4, Có BHYT, Thanh toán 1 phần
(5, '2025-04-19', 0.00, 0.00, 275000.00, 'Unpaid', 275000.00, FALSE);      -- BN 5, Không có BHYT, Chưa thanh toán

-- 11. Bảng Services (Liên kết với Invoices nếu có)
-- Lấy InvoiceID từ bảng Invoices vừa insert (giả sử ID là 1 đến 5)
INSERT INTO Services (ServiceName, ServiceCode, ServiceCost, Description) VALUES
('Khám tổng quát', 'KHAMTQ01', 150000.00, 'Khám sức khỏe tổng quát ban đầu'),
('Xét nghiệm máu cơ bản', 'XNMAU01', 250000.00, 'Gói xét nghiệm công thức máu, đường huyết, mỡ máu, chức năng gan, thận cơ bản'),
('Điện tâm đồ (ECG)', 'ECG01', 100000.00, 'Ghi lại hoạt động điện của tim'),
('Chụp X-quang khớp gối (thẳng/nghiêng)', 'XQKGOI01', 180000.00, 'Chụp hình ảnh khớp gối bằng tia X ở hai tư thế'),
('Khám chuyên khoa Cơ Xương Khớp', 'KHAMCXK01', 200000.00, 'Phí khám với bác sĩ chuyên khoa Cơ Xương Khớp'),
('Siêu âm ổ bụng tổng quát', 'SAOBUNG01', 150000.00, 'Siêu âm kiểm tra các tạng trong ổ bụng'),
('Khám chuyên khoa Ngoại tổng quát', 'KHAMNGOAI01', 200000.00, 'Phí khám với bác sĩ chuyên khoa Ngoại'),
('Khám chuyên khoa Nội thần kinh', 'KHAMTK01', 220000.00, 'Phí khám với bác sĩ chuyên khoa Nội thần kinh'),
('Khám chuyên khoa Nhi', 'KHAMNHI01', 180000.00, 'Phí khám với bác sĩ chuyên khoa Nhi'),
('Nội soi dạ dày (không gây mê)', 'NSDD01', 800000.00, 'Nội soi kiểm tra thực quản, dạ dày, tá tràng'),
('Nội soi dạ dày (có gây mê)', 'NSDDGM01', 1500000.00, 'Nội soi kiểm tra thực quản, dạ dày, tá tràng có gây mê');

-- 12. Bảng Prescription
INSERT INTO Prescription (AppointmentID, PatientID, DoctorID, PrescriptionDate, Diagnosis, Notes) VALUES
(1, 1, 1, '2025-04-15', 'Sốt virus', 'Nghỉ ngơi, uống nhiều nước, hạ sốt khi cần thiết.'),
(2, 2, 2, '2025-04-16', 'Viêm họng cấp do vi khuẩn', 'Uống đủ liều kháng sinh, tái khám nếu không đỡ sau 3 ngày.'),
(3, 1, 1, '2025-04-17', 'Trào ngược dạ dày thực quản', 'Điều chỉnh chế độ ăn uống, tránh đồ cay nóng, chua.'),
(4, 4, 4, '2025-04-18', 'Viêm mũi dị ứng', 'Tránh tiếp xúc dị nguyên nếu biết.');
INSERT INTO PrescriptionDetails (PrescriptionID, MedicineID, Dosage, Frequency, Duration, Instruction, QuantityPrescribed) VALUES
(1, 1, '500mg', 'Khi sốt > 38.5°C, tối đa 4 lần/ngày', '3 ngày', 'Uống cách nhau ít nhất 4-6 tiếng', 10), -- Giả sử MedicineID 1 là Paracetamol
(2, 2, '500mg', '3 lần/ngày sau ăn', '7 ngày', NULL, 21), -- Giả sử MedicineID 2 là Amoxicillin
(3, 3, '20mg', '1 lần/ngày trước ăn sáng 30 phút', '1 tháng', NULL, 30), -- Giả sử MedicineID 3 là Omeprazole
(4, 5, '10mg', '1 lần/ngày vào buổi tối', '14 ngày', NULL, 14); -- Giả sử MedicineID 5 là Loratadine
-- 13. Bảng Insurance 
INSERT INTO Insurance (PatientID, InsuranceProvider, PolicyNumber, BHYTCardNumber, EffectiveDate, EndDate, CoverageDetails) VALUES
(1, 'Bảo hiểm Y tế Nhà nước', '4543456', 'HS12345678', '2025-01-01', '2025-12-31', 'Chi trả 80% chi phí khám chữa bệnh,50% tiền phòng theo quy định BHYT'),
(2, 'Bảo hiểm Y tế Bắt buộc', '34565432', 'HS4953045685', '2024-07-01', '2026-06-30', 'Chi trả 20% chi phí một số thuốc đặc trị'),
(4, 'Bảo hiểm Y tế Nhà nước', '234565432', 'JT355453332', '2024-09-16', '2025-09-15', 'Chi trả hầu hết (100%) chi phí KCB theo quy định'),
(5, 'Bảo Việt HealthCare', 'BVHC/2024/10594', '354534', '2025-04-01', '2026-03-31', 'Bảo lãnh chi phí phẫu thuật nội trú');

INSERT INTO PatientServices 
(PatientID, ServiceID, DoctorID, ServiceDate, Quantity, CostAtTime, InvoiceID, Notes)
VALUES
(1, 1, 2, '2025-05-01', 1, 120000, NULL, 'Xét nghiệm định kỳ'),
(1, 3, 2, '2025-05-01', 1, 250000, NULL, NULL),
(2, 2, 3, '2025-04-30', 1, 180000, NULL, 'Chẩn đoán đau bụng'),
(3, 4, 1, '2025-05-02', 1, 150000, NULL, 'Theo dõi tim mạch'),
(3, 5, 1, '2025-05-02', 1, 100000, NULL, 'Trước ăn sáng');
