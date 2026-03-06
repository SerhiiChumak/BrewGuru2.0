# from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Table, DateTime
# from sqlalchemy.orm import relationship
# from database import Base
#
#
#
# # class MenuItem(Base):
# #     __tablename__ = "menu_items"
# #
# #     id = Column(Integer, primary_key=True, index=True)
# #     name = Column(String)
# #     description = Column(String)
# #     price = Column(Float)
# #     is_available = Column(Boolean, default=True)
# #     cafe_id = Column(Integer)  # В ідеалі це ForeignKey на таблицю Cafe
#
#
# # class Order(Base):
# #     __tablename__ = "orders"
# #
# #     id = Column(Integer, primary_key=True, index=True)
# #     customer_name = Column(String)
# #     total_price = Column(Float)
# #     status = Column(String, default="pending")  # pending, confirmed, cancelled, ready
# #
# #     # Зв'язок: одне замовлення може мати багато страв
# #     items = relationship("OrderItem", back_populates="order")
#
#
# class OrderItem(Base):
#     __tablename__ = "order_items"
#     id = Column(Integer, primary_key=True)
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
#     quantity = Column(Integer)
#
#     order = relationship("Order", back_populates="items")
#
#
# class Reservation(Base):
#     __tablename__ = "reservations"
#
#     id = Column(Integer, primary_key=True, index=True)
#     cafe_id = Column(Integer) # В майбутньому ForeignKey
#     customer_name = Column(String)
#     customer_phone = Column(String)
#     reservation_time = Column(DateTime)
#     number_of_people = Column(Integer)
#     status = Column(String, default="pending") # pending, confirmed, rejected
#
#
# class Cafe(Base):
#     __tablename__ = "cafes"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     description = Column(String)
#     address = Column(String)
#     city = Column(String)
#     working_hours = Column(String)  # Наприклад: "09:00 - 21:00"
#
#     menu = relationship("MenuItem", back_populates="cafe")
#
#     # Додаткові штучки (Amenities)
#     has_wifi = Column(Boolean, default=False)
#     has_parking = Column(Boolean, default=False)
#     has_terrace = Column(Boolean, default=False)
#     is_pet_friendly = Column(Boolean, default=False)
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     role = Column(String, default="customer") # "admin", "manager", "customer"
#     is_active = Column(Boolean, default=True)
#
#
# class MenuItem(Base):
#     __tablename__ = "menu_items"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     price = Column(Float)
#     description = Column(String, nullable=True)
#     # Зв'язок: кожна страва належить кафе
#     cafe_id = Column(Integer, ForeignKey("cafes.id"))
#
#     cafe = relationship("Cafe", back_populates="menu")
#
#
# class Order(Base):
#     __tablename__ = "orders"
#     id = Column(Integer, primary_key=True, index=True)
#     customer_name = Column(String)  # Можна залишити для зручності або прибрати
#     total_price = Column(Float)
#     status = Column(String, default="pending")
#     # Зв'язок: замовлення належить користувачу
#     user_id = Column(Integer, ForeignKey("users.id"))
#
#     user = relationship("User")
#     items = relationship("OrderItem")


from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="customer")
    is_active = Column(Boolean, default=True)


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

    # Зв'язок з меню
    menu = relationship("MenuItem", back_populates="cafe")


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
