import os
import httpx
from fastapi import HTTPException

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")


def get_order(order_id: int) -> dict:
    try:
        response = httpx.get(f"{ORDER_SERVICE_URL}/orders/{order_id}", timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Order Service indisponível")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao consultar Order Service")
    return response.json()


def update_order_status(order_id: int, status: str):
    try:
        response = httpx.patch(
            f"{ORDER_SERVICE_URL}/orders/{order_id}/status",
            json={"status": status},
            timeout=5
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Order Service indisponível")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao atualizar estado da encomenda")


def send_notification(customer_id: int, subject: str, message: str):
    payload = {
        "customer_id": customer_id,
        "type": "APP",
        "subject": subject,
        "message": message,
    }
    try:
        httpx.post(f"{NOTIFICATION_SERVICE_URL}/notifications", json=payload, timeout=5)
    except httpx.RequestError:
        pass
