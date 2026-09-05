-- ============================================================================
-- Stored Procedures
-- ============================================================================
USE student_management_system;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- sp_enroll_student
-- Enrolls a student into a course offering inside a transaction: checks
-- seat capacity, prevents duplicate enrollment, and rolls back on failure.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_enroll_student $$
CREATE PROCEDURE sp_enroll_student (
    IN  p_student_id  INT,
    IN  p_offering_id INT,
    OUT p_status       VARCHAR(100)
)
BEGIN
    DECLARE v_capacity     INT;
    DECLARE v_taken        INT;
    DECLARE v_already      INT;
    DECLARE v_duplicate_key TINYINT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: transaction rolled back';
    END;

    START TRANSACTION;

    SELECT max_capacity INTO v_capacity
    FROM course_offerings
    WHERE offering_id = p_offering_id
    FOR UPDATE;

    IF v_capacity IS NULL THEN
        SET p_status = 'ERROR: offering not found';
        ROLLBACK;
    ELSE
        SELECT COUNT(*) INTO v_taken
        FROM enrollments
        WHERE offering_id = p_offering_id AND status = 'enrolled';

        SELECT COUNT(*) INTO v_already
        FROM enrollments
        WHERE offering_id = p_offering_id AND student_id = p_student_id
              AND status = 'enrolled';

        IF v_already > 0 THEN
            SET p_status = 'ERROR: student already enrolled';
            ROLLBACK;
        ELSEIF v_taken >= v_capacity THEN
            SET p_status = 'ERROR: offering is full';
            ROLLBACK;
        ELSE
            INSERT INTO enrollments (student_id, offering_id)
            VALUES (p_student_id, p_offering_id);
            SET p_status = 'SUCCESS';
            COMMIT;
        END IF;
    END IF;
END $$

-- ----------------------------------------------------------------------------
-- sp_record_fee_payment
-- Records a payment and reports outstanding balance for that fee structure,
-- all inside one transaction.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_record_fee_payment $$
CREATE PROCEDURE sp_record_fee_payment (
    IN  p_student_id       INT,
    IN  p_fee_structure_id INT,
    IN  p_amount            DECIMAL(10,2),
    IN  p_mode              VARCHAR(20),
    IN  p_txn_ref           VARCHAR(50),
    OUT p_balance_due       DECIMAL(10,2)
)
BEGIN
    DECLARE v_total_due DECIMAL(10,2);
    DECLARE v_total_paid DECIMAL(10,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_balance_due = -1;
    END;

    START TRANSACTION;

    SELECT (tuition_fee + hostel_fee + other_fee) INTO v_total_due
    FROM fee_structure WHERE fee_structure_id = p_fee_structure_id;

    INSERT INTO fee_payments (student_id, fee_structure_id, amount_paid, payment_mode, transaction_ref, status)
    VALUES (p_student_id, p_fee_structure_id, p_amount, p_mode, p_txn_ref, 'completed');

    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM fee_payments
    WHERE student_id = p_student_id
      AND fee_structure_id = p_fee_structure_id
      AND status = 'completed';

    SET p_balance_due = v_total_due - v_total_paid;

    COMMIT;
END $$

-- ----------------------------------------------------------------------------
-- sp_calculate_final_grade
-- Aggregates a student's weighted exam performance for one course offering
-- and inserts/updates a letter grade on each linked exam_results row's
-- companion summary (used by the grading trigger too).
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_calculate_final_grade $$
CREATE PROCEDURE sp_calculate_final_grade (
    IN p_student_id  INT,
    IN p_offering_id INT
)
BEGIN
    DECLARE v_weighted_pct DECIMAL(6,2);

    SELECT SUM( (er.marks_obtained / e.max_marks) * e.weightage_pct )
    INTO v_weighted_pct
    FROM exam_results er
    JOIN exams e ON e.exam_id = er.exam_id
    WHERE er.student_id = p_student_id
      AND e.offering_id = p_offering_id;

    SELECT
        p_student_id                                   AS student_id,
        p_offering_id                                  AS offering_id,
        COALESCE(v_weighted_pct, 0)                     AS weighted_percentage,
        CASE
            WHEN v_weighted_pct >= 90 THEN 'A+'
            WHEN v_weighted_pct >= 80 THEN 'A'
            WHEN v_weighted_pct >= 70 THEN 'B'
            WHEN v_weighted_pct >= 60 THEN 'C'
            WHEN v_weighted_pct >= 50 THEN 'D'
            ELSE 'F'
        END                                              AS letter_grade;
END $$

-- ----------------------------------------------------------------------------
-- sp_mark_attendance_bulk
-- Marks attendance for every enrolled student of an offering on a given
-- date in one transaction (used by the "mark whole class present" action).
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_mark_attendance_bulk $$
CREATE PROCEDURE sp_mark_attendance_bulk (
    IN p_offering_id INT,
    IN p_class_date   DATE,
    IN p_marked_by    INT,
    IN p_default_status VARCHAR(10)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO attendance (enrollment_id, class_date, status, marked_by)
    SELECT e.enrollment_id, p_class_date, p_default_status, p_marked_by
    FROM enrollments e
    WHERE e.offering_id = p_offering_id AND e.status = 'enrolled'
    ON DUPLICATE KEY UPDATE status = VALUES(status), marked_by = VALUES(marked_by);

    COMMIT;
END $$

DELIMITER ;
