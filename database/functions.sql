-- ============================================================================
-- Functions
-- ============================================================================
USE student_management_system;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- fn_letter_grade(pct) — maps a percentage to a letter grade
-- ----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_letter_grade $$
CREATE FUNCTION fn_letter_grade(p_pct DECIMAL(6,2))
RETURNS CHAR(2)
DETERMINISTIC
BEGIN
    RETURN CASE
        WHEN p_pct >= 90 THEN 'A+'
        WHEN p_pct >= 80 THEN 'A'
        WHEN p_pct >= 70 THEN 'B'
        WHEN p_pct >= 60 THEN 'C'
        WHEN p_pct >= 50 THEN 'D'
        ELSE 'F'
    END;
END $$

-- ----------------------------------------------------------------------------
-- fn_student_age(dob) — current age in years for a given date of birth
-- ----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_student_age $$
CREATE FUNCTION fn_student_age(p_dob DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN TIMESTAMPDIFF(YEAR, p_dob, CURDATE());
END $$

-- ----------------------------------------------------------------------------
-- fn_attendance_percentage(enrollment_id) — attendance % for one enrollment
-- ----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_attendance_percentage $$
CREATE FUNCTION fn_attendance_percentage(p_enrollment_id INT)
RETURNS DECIMAL(5,2)
READS SQL DATA
BEGIN
    DECLARE v_total INT;
    DECLARE v_present INT;

    SELECT COUNT(*), SUM(CASE WHEN status IN ('present','late') THEN 1 ELSE 0 END)
    INTO v_total, v_present
    FROM attendance
    WHERE enrollment_id = p_enrollment_id;

    IF v_total = 0 OR v_total IS NULL THEN
        RETURN 0.00;
    END IF;

    RETURN ROUND((v_present / v_total) * 100, 2);
END $$

-- ----------------------------------------------------------------------------
-- fn_outstanding_balance(student_id, fee_structure_id) — remaining fee due
-- ----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_outstanding_balance $$
CREATE FUNCTION fn_outstanding_balance(p_student_id INT, p_fee_structure_id INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_total_due DECIMAL(10,2);
    DECLARE v_total_paid DECIMAL(10,2);

    SELECT (tuition_fee + hostel_fee + other_fee) INTO v_total_due
    FROM fee_structure WHERE fee_structure_id = p_fee_structure_id;

    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM fee_payments
    WHERE student_id = p_student_id
      AND fee_structure_id = p_fee_structure_id
      AND status = 'completed';

    RETURN v_total_due - v_total_paid;
END $$

DELIMITER ;
