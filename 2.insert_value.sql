-- Insert sample departments
INSERT INTO Departments (DepartmentName) VALUES 
('Cardiology'), ('Neurology'), ('Orthopedics'), ('Pediatrics'), ('General Surgery');

-- Insert sample doctors
INSERT INTO Doctors (DoctorName, DepartmentID, Specialty) VALUES 
('Dr. Smith', 1, 'Cardiac Surgery'),
('Dr. Johnson', 2, 'Neurological Disorders'),
('Dr. Williams', 3, 'Joint Replacement'),
('Dr. Brown', 4, 'Child Healthcare'),
('Dr. Davis', 5, 'General Surgery');

-- Insert sample patients
INSERT INTO Patients (PatientName, DateOfBirth, Gender, Address, PhoneNumber) VALUES 
('John Doe', '1980-05-15', 'M', '123 Main St, Anytown', '555-0101'),
('Jane Smith', '1975-08-22', 'F', '456 Oak Ave, Somewhere', '555-0102'),
('Robert Johnson', '1990-03-10', 'M', '789 Pine Rd, Nowhere', '555-0103'),
('Emily Davis', '1988-11-30', 'F', '321 Elm Blvd, Anycity', '555-0104'),
('Michael Wilson', '1972-07-18', 'M', '654 Maple Ln, Yourtown', '555-0105');

-- Insert sample appointments
INSERT INTO Appointments (DoctorID, PatientID, AppointmentDate, AppointmentTime) VALUES 
(1, 1, '2023-06-15', '09:00:00'),
(2, 2, '2023-06-15', '10:30:00'),
(3, 3, '2023-06-16', '14:00:00'),
(4, 4, '2023-06-17', '11:15:00'),
(5, 5, '2023-06-18', '15:45:00');

-- Insert sample invoices
INSERT INTO Invoices (PatientID, InvoiceDate, TotalAmount, Status) VALUES 
(1, '2023-06-15', 250.00, 'Paid'),
(2, '2023-06-15', 180.00, 'Unpaid'),
(3, '2023-06-16', 320.00, 'Paid'),
(4, '2023-06-17', 150.00, 'Unpaid'),
(5, '2023-06-18', 275.00, 'Paid');
