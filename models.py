from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Time, Date
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    img = Column(String, nullable=True)  # аватарка
    phone = Column(String, nullable=True)

    email_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

    role = Column(String, default="customer")
    is_active = Column(Boolean, default=True)

    birthday = Column(Date, nullable=True)
    country = Column(String, nullable=True)

    # Сетінги (можна розширювати)
    is_private_profile = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)

    # Автоматичні дати
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    settings = relationship("UserSettings", back_populates="user", uselist=False)


class Cafe(Base):
    __tablename__ = "cafes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    address = Column(String)
    city = Column(String)
    working_hours = Column(String)
    has_wifi = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_terrace = Column(Boolean, default=False)
    is_pet_friendly = Column(Boolean, default=False)
    img = Column(String, nullable=True)

    # Зв'язок з меню
    menu = relationship("MenuItem", back_populates="cafe")
    opening_hours = relationship("OpeningHours", back_populates="cafe")


class OpeningHours(Base):
    __tablename__ = "opening_hours"
    id = Column(Integer, primary_key=True, index=True)
    cafe_id = Column(Integer, ForeignKey("cafes.id"))
    weekday = Column(Integer) # 1-7 (Пн-Нд)
    open_time = Column(String) # Наприклад "08:00"
    close_time = Column(String) # Наприклад "22:00"
    is_open = Column(Boolean, default=True)

    cafe = relationship("Cafe", back_populates="opening_hours")


class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cafe_id = Column(Integer, ForeignKey("cafes.id"))
    visit_time = Column(DateTime, server_default=func.now())

    user = relationship("User")
    cafe = relationship("Cafe")


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String, nullable=True)
    cafe_id = Column(Integer, ForeignKey("cafes.id"))

    cafe = relationship("Cafe", back_populates="menu")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float)
    status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey("users.id"))

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    cafe_id = Column(Integer, ForeignKey("cafes.id"))
    customer_name = Column(String)
    customer_phone = Column(String)
    reservation_time = Column(DateTime)
    number_of_people = Column(Integer)
    status = Column(String, default="pending")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    nearest_reservation_reminder = Column(Boolean, default=True)
    comment_reply_notification = Column(Boolean, default=True)
    saved_payment_methods = Column(Boolean, default=False)
    allow_analytics = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    cafe_id = Column(Integer, ForeignKey("cafes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer) # 1-5
    comment = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    replies = relationship("ReviewReply", back_populates="review")

class ReviewReply(Base):
    __tablename__ = "review_replies"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    review = relationship("Review", back_populates="replies")


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("reviews.id")) # ID коментаря
    reported_user_id = Column(Integer) # Кого репортуємо
    reporter_id = Column(Integer, ForeignKey("users.id")) # Хто репортує
    reason = Column(String)
    system_message = Column(String, default="Report received and pending moderation.")
    status = Column(String, default="Under review")
    # created_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Зв'язки для того, щоб витягнути дані одним запитом
    reporter = relationship("User")
    review = relationship("Review")
