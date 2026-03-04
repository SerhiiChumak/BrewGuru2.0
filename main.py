from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cafe Service API")


@app.get("/menu", response_model=List[schemas.MenuItemBase])
def read_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).all()


@app.post("/orders")
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. Рахуємо ціну (дуже спрощено)
    items = db.query(models.MenuItem).filter(models.MenuItem.id.in_(order_data.item_ids)).all()
    total = sum([item.price for item in items])

    # 2. Створюємо запис замовлення
    new_order = models.Order(customer_name=order_data.customer_name, total_price=total)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {"message": "Order created!", "order_id": new_order.id, "total": total}

# Схема даних для фронтенда (Pydantic)
class CafeBase(BaseModel):
    id: int
    name: str
    city: str
    address: str
    has_wifi: bool
    is_pet_friendly: bool
    rating: float

# Імітація бази даних (для швидкого старту)
fake_cafes_db = [
    {
        "id": 1,
        "name": "Зерно",
        "city": "Київ",
        "address": "вул. Політехнічна, 5",
        "has_wifi": True,
        "is_pet_friendly": True,
        "rating": 4.9
    },
    {
        "id": 2,
        "name": "Кавовий куточок",
        "city": "Львів",
        "address": "Площа Ринок, 1",
        "has_wifi": False,
        "is_pet_friendly": True,
        "rating": 4.5
    },
]

@app.get("/cafes", response_model=List[CafeBase])
async def get_cafes(city: Optional[str] = None):
    """
    Повертає список кафе. Можна фільтрувати за містом.
    """
    if city:
        return [c for c in fake_cafes_db if c["city"].lower() == city.lower()]
    return fake_cafes_db

@app.get("/cafes/{cafe_id}")
async def get_cafe_details(cafe_id: int):
    """
    Повертає повну інформацію про конкретне кафе.
    """
    cafe = next((c for c in fake_cafes_db if c["id"] == cafe_id), None)
    return cafe or {"error": "Cafe not found"}
