from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role, get_current_user
from models.schemas import FeePaymentRequest, FeeBalanceOut

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("/structure")
def list_fee_structures(
    program_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    query = "SELECT * FROM fee_structure WHERE 1=1"
    params = {}
    if program_id:
        query += " AND program_id = :program_id"
        params["program_id"] = program_id
    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


@router.get("/balance/{student_id}", response_model=list[FeeBalanceOut])
def student_fee_balance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] == "student":
        owner_check = db.execute(
            text("SELECT student_id FROM students WHERE user_id = :uid"),
            {"uid": current_user["user_id"]},
        ).first()
        if not owner_check or owner_check[0] != student_id:
            raise HTTPException(status_code=403, detail="Cannot view another student's fee balance")

    rows = db.execute(
        text("SELECT * FROM vw_student_fee_balance WHERE student_id = :sid"),
        {"sid": student_id},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.post("/pay", status_code=201)
def pay_fee(
    payload: FeePaymentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "student")),
):
    """
    Calls sp_record_fee_payment, which inserts the payment and computes the
    resulting balance inside one transaction (rolled back on any failure).
    """
    if current_user["role"] == "student":
        owner_check = db.execute(
            text("SELECT student_id FROM students WHERE user_id = :uid"),
            {"uid": current_user["user_id"]},
        ).first()
        if not owner_check or owner_check[0] != payload.student_id:
            raise HTTPException(status_code=403, detail="Cannot pay fees for another student")

    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    try:
        cursor.callproc(
            "sp_record_fee_payment",
            (
                payload.student_id,
                payload.fee_structure_id,
                payload.amount,
                payload.payment_mode,
                payload.transaction_ref,
                0,
            ),
        )
        cursor.execute("SELECT @_sp_record_fee_payment_5")
        balance_due = cursor.fetchone()[0]
        raw_conn.commit()
    except Exception as exc:
        raw_conn.rollback()
        raise HTTPException(status_code=400, detail=f"Payment failed: {exc}")
    finally:
        cursor.close()

    if balance_due is not None and float(balance_due) < 0:
        raise HTTPException(status_code=400, detail="Payment could not be processed")

    return {"message": "Payment recorded", "balance_due": balance_due}
