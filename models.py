from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Table, DateTime
from sqlalchemy.orm import relationship
from database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    is_available = Column(Boolean, default=True)
    cafe_id = Column(Integer)  # В ідеалі це ForeignKey на таблицю Cafe


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    total_price = Column(Float)
    status = Column(String, default="pending")  # pending, confirmed, cancelled, ready

    # Зв'язок: одне замовлення може мати багато страв
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
    cafe_id = Column(Integer) # В майбутньому ForeignKey
    customer_name = Column(String)
    customer_phone = Column(String)
    reservation_time = Column(DateTime)
    number_of_people = Column(Integer)
    status = Column(String, default="pending") # pending, confirmed, rejected
