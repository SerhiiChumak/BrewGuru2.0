from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
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


class MenuItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    cafe_id: int


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
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[date] = None
    country: Optional[str] = None
    role: Optional[str] = "customer"

    # Це налаштування дозволить фронтенду присилати JSON з camelCase
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(s.split("_"))
        )
    )


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    img: Optional[str] = None
    phone: Optional[str] = None


# Схема для відповіді фронтенду
class UserOut(UserBase):
    id: int
    email_verified: bool
    two_factor_enabled: bool
    created_at: datetime
    updated_at: datetime

    # Магія для відповідності фронтенд-формату (camelCase)
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(s.split("_"))
        )
    )


class UserWithToken(BaseModel):
    user: UserOut
    access_token: str
    token_type: str


class UserSettings(BaseModel):
    firstName: str
    lastName: str
    email: str
    birthday: Optional[date]
    country: Optional[str]
    isPrivateProfile: bool
    notificationsEnabled: bool

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize()
            if i > 0
            else word
            for i, word in enumerate(s.split("_")))
    )


class UserSettingsSchema(BaseModel):
    email_notifications: bool
    push_notifications: bool
    nearest_reservation_reminder: bool
    comment_reply_notification: bool
    saved_payment_methods: bool
    allow_analytics: bool

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(s.split("_"))
        )
    )


class OpeningHoursOut(BaseModel):
    id: int
    weekday: int
    open_time: str
    close_time: str
    is_open: bool
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize() if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


class CafeInVisit(BaseModel):
    id: int
    name: str
    img: Optional[str]
    address: str
    opening_hours: List[OpeningHoursOut]
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize()
                                          if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


class VisitItem(BaseModel):
    id: int
    cafe: CafeInVisit
    time: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class HistoryResponse(BaseModel):
    id: int
    user_id: int
    date: str
    items: List[VisitItem]
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize()
                                          if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


# Спрощена схема юзера для відгуків
class UserShort(BaseModel):
    id: int
    img: Optional[str]
    first_name: str
    last_name: str
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize()
                                          if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


class ReviewReplyOut(BaseModel):
    id: int
    review_id: int
    user: UserShort
    comment: str
    likes: int
    dislikes: int
    created_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize()
                                          if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


class ReviewOut(BaseModel):
    id: int
    cafe_id: int
    user: UserShort
    rating: int
    comment: str
    likes: int
    dislikes: int
    created_at: datetime
    replies: List[ReviewReplyOut] = []
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize()
                                          if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


class ReviewCreate(BaseModel):
    rating: int
    comment: str

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(s.split("_"))
        )
    )


class ReviewReplyCreate(BaseModel):
    comment: str

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(s.split("_"))
        )
    )


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
