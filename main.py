from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import models, schemas, auth
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cafe Service API")


@app.get("/menu", response_model=List[schemas.MenuItemBase])
def read_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).all()


# @app.post("/orders", response_model=schemas.Order)
# def create_order(
#         order_data: schemas.OrderCreate,
#         db: Session = Depends(get_db),
#         current_user: models.User = Depends(auth.get_current_user)  # Дістаємо юзера з токена
# ):
#     total = 0.0
#
#     # Створюємо замовлення, прив'язуючи його до current_user.id
#     new_order = models.Order(
#         customer_name=current_user.email,  # Або current_user.full_name, якщо є
#         total_price=0,
#         status="pending",
#         user_id=current_user.id  # ПРИВ'ЯЗКА ТУТ
#     )
#     db.add(new_order)
#     db.flush()
#
#     for item in order_data.items:
#         menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
#         if not menu_item:
#             raise HTTPException(status_code=404, detail=f"Item {item.menu_item_id} not found")
#
#         total += menu_item.price * item.quantity
#         oi = models.OrderItem(
#             order_id=new_order.id,
#             menu_item_id=menu_item.id,
#             quantity=item.quantity
#         )
#         db.add(oi)
#
#     new_order.total_price = total
#     db.commit()
#     db.refresh(new_order)
#     return new_order

@app.post("/orders", response_model=schemas.Order)
def create_order(
        order_data: schemas.OrderCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Беремо першу страву, щоб дізнатися, з якого кафе йде замовлення
    first_item = db.query(models.MenuItem).filter(models.MenuItem.id == order_data.items[0].menu_item_id).first()
    if not first_item:
        raise HTTPException(status_code=404, detail="First menu item not found")

    target_cafe_id = first_item.cafe_id
    total = 0.0

    # 2. Перевіряємо всі інші страви
    for item in order_data.items:
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()

        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Item {item.menu_item_id} not found")

        # ОСЬ ТУТ ПЕРЕВІРКА:
        if menu_item.cafe_id != target_cafe_id:
            raise HTTPException(
                status_code=400,
                detail="You can only order items from one cafe at a time"
            )

        total += menu_item.price * item.quantity

    # 3. Якщо все ок — створюємо замовлення
    new_order = models.Order(
        total_price=total,
        status="pending",
        user_id=current_user.id
    )
    db.add(new_order)
    db.flush()

    # Додаємо зв'язки...
    for item in order_data.items:
        oi = models.OrderItem(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        )
        db.add(oi)

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


@app.get("/cafes", response_model=List[schemas.Cafe])
def get_cafes(city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Cafe)

    if city:
        # Фільтруємо по місту (незалежно від регістру)
        query = query.filter(models.Cafe.city.ilike(f"%{city}%"))

    return query.all()


@app.get("/cafes/{cafe_id}", response_model=schemas.Cafe)
def get_cafe(cafe_id: int, db: Session = Depends(get_db)):
    cafe = db.query(models.Cafe).filter(models.Cafe.id == cafe_id).first()
    if not cafe:
        raise HTTPException(status_code=404, detail="Cafe not found")
    return cafe


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

    new_res = models.Reservation(**res_data.model_dump())
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res


@app.get("/reservations")
def get_reservations(db: Session = Depends(get_db)):
    return db.query(models.Reservation).all()


@app.put("/cafes/{cafe_id}", response_model=schemas.Cafe)
def update_cafe(
    cafe_id: int,
    updated_cafe: schemas.CafeCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_admin_user)
):
    db_cafe = db.query(models.Cafe).filter(models.Cafe.id == cafe_id).first()

    if not db_cafe:
        raise HTTPException(status_code=404, detail="Cafe not found")

    # Оновлюємо кожне поле
    for key, value in updated_cafe.model_dump().items():
        setattr(db_cafe, key, value)

    db.commit()
    db.refresh(db_cafe)
    return db_cafe


# @app.post("/register", response_model=schemas.UserOut)
# def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
#     # Перевіряємо, чи такий email вже існує
#     db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#
#     # Хешуємо пароль перед збереженням!
#     hashed_pwd = auth.get_password_hash(user_data.password)
#
#     new_user = models.User(
#         email=user_data.email,
#         hashed_password=hashed_pwd,
#         role=user_data.role
#     )
#
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

@app.post("/register", response_model=schemas.UserOut)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Перевіряємо, чи такий email вже існує
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Хешуємо пароль
    hashed_pwd = auth.get_password_hash(user_data.password)

    # 3. Створюємо юзера з усіма новими полями
    # Використовуємо model_dump() для зручності, але виключаємо пароль
    user_dict = user_data.model_dump(exclude={"password"})
    new_user = models.User(
        hashed_password=hashed_pwd,
        **user_dict
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token")
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    # 1. Шукаємо юзера за email (у формі це поле username)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    # 2. Перевіряємо чи юзер існує і чи правильний пароль
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Створюємо токен
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role},  # Додаємо роль у токен!
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/cafes", response_model=schemas.Cafe)
def create_cafe(
    cafe: schemas.CafeCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_admin_user) # ОСЬ ТУТ МАГІЯ
):
    """Створювати кафе тепер може ТІЛЬКИ адмін"""
    new_cafe = models.Cafe(**cafe.model_dump())
    db.add(new_cafe)
    db.commit()
    db.refresh(new_cafe)
    return new_cafe


@app.post("/menu-items", response_model=schemas.MenuItem)
def create_menu_item(
        item: schemas.MenuItemCreate,
        db: Session = Depends(get_db),
        admin: models.User = Depends(auth.get_admin_user)  # Тільки адмін
):
    # Перевіряємо, чи існує таке кафе
    cafe = db.query(models.Cafe).filter(models.Cafe.id == item.cafe_id).first()
    if not cafe:
        raise HTTPException(status_code=404, detail="Cafe not found")

    new_item = models.MenuItem(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.get("/cafes/{cafe_id}/menu", response_model=List[schemas.MenuItem])
def get_cafe_menu(cafe_id: int, db: Session = Depends(get_db)):
    # Шукаємо всі страви, де cafe_id збігається з ID в URL
    menu_items = db.query(models.MenuItem).filter(models.MenuItem.cafe_id == cafe_id).all()

    if not menu_items:
        # Можна або повернути пустий список, або помилку, якщо кафе не існує
        cafe = db.query(models.Cafe).filter(models.Cafe.id == cafe_id).first()
        if not cafe:
            raise HTTPException(status_code=404, detail="Cafe not found")

    return menu_items


@app.get("/cafes/{cafe_id}/orders", response_model=List[schemas.Order])
def get_cafe_orders(
        cafe_id: int,
        db: Session = Depends(get_db),
        manager: models.User = Depends(auth.get_manager_user)
):
    # Тут ми кажемо: "Дай мені замовлення, в яких є хоча б одна страва з цього кафе"
    orders = db.query(models.Order).join(models.OrderItem).join(models.MenuItem).filter(
        models.MenuItem.cafe_id == cafe_id
    ).distinct().all()

    return orders

@app.get("/users/me", response_model=schemas.UserOut)
def get_user_profile(current_user: models.User = Depends(auth.get_current_user)):
    """Повертає дані профілю поточного юзера для фронтенда"""
    return current_user
