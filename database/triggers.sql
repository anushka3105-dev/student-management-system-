-- ============================================================================
-- Triggers
-- ============================================================================
USE student_management_system;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- trg_exam_results_grade
-- Auto-assigns a letter grade whenever marks are inserted, based on the
-- percentage of max_marks for that exam.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_exam_results_grade $$
CREATE TRIGGER trg_exam_results_grade
BEFORE INSERT ON exam_results
FOR EACH ROW
BEGIN
    DECLARE v_max_marks DECIMAL(6,2);
    DECLARE v_pct DECIMAL(6,2);

    SELECT max_marks INTO v_max_marks FROM exams WHERE exam_id = NEW.exam_id;
    SET v_pct = (NEW.marks_obtained / v_max_marks) * 100;

    SET NEW.grade = CASE
        WHEN v_pct >= 90 THEN 'A+'
        WHEN v_pct >= 80 THEN 'A'
        WHEN v_pct >= 70 THEN 'B'
        WHEN v_pct >= 60 THEN 'C'
        WHEN v_pct >= 50 THEN 'D'
        ELSE 'F'
    END;
END $$

-- ----------------------------------------------------------------------------
-- trg_exam_results_no_overmark
-- Prevents marks_obtained from exceeding an exam's max_marks (defense in
-- depth beyond application-layer validation).
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_exam_results_no_overmark $$
CREATE TRIGGER trg_exam_results_no_overmark
BEFORE INSERT ON exam_results
FOR EACH ROW
BEGIN
    DECLARE v_max_marks DECIMAL(6,2);
    SELECT max_marks INTO v_max_marks FROM exams WHERE exam_id = NEW.exam_id;
    IF NEW.marks_obtained > v_max_marks THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'marks_obtained cannot exceed the exam max_marks';
    END IF;
END $$

-- ----------------------------------------------------------------------------
-- trg_enrollment_capacity_check
-- Blocks an INSERT into enrollments once a course offering is at capacity
-- (belt-and-suspenders alongside sp_enroll_student's own check).
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_enrollment_capacity_check $$
CREATE TRIGGER trg_enrollment_capacity_check
BEFORE INSERT ON enrollments
FOR EACH ROW
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_taken     INT;

    SELECT max_capacity INTO v_capacity
    FROM course_offerings WHERE offering_id = NEW.offering_id;

    SELECT COUNT(*) INTO v_taken
    FROM enrollments
    WHERE offering_id = NEW.offering_id AND status = 'enrolled';

    IF v_taken >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Course offering has reached maximum capacity';
    END IF;
END $$

-- ----------------------------------------------------------------------------
-- trg_student_status_on_graduation
-- When a student's current_semester is updated past their program's total
-- semesters, auto-flip their status to 'graduated'.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_student_status_on_graduation $$
CREATE TRIGGER trg_student_status_on_graduation
BEFORE UPDATE ON students
FOR EACH ROW
BEGIN
    DECLARE v_total_semesters TINYINT;

    SELECT total_semesters INTO v_total_semesters
    FROM programs WHERE program_id = NEW.program_id;

    IF NEW.current_semester > v_total_semesters AND OLD.status = 'active' THEN
        SET NEW.status = 'graduated';
    END IF;
END $$

-- ----------------------------------------------------------------------------
-- trg_fee_payment_audit
-- Logs completed payments to a lightweight audit table (created here) so
-- payment history survives even if a payment row is later corrected.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fee_payment_audit (
    audit_id     INT AUTO_INCREMENT PRIMARY KEY,
    payment_id   INT NOT NULL,
    student_id   INT NOT NULL,
    amount_paid  DECIMAL(10,2) NOT NULL,
    logged_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB $$

DROP TRIGGER IF EXISTS trg_fee_payment_audit $$
CREATE TRIGGER trg_fee_payment_audit
AFTER INSERT ON fee_payments
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' THEN
        INSERT INTO fee_payment_audit (payment_id, student_id, amount_paid)
        VALUES (NEW.payment_id, NEW.student_id, NEW.amount_paid);
    END IF;
END $$

DELIMITER ;
