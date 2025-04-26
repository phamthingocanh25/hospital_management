-- Create the database
CREATE DATABASE HospitalManagementSystem;
USE HospitalManagementSystem;
Select * from 
-- Departments table
CREATE TABLE Departments (
    DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL
);

-- Doctors table
CREATE TABLE Doctors (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    DoctorName VARCHAR(100) NOT NULL,
    DepartmentID INT,
    Specialty VARCHAR(100),
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

-- Patients table
CREATE TABLE Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    PatientName VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    Gender CHAR(1),
    Address VARCHAR(200),
    PhoneNumber VARCHAR(15)
);

-- Appointments table
CREATE TABLE Appointments (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    DoctorID INT,
    PatientID INT,
    AppointmentDate DATE NOT NULL,
    AppointmentTime TIME NOT NULL,
    Status VARCHAR(20) DEFAULT 'Scheduled', # tao thêm cột này là có lí do nha
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID),
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

-- Invoices table
CREATE TABLE Invoices (
    InvoiceID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT,
    InvoiceDate DATE NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    Status VARCHAR(20) DEFAULT 'Unpaid', # cả cột này nữa có lí do nha
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

-- Create indexes for performance optimization
CREATE INDEX idx_patient_name ON Patients(PatientName);
CREATE INDEX idx_doctor_name ON Doctors(DoctorName);
CREATE INDEX idx_appointment_date ON Appointments(AppointmentDate);
CREATE INDEX idx_invoice_date ON Invoices(InvoiceDate);

SELECT User, Host FROM mysql.user WHERE User = 'user_name';

ALTER TABLE doctors ADD DoctorUser VARCHAR(50) UNIQUE;
ALTER TABLE invoices DROP COLUMN Status;
