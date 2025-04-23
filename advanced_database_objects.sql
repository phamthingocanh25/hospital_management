-- View for today's appointments
CREATE VIEW vw_TodaysAppointments AS
SELECT a.AppointmentID, d.DoctorName, p.PatientName, a.AppointmentTime
FROM Appointments a
JOIN Doctors d ON a.DoctorID = d.DoctorID
JOIN Patients p ON a.PatientID = p.PatientID
WHERE a.AppointmentDate = CURDATE();
appointmentsappointments
-- Stored procedure to get appointments by doctor
DELIMITER //
CREATE PROCEDURE sp_GetDoctorAppointments(IN doc_id INT)
BEGIN
    SELECT a.AppointmentID, p.PatientName, a.AppointmentDate, a.AppointmentTime
    FROM Appointments a
    JOIN Patients p ON a.PatientID = p.PatientID
    WHERE a.DoctorID = doc_id
    ORDER BY a.AppointmentDate, a.AppointmentTime;
END //
DELIMITER ;

-- Stored procedure to create invoice for appointment
DELIMITER //
CREATE PROCEDURE sp_CreateInvoiceForAppointment(IN app_id INT, IN amount DECIMAL(10,2))
BEGIN
    DECLARE pat_id INT;
    
    SELECT PatientID INTO pat_id FROM Appointments WHERE AppointmentID = app_id;
    
    INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount)
    VALUES (pat_id, CURDATE(), amount);
    
    UPDATE Appointments SET Status = 'Completed' WHERE AppointmentID = app_id;
    
    SELECT LAST_INSERT_ID() AS NewInvoiceID;
END //
DELIMITER ;

-- Function to calculate total revenue
DELIMITER //
CREATE FUNCTION fn_CalculateTotalRevenue(start_date DATE, end_date DATE) 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    
    SELECT SUM(TotalAmount) INTO total
    FROM Invoices
    WHERE InvoiceDate BETWEEN start_date AND end_date
    AND Status = 'Paid';
    
    RETURN IFNULL(total, 0);
END //
DELIMITER ;

-- Trigger to prevent double booking of doctors
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
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor already has an appointment at this time';
    END IF;
END //
DELIMITER ;

-- Database Security and Administration
-- Configure user roles, permissions, and security settings.
CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin_pass';
GRANT ALL PRIVILEGES ON hospital_db.* TO 'admin_user'@'localhost';

CREATE USER 'doctor_user'@'localhost' IDENTIFIED BY 'doctor_pass';
GRANT SELECT ON hospital_db.Patients TO 'doctor_user'@'localhost';
GRANT SELECT, UPDATE ON hospital_db.Appointments TO 'doctor_user'@'localhost';

CREATE USER 'receptionist_user'@'localhost' IDENTIFIED BY 'recept_pass';
GRANT SELECT, INSERT, UPDATE ON hospital_db.Patients TO 'receptionist_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospital_db.Appointments TO 'receptionist_user'@'localhost';

CREATE USER 'accountant_user'@'localhost' IDENTIFIED BY 'acct_pass';
GRANT SELECT, INSERT, UPDATE ON hospital_db.Invoices TO 'accountant_user'@'localhost';
GRANT SELECT (PatientID, PatientName) ON hospital_db.Patients TO 'accountant_user'@'localhost';

FLUSH PRIVILEGES;