CREATE DATABASE IF NOT EXISTS HospitalManagementSystem;
USE HospitalManagementSystem;
drop database HospitalmanagementSystem;
show tables;

-- Patients Table
CREATE TABLE patients (
    patient_id INT PRIMARY KEY auto_increment,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age>0),
    gender ENUM('M','F','Other'),
    admission_date DATE,
    contact_no VARCHAR(15)
);

-- Doctors Table
CREATE TABLE doctors (
    doctor_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    contact_no VARCHAR(15) UNIQUE
);

-- Services Table
CREATE TABLE services (
    service_id VARCHAR(10) PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    cost decimal(7,2)
);

-- Appointments Table
CREATE TABLE appointments (
    appt_id VARCHAR(10) PRIMARY KEY,
    patient_id INT,
    doctor_id VARCHAR(10),
    date DATE,
    diagnosis VARCHAR(255),
    consulting_charge DECIMAL(7,2) DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
);

-- Billing Table
CREATE TABLE billing (
    bill_id VARCHAR(10) PRIMARY KEY,
    patient_id INT,
    total_amount decimal(10,2),
    billing_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Temporary Table for service usage
CREATE TABLE temp_service_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    service_id VARCHAR(20) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Billed services for invoice generation
CREATE TABLE billed_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id VARCHAR(10),
    patient_id INT,
    service_id VARCHAR(10),
    service_name VARCHAR(100),
    cost DECIMAL(10,2),
    billed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES billing(bill_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE SET NULL
);

select * from patients;
select * from doctors;
select * from services;
select * from appointments;
select * from billing;
select * from temp_service_usage;
select * from billed_services;

DELETE FROM patients;
DELETE FROM doctors;
DELETE FROM services;
DELETE FROM appointments;
DELETE FROM billing;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE appointments;
TRUNCATE TABLE billing;
TRUNCATE TABLE patients;
TRUNCATE TABLE doctors;
TRUNCATE TABLE services;
TRUNCATE TABLE temp_service_usage;
TRUNCATE TABLE billed_services;
SET FOREIGN_KEY_CHECKS = 1;

-- Task Discription 8 : Implement data-based filtering 
select * from appointments where date = curdate();
select * from appointments where date >= date_sub(curdate(), interval 6 day) and date <= curdate();
select * from appointments where date >= date_sub(curdate(), interval 10 day) and date < curdate();

-- Task Description 11 : Insert billing details to the billing table with current date
INSERT INTO billing (bill_id, patient_id, total_amount, billing_date) VALUES ('B001', 1001, 1200.50, CURDATE());

-- Task Description 12 : Fetch complete patient history including doctor visits and services used
SELECT
    p.patient_id,
    p.name AS patient_name,
    p.age,
    p.gender,
    p.admission_date,
    p.contact_no,
    a.appt_id,
    a.date AS appointment_date,
    d.doctor_id,
    d.name AS doctor_name,
    d.specialization,
    a.diagnosis,
    a.consulting_charge,
    temp.service_id,
    temp.service_name,
    temp.cost AS service_cost,
    temp.created_at AS service_used_at
FROM
    patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
LEFT JOIN temp_service_usage temp ON p.patient_id = temp.patient_id
WHERE
    p.patient_id = 1001
ORDER BY
    a.date, temp.created_at;
    
-- Task Descriptiom : Add reporting features: daily visits, most consulted doctors - SQL Aggregates
-- 1. Daily visits report
select date, count(*) as visit_count from appointments group by date order by date desc;

-- 2. Most consulted report
select
	d.doctor_id, 
    d.name, 
    d.specialization, 
    count(*) as num_appointments 
from 
	appointments a 
join doctors d on a.doctor_id = d.doctor_id
group by
	d.doctor_id,
    d.name,
    d.specialization
order by
	num_appointments
desc;
 

select a.appt_id, p.name as patient_name, d.name as doctor_name, a.date, a.diagnosis, a.consulting_charge from appointments a join patients p on a.patient_id = p.patient_id
left join doctors d on a.doctor_id = d.doctor_id;

select b.bill_id, p.name as patient_name, bs.service_name, bs.cost, b.total_amount, b.billing_date from billing b join patients p on b.patient_id = p.patient_id join billed_services bs on b.bill_id = bs.bill_id order by b.billing_date desc;

select p.name as patient_name, temp.service_name, temp.cost, temp.created_at from temp_service_usage temp join patients p on temp.patient_id = p.patient_id;

select d.name as doctor_name, count(a.appt_id) as totot_appointments from doctors d left join appointments a on d.doctor_id = a.doctor_id group by d.doctor_id;




