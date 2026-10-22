CREATE DATABASE IF NOT EXISTS quan_ly_hoc_sinh_thpt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE quan_ly_hoc_sinh_thpt;

CREATE TABLE IF NOT EXISTS teachers (
 teacher_id INT AUTO_INCREMENT PRIMARY KEY, teacher_code VARCHAR(20) NOT NULL UNIQUE,
 full_name VARCHAR(100) NOT NULL, phone VARCHAR(20), email VARCHAR(100), address VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS school_years (
 school_year_id INT AUTO_INCREMENT PRIMARY KEY, year_name VARCHAR(20) NOT NULL UNIQUE,
 start_date DATE, end_date DATE
);
CREATE TABLE IF NOT EXISTS school_classes (
 class_id INT AUTO_INCREMENT PRIMARY KEY, class_name VARCHAR(30) NOT NULL,
 grade_level TINYINT NOT NULL, school_year_id INT, homeroom_teacher_id INT,
 UNIQUE KEY uq_class_year(class_name, school_year_id),
 FOREIGN KEY (school_year_id) REFERENCES school_years(school_year_id) ON DELETE SET NULL,
 FOREIGN KEY (homeroom_teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
 CHECK (grade_level IN (10,11,12))
);
CREATE TABLE IF NOT EXISTS students (
 student_id INT AUTO_INCREMENT PRIMARY KEY, student_code VARCHAR(20) NOT NULL UNIQUE,
 full_name VARCHAR(100) NOT NULL, date_of_birth DATE, gender ENUM('Nam','Nữ','Khác') DEFAULT 'Nam',
 phone VARCHAR(20), email VARCHAR(100), address VARCHAR(255), parent_name VARCHAR(100),
 parent_phone VARCHAR(20), class_id INT, enrollment_date DATE,
 status ENUM('Đang học','Bảo lưu','Đã chuyển trường','Đã tốt nghiệp') NOT NULL DEFAULT 'Đang học',
 notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (class_id) REFERENCES school_classes(class_id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS subjects (
 subject_id INT AUTO_INCREMENT PRIMARY KEY, subject_code VARCHAR(20) NOT NULL UNIQUE,
 subject_name VARCHAR(100) NOT NULL, description VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS semesters (
 semester_id INT AUTO_INCREMENT PRIMARY KEY, school_year_id INT NOT NULL,
 semester_name ENUM('Học kỳ 1','Học kỳ 2') NOT NULL,
 UNIQUE KEY uq_semester(school_year_id, semester_name),
 FOREIGN KEY (school_year_id) REFERENCES school_years(school_year_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS grades (
 grade_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, subject_id INT NOT NULL,
 semester_id INT NOT NULL, oral_score DECIMAL(4,2), fifteen_min_score DECIMAL(4,2),
 midterm_score DECIMAL(4,2), final_score DECIMAL(4,2), average_score DECIMAL(4,2),
 UNIQUE KEY uq_student_subject_semester(student_id, subject_id, semester_id),
 FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
 FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
 FOREIGN KEY (semester_id) REFERENCES semesters(semester_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS attendance (
 attendance_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, attendance_date DATE NOT NULL,
 attendance_status ENUM('Có mặt','Vắng có phép','Vắng không phép','Đi muộn') NOT NULL, note VARCHAR(255),
 UNIQUE KEY uq_attendance(student_id, attendance_date),
 FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS conduct_records (
 record_id INT AUTO_INCREMENT PRIMARY KEY, student_id INT NOT NULL, record_date DATE NOT NULL,
 record_type ENUM('Khen thưởng','Kỷ luật') NOT NULL, description VARCHAR(500) NOT NULL,
 FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS users (
 user_id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL, full_name VARCHAR(100) NOT NULL,
 role ENUM('admin','staff','teacher') NOT NULL DEFAULT 'staff',
 is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_student_name ON students(full_name);
CREATE INDEX idx_student_class ON students(class_id);
