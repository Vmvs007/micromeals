from sqlalchemy.orm import Session
from . import models, schemas


def create_notification(db: Session, notification: schemas.NotificationCreate):
    db_notification = models.Notification(
        customer_id=notification.customer_id,
        type=notification.type.upper(),
        subject=notification.subject,
        message=notification.message,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notification(db: Session, notification_id: int):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()


def get_notifications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).offset(skip).limit(limit).all()


def get_notifications_by_customer(db: Session, customer_id: int):
    return db.query(models.Notification).filter(models.Notification.customer_id == customer_id).all()
