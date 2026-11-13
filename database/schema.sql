-- =====================================================================
-- SHARE & REUSE - Database Schema (MySQL 8.0+)
-- Concept: Food & Reusable/Recycled Clothes Redistribution Network
-- Evaluated for: 5th Semester Computer Science / Engineering Project
-- Location Focus: Bagalkote & Surroundings
-- =====================================================================

CREATE DATABASE IF NOT EXISTS share_and_reuse
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE share_and_reuse;

-- -----------------------------------------------------
-- 1. Table: users
-- Roles: 'donor', 'organization', 'admin'
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM('donor', 'organization', 'admin') NOT NULL DEFAULT 'donor',
    donor_type ENUM('person', 'hotel', 'function_hall', 'college', 'company') NULL,
    address VARCHAR(255) NOT NULL DEFAULT '',
    city VARCHAR(100) NOT NULL DEFAULT 'Bagalkote',
    latitude DECIMAL(10, 6) DEFAULT 16.185300,
    longitude DECIMAL(10, 6) DEFAULT 75.696800,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_city (city)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 2. Table: organizations
-- Types: 'ngo', 'orphanage', 'old_age_home', 'food_bank', 'recycler'
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS organizations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    org_name VARCHAR(150) NOT NULL,
    org_type ENUM('ngo', 'orphanage', 'old_age_home', 'food_bank', 'recycler') NOT NULL,
    registration_no VARCHAR(100) NOT NULL,
    description TEXT,
    accepts_food BOOLEAN DEFAULT TRUE,
    accepts_clothes BOOLEAN DEFAULT TRUE,
    accepts_damaged_clothes BOOLEAN DEFAULT FALSE,
    capacity_note VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_org_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_org_type (org_type),
    INDEX idx_org_verified (is_verified)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 3. Table: donations
-- Categories: 'food', 'clothes'
-- Statuses: 'available', 'requested', 'accepted', 'in_transit', 'completed', 'cancelled', 'expired'
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    category ENUM('food', 'clothes') NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(8, 2) NOT NULL,
    quantity_unit VARCHAR(50) NOT NULL DEFAULT 'kg',
    status ENUM('available', 'requested', 'accepted', 'in_transit', 'completed', 'cancelled', 'expired') DEFAULT 'available',
    pickup_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Bagalkote',
    latitude DECIMAL(10, 6) NOT NULL DEFAULT 16.185300,
    longitude DECIMAL(10, 6) NOT NULL DEFAULT 75.696800,
    image_url VARCHAR(255),
    verification_pin VARCHAR(10) NOT NULL DEFAULT '1234',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    CONSTRAINT fk_donation_donor FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_donation_status (status),
    INDEX idx_donation_cat (category),
    INDEX idx_donation_coords (latitude, longitude)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 4. Table: food_details
-- Specialized for Urgent Food Matching & Safety Tracking
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS food_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL UNIQUE,
    food_type ENUM('cooked', 'packaged', 'bakery', 'raw_produce') NOT NULL DEFAULT 'cooked',
    preparation_time DATETIME NULL,
    expiry_deadline DATETIME NOT NULL,
    storage_condition ENUM('hot', 'ambient', 'refrigerated', 'frozen') NOT NULL DEFAULT 'ambient',
    allergen_info VARCHAR(255),
    is_urgent BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_food_donation FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
    INDEX idx_food_deadline (expiry_deadline),
    INDEX idx_food_urgent (is_urgent)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 5. Table: clothes_details
-- Segregation: Reusable (NGOs) vs Damaged (Recycling)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS clothes_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL UNIQUE,
    clothes_type ENUM('men', 'women', 'kids', 'winterwear', 'mixed') NOT NULL DEFAULT 'mixed',
    `condition` ENUM('reusable', 'damaged_recycling') NOT NULL DEFAULT 'reusable',
    target_age_group VARCHAR(50) DEFAULT 'all',
    clean_washed BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_clothes_donation FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
    INDEX idx_clothes_condition (`condition`)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 6. Table: donation_assignments
-- Manages Pickup Scheduling, Driver Info, and OTP Handover
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS donation_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL UNIQUE,
    organization_id INT NOT NULL,
    status ENUM('assigned', 'accepted', 'in_transit', 'completed', 'rejected') DEFAULT 'accepted',
    scheduled_pickup_time DATETIME NULL,
    actual_pickup_time DATETIME NULL,
    volunteer_name VARCHAR(100),
    volunteer_phone VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_assign_donation FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
    CONSTRAINT fk_assign_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    INDEX idx_assign_status (status)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- 7. Table: reports_feedback
-- Handles Complaints, Quality Notifications, Admin Resolution
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS reports_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT NOT NULL,
    reported_user_id INT NULL,
    donation_id INT NULL,
    report_type VARCHAR(50) NOT NULL,
    subject VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    status ENUM('pending', 'resolved', 'dismissed') DEFAULT 'pending',
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rep_reporter FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_rep_reported FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_rep_donation FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE SET NULL,
    INDEX idx_rep_status (status)
) ENGINE=InnoDB;
