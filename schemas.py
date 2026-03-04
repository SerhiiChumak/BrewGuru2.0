from pydantic import BaseModel
from typing import List

class MenuItemBase(BaseModel):
    name: str
    price: float
    description: str

class OrderCreate(BaseModel):
    customer_name: str
    item_ids: List[int] # Список ID страв, які хоче юзер
