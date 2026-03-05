from fastapi import FastAPI, Depends, HTTPException, Body
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


# @app.post("/orders")
# def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
#     # 1. Рахуємо ціну (дуже спрощено)
#     items = db.query(models.MenuItem).filter(models.MenuItem.id.in_(order_data.item_ids)).all()
#     total = sum([item.price for item in items])
#
#     # 2. Створюємо запис замовлення
#     new_order = models.Order(customer_name=order_data.customer_name, total_price=total)
#     db.add(new_order)
#     db.commit()
#     db.refresh(new_order)
#
#     return {"message": "Order created!", "order_id": new_order.id, "total": total}
@app.post("/orders", response_model=schemas.Order)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    total = 0.0
    order_items = []

    # 1. Створюємо об'єкт замовлення (спочатку без суми)
    new_order = models.Order(
        customer_name=order_data.customer_name,
        total_price=0,
        status="pending"
    )
    db.add(new_order)
    db.flush()  # flush дозволяє отримати ID замовлення, не завершуючи транзакцію

    # 2. Обробляємо кожну страву в замовленні
    for item in order_data.items:
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Item {item.menu_item_id} not found")

        # Рахуємо суму: ціна страви * кількість
        total += menu_item.price * item.quantity

        # Створюємо запис у проміжній таблиці order_items
        oi = models.OrderItem(
            order_id=new_order.id,
            menu_item_id=menu_item.id,
            quantity=item.quantity
        )
        db.add(oi)

    # 3. Оновлюємо фінальну суму замовлення
    new_order.total_price = total
    db.commit()
    db.refresh(new_order)

    return new_order


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


# Отримати всі замовлення (для менеджера)
@app.get("/orders", response_model=List[schemas.Order])  # Треба додати схему Order в schemas.py
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


# Змінити статус замовлення (Підтвердити/Скасувати)
@app.patch("/orders/{order_id}/status")
def update_order_status(
        order_id: int,
        status: str = Body(..., embed=True),  # Очікуємо статус: "confirmed" або "cancelled"
        db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    return {"message": f"Order status updated to {status}", "order_id": order_id}


@app.post("/reservations", response_model=schemas.Reservation)
def create_reservation(res_data: schemas.ReservationCreate, db: Session = Depends(get_db)):
    # Можна додати перевірку: чи не в минулому часі бронювання
    if res_data.reservation_time < datetime.now():
        raise HTTPException(status_code=400, detail="Cannot book in the past")

    new_res = models.Reservation(**res_data.dict())
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res


@app.get("/reservations")
def get_reservations(db: Session = Depends(get_db)):
    return db.query(models.Reservation).all()
