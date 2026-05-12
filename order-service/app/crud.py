from sqlalchemy.orm import Session
from . import models


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_orders_by_customer(db: Session, customer_id: int):
    return db.query(models.Order).filter(models.Order.customer_id == customer_id).all()


def create_order(db: Session, customer_id: int, restaurant_id: int, items_data: list, total: float):
    db_order = models.Order(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        total_amount=total,
        status="CREATED",
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in items_data:
        db_item = models.OrderItem(
            order_id=db_order.id,
            menu_item_id=item["menu_item_id"],
            name=item["name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            subtotal=item["subtotal"],
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(db: Session, order_id: int, status: str):
    db_order = get_order(db, order_id)
    if db_order is None:
        return None
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order
