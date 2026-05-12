from sqlalchemy.orm import Session
from . import models


def get_payment(db: Session, payment_id: int):
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()


def get_payments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Payment).offset(skip).limit(limit).all()


def get_payments_by_order(db: Session, order_id: int):
    return db.query(models.Payment).filter(models.Payment.order_id == order_id).all()


def create_payment(db: Session, order_id: int, amount: float, payment_method: str, status: str):
    db_payment = models.Payment(
        order_id=order_id,
        amount=amount,
        payment_method=payment_method,
        status=status,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
