from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Cafe Service API")

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
