-- Simplified database schema (MySQL)
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  role ENUM('doctor','patient','pharmacy') NOT NULL,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255)
);

CREATE TABLE appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT,
  doctor_id INT,
  date DATE,
  time TIME,
  status VARCHAR(50)
);

CREATE TABLE prescriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  appointment_id INT,
  doctor_id INT,
  patient_id INT,
  medicines TEXT,
  diagnosis TEXT
);

CREATE TABLE pharmacy_orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prescription_id INT,
  pharmacy_id INT,
  status VARCHAR(50)
);
