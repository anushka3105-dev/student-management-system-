-- ============================================================================
-- Student Management System — Database Schema
-- Engine: MySQL 8.0+
-- Normalized to 3NF. 14 tables covering identity, academics, attendance,
-- examinations, fees and communication.
-- ============================================================================

DROP DATABASE IF EXISTS student_management_system;
CREATE DATABASE student_management_system
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_management_system;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. departments
-- ----------------------------------------------------------------------------
CREATE TABLE departments (
    department_id     INT AUTO_INCREMENT PRIMARY KEY,
    department_name   VARCHAR(100) NOT NULL UNIQUE,
    department_code   VARCHAR(10)  NOT NULL UNIQUE,
    hod_name           VARCHAR(100),
    established_year  YEAR,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. programs (degree programs offered by a department)
-- ----------------------------------------------------------------------------
CREATE TABLE programs (
    program_id       INT AUTO_INCREMENT PRIMARY KEY,
    department_id    INT NOT NULL,
    program_name     VARCHAR(100) NOT NULL,
    program_level    ENUM('UG', 'PG', 'PhD') NOT NULL DEFAULT 'UG',
    duration_years   TINYINT NOT NULL CHECK (duration_years BETWEEN 1 AND 6),
    total_semesters  TINYINT NOT NULL CHECK (total_semesters BETWEEN 1 AND 12),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_programs_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_program_dept (department_id, program_name)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. users (auth identity shared by admin / faculty / student)
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(50)  NOT NULL UNIQUE,
    email          VARCHAR(120) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    role           ENUM('admin', 'faculty', 'student') NOT NULL,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    last_login     DATETIME NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. faculty
-- ----------------------------------------------------------------------------
CREATE TABLE faculty (
    faculty_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL UNIQUE,
    department_id    INT NOT NULL,
    employee_code    VARCHAR(20) NOT NULL UNIQUE,
    first_name       VARCHAR(60) NOT NULL,
    last_name        VARCHAR(60) NOT NULL,
    designation      VARCHAR(60) NOT NULL DEFAULT 'Assistant Professor',
    qualification    VARCHAR(120),
    phone            VARCHAR(15),
    date_of_joining  DATE NOT NULL,
    salary           DECIMAL(10,2) CHECK (salary >= 0),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_faculty_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_faculty_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 5. students
-- ----------------------------------------------------------------------------
CREATE TABLE students (
    student_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL UNIQUE,
    program_id        INT NOT NULL,
    enrollment_number VARCHAR(20) NOT NULL UNIQUE,
    first_name        VARCHAR(60) NOT NULL,
    last_name         VARCHAR(60) NOT NULL,
    date_of_birth     DATE NOT NULL,
    gender            ENUM('Male', 'Female', 'Other') NOT NULL,
    phone             VARCHAR(15),
    address            VARCHAR(255),
    admission_year    YEAR NOT NULL,
    current_semester  TINYINT NOT NULL DEFAULT 1 CHECK (current_semester BETWEEN 1 AND 12),
    guardian_name     VARCHAR(100),
    guardian_phone    VARCHAR(15),
    status             ENUM('active', 'graduated', 'suspended', 'dropped') NOT NULL DEFAULT 'active',
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_students_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_students_program
        FOREIGN KEY (program_id) REFERENCES programs(program_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 6. courses (subject catalogue)
-- ----------------------------------------------------------------------------
CREATE TABLE courses (
    course_id      INT AUTO_INCREMENT PRIMARY KEY,
    department_id  INT NOT NULL,
    course_code    VARCHAR(15) NOT NULL UNIQUE,
    course_name    VARCHAR(150) NOT NULL,
    credits        TINYINT NOT NULL CHECK (credits BETWEEN 1 AND 6),
    course_type    ENUM('core', 'elective', 'lab') NOT NULL DEFAULT 'core',
    semester        TINYINT NOT NULL CHECK (semester BETWEEN 1 AND 12),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_courses_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 7. course_offerings (a course taught by a faculty member in a given term)
-- ----------------------------------------------------------------------------
CREATE TABLE course_offerings (
    offering_id     INT AUTO_INCREMENT PRIMARY KEY,
    course_id       INT NOT NULL,
    faculty_id      INT NOT NULL,
    academic_year   VARCHAR(9) NOT NULL,          -- e.g. '2025-2026'
    semester_term   ENUM('odd', 'even') NOT NULL,
    max_capacity    INT NOT NULL DEFAULT 60 CHECK (max_capacity > 0),
    room_number     VARCHAR(20),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_offering_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_offering_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_offering (course_id, academic_year, semester_term, faculty_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 8. enrollments (student <-> course_offering, many-to-many resolved)
-- ----------------------------------------------------------------------------
CREATE TABLE enrollments (
    enrollment_id    INT AUTO_INCREMENT PRIMARY KEY,
    student_id       INT NOT NULL,
    offering_id      INT NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    status            ENUM('enrolled', 'completed', 'dropped') NOT NULL DEFAULT 'enrolled',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enroll_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_enroll_offering
        FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY uq_enrollment (student_id, offering_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 9. attendance (per-session record against an enrollment)
-- ----------------------------------------------------------------------------
CREATE TABLE attendance (
    attendance_id  INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id  INT NOT NULL,
    class_date     DATE NOT NULL,
    status          ENUM('present', 'absent', 'late', 'excused') NOT NULL,
    marked_by      INT NOT NULL,                 -- faculty_id
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_enrollment
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attendance_faculty
        FOREIGN KEY (marked_by) REFERENCES faculty(faculty_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_attendance_day (enrollment_id, class_date)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 10. exams
-- ----------------------------------------------------------------------------
CREATE TABLE exams (
    exam_id       INT AUTO_INCREMENT PRIMARY KEY,
    offering_id   INT NOT NULL,
    exam_name     VARCHAR(100) NOT NULL,          -- 'Midterm', 'Final', 'Quiz 1'
    exam_type     ENUM('quiz', 'midterm', 'final', 'assignment') NOT NULL,
    exam_date     DATE NOT NULL,
    max_marks     DECIMAL(6,2) NOT NULL CHECK (max_marks > 0),
    weightage_pct DECIMAL(5,2) NOT NULL CHECK (weightage_pct BETWEEN 0 AND 100),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_offering
        FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 11. exam_results
-- ----------------------------------------------------------------------------
CREATE TABLE exam_results (
    result_id      INT AUTO_INCREMENT PRIMARY KEY,
    exam_id        INT NOT NULL,
    student_id     INT NOT NULL,
    marks_obtained DECIMAL(6,2) NOT NULL CHECK (marks_obtained >= 0),
    grade           CHAR(2),
    remarks         VARCHAR(255),
    graded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_result_exam
        FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_result_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY uq_result (exam_id, student_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 12. fee_structure (defines what each program/semester owes)
-- ----------------------------------------------------------------------------
CREATE TABLE fee_structure (
    fee_structure_id INT AUTO_INCREMENT PRIMARY KEY,
    program_id       INT NOT NULL,
    semester          TINYINT NOT NULL CHECK (semester BETWEEN 1 AND 12),
    tuition_fee       DECIMAL(10,2) NOT NULL CHECK (tuition_fee >= 0),
    hostel_fee        DECIMAL(10,2) NOT NULL DEFAULT 0,
    other_fee         DECIMAL(10,2) NOT NULL DEFAULT 0,
    due_date           DATE NOT NULL,
    academic_year     VARCHAR(9) NOT NULL,
    CONSTRAINT fk_feestructure_program
        FOREIGN KEY (program_id) REFERENCES programs(program_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY uq_fee_structure (program_id, semester, academic_year)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 13. fee_payments
-- ----------------------------------------------------------------------------
CREATE TABLE fee_payments (
    payment_id        INT AUTO_INCREMENT PRIMARY KEY,
    student_id        INT NOT NULL,
    fee_structure_id  INT NOT NULL,
    amount_paid        DECIMAL(10,2) NOT NULL CHECK (amount_paid >= 0),
    payment_date       DATE NOT NULL DEFAULT (CURRENT_DATE),
    payment_mode       ENUM('cash', 'card', 'upi', 'bank_transfer') NOT NULL,
    transaction_ref    VARCHAR(50) UNIQUE,
    status              ENUM('pending', 'completed', 'failed', 'refunded') NOT NULL DEFAULT 'completed',
    CONSTRAINT fk_payment_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_payment_feestructure
        FOREIGN KEY (fee_structure_id) REFERENCES fee_structure(fee_structure_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 14. announcements
-- ----------------------------------------------------------------------------
CREATE TABLE announcements (
    announcement_id  INT AUTO_INCREMENT PRIMARY KEY,
    posted_by         INT NOT NULL,               -- user_id (admin or faculty)
    title              VARCHAR(150) NOT NULL,
    body               TEXT NOT NULL,
    target_role       ENUM('all', 'admin', 'faculty', 'student') NOT NULL DEFAULT 'all',
    department_id     INT NULL,
    posted_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at         DATETIME NULL,
    CONSTRAINT fk_announcement_user
        FOREIGN KEY (posted_by) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_announcement_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
