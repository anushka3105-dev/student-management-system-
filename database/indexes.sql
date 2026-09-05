-- ============================================================================
-- Indexes — beyond PK / UNIQUE constraints already declared in schema.sql
-- ============================================================================
USE student_management_system;

-- Lookups by role during auth
CREATE INDEX idx_users_role ON users(role);

-- Frequent filters: student status, program, semester
CREATE INDEX idx_students_status ON students(status);
CREATE INDEX idx_students_program_sem ON students(program_id, current_semester);

-- Faculty by department (staff directory / dropdowns)
CREATE INDEX idx_faculty_department ON faculty(department_id);

-- Course catalogue browsing
CREATE INDEX idx_courses_department_sem ON courses(department_id, semester);

-- Offerings by term (timetable / registration screens)
CREATE INDEX idx_offerings_year_term ON course_offerings(academic_year, semester_term);
CREATE INDEX idx_offerings_faculty ON course_offerings(faculty_id);

-- Enrollment lookups both directions
CREATE INDEX idx_enrollments_student ON enrollments(student_id, status);
CREATE INDEX idx_enrollments_offering ON enrollments(offering_id, status);

-- Attendance reporting by date range
CREATE INDEX idx_attendance_date ON attendance(class_date);
CREATE INDEX idx_attendance_status ON attendance(enrollment_id, status);

-- Exam / result reporting
CREATE INDEX idx_exams_offering ON exams(offering_id, exam_type);
CREATE INDEX idx_results_student ON exam_results(student_id);

-- Fees: overdue / outstanding queries
CREATE INDEX idx_feestructure_program_sem ON fee_structure(program_id, semester);
CREATE INDEX idx_payments_student_status ON fee_payments(student_id, status);
CREATE INDEX idx_payments_date ON fee_payments(payment_date);

-- Announcements feed, most recent first, filtered by audience
CREATE INDEX idx_announcements_role_date ON announcements(target_role, posted_at);
