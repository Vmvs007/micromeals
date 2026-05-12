from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from . import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Service", description="Gestão de restaurantes e menus da MicroMeals")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "restaurant-service"}


# --- Restaurants ---

@app.post("/restaurants", response_model=schemas.RestaurantResponse, status_code=201)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    return crud.create_restaurant(db, restaurant)


@app.get("/restaurants", response_model=List[schemas.RestaurantResponse])
def list_restaurants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_restaurants(db, skip=skip, limit=limit)


@app.get("/restaurants/{restaurant_id}", response_model=schemas.RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = crud.get_restaurant(db, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    return restaurant


@app.put("/restaurants/{restaurant_id}", response_model=schemas.RestaurantResponse)
def update_restaurant(restaurant_id: int, restaurant: schemas.RestaurantUpdate, db: Session = Depends(get_db)):
    updated = crud.update_restaurant(db, restaurant_id, restaurant)
    if updated is None:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    return updated


@app.delete("/restaurants/{restaurant_id}", response_model=schemas.RestaurantResponse)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_restaurant(db, restaurant_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    return deleted


# --- Menu Items ---

@app.post("/restaurants/{restaurant_id}/menu-items", response_model=schemas.MenuItemResponse, status_code=201)
def create_menu_item(restaurant_id: int, item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    restaurant = crud.get_restaurant(db, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    return crud.create_menu_item(db, restaurant_id, item)


@app.get("/restaurants/{restaurant_id}/menu-items", response_model=List[schemas.MenuItemResponse])
def list_menu_items(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = crud.get_restaurant(db, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    return crud.get_menu_items_by_restaurant(db, restaurant_id)


@app.get("/menu-items/{menu_item_id}", response_model=schemas.MenuItemResponse)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    item = crud.get_menu_item(db, menu_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item de menu não encontrado")
    return item


@app.put("/menu-items/{menu_item_id}", response_model=schemas.MenuItemResponse)
def update_menu_item(menu_item_id: int, item: schemas.MenuItemUpdate, db: Session = Depends(get_db)):
    updated = crud.update_menu_item(db, menu_item_id, item)
    if updated is None:
        raise HTTPException(status_code=404, detail="Item de menu não encontrado")
    return updated
