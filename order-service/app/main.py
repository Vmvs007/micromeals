from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from . import models, schemas, crud
from .service_clients import get_customer, get_restaurant, get_menu_item, send_notification

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service", description="Gestão de encomendas da MicroMeals")

VALID_STATUSES = ["CREATED", "PAID", "PREPARING", "DELIVERED", "CANCELLED"]

# Transições de estado permitidas
STATUS_TRANSITIONS = {
    "CREATED": ["PAID", "CANCELLED"],
    "PAID": ["PREPARING", "CANCELLED"],
    "PREPARING": ["DELIVERED", "CANCELLED"],
    "DELIVERED": [],
    "CANCELLED": [],
}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "order-service"}


@app.post("/orders", response_model=schemas.OrderResponse, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. Validar cliente
    customer = get_customer(order.customer_id)

    # 2. Validar restaurante
    restaurant = get_restaurant(order.restaurant_id)
    if not restaurant["active"]:
        raise HTTPException(status_code=400, detail="Restaurante não está ativo")

    # 3. Validar e recolher dados dos itens
    items_data = []
    for item_request in order.items:
        menu_item = get_menu_item(item_request.menu_item_id)

        # Verificar se o item pertence ao restaurante
        if menu_item["restaurant_id"] != order.restaurant_id:
            raise HTTPException(
                status_code=400,
                detail=f"Item {item_request.menu_item_id} não pertence ao restaurante {order.restaurant_id}"
            )

        # Verificar se o item está disponível
        if not menu_item["available"]:
            raise HTTPException(
                status_code=400,
                detail=f"Item '{menu_item['name']}' não está disponível"
            )

        subtotal = round(menu_item["price"] * item_request.quantity, 2)
        items_data.append({
            "menu_item_id": menu_item["id"],
            "name": menu_item["name"],
            "unit_price": menu_item["price"],
            "quantity": item_request.quantity,
            "subtotal": subtotal,
        })

    # 4. Calcular total
    total = round(sum(i["subtotal"] for i in items_data), 2)

    # 5. Guardar encomenda
    db_order = crud.create_order(db, order.customer_id, order.restaurant_id, items_data, total)

    # 6. Notificar cliente
    send_notification(
        customer_id=order.customer_id,
        subject="Encomenda criada",
        message=f"A sua encomenda #{db_order.id} foi criada com sucesso. Total: {total}€"
    )

    return db_order


@app.get("/orders", response_model=List[schemas.OrderResponse])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)


@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada")
    return order


@app.get("/customers/{customer_id}/orders", response_model=List[schemas.OrderResponse])
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_orders_by_customer(db, customer_id)


@app.patch("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, body: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    new_status = body.status.upper()

    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Valores possíveis: {VALID_STATUSES}")

    order = crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada")

    allowed = STATUS_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível mudar de '{order.status}' para '{new_status}'. Transições permitidas: {allowed}"
        )

    updated = crud.update_order_status(db, order_id, new_status)

    # Notificar cliente sobre a mudança de estado
    send_notification(
        customer_id=order.customer_id,
        subject="Estado da encomenda atualizado",
        message=f"A sua encomenda #{order_id} está agora em estado: {new_status}"
    )

    return updated
