from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from . import models, schemas, crud
from .service_clients import get_order, update_order_status, send_notification

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service", description="Simulação de pagamentos da MicroMeals")

VALID_METHODS = ["MBWAY", "CARD", "CASH"]

# Regra de simulação: encomendas até 50€ são aprovadas, acima são rejeitadas
APPROVAL_LIMIT = 50.0


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "payment-service"}


@app.post("/payments", response_model=schemas.PaymentResponse, status_code=201)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    method = payment.payment_method.upper()
    if method not in VALID_METHODS:
        raise HTTPException(status_code=400, detail=f"Método inválido. Valores possíveis: {VALID_METHODS}")

    # 1. Consultar encomenda no order-service
    order = get_order(payment.order_id)

    if order["status"] != "CREATED":
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível pagar uma encomenda com estado '{order['status']}'"
        )

    # 2. Simular aprovação/rejeição com base no valor
    amount = order["total_amount"]
    status = "APPROVED" if amount <= APPROVAL_LIMIT else "REJECTED"

    # 3. Guardar pagamento
    db_payment = crud.create_payment(db, payment.order_id, amount, method, status)

    # 4. Se aprovado, atualizar estado da encomenda para PAID
    if status == "APPROVED":
        update_order_status(payment.order_id, "PAID")
        send_notification(
            customer_id=order["customer_id"],
            subject="Pagamento aprovado",
            message=f"O pagamento de {amount}€ para a encomenda #{payment.order_id} foi aprovado via {method}."
        )
    else:
        send_notification(
            customer_id=order["customer_id"],
            subject="Pagamento rejeitado",
            message=f"O pagamento de {amount}€ para a encomenda #{payment.order_id} foi rejeitado. O valor excede {APPROVAL_LIMIT}€."
        )

    return db_payment


@app.get("/payments", response_model=List[schemas.PaymentResponse])
def list_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_payments(db, skip=skip, limit=limit)


@app.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = crud.get_payment(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return payment


@app.get("/orders/{order_id}/payments", response_model=List[schemas.PaymentResponse])
def get_payments_by_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_payments_by_order(db, order_id)
