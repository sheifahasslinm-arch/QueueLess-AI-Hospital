-- =============================================================
-- QUEUELESS AI HOSPITAL — DATABASE SCHEMA + SEED DATA
-- =============================================================
--
-- Run this whole file against MySQL (e.g. in phpMyAdmin's SQL
-- tab, or `mysql -u root -p < schema.sql`) to create the
-- database from scratch with realistic sample data:
-- several services, each with MULTIPLE doctors, so doctor
-- selection actually looks and behaves like a real hospital.
--
-- WARNING: this drops and recreates the database. Back up
-- first if you already have real data you care about.
-- =============================================================

DROP DATABASE IF EXISTS queueless_hospital;
CREATE DATABASE queueless_hospital;
USE queueless_hospital;

-- =============================================================
-- USERS  (patients + hospital staff/admin accounts)
-- =============================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'admin') NOT NULL DEFAULT 'patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- SERVICES  (hospital departments / treatment types)
-- =============================================================

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(120) NOT NULL,
    description VARCHAR(255) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1
);

-- =============================================================
-- DOCTORS  (each belongs to one service/department)
-- =============================================================

CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    specialization VARCHAR(150) NOT NULL,
    service_id INT NOT NULL,
    is_available TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (service_id) REFERENCES services(id)
        ON DELETE CASCADE
);

-- =============================================================
-- TOKENS  (a patient's place in a specific doctor's queue)
-- =============================================================

CREATE TABLE tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_number INT NOT NULL,
    user_id INT NOT NULL,
    service_id INT NOT NULL,
    doctor_id INT NOT NULL,
    status ENUM('waiting', 'called', 'completed', 'skipped', 'cancelled')
        NOT NULL DEFAULT 'waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    called_at TIMESTAMP NULL DEFAULT NULL,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id)
        ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        ON DELETE CASCADE
);

-- =============================================================
-- SEED DATA — SERVICES
-- =============================================================

INSERT INTO services (service_name, description, is_active) VALUES
('General Medicine', 'Routine check-ups, common illnesses, and general health concerns.', 1),
('Cardiology', 'Heart health, blood pressure, and cardiovascular consultations.', 1),
('Pediatrics', 'Medical care for infants, children, and teenagers.', 1),
('Dermatology', 'Skin, hair, and nail conditions.', 1),
('Orthopedics', 'Bones, joints, muscles, and sports injuries.', 1),
('Dental Care', 'Dental check-ups, cleanings, and oral health treatment.', 1);

-- =============================================================
-- SEED DATA — DOCTORS
-- (Multiple doctors per service, so patients get real choice.)
-- =============================================================

-- General Medicine (service_id = 1)
INSERT INTO doctors (name, specialization, service_id, is_available) VALUES
('Dr. Amara Osei', 'General Physician', 1, 1),
('Dr. Liam Chen', 'Family Medicine', 1, 1),
('Dr. Priya Nair', 'Internal Medicine', 1, 1);

-- Cardiology (service_id = 2)
INSERT INTO doctors (name, specialization, service_id, is_available) VALUES
('Dr. Marcus Webb', 'Cardiologist', 2, 1),
('Dr. Elena Rossi', 'Interventional Cardiology', 2, 1);

-- Pediatrics (service_id = 3)
INSERT INTO doctors (name, specialization, service_id, is_available) VALUES
('Dr. Sofia Martinez', 'Pediatrician', 3, 1),
('Dr. James Okafor', 'Pediatric Care', 3, 1),
('Dr. Hana Suzuki', 'Neonatal & Child Health', 3, 1);

-- Dermatology (service_id = 4)
INSERT INTO doctors (name, specialization, service_id, is_available) VALUES
('Dr. Grace Kim', 'Dermatologist', 4, 1),
('Dr. Noah Bennett', 'Cosmetic Dermatology', 4, 1);

-- Orthopedics (service_id = 5)
INSERT INTO doctors (name, specialization, service_id, is_available) VALUES
('Dr. Victor Adeyemi', 'Orthopedic Surgeon', 5, 1),
('Dr. Clara Jensen', 'Sports Medicine', 5, 1);

-- Dental Care (service_id = 6)
INSERT INTO doctors (name, specialization, service_id, is_available) VALUES
('Dr. Omar Farouk', 'General Dentist', 6, 1),
('Dr. Ines Duarte', 'Orthodontics', 6, 1);

-- =============================================================