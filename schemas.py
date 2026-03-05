from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class MenuItemBase(BaseModel):
    name: str
    price: float
    description: str


class OrderCreate(BaseModel):
    customer_name: str
    item_ids: List[int] # Список ID страв, які хоче юзер


class ReservationCreate(BaseModel):
    cafe_id: int
    customer_name: str
    customer_phone: str
    reservation_time: datetime
    number_of_people: int


class Reservation(ReservationCreate):
    id: int
    status: str

    class Config:
        orm_mode = True


# Базова схема для страви (те, що бачимо в меню)
class MenuItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class MenuItem(MenuItemBase):
    id: int

    class Config:
        orm_mode = True


# Схема для елемента в замовленні (страва + кількість)
class OrderItemSchema(BaseModel):
    menu_item_id: int
    quantity: int

    class Config:
        orm_mode = True


# Схема для створення замовлення (те, що присилає фронтенд)
class OrderCreate(BaseModel):
    customer_name: str
    items: List[OrderItemSchema]  # Список id страв та їх кількості


# Повна схема замовлення (те, що ми повертаємо фронтенду)
class Order(BaseModel):
    id: int
    customer_name: str
    total_price: float
    status: str

    # Тут ми можемо додати список самих страв, якщо налаштуємо релейшни

    class Config:
        orm_mode = True