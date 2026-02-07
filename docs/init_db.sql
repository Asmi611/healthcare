CREATE DATABASE IF NOT EXISTS healthcare_db;
USE healthcare_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  role ENUM('doctor','patient','pharmacy') NOT NULL,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  phone VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT,
  doctor_id INT,
  date DATE,
  time TIME,
  status VARCHAR(50),
  FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS prescriptions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  appointment_id INT,
  doctor_id INT,
  patient_id INT,
  medicines TEXT,
  diagnosis TEXT
);

CREATE TABLE IF NOT EXISTS pharmacy_orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prescription_id INT,
  pharmacy_id INT,
  status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  message TEXT,
  is_read TINYINT DEFAULT 0,
  created_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

