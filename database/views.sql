-- ============================================================================
-- Views
-- ============================================================================
USE student_management_system;

-- ----------------------------------------------------------------------------
-- vw_student_directory — flattened student info for admin/faculty listing
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_student_directory AS
SELECT
    s.student_id,
    s.enrollment_number,
    CONCAT(s.first_name, ' ', s.last_name) AS full_name,
    u.email,
    u.is_active,
    p.program_name,
    d.department_name,
    s.current_semester,
    s.status
FROM students s
JOIN users u      ON u.user_id = s.user_id
JOIN programs p   ON p.program_id = s.program_id
JOIN departments d ON d.department_id = p.department_id;

-- ----------------------------------------------------------------------------
-- vw_course_offering_summary — enrollment fill-rate per offering
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_course_offering_summary AS
SELECT
    co.offering_id,
    c.course_code,
    c.course_name,
    CONCAT(f.first_name, ' ', f.last_name) AS faculty_name,
    co.academic_year,
    co.semester_term,
    co.max_capacity,
    COUNT(e.enrollment_id) AS enrolled_count,
    co.max_capacity - COUNT(e.enrollment_id) AS seats_remaining
FROM course_offerings co
JOIN courses c   ON c.course_id = co.course_id
JOIN faculty f   ON f.faculty_id = co.faculty_id
LEFT JOIN enrollments e ON e.offering_id = co.offering_id AND e.status = 'enrolled'
GROUP BY co.offering_id, c.course_code, c.course_name, faculty_name,
         co.academic_year, co.semester_term, co.max_capacity;

-- ----------------------------------------------------------------------------
-- vw_student_attendance_pct — attendance percentage per student per offering
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_student_attendance_pct AS
SELECT
    e.student_id,
    e.offering_id,
    COUNT(a.attendance_id) AS total_sessions,
    SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) AS sessions_attended,
    ROUND(
        SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) * 100.0
        / NULLIF(COUNT(a.attendance_id), 0), 2
    ) AS attendance_percentage
FROM enrollments e
LEFT JOIN attendance a ON a.enrollment_id = e.enrollment_id
GROUP BY e.student_id, e.offering_id;

-- ----------------------------------------------------------------------------
-- vw_student_fee_balance — outstanding balance per student per fee structure
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_student_fee_balance AS
SELECT
    s.student_id,
    s.enrollment_number,
    fs.fee_structure_id,
    fs.academic_year,
    fs.semester,
    (fs.tuition_fee + fs.hostel_fee + fs.other_fee) AS total_due,
    COALESCE(SUM(fp.amount_paid), 0) AS total_paid,
    (fs.tuition_fee + fs.hostel_fee + fs.other_fee) - COALESCE(SUM(fp.amount_paid), 0) AS balance_due,
    fs.due_date
FROM students s
JOIN fee_structure fs ON fs.program_id = s.program_id
LEFT JOIN fee_payments fp
    ON fp.student_id = s.student_id
    AND fp.fee_structure_id = fs.fee_structure_id
    AND fp.status = 'completed'
GROUP BY s.student_id, s.enrollment_number, fs.fee_structure_id,
         fs.academic_year, fs.semester, total_due, fs.due_date;

-- ----------------------------------------------------------------------------
-- vw_faculty_workload — course count and total students taught per faculty
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_faculty_workload AS
SELECT
    f.faculty_id,
    CONCAT(f.first_name, ' ', f.last_name) AS faculty_name,
    d.department_name,
    COUNT(DISTINCT co.offering_id) AS courses_taught,
    COUNT(e.enrollment_id) AS total_students
FROM faculty f
JOIN departments d ON d.department_id = f.department_id
LEFT JOIN course_offerings co ON co.faculty_id = f.faculty_id
LEFT JOIN enrollments e ON e.offering_id = co.offering_id AND e.status = 'enrolled'
GROUP BY f.faculty_id, faculty_name, d.department_name;

-- ----------------------------------------------------------------------------
-- vw_top_performers — window-function ranked students by weighted average
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_top_performers AS
SELECT
    student_id,
    offering_id,
    weighted_percentage,
    RANK() OVER (PARTITION BY offering_id ORDER BY weighted_percentage DESC) AS rank_in_course
FROM (
    SELECT
        er.student_id,
        e.offering_id,
        SUM((er.marks_obtained / e.max_marks) * e.weightage_pct) AS weighted_percentage
    FROM exam_results er
    JOIN exams e ON e.exam_id = er.exam_id
    GROUP BY er.student_id, e.offering_id
) t;
