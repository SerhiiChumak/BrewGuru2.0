from pydantic import BaseModel, EmailStr, ConfigDict, model_validator, Field
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
    phone: Optional[str] = None
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
    open_time: Optional[str]
    close_time: Optional[str]
    is_open: bool
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda s: "".join(word.capitalize() if i > 0
                                          else word for i, word in enumerate(
            s.split("_")))
    )


# class OpeningHourOut(BaseModel):
#     weekday: int
#     open_time: Optional[str]
#     close_time: Optional[str]
#     is_open: bool
#
#     model_config = ConfigDict(from_attributes=True)


class TableOut(BaseModel):
    id: int
    name: str
    seats: int

    model_config = ConfigDict(from_attributes=True)


class CafeOut(BaseModel):
    id: int
    name: str
    address: str
    # Додай Optional та = None до всіх полів, яких може не бути в базі
    working_hours: Optional[str] = None
    image_url: Optional[str] = None
    phone: Optional[str] = None

    opening_hours: List[OpeningHoursOut] = []

    class Config:
        from_attributes = True


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


class ReportCreate(BaseModel):
    target_id: int
    reason: str


class ReportOut(BaseModel):
    id: int
    targetId: int = Field(alias="target_id")
    reportedUserId: int = Field(alias="reported_user_id")
    reportedBy: dict
    createdAt: datetime = Field(alias="created_at")
    comment: str
    reportReason: str = Field(alias="reason")
    systemMessage: str = Field(alias="system_message")
    status: str

    model_config = {"from_attributes": True, "populate_by_name": True}

    @model_validator(mode='before')
    @classmethod
    def format_report_data(cls, data):
        # Якщо дані прийшли з бази (об'єкт SQLAlchemy), перетворюємо їх
        if hasattr(data, 'id'):
            return {
                "id": data.id,
                "target_id": data.target_id,
                "reported_user_id": data.reported_user_id,
                "reportedBy": {
                    "id": data.reporter.id,
                    "firstName": data.reporter.first_name,
                    "lastName": data.reporter.last_name
                },
                "created_at": data.created_at,
                "comment": data.review.comment, # Дістаємо текст коментаря через зв'язок
                "reason": data.reason,
                "system_message": data.system_message,
                "status": data.status
            }
        return data
