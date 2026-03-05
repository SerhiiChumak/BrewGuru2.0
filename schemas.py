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

    model_config = {"from_attributes": True}


# Базова схема для страви (те, що бачимо в меню)
class MenuItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class MenuItem(MenuItemBase):
    id: int

    model_config = {"from_attributes": True}


# Схема для елемента в замовленні (страва + кількість)
class OrderItemSchema(BaseModel):
    menu_item_id: int
    quantity: int

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


class CafeBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    city: str
    working_hours: str
    has_wifi: bool
    has_parking: bool
    has_terrace: bool
    is_pet_friendly: bool

class CafeCreate(CafeBase):
    pass # Використовуємо для створення нового кафе (Адміном)

class Cafe(CafeBase):
    id: int

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "customer"


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}
