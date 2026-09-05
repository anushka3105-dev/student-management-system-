-- ============================================================================
-- Sample Data
-- All demo accounts share the password: Password123!
-- (bcrypt hash below was generated once with Python's `bcrypt` package)
-- ============================================================================
USE student_management_system;

SET @DEMO_HASH = '$2b$12$1di/Ch7w8KzBAVsgicz5EOGe8kJpr3TrmYML8GH0ILfTPZ399GXZ2';

-- ----------------------------------------------------------------------------
-- Departments
-- ----------------------------------------------------------------------------
INSERT INTO departments (department_name, department_code, hod_name, established_year) VALUES
('Computer Science & Engineering', 'CSE', 'Dr. Ramesh Iyer', 1998),
('Electronics & Communication',    'ECE', 'Dr. Sunita Rao',  2001),
('Mechanical Engineering',         'ME',  'Dr. Ajay Kumar',  1995),
('Information Technology',         'IT',  'Dr. Meera Nair',  2005);

-- ----------------------------------------------------------------------------
-- Programs
-- ----------------------------------------------------------------------------
INSERT INTO programs (department_id, program_name, program_level, duration_years, total_semesters) VALUES
(1, 'B.Tech Computer Science',       'UG', 4, 8),
(1, 'M.Tech Computer Science',       'PG', 2, 4),
(2, 'B.Tech Electronics',            'UG', 4, 8),
(3, 'B.Tech Mechanical',             'UG', 4, 8),
(4, 'B.Tech Information Technology', 'UG', 4, 8);

-- ----------------------------------------------------------------------------
-- Users (1 admin, 4 faculty, 8 students)
-- ----------------------------------------------------------------------------
INSERT INTO users (username, email, password_hash, role) VALUES
('admin1',    'admin@smsuniversity.edu',    @DEMO_HASH, 'admin'),
('fac.iyer',  'r.iyer@smsuniversity.edu',   @DEMO_HASH, 'faculty'),
('fac.rao',   's.rao@smsuniversity.edu',    @DEMO_HASH, 'faculty'),
('fac.kumar', 'a.kumar@smsuniversity.edu',  @DEMO_HASH, 'faculty'),
('fac.nair',  'm.nair@smsuniversity.edu',   @DEMO_HASH, 'faculty'),
('stu.arjun', 'arjun.sharma@smsuniversity.edu',  @DEMO_HASH, 'student'),
('stu.priya', 'priya.singh@smsuniversity.edu',   @DEMO_HASH, 'student'),
('stu.rahul', 'rahul.verma@smsuniversity.edu',   @DEMO_HASH, 'student'),
('stu.anushka','anushka.gupta@smsuniversity.edu',@DEMO_HASH, 'student'),
('stu.karan', 'karan.mehta@smsuniversity.edu',   @DEMO_HASH, 'student'),
('stu.divya', 'divya.patel@smsuniversity.edu',   @DEMO_HASH, 'student'),
('stu.vikram','vikram.joshi@smsuniversity.edu',  @DEMO_HASH, 'student'),
('stu.neha',  'neha.reddy@smsuniversity.edu',    @DEMO_HASH, 'student');

-- ----------------------------------------------------------------------------
-- Faculty
-- ----------------------------------------------------------------------------
INSERT INTO faculty (user_id, department_id, employee_code, first_name, last_name, designation, qualification, phone, date_of_joining, salary) VALUES
(2, 1, 'EMP001', 'Ramesh', 'Iyer',  'Professor',           'PhD Computer Science', '9800000001', '2015-06-01', 145000),
(3, 2, 'EMP002', 'Sunita', 'Rao',   'Associate Professor', 'PhD Electronics',      '9800000002', '2017-07-15', 125000),
(4, 3, 'EMP003', 'Ajay',   'Kumar', 'Professor',            'PhD Mechanical',       '9800000003', '2012-01-10', 150000),
(5, 4, 'EMP004', 'Meera',  'Nair',  'Assistant Professor',  'M.Tech IT',            '9800000004', '2020-08-20',  95000);

-- ----------------------------------------------------------------------------
-- Students
-- ----------------------------------------------------------------------------
INSERT INTO students (user_id, program_id, enrollment_number, first_name, last_name, date_of_birth, gender, phone, address, admission_year, current_semester, guardian_name, guardian_phone, status) VALUES
(6,  1, 'CSE2023001', 'Arjun',    'Sharma', '2005-03-14', 'Male',   '9911100001', 'Bhopal, MP', 2023, 3, 'Rakesh Sharma', '9911100011', 'active'),
(7,  1, 'CSE2023002', 'Priya',    'Singh',  '2005-07-22', 'Female', '9911100002', 'Indore, MP', 2023, 3, 'Manoj Singh',   '9911100012', 'active'),
(8,  1, 'CSE2022003', 'Rahul',    'Verma',  '2004-11-05', 'Male',   '9911100003', 'Bhopal, MP', 2022, 5, 'Suresh Verma',  '9911100013', 'active'),
(9,  3, 'ECE2023004', 'Anushka',  'Gupta',  '2005-01-30', 'Female', '9911100004', 'Gwalior, MP', 2023, 3, 'Vinod Gupta',  '9911100014', 'active'),
(10, 4, 'ME2022005',  'Karan',    'Mehta',  '2004-05-18', 'Male',   '9911100005', 'Jabalpur, MP',2022, 5, 'Deepak Mehta', '9911100015', 'active'),
(11, 5, 'IT2023006',  'Divya',    'Patel',  '2005-09-09', 'Female', '9911100006', 'Bhopal, MP',  2023, 3, 'Nilesh Patel', '9911100016', 'active'),
(12, 1, 'CSE2021007', 'Vikram',   'Joshi',  '2003-12-25', 'Male',   '9911100007', 'Indore, MP',  2021, 7, 'Anil Joshi',   '9911100017', 'active'),
(13, 2, 'CSE2023008', 'Neha',     'Reddy',  '2005-02-17', 'Female', '9911100008', 'Bhopal, MP',  2023, 2, 'Kiran Reddy',  '9911100018', 'active');

-- ----------------------------------------------------------------------------
-- Courses
-- ----------------------------------------------------------------------------
INSERT INTO courses (department_id, course_code, course_name, credits, course_type, semester) VALUES
(1, 'CSE301', 'Database Management Systems', 4, 'core', 3),
(1, 'CSE302', 'Operating Systems',           4, 'core', 3),
(1, 'CSE303', 'Data Structures Lab',         2, 'lab',  3),
(1, 'CSE501', 'Machine Learning',            4, 'elective', 5),
(2, 'ECE301', 'Digital Signal Processing',   4, 'core', 3),
(3, 'ME501',  'Thermodynamics II',           3, 'core', 5),
(4, 'IT301',  'Web Technologies',            4, 'core', 3);

-- ----------------------------------------------------------------------------
-- Course offerings (2025-2026, odd semester)
-- ----------------------------------------------------------------------------
INSERT INTO course_offerings (course_id, faculty_id, academic_year, semester_term, max_capacity, room_number) VALUES
(1, 1, '2025-2026', 'odd', 60, 'CSE-101'),
(2, 1, '2025-2026', 'odd', 60, 'CSE-102'),
(3, 1, '2025-2026', 'odd', 30, 'CSE-LAB1'),
(4, 1, '2025-2026', 'odd', 40, 'CSE-201'),
(5, 2, '2025-2026', 'odd', 50, 'ECE-101'),
(6, 3, '2025-2026', 'odd', 55, 'ME-101'),
(7, 4, '2025-2026', 'odd', 45, 'IT-101');

-- ----------------------------------------------------------------------------
-- Enrollments
-- ----------------------------------------------------------------------------
INSERT INTO enrollments (student_id, offering_id, status) VALUES
(1, 1, 'enrolled'), (1, 2, 'enrolled'), (1, 3, 'enrolled'),
(2, 1, 'enrolled'), (2, 2, 'enrolled'), (2, 3, 'enrolled'),
(3, 4, 'enrolled'),
(4, 5, 'enrolled'),
(5, 6, 'enrolled'),
(6, 7, 'enrolled'),
(7, 4, 'enrolled'),
(8, 1, 'enrolled');

-- ----------------------------------------------------------------------------
-- Exams
-- ----------------------------------------------------------------------------
INSERT INTO exams (offering_id, exam_name, exam_type, exam_date, max_marks, weightage_pct) VALUES
(1, 'Midterm', 'midterm', '2026-02-15', 30, 30),
(1, 'Final',   'final',   '2026-04-25', 70, 70),
(2, 'Midterm', 'midterm', '2026-02-16', 30, 30),
(2, 'Final',   'final',   '2026-04-26', 70, 70),
(4, 'Quiz 1',  'quiz',    '2026-01-30', 10, 10),
(4, 'Final',   'final',   '2026-04-27', 90, 90);

-- ----------------------------------------------------------------------------
-- Exam results
-- ----------------------------------------------------------------------------
INSERT INTO exam_results (exam_id, student_id, marks_obtained, remarks) VALUES
(1, 1, 26, 'Good grasp of normalization'),
(1, 2, 28, 'Excellent'),
(1, 8, 19, 'Needs revision on joins'),
(3, 1, 24, NULL),
(3, 2, 27, NULL),
(3, 8, 22, NULL),
(5, 3, 9, NULL),
(5, 7, 8, NULL);

-- ----------------------------------------------------------------------------
-- Attendance (sample week)
-- ----------------------------------------------------------------------------
INSERT INTO attendance (enrollment_id, class_date, status, marked_by) VALUES
(1, '2026-07-14', 'present', 1),
(1, '2026-07-15', 'present', 1),
(1, '2026-07-16', 'absent',  1),
(2, '2026-07-14', 'present', 1),
(2, '2026-07-15', 'late',    1),
(2, '2026-07-16', 'present', 1);

-- ----------------------------------------------------------------------------
-- Fee structure
-- ----------------------------------------------------------------------------
INSERT INTO fee_structure (program_id, semester, tuition_fee, hostel_fee, other_fee, due_date, academic_year) VALUES
(1, 3, 85000, 30000, 5000, '2026-08-15', '2025-2026'),
(3, 3, 75000, 30000, 5000, '2026-08-15', '2025-2026'),
(4, 5, 70000, 25000, 5000, '2026-08-15', '2025-2026'),
(5, 3, 72000, 25000, 5000, '2026-08-15', '2025-2026');

-- ----------------------------------------------------------------------------
-- Fee payments
-- ----------------------------------------------------------------------------
INSERT INTO fee_payments (student_id, fee_structure_id, amount_paid, payment_date, payment_mode, transaction_ref, status) VALUES
(1, 1, 60000, '2026-06-01', 'upi',           'TXN100001', 'completed'),
(2, 1, 120000,'2026-06-02', 'bank_transfer', 'TXN100002', 'completed'),
(8, 1, 30000, '2026-06-05', 'card',          'TXN100003', 'completed');

-- ----------------------------------------------------------------------------
-- Announcements
-- ----------------------------------------------------------------------------
INSERT INTO announcements (posted_by, title, body, target_role, department_id, expires_at) VALUES
(1, 'Semester Fee Due Date Extended', 'The due date for semester fee payment has been extended by two weeks.', 'student', NULL, '2026-09-01 00:00:00'),
(1, 'Faculty Meeting Rescheduled', 'The monthly faculty meeting is moved to next Friday, 3 PM, Seminar Hall.', 'faculty', NULL, '2026-08-01 00:00:00'),
(2, 'DBMS Assignment 2 Released', 'Assignment 2 on normalization is now available on the course page. Due in two weeks.', 'student', 1, '2026-08-10 00:00:00');
