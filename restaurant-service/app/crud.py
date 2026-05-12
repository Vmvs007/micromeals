from sqlalchemy.orm import Session
from . import models, schemas


# --- Restaurants ---

def get_restaurant(db: Session, restaurant_id: int):
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()


def get_restaurants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Restaurant).offset(skip).limit(limit).all()


def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    db_restaurant = models.Restaurant(**restaurant.model_dump())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def update_restaurant(db: Session, restaurant_id: int, restaurant: schemas.RestaurantUpdate):
    db_restaurant = get_restaurant(db, restaurant_id)
    if db_restaurant is None:
        return None
    for field, value in restaurant.model_dump(exclude_unset=True).items():
        setattr(db_restaurant, field, value)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def delete_restaurant(db: Session, restaurant_id: int):
    db_restaurant = get_restaurant(db, restaurant_id)
    if db_restaurant is None:
        return None
    db.delete(db_restaurant)
    db.commit()
    return db_restaurant


# --- Menu Items ---

def get_menu_item(db: Session, menu_item_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()


def get_menu_items_by_restaurant(db: Session, restaurant_id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == restaurant_id).all()


def create_menu_item(db: Session, restaurant_id: int, item: schemas.MenuItemCreate):
    db_item = models.MenuItem(**item.model_dump(), restaurant_id=restaurant_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_menu_item(db: Session, menu_item_id: int, item: schemas.MenuItemUpdate):
    db_item = get_menu_item(db, menu_item_id)
    if db_item is None:
        return None
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item
