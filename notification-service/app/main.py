from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from . import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification Service", description="Simulação de notificações da MicroMeals")

VALID_TYPES = ["EMAIL", "SMS", "APP"]


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification-service"}


@app.post("/notifications", response_model=schemas.NotificationResponse, status_code=201)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    if notification.type.upper() not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Valores possíveis: {VALID_TYPES}")
    db_notification = crud.create_notification(db, notification)
    print(f"[NOTIFICAÇÃO] Cliente #{notification.customer_id} | {notification.type} | {notification.subject}: {notification.message}")
    return db_notification


@app.get("/notifications", response_model=List[schemas.NotificationResponse])
def list_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_notifications(db, skip=skip, limit=limit)


@app.get("/notifications/{notification_id}", response_model=schemas.NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = crud.get_notification(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    return notification


@app.get("/customers/{customer_id}/notifications", response_model=List[schemas.NotificationResponse])
def get_customer_notifications(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_notifications_by_customer(db, customer_id)
