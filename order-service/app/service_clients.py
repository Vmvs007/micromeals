import os
import httpx
from fastapi import HTTPException

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8000")
RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")


def get_customer(customer_id: int) -> dict:
    try:
        response = httpx.get(f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}", timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Customer Service indisponível")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao consultar Customer Service")
    return response.json()


def get_restaurant(restaurant_id: int) -> dict:
    try:
        response = httpx.get(f"{RESTAURANT_SERVICE_URL}/restaurants/{restaurant_id}", timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Restaurant Service indisponível")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao consultar Restaurant Service")
    return response.json()


def get_menu_item(menu_item_id: int) -> dict:
    try:
        response = httpx.get(f"{RESTAURANT_SERVICE_URL}/menu-items/{menu_item_id}", timeout=5)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Restaurant Service indisponível")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Item de menu {menu_item_id} não encontrado")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao consultar Restaurant Service")
    return response.json()


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
        # Notificações são best-effort; não bloqueamos o fluxo principal se falhar
        pass
